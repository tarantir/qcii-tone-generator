#!/usr/bin/env python3
"""
QCII Two-Tone + Warble Tone Generator — Desktop GUI
----------------------------------------------------
Tkinter front end for qcii_tone_gen.py. Lets you set A/B/C/D tone
frequencies, timing, and output path, then generate and play back the
resulting WAV without touching the command line.

Conveniences over the raw script:
  - A QCII address (A/B), picked from three dropdowns (Table 1 group-
    assignment digit + two tone position digits), can populate the A/B
    frequency fields directly, using the same group/position logic as
    generate_all_pairs.py. A/B default to QCII address 000.
  - The warble tail is on by default with an independent C/D pair
    (1500/800 Hz) and can be suppressed with one checkbox.
  - C/D can also be populated from a Motorola Centracom "Alert 1/2/3"
    style preset (Alert 2 matches the 1500/800 Hz default).
  - Play always (re)generates from the current field values first, so a
    single click renders and previews the page.
  - Reset restores every field to its default.
  - Durations, sample rate, and amplitude live in a secondary "Config"
    window, keeping the main window focused on tone selection.
  - Visualize draws a timeline of the page that would be generated right
    now, from the current main + config values (including suppress/
    warble-only), without writing a WAV file.

Usage:
  python3 qcii_gui.py
"""

import os
import platform
import shutil
import subprocess
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, filedialog, messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qcii_tone_gen import build_page, write_wav, default_output_dir
from generate_all_pairs import GROUP_ASSIGNMENT, POSITION_DIGITS, tone_at_position

DEFAULT_OUT = os.path.join(default_output_dir(), "qcii_page.wav")
DEFAULT_C = "1500"
DEFAULT_D = "800"

# A/B default to QCII address 000: digit1 '0' -> GROUP_ASSIGNMENT groups, position
# digit '0' -> index 9 in each group (see tone_at_position).
_default_group_a, _default_group_b = GROUP_ASSIGNMENT["0"]
DEFAULT_A = str(tone_at_position(_default_group_a, "0"))
DEFAULT_B = str(tone_at_position(_default_group_b, "0"))

MAIN_FIELDS = [
    ("a", "A tone (Hz)", DEFAULT_A),
    ("b", "B tone (Hz)", DEFAULT_B),
    ("c", "C tone (Hz, blank = reuse A)", DEFAULT_C),
    ("d", "D tone (Hz, blank = reuse B)", DEFAULT_D),
]

CONFIG_FIELDS = [
    ("a_dur", "A duration (s)", "1.0"),
    ("b_dur", "B duration (s)", "3.0"),
    ("gap", "A/B gap (s)", "0.0"),
    ("warble_dur", "Alert duration (s)", "3.0"),
    ("warble_seg", "Alert segment length (s)", "0.25"),
    ("pre_silence", "Pre-silence (s)", "0.25"),
    ("post_silence", "Post-silence (s)", "0.25"),
    ("rate", "Sample rate (Hz)", "44100"),
    ("amplitude", "Amplitude (0.0-1.0)", "0.8"),
]

FIELDS = MAIN_FIELDS + CONFIG_FIELDS

WARBLE_KEYS = ("c", "d", "warble_dur", "warble_seg")
PAGE_KEYS = ("a_dur", "b_dur", "gap")
GROUP_DIGIT_ORDER = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A"]
POSITION_DIGIT_ORDER = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

# Motorola Centracom console alert styles (per RadioReference/Batboard forum
# consensus - console vendors vary slightly on the Alert 2 low tone, 800 vs
# 900 Hz; this project already used 800 Hz as its C/D default so that's kept
# here for consistency). Alert 1 is a steady tone (C == D); Alert 3 is a
# single tone keyed on/off (D == 0 Hz -> silence during the "low" segments).
ALERT_PRESETS = {
    "Alert 1 (steady 1000 Hz)": (1000.0, 1000.0),
    "Alert 2 (1500/800 Hz warble, default)": (1500.0, 800.0),
    "Alert 3 (1000 Hz beeping)": (1000.0, 0.0),
}
DEFAULT_ALERT = "Alert 2 (1500/800 Hz warble, default)"

DISCLAIMER_TEXT = (
    "This tool generates reference tones for testing pager/decoder programming "
    "(Minitor V, MOTOTRBO QCII decode, RXC-2000/RDC station alerting boxes, DIY "
    "tone decoders, etc).\n\n"
    "It is for testing purposes only and is not a dispatch or alerting system."
)

# Non-frequency dropdown entries: these drive other widgets/fields instead
# of setting a literal C/D tone pair, so apply_alert_preset() special-cases
# them rather than looking them up in ALERT_PRESETS.
SAME_AS_AB_OPTION = "Same as A/B (reuse page tones)"
SUPPRESS_ALERT_OPTION = "Suppress Alert (no C/D warble)"
ALERT_OPTIONS = list(ALERT_PRESETS.keys()) + [SAME_AS_AB_OPTION, SUPPRESS_ALERT_OPTION]

# Color tokens. signal-amber is the one accent thread running through the
# app: it's the "Warble C" viz color, the Generate button, and (via the
# viz's dark console treatment) the thing this whole tool is about --
# the alert tone. Everything else stays quiet/native.
COLOR_INK = "#1C1F26"
COLOR_SLATE = "#5B6472"
COLOR_ACCENT = "#EF9F27"
COLOR_ACCENT_ACTIVE = "#E08A12"
COLOR_CONSOLE_BG = "#2E323C"
COLOR_CONSOLE_TEXT = "#E7E4DC"

# Fill colors for the timeline visualization canvas -- tuned bright/saturated
# for the dark "console readout" background (see _build_viz_window), not the
# plain white a generic form control would use.
VIZ_COLORS = {
    "silence": "#565C68",
    "a": "#4FA8FF",
    "b": "#2FE3A8",
    "c": COLOR_ACCENT_ACTIVE,
    "d": "#B58CFF",
}
VIZ_LEGEND_LABELS = {"silence": "Silence", "a": "A Tone", "b": "B Tone", "c": "Warble C", "d": "Warble D"}


def _first_available_font(candidates):
    """Return the first font family from candidates installed on this
    system, falling back to the last (generic) candidate if none match."""
    available = set(tkfont.families())
    for name in candidates:
        if name in available:
            return name
    return candidates[-1]


def group_digit_choices():
    """QCII address first-digit choices, 0 first, in natural digit/letter order."""
    return [d for d in GROUP_DIGIT_ORDER if d in GROUP_ASSIGNMENT]


def position_digit_choices():
    """QCII address position-digit choices, 0 first, in natural digit order."""
    return [d for d in POSITION_DIGIT_ORDER if d in POSITION_DIGITS]


def capcode_to_ab(capcode):
    """Look up A/B tone frequencies for a 3-char QCII address (digit1 = group
    assignment per Table 1, digit2/digit3 = tone position within each group).
    Returns (a_freq, b_freq, group_a, group_b)."""
    capcode = capcode.strip().upper()
    if len(capcode) != 3:
        raise ValueError("QCII address must be exactly 3 characters, e.g. 319.")
    d1, d2, d3 = capcode[0], capcode[1], capcode[2]
    if d1 not in GROUP_ASSIGNMENT:
        raise ValueError(f"Invalid first digit '{d1}'. Must be 0-9 or A.")
    if d2 not in POSITION_DIGITS or d3 not in POSITION_DIGITS:
        raise ValueError("Second and third digits must be 0-9.")
    group_a, group_b = GROUP_ASSIGNMENT[d1]
    a_freq = tone_at_position(group_a, d2)
    b_freq = tone_at_position(group_b, d3)
    return a_freq, b_freq, group_a, group_b


def find_player():
    system = platform.system()
    if system == "Linux":
        for cmd in ("paplay", "aplay", "ffplay"):
            if shutil.which(cmd):
                return [cmd]
    elif system == "Darwin":
        return ["afplay"]
    elif system == "Windows":
        return None  # handled via winsound
    return None


class QCIIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QCII Tone Generator")
        self.resizable(False, False)
        self.last_output = None
        self.entries = {}
        self.entry_widgets = {}

        self._init_style()

        form = ttk.Frame(self, padding=12)
        form.grid(row=0, column=0, sticky="nsew")
        row = 0

        capcode_frame = ttk.LabelFrame(form, text="Populate A/B from QCII address", padding=(8, 6))
        capcode_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        row += 1
        group_digits = group_digit_choices()
        position_digits = position_digit_choices()
        self.d1_var = tk.StringVar(value=group_digits[0])
        self.d2_var = tk.StringVar(value=position_digits[0])
        self.d3_var = tk.StringVar(value=position_digits[0])
        ttk.Combobox(capcode_frame, textvariable=self.d1_var, values=group_digits,
                     width=3, state="readonly").pack(side="left", padx=(8, 2), pady=6)
        ttk.Combobox(capcode_frame, textvariable=self.d2_var, values=position_digits,
                     width=3, state="readonly").pack(side="left", padx=2, pady=6)
        ttk.Combobox(capcode_frame, textvariable=self.d3_var, values=position_digits,
                     width=3, state="readonly").pack(side="left", padx=2, pady=6)
        ttk.Button(capcode_frame, text="Apply to A/B", command=self.apply_capcode).pack(
            side="left", padx=(8, 8), pady=6
        )

        alert_frame = ttk.LabelFrame(form, text="Populate C/D from Motorola alert style (optional)", padding=(8, 6))
        alert_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        row += 1
        self.alert_var = tk.StringVar(value=DEFAULT_ALERT)
        alert_combo = ttk.Combobox(alert_frame, textvariable=self.alert_var,
                                    values=ALERT_OPTIONS, width=32, state="readonly")
        alert_combo.pack(side="left", pady=2)
        alert_combo.bind("<<ComboboxSelected>>", lambda _e: self.apply_alert_preset())

        tone_frame = ttk.LabelFrame(form, text="Tone frequencies", padding=(8, 6))
        tone_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        tone_frame.columnconfigure(1, weight=1)
        row += 1
        for i, (key, label, default) in enumerate(MAIN_FIELDS):
            ttk.Label(tone_frame, text=label, style="Field.TLabel").grid(
                row=i, column=0, sticky="w", pady=4
            )
            var = tk.StringVar(value=default)
            entry = ttk.Entry(tone_frame, textvariable=var, width=28, font=self.mono_font)
            entry.grid(row=i, column=1, sticky="ew", pady=4, padx=(8, 0))
            self.entries[key] = var
            self.entry_widgets[key] = entry

        self.suppress_warble = tk.BooleanVar(value=False)
        self.suppress_warble_chk = ttk.Checkbutton(
            form, text="Page Only (supress C/D Tones)", variable=self.suppress_warble,
            command=self.on_toggle_warble,
        )
        self.suppress_warble_chk.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 4))
        row += 1

        self.warble_only = tk.BooleanVar(value=False)
        self.warble_only_chk = ttk.Checkbutton(
            form, text="Alert Only (surpress A/B Tones)", variable=self.warble_only,
            command=self.on_toggle_warble_only,
        )
        self.warble_only_chk.grid(row=row, column=0, columnspan=2, sticky="w", pady=(0, 16))
        row += 1

        ttk.Label(form, text="Output WAV path", style="Field.TLabel").grid(
            row=row, column=0, sticky="w", pady=4
        )
        self.out_var = tk.StringVar(value=DEFAULT_OUT)
        out_frame = ttk.Frame(form)
        out_frame.grid(row=row, column=1, sticky="ew", pady=4, padx=(8, 0))
        ttk.Entry(out_frame, textvariable=self.out_var, width=22, font=self.mono_font).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(out_frame, text="Browse...", command=self.browse_output).pack(side="left", padx=(4, 0))
        row += 1

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=(16, 4), sticky="ew")
        self.generate_btn = ttk.Button(
            btn_frame, text="Generate", command=self.generate, style="Accent.TButton"
        )
        self.generate_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))
        self.play_btn = ttk.Button(btn_frame, text="Play", command=self.play)
        self.play_btn.pack(side="left", expand=True, fill="x", padx=4)
        self.reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset)
        self.reset_btn.pack(side="left", expand=True, fill="x", padx=(4, 0))
        row += 1

        btn_frame2 = ttk.Frame(form)
        btn_frame2.grid(row=row, column=0, columnspan=2, sticky="ew")
        self.config_btn = ttk.Button(btn_frame2, text="Config...", command=self.open_config_window)
        self.config_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))
        self.viz_btn = ttk.Button(btn_frame2, text="Visualize", command=self.visualize)
        self.viz_btn.pack(side="left", expand=True, fill="x", padx=(4, 0))
        row += 1

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(form, textvariable=self.status_var, style="Status.TLabel").grid(
            row=row, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )

        self._build_config_window()
        self._build_viz_window()

        # Let the main window paint first, then show the disclaimer on top.
        self.after(150, self._show_disclaimer)

    def _show_disclaimer(self):
        """Modal disclaimer shown once at launch. Agree continues into the
        app; Cancel (or closing the dialog) quits the whole program --
        this isn't a dismissable notice, it's a gate."""
        dialog = tk.Toplevel(self)
        dialog.title("Testing Purposes Only")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.protocol("WM_DELETE_WINDOW", self.destroy)

        frame = ttk.Frame(dialog, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text=DISCLAIMER_TEXT, wraplength=360, justify="left").grid(
            row=0, column=0, columnspan=2, pady=(0, 16)
        )
        ttk.Button(
            frame, text="Cancel", command=self.destroy,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(
            frame, text="I Agree, Continue", style="Accent.TButton", command=dialog.destroy,
        ).grid(row=1, column=1, sticky="ew", padx=(4, 0))

        dialog.grab_set()
        dialog.wait_window(dialog)

    def _init_style(self):
        """Set up the color/type tokens: a bold heading face for group
        titles, a monospace face for numeric fields (this is a tone-
        frequency instrument, not a generic form), and one accent color
        (signal-amber) reserved for the Generate button. ttk's 'clam'
        theme is used as a base because it actually honors style
        configuration, unlike the native platform themes."""
        base_family = tkfont.nametofont("TkDefaultFont").actual("family")
        mono_family = _first_available_font(
            ["Consolas", "Menlo", "DejaVu Sans Mono", "Courier New", "Courier"]
        )
        # Keep references alive on self -- Font objects get garbage
        # collected (and silently revert) if nothing holds onto them.
        self.heading_font = tkfont.Font(family=base_family, size=10, weight="bold")
        self.mono_font = tkfont.Font(family=mono_family, size=10)
        self.status_font = tkfont.Font(family=base_family, size=9, slant="italic")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", foreground=COLOR_INK)
        style.configure("TLabelframe.Label", font=self.heading_font, foreground=COLOR_INK)
        style.configure("Field.TLabel", foreground=COLOR_SLATE)
        style.configure("Status.TLabel", font=self.status_font, foreground=COLOR_SLATE)
        style.configure(
            "Accent.TButton", background=COLOR_ACCENT, foreground=COLOR_INK,
            font=(base_family, 10, "bold"), padding=6,
        )
        style.map(
            "Accent.TButton",
            background=[("active", COLOR_ACCENT_ACTIVE), ("disabled", "#D9B98A")],
        )

    def _build_config_window(self):
        win = tk.Toplevel(self)
        win.title("QCII Tone Generator - Config")
        win.resizable(False, False)
        win.withdraw()
        win.protocol("WM_DELETE_WINDOW", win.withdraw)
        self.config_win = win

        config_form = ttk.Frame(win, padding=12)
        config_form.grid(row=0, column=0, sticky="nsew")

        for i, (key, label, default) in enumerate(CONFIG_FIELDS):
            ttk.Label(config_form, text=label, style="Field.TLabel").grid(
                row=i, column=0, sticky="w", pady=4
            )
            var = tk.StringVar(value=default)
            entry = ttk.Entry(config_form, textvariable=var, width=20, font=self.mono_font)
            entry.grid(row=i, column=1, sticky="ew", pady=4, padx=(8, 0))
            self.entries[key] = var
            self.entry_widgets[key] = entry

        ttk.Button(config_form, text="Close", command=win.withdraw).grid(
            row=len(CONFIG_FIELDS), column=0, columnspan=2, pady=(10, 0), sticky="ew"
        )

    def open_config_window(self):
        self.config_win.deiconify()
        self.config_win.lift()

    def _build_viz_window(self):
        win = tk.Toplevel(self)
        win.title("QCII Tone Generator - Visualization")
        win.resizable(False, False)
        win.withdraw()
        win.protocol("WM_DELETE_WINDOW", win.withdraw)
        self.viz_win = win

        win.configure(bg=COLOR_CONSOLE_BG)
        self.viz_canvas = tk.Canvas(
            win, width=640, height=220, bg=COLOR_CONSOLE_BG, highlightthickness=0
        )
        self.viz_canvas.pack(padx=12, pady=(12, 0))
        ttk.Button(win, text="Refresh", command=self.visualize).pack(pady=12)

    def apply_capcode(self):
        capcode = f"{self.d1_var.get()}{self.d2_var.get()}{self.d3_var.get()}"
        try:
            a_freq, b_freq, group_a, group_b = capcode_to_ab(capcode)
        except ValueError as e:
            messagebox.showerror("Invalid QCII address", str(e))
            return
        self.entries["a"].set(str(a_freq))
        self.entries["b"].set(str(b_freq))
        self.status_var.set(
            f"QCII address {capcode} -> tone pair A={a_freq} Hz (group{group_a}), "
            f"B={b_freq} Hz (group{group_b})"
        )

    def apply_alert_preset(self):
        selection = self.alert_var.get()

        if selection == SUPPRESS_ALERT_OPTION:
            self.suppress_warble.set(True)
            self.on_toggle_warble()
            self.status_var.set("Alert suppressed (no C/D warble).")
            return

        # Any other selection means an audible warble is wanted, so undo a
        # prior "Suppress Alert" pick and re-enable the C/D/warble fields.
        if self.suppress_warble.get():
            self.suppress_warble.set(False)
            self.on_toggle_warble()

        if selection == SAME_AS_AB_OPTION:
            self.entries["c"].set("")
            self.entries["d"].set("")
            self.status_var.set("Warble will reuse A/B tones (C/D cleared).")
            return

        c_freq, d_freq = ALERT_PRESETS[selection]
        self.entries["c"].set(str(c_freq))
        self.entries["d"].set(str(d_freq))
        self.status_var.set(f"{selection}: C={c_freq} Hz, D={d_freq} Hz")

    def on_toggle_warble(self):
        suppressed = self.suppress_warble.get()
        state = "disabled" if suppressed else "normal"
        for key in WARBLE_KEYS:
            self.entry_widgets[key].config(state=state)
        self.warble_only_chk.config(state="disabled" if suppressed else "normal")

    def on_toggle_warble_only(self):
        only = self.warble_only.get()
        state = "disabled" if only else "normal"
        for key in PAGE_KEYS:
            self.entry_widgets[key].config(state=state)
        self.suppress_warble_chk.config(state="disabled" if only else "normal")

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")],
            initialfile=os.path.basename(self.out_var.get()) or "qcii_page.wav",
            initialdir=os.path.dirname(self.out_var.get()) or os.path.expanduser("~"),
        )
        if path:
            self.out_var.set(path)

    def _read_float(self, key, allow_blank=False):
        raw = self.entries[key].get().strip()
        if allow_blank and raw == "":
            return None
        return float(raw)

    def _effective_values(self):
        """Read current field values (main + config windows) and apply the
        warble-only / suppress-warble overrides, same as generate() does."""
        values = {key: self._read_float(key, allow_blank=(key in ("c", "d"))) for key, _, _ in FIELDS}
        if self.warble_only.get():
            values["a_dur"] = 0.0
            values["b_dur"] = 0.0
            values["gap"] = 0.0
        elif self.suppress_warble.get():
            values["warble_dur"] = 0.0
        return values

    def _compute_segments(self, values):
        """Break the effective values into the ordered list of audible
        segments (kind, info, duration) that build_page would produce."""
        c_freq = values["c"] if values["c"] is not None else values["a"]
        d_freq = values["d"] if values["d"] is not None else values["b"]
        segments = []
        if values["pre_silence"] > 0:
            segments.append(("silence", None, values["pre_silence"]))
        if values["a_dur"] > 0:
            segments.append(("a", values["a"], values["a_dur"]))
        if values["gap"] > 0:
            segments.append(("silence", None, values["gap"]))
        if values["b_dur"] > 0:
            segments.append(("b", values["b"], values["b_dur"]))
        if values["warble_dur"] > 0:
            segments.append(("warble", (c_freq, d_freq, values["warble_seg"]), values["warble_dur"]))
        if values["post_silence"] > 0:
            segments.append(("silence", None, values["post_silence"]))
        return segments

    def visualize(self):
        """Draw a timeline of the page that would be generated right now,
        from the current main + config window values."""
        try:
            values = self._effective_values()
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return
        segments = self._compute_segments(values)
        self.viz_win.deiconify()
        self.viz_win.lift()
        self._draw_viz(segments)

    def _draw_viz(self, segments):
        canvas = self.viz_canvas
        canvas.delete("all")
        total = sum(seg[2] for seg in segments)
        if total <= 0:
            canvas.create_text(
                320, 100, text="Nothing to draw - all durations are 0.",
                fill=COLOR_CONSOLE_TEXT,
            )
            return

        margin, bar_width, bar_y, bar_h = 10, 620, 60, 40
        scale = bar_width / total
        x = margin
        used = []
        for kind, info, dur in segments:
            w = dur * scale
            if kind == "warble":
                c_freq, d_freq, seg_len = info
                seg_len = seg_len if seg_len and seg_len > 0 else dur
                n = max(1, round(dur / seg_len))
                seg_w = w / n
                for i in range(n):
                    color = VIZ_COLORS["c"] if i % 2 == 0 else VIZ_COLORS["d"]
                    canvas.create_rectangle(x + i * seg_w, bar_y, x + (i + 1) * seg_w, bar_y + bar_h,
                                             fill=color, outline="")
                canvas.create_text(
                    x + w / 2, bar_y - 14, text=f"C/D {c_freq:g}/{d_freq:g} Hz",
                    fill=COLOR_CONSOLE_TEXT,
                )
                for key in ("c", "d"):
                    if key not in used:
                        used.append(key)
            else:
                canvas.create_rectangle(x, bar_y, x + w, bar_y + bar_h, fill=VIZ_COLORS[kind], outline="")
                if kind != "silence":
                    label = "A" if kind == "a" else "B"
                    canvas.create_text(
                        x + w / 2, bar_y - 14, text=f"{label} {info:g} Hz",
                        fill=COLOR_CONSOLE_TEXT,
                    )
                if kind not in used:
                    used.append(kind)
            canvas.create_text(
                x + w / 2, bar_y + bar_h + 14, text=f"{dur:.2f}s", fill=COLOR_CONSOLE_TEXT
            )
            x += w

        lx, ly = margin, bar_y + bar_h + 40
        for key in used:
            canvas.create_rectangle(lx, ly, lx + 14, ly + 14, fill=VIZ_COLORS[key], outline="")
            canvas.create_text(
                lx + 20, ly + 7, anchor="w", text=VIZ_LEGEND_LABELS[key], fill=COLOR_CONSOLE_TEXT
            )
            lx += 100
        canvas.create_text(
            margin, ly + 30, anchor="w", text=f"Total duration: {total:.2f}s",
            fill=COLOR_CONSOLE_TEXT,
        )

    def generate(self):
        """Render a WAV from the current field values. Returns True on success."""
        try:
            values = self._effective_values()
            rate = int(values.pop("rate"))
            out_path = self.out_var.get().strip()
            if not out_path:
                raise ValueError("Output path cannot be empty.")

            samples = build_page(
                a_freq=values["a"], b_freq=values["b"],
                sample_rate=rate,
                a_duration=values["a_dur"], b_duration=values["b_dur"],
                gap_duration=values["gap"],
                warble_duration=values["warble_dur"], warble_segment=values["warble_seg"],
                pre_silence=values["pre_silence"], post_silence=values["post_silence"],
                amplitude=values["amplitude"],
                c_freq=values["c"], d_freq=values["d"],
            )
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
            write_wav(out_path, samples, rate)
            self.last_output = out_path
            total_len = len(samples) / rate
            self.status_var.set(f"Saved {out_path} ({total_len:.2f}s).")
            return True
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
        except Exception as e:
            messagebox.showerror("Generation failed", str(e))
        return False

    def reset(self):
        for key, _, default in FIELDS:
            self.entries[key].set(default)
        self.suppress_warble.set(False)
        self.warble_only.set(False)
        self.on_toggle_warble()
        self.on_toggle_warble_only()
        group_digits = group_digit_choices()
        position_digits = position_digit_choices()
        self.d1_var.set(group_digits[0])
        self.d2_var.set(position_digits[0])
        self.d3_var.set(position_digits[0])
        self.alert_var.set(DEFAULT_ALERT)
        self.out_var.set(DEFAULT_OUT)
        self.last_output = None
        self.status_var.set("Ready.")

    def play(self):
        if not self.generate() or not os.path.exists(self.last_output):
            return
        try:
            if platform.system() == "Windows":
                import winsound
                winsound.PlaySound(self.last_output, winsound.SND_FILENAME | winsound.SND_ASYNC)
            else:
                player = find_player()
                if not player:
                    messagebox.showerror(
                        "No player found",
                        "Install 'paplay', 'aplay', or 'ffplay' to preview audio, "
                        f"or open the file manually: {self.last_output}",
                    )
                    return
                subprocess.Popen(player + [self.last_output],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            messagebox.showerror("Playback failed", str(e))


if __name__ == "__main__":
    QCIIApp().mainloop()

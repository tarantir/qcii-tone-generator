---
name: qcii-tone-generator
description: Generate WAV audio files of Motorola Quick Call II (QCII) two-tone sequential paging signals, optionally followed by a QC-D style hi-lo warble alerting tail. Use this whenever the user asks to generate, synthesize, or test two-tone pages, QCII/QC2 tones, fire/EMS station alerting tones, warble tones, or Motorola paging tone sets (A/B tone pairs, C/D warble pairs) — including requests like "make a two-tone page", "generate a warble tone", "test my Minitor/decoder with these tones", or "build an alert tone for my station alerting box/RXC/RDC."
---

# QCII Two-Tone + Warble Tone Generator

Generates WAV files that replicate real-world Motorola Quick Call II (QCII)
paging signals: a sequential two-tone page (A tone, then B tone) optionally
followed by a hi-lo warble alerting tail (the "QC-D" behavior used by fire
dispatch consoles to wake up volunteer responders after the page).

This is used for testing pager/decoder programming (e.g. Minitor V, MOTOTRBO
QCII decode, RXC-2000/RDC station alerting boxes, DIY tone decoders) by
generating known-good reference audio to play into a radio or feed directly
into decode/DSP software.

## Background (for context, not required reading to use the skill)

- **QCII ("1+1" signaling)**: standard timing is A tone for 1s, then B tone
  for 3s, with no gap ("1/3 timing"). This is the address — a receiving
  pager/decoder only unmutes when it hears its exact A/B frequency pair in
  that order.
- **QC-D / warble tail**: some consoles append a third alerting element after
  the standard page — usually an alternating hi-lo warble — to grab
  attention before voice traffic starts. This can either reuse the same A/B
  tones (alternating rapidly instead of sequentially) or use a completely
  independent tone pair, referred to here as C and D.
- Real-world example tone set used in prior work: A = 321.7 Hz, B = 569.1 Hz.
- The full standard tone charts (Motorola QC1/QC2 Reed groups, GE Type 99, REACH,
  Plectron, CTCSS, DTMF, and per-format paging timing table) are in
  `docs/tone_charts.md`. Load that file when the user needs a specific
  standard frequency/group, wants to generate a page for a non-default tone set
  they can't supply themselves, or wants to extend the script to another paging
  format (GE, REACH, Plectron, etc). Not needed for ordinary requests where the
  user supplies their own A/B (and optional C/D) frequencies directly.

## Script

`scripts/qcii_tone_gen.py` — a self-contained Python script (numpy +
stdlib `wave`) that builds the page as: pre-silence → A tone → optional gap →
B tone → optional warble tail (C/D tones, or A/B if C/D not given) →
post-silence, then writes a 16-bit PCM mono WAV.

### Running it

```bash
pip install numpy --break-system-packages  # if not already available

# Basic page, no warble tail
python3 scripts/qcii_tone_gen.py --a 321.7 --b 569.1 --warble-dur 0 --out page.wav

# Standard page + warble tail reusing A/B tones (QC-D default behavior)
python3 scripts/qcii_tone_gen.py --a 321.7 --b 569.1 --out page.wav

# Standard page + warble tail using independent C/D tones
python3 scripts/qcii_tone_gen.py --a 321.7 --b 569.1 --c 1500 --d 800 --out page.wav
```

### Key flags

| Flag | Meaning | Default |
|---|---|---|
| `--a` / `--b` | Page tone frequencies (Hz) | 321.7 / 569.1 |
| `--c` / `--d` | Independent warble tone frequencies (Hz). If omitted, warble reuses A/B. | none (falls back to A/B) |
| `--a-dur` / `--b-dur` | Page tone durations (s) | 1.0 / 3.0 (standard QCII "1/3") |
| `--gap` | Silence between A and B tones (s) | 0.0 |
| `--warble-dur` | Total warble tail length (s); set to 0 to disable | 3.0 |
| `--warble-seg` | Duration of each hi/lo segment within the warble (s) | 0.25 |
| `--pre-silence` / `--post-silence` | Padding before/after the page (s) | 0.25 / 0.25 |
| `--rate` | Sample rate (Hz) | 44100 |
| `--amplitude` | Peak amplitude, 0.0–1.0 | 0.8 |
| `--out` | Output WAV path | `output/qcii_tone_page.wav` (repo-root `output/` folder; override with `--out /mnt/user-data/outputs/<name>.wav` when running as this skill — see Workflow step 3) |

Run `python3 scripts/qcii_tone_gen.py --help` for the full list.

`scripts/generate_all_pairs.py` batch-generates QCII page WAVs from the real
Table 1 group-assignment + tone-position construction documented in
`docs/tone_charts.md` — **not** adjacent tones from the same group's
frequency list, which are only 8-40 Hz apart and undecodable in practice.

- `--mode representative` (default): one sample per valid first-digit (11
  files), tone position 2 for A / position 8 for B.
- `--mode full`: every digit2 x digit3 position combination for every
  first-digit (11 x 10 x 10 = 1100 files, ~700MB, ~10s to generate) — the
  complete set of QCII addresses buildable from Table 1's base groups (1-5). Some
  same-group first-digits (1, 2, 4, 5, A) will produce closely-spaced or
  identical A/B pairs when the two position digits land near each other —
  that's a real property of the tone plan, not a bug.

Groups 6, 10, and 11 aren't covered by either mode (see Table 3 caveat above).

## Workflow

1. Confirm the tone set with the user (A/B frequencies at minimum; ask about
   C/D warble tones only if they mention a warble/alert tail and want it
   distinct from A/B).
2. Confirm timing if it deviates from standard QCII 1/3 (e.g. pager
   battery-save uses shorter B-tone durations; some legacy systems use
   longer tones — see conversation history / RadioReference forum posts for
   real-world variants like Dallas TX FD's 3s/2s/4s timing).
3. Run the script with the appropriate flags. The script's own default
   writes to the repo-root `output/` folder, but when running as this
   skill (sandboxed environment), pass `--out /mnt/user-data/outputs/<name>.wav`
   explicitly so the file lands where `present_files` (step 4) can find it.
4. Present the resulting WAV file to the user via `present_files`.
5. If the user wants to iterate on timing/frequencies, just rerun with
   different flags rather than regenerating the script — it's parameterized
   for exactly this.

## Extending the script

If asked to extend further (e.g. stacked multi-page sequences, all-call
single-tone format, group-call variants, batch-generating a whole tone
chart), modify `scripts/qcii_tone_gen.py` directly:
- `tone()` — generates a single sine tone with fade in/out (reusable building
  block).
- `warble_tail()` — alternates between two frequencies in fixed segments.
- `build_page()` — assembles pre-silence, A, gap, B, warble, post-silence
  into one sample array. Extend this to add new page types (e.g. all-call:
  single tone for 8s with no B tone).
- `write_wav()` — PCM16 mono WAV writer.

Keep new features behind CLI flags with sane QCII-standard defaults so
existing invocations don't break.

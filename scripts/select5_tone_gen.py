#!/usr/bin/env python3
"""
Select-5 (Five-Tone Sequential) Selective-Calling Generator
--------------------------------------------------------------
Generates a WAV file for a five-tone sequential selective-calling burst —
the European/Motorola family of formats (ZVEI, CCIR, EEA and variants)
still in everyday use by German BOS/Feuerwehr rescue services and other
European dispatch systems, unlike QCII (US-only, largely retired outside
North America). A call is normally 5 tones, back-to-back, each 40-100ms
depending on format.

Supported --format values and their digit 0-9 tables are the same ones
already in docs/tone_charts.md (Five/Six/Seven Tone Sequential
table), cross-checked against sigidwiki.com/wiki/ZVEI_Selcall and
sigidwiki.com/wiki/CCIR_Selcall:
  ZVEI1 ZVEI2 ZVEI3 PZVEI DZVEI PDZVEI CCIR1 CCIR2 PCCIR EEA

Per-format default tone duration (ms):
  ZVEI1/2/3, PZVEI, DZVEI, PDZVEI : 70ms  (max inter-tone gap tolerance 15ms)
  CCIR1, PCCIR                    : 100ms
  CCIR2                           : 70ms
  EEA                             : 40ms

Control tones (A-F: group/reset/repeat, digit E is the conventional
"repeat previous digit" tone) are only reliably documented for the ZVEI
family and are included here for ZVEI1/ZVEI2/ZVEI3/PZVEI/DZVEI/PDZVEI
(sourced from sigidwiki.com/wiki/ZVEI_Selcall). Public sources disagree or
are incomplete on CCIR/EEA control-tone frequencies, so those formats
accept digits 0-9 only here — passing A-F for CCIR1/CCIR2/PCCIR/EEA is a
hard error rather than a guess. Note DZVEI's "A" tone is 825 Hz per spec
but several manufacturers use 885 Hz instead (same caveat already noted
in docs/tone_charts.md); 885 Hz is used below to match that file's
existing DZVEI column values.

This script does not auto-apply the repeat-digit convention (e.g.
rewriting "12334" to "123E4") — it renders the literal tone sequence you
give it. Type "E" yourself where you want the repeat tone (ZVEI formats
only).

Usage:
  python3 select5_tone_gen.py --format ZVEI1 --code 12345
  python3 select5_tone_gen.py --format CCIR1 --code 98765 --play
"""

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qcii_tone_gen import tone, silence, write_wav, default_output_dir  # noqa: E402
from playback import play_file  # noqa: E402


# Digit 0-9 frequencies, matching docs/tone_charts.md exactly.
DIGIT_FREQ = {
    "ZVEI1":  [2400, 1060, 1160, 1270, 1400, 1530, 1670, 1830, 2000, 2200],
    "ZVEI2":  [2400, 1060, 1160, 1270, 1400, 1530, 1670, 1830, 2000, 2200],
    "ZVEI3":  [2200, 970, 1060, 1160, 1270, 1400, 1530, 1670, 1830, 2000],
    "PZVEI":  [2400, 1060, 1160, 1270, 1400, 1530, 1670, 1830, 2000, 2200],
    "DZVEI":  [2200, 970, 1060, 1160, 1270, 1400, 1530, 1670, 1830, 2000],
    "PDZVEI": [2200, 970, 1060, 1160, 1270, 1400, 1530, 1670, 1830, 2000],
    "CCIR1":  [1981, 1124, 1197, 1275, 1358, 1446, 1540, 1640, 1747, 1860],
    "CCIR2":  [1981, 1124, 1197, 1275, 1358, 1446, 1540, 1640, 1747, 1860],
    "PCCIR":  [1981, 1124, 1197, 1275, 1358, 1446, 1540, 1640, 1747, 1860],
    "EEA":    [1981, 1124, 1197, 1275, 1358, 1446, 1540, 1640, 1747, 1860],
}

# Control (group/reset/repeat) tones A-F, only reliably documented for the
# ZVEI family. Formats not listed here accept digits 0-9 only.
CONTROL_FREQ = {
    "ZVEI1":  {"A": 2800, "B": 810, "C": 970, "D": 885, "E": 2600, "F": 680},
    "ZVEI2":  {"A": 885, "B": 810, "C": 740, "D": 680, "E": 970, "F": 2600},
    "ZVEI3":  {"A": 885, "E": 2400},
    "PZVEI":  {"A": 970, "B": 810, "C": 2800, "D": 885, "E": 2600, "F": 680},
    "DZVEI":  {"A": 885, "B": 740, "C": 2600, "D": 885, "E": 2400, "F": 680},
    "PDZVEI": {"A": 825, "B": 886, "C": 2600, "D": 856, "E": 2400},
}

TONE_DUR_DEFAULT = {
    "ZVEI1": 0.07, "ZVEI2": 0.07, "ZVEI3": 0.07,
    "PZVEI": 0.07, "DZVEI": 0.07, "PDZVEI": 0.07,
    "CCIR1": 0.10, "PCCIR": 0.10, "CCIR2": 0.07,
    "EEA": 0.04,
}

FORMATS = list(DIGIT_FREQ)
EXPECTED_LEN = 5


def freq_table(fmt):
    table = {str(d): DIGIT_FREQ[fmt][d] for d in range(10)}
    table.update(CONTROL_FREQ.get(fmt, {}))
    return table


def parse_code(fmt, code):
    code = code.upper()
    table = freq_table(fmt)
    for ch in code:
        if ch not in table:
            if ch in "ABCDEF":
                if CONTROL_FREQ.get(fmt):
                    raise ValueError(
                        f"Control tone '{ch}' is not documented for format '{fmt}' "
                        f"(supported control tones for this format: {', '.join(sorted(CONTROL_FREQ[fmt]))})"
                    )
                raise ValueError(
                    f"Control tone '{ch}' is not defined for format '{fmt}' "
                    f"(control-tone frequencies aren't reliably documented for this "
                    f"format; only digits 0-9 are supported here)"
                )
            raise ValueError(f"Invalid character '{ch}' for format '{fmt}' (must be 0-9"
                              + (", A-F" if CONTROL_FREQ.get(fmt) else "") + ")")
    return code, table


def build_call(code, table, sample_rate, tone_duration, gap_duration,
                pre_silence, post_silence, amplitude):
    parts = []
    if pre_silence > 0:
        parts.append(silence(pre_silence, sample_rate))

    for i, ch in enumerate(code):
        if i > 0 and gap_duration > 0:
            parts.append(silence(gap_duration, sample_rate))
        parts.append(tone(table[ch], tone_duration, sample_rate, amplitude))

    if post_silence > 0:
        parts.append(silence(post_silence, sample_rate))

    return np.concatenate(parts)


def main():
    p = argparse.ArgumentParser(description="Generate a five-tone sequential (Select-5) selective-calling WAV file.")
    p.add_argument("--format", type=str, required=True, choices=FORMATS,
                   help="Five-tone format/standard to use")
    p.add_argument("--code", type=str, required=True,
                   help="Tone sequence to transmit, e.g. 12345 (digits 0-9; A-F control tones on ZVEI formats only)")
    p.add_argument("--tone-dur", type=float, default=None,
                   help="Duration of each tone in seconds (default: per-format standard, e.g. 0.07 for ZVEI, 0.04 for EEA)")
    p.add_argument("--gap", type=float, default=0.0, help="Silence between tones in seconds (default 0.0, tones are back-to-back)")
    p.add_argument("--pre-silence", type=float, default=0.25, help="Silence before the call in seconds (default 0.25)")
    p.add_argument("--post-silence", type=float, default=0.25, help="Silence after the call in seconds (default 0.25)")
    p.add_argument("--rate", type=int, default=44100, help="Sample rate (default 44100)")
    p.add_argument("--amplitude", type=float, default=0.8, help="Peak amplitude 0.0-1.0 (default 0.8)")
    p.add_argument("--out", type=str, default=None, help="Output WAV filename (default output/select5_<format>_page.wav)")
    p.add_argument("--play", action="store_true", help="Play the generated WAV after writing it")

    args = p.parse_args()

    try:
        code, table = parse_code(args.format, args.code)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if len(code) != EXPECTED_LEN:
        print(f"Warning: a standard {args.format} call is {EXPECTED_LEN} tones long; "
              f"'{code}' is {len(code)}. Proceeding anyway.")

    tone_dur = args.tone_dur if args.tone_dur is not None else TONE_DUR_DEFAULT[args.format]
    out = args.out or os.path.join(default_output_dir(), f"select5_{args.format.lower()}_page.wav")

    samples = build_call(
        code, table, args.rate, tone_dur, args.gap,
        args.pre_silence, args.post_silence, args.amplitude,
    )

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    write_wav(out, samples, args.rate)
    total_len = len(samples) / args.rate

    print(f"Wrote {out}")
    print(f"  Format: {args.format}")
    for ch in code:
        print(f"  {ch}: {table[ch]} Hz")
    print(f"  Tone duration: {tone_dur}s, gap: {args.gap}s")
    print(f"  Total length: {total_len:.2f}s")

    if args.play:
        play_file(out)


if __name__ == "__main__":
    main()

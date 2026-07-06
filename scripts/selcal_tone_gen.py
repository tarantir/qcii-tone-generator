#!/usr/bin/env python3
"""
SELCAL Aircraft Selective-Calling Generator
--------------------------------------------
Generates a WAV file for a SELCAL tone sequence: the ICAO Annex 10 Vol II
Section 5.2.4 / ARINC 714A selective-calling system used by ground
stations to call a specific aircraft over HF/VHF radio without the crew
having to monitor the channel continuously.

A SELCAL code is 4 letters, written as two pairs (e.g. "AB-CD"). Each pair
is transmitted as a single pulse of its two tones sounding *simultaneously*
(not sequentially), followed by a short gap, then the second pulse.

Tone table (16 letters, I/N/O intentionally unused):
  A=312.6  B=346.7  C=384.6  D=426.6  E=473.2  F=524.8  G=582.1  H=645.7
  J=716.1  K=794.3  L=881.0  M=977.2  P=1083.9 Q=1202.3 R=1333.5 S=1479.1

Sourced from ICAO Annex 10 Vol II Section 5.2.4, en.wikipedia.org/wiki/SELCAL,
and code7700.com/selcal.htm.

Nominal pulse timing per spec: 1.0 +/- 0.25s pulse duration, 0.2 +/- 0.1s
gap between pulses. Convention (not a physical requirement) is that the
two letters within each pair are in alphabetical order and no letter
repeats across the 4-letter code; this script warns rather than rejects
on that convention, but does reject invalid/repeated/wrong-count letters.

Usage:
  python3 selcal_tone_gen.py --code AB-CD
  python3 selcal_tone_gen.py --code ABCD --play
"""

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qcii_tone_gen import tone, silence, write_wav, default_output_dir  # noqa: E402
from playback import play_file  # noqa: E402


LETTER_FREQ = {
    "A": 312.6, "B": 346.7, "C": 384.6, "D": 426.6,
    "E": 473.2, "F": 524.8, "G": 582.1, "H": 645.7,
    "J": 716.1, "K": 794.3, "L": 881.0, "M": 977.2,
    "P": 1083.9, "Q": 1202.3, "R": 1333.5, "S": 1479.1,
}

DEFAULT_OUT = os.path.join(default_output_dir(), "selcal_page.wav")


def parse_code(code):
    code = code.upper().replace("-", "")
    if len(code) != 4:
        raise ValueError(f"SELCAL code must be 4 letters, got '{code}' ({len(code)})")
    for ch in code:
        if ch not in LETTER_FREQ:
            raise ValueError(f"Invalid SELCAL letter '{ch}' (must be one of {''.join(LETTER_FREQ)})")
    if len(set(code)) != 4:
        raise ValueError(f"SELCAL letters must not repeat within a code, got '{code}'")
    return code


def check_convention(code):
    warnings = []
    pair1, pair2 = code[:2], code[2:]
    if list(pair1) != sorted(pair1):
        warnings.append(f"pair '{pair1}' is not in alphabetical order")
    if list(pair2) != sorted(pair2):
        warnings.append(f"pair '{pair2}' is not in alphabetical order")
    return warnings


def dual_tone(freq_a, freq_b, duration_s, sample_rate, amplitude):
    return (tone(freq_a, duration_s, sample_rate, amplitude / 2)
            + tone(freq_b, duration_s, sample_rate, amplitude / 2))


def build_selcal(code, sample_rate, pulse_duration, pulse_gap,
                  pre_silence, post_silence, amplitude):
    parts = []
    if pre_silence > 0:
        parts.append(silence(pre_silence, sample_rate))

    pair1, pair2 = code[:2], code[2:]
    parts.append(dual_tone(LETTER_FREQ[pair1[0]], LETTER_FREQ[pair1[1]],
                            pulse_duration, sample_rate, amplitude))
    if pulse_gap > 0:
        parts.append(silence(pulse_gap, sample_rate))
    parts.append(dual_tone(LETTER_FREQ[pair2[0]], LETTER_FREQ[pair2[1]],
                            pulse_duration, sample_rate, amplitude))

    if post_silence > 0:
        parts.append(silence(post_silence, sample_rate))

    return np.concatenate(parts)


def main():
    p = argparse.ArgumentParser(description="Generate a SELCAL aircraft selective-calling tone WAV file.")
    p.add_argument("--code", type=str, required=True,
                   help="SELCAL code, e.g. AB-CD or ABCD (4 letters from A-S excluding I/N/O)")
    p.add_argument("--pulse-dur", type=float, default=1.0, help="Duration of each pulse in seconds (default 1.0, per ICAO nominal)")
    p.add_argument("--pulse-gap", type=float, default=0.2, help="Silence between the two pulses in seconds (default 0.2, per ICAO nominal)")
    p.add_argument("--pre-silence", type=float, default=0.25, help="Silence before the call in seconds (default 0.25)")
    p.add_argument("--post-silence", type=float, default=0.25, help="Silence after the call in seconds (default 0.25)")
    p.add_argument("--rate", type=int, default=44100, help="Sample rate (default 44100)")
    p.add_argument("--amplitude", type=float, default=0.8, help="Peak amplitude 0.0-1.0 (default 0.8)")
    p.add_argument("--out", type=str, default=DEFAULT_OUT, help="Output WAV filename")
    p.add_argument("--play", action="store_true", help="Play the generated WAV after writing it")

    args = p.parse_args()

    try:
        code = parse_code(args.code)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    for warning in check_convention(code):
        print(f"Warning: {warning} (not a physical requirement, but not standard SELCAL convention)")

    samples = build_selcal(
        code, args.rate, args.pulse_dur, args.pulse_gap,
        args.pre_silence, args.post_silence, args.amplitude,
    )

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    write_wav(args.out, samples, args.rate)
    total_len = len(samples) / args.rate

    print(f"Wrote {args.out}")
    print(f"  Pulse 1: {code[0]}+{code[1]} = {LETTER_FREQ[code[0]]}+{LETTER_FREQ[code[1]]} Hz")
    print(f"  Pulse 2: {code[2]}+{code[3]} = {LETTER_FREQ[code[2]]}+{LETTER_FREQ[code[3]]} Hz")
    print(f"  Pulse duration: {args.pulse_dur}s, gap: {args.pulse_gap}s")
    print(f"  Total length: {total_len:.2f}s")

    if args.play:
        play_file(args.out)


if __name__ == "__main__":
    main()

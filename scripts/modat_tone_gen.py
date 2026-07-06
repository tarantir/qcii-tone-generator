#!/usr/bin/env python3
"""
MODAT Seven-Tone Sequential Burst Generator
--------------------------------------------
Generates a WAV file for a Motorola MODAT tone burst: a legacy 7-tone
sequential ANI/status signaling format used on MT500/MX300/Syntor/MICOR/
ASTRO-era radios to send a unit ID and emergency/status condition ahead of
a voice transmission.

Tone table (11 tones total, ~40ms each, back-to-back with no documented
inter-tone gap):
  0-9 : 637.5-1987.5 Hz in 150 Hz steps
  R   : 487.5 Hz (repeat)

Sourced from batboard.batlabs.com MODAT format threads and
sigidwiki.com/wiki/MODAT.

Scope note: the algorithm Motorola radios use to encode a 4-digit unit ID
(0000-8999) into the transmitted 7-tone burst is not publicly documented —
field reports show inconsistent tone counts (6 vs 7) for the same ID. This
script does not attempt that encoding. Instead it takes the literal tone
sequence to transmit, as a string of characters 0-9 and R.

Usage:
  python3 modat_tone_gen.py --code 1981R12
  python3 modat_tone_gen.py --code 1981R12 --play
"""

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qcii_tone_gen import tone, silence, write_wav, default_output_dir  # noqa: E402
from playback import play_file  # noqa: E402


DIGIT_FREQ = {str(d): 637.5 + 150.0 * d for d in range(10)}
DIGIT_FREQ["R"] = 487.5

DEFAULT_OUT = os.path.join(default_output_dir(), "modat_page.wav")
EXPECTED_LEN = 7


def parse_code(code):
    code = code.upper()
    for ch in code:
        if ch not in DIGIT_FREQ:
            raise ValueError(f"Invalid MODAT character '{ch}' (must be 0-9 or R)")
    return code


def build_burst(code, sample_rate, tone_duration, gap_duration,
                 pre_silence, post_silence, amplitude):
    parts = []
    if pre_silence > 0:
        parts.append(silence(pre_silence, sample_rate))

    for i, ch in enumerate(code):
        if i > 0 and gap_duration > 0:
            parts.append(silence(gap_duration, sample_rate))
        parts.append(tone(DIGIT_FREQ[ch], tone_duration, sample_rate, amplitude))

    if post_silence > 0:
        parts.append(silence(post_silence, sample_rate))

    return np.concatenate(parts)


def main():
    p = argparse.ArgumentParser(description="Generate a MODAT seven-tone sequential burst WAV file.")
    p.add_argument("--code", type=str, required=True,
                   help="MODAT tone sequence to transmit, e.g. 1981R12 (characters 0-9 and R)")
    p.add_argument("--tone-dur", type=float, default=0.04, help="Duration of each tone in seconds (default 0.04, ~40ms per spec)")
    p.add_argument("--gap", type=float, default=0.0, help="Silence between tones in seconds (default 0.0, bursts are back-to-back)")
    p.add_argument("--pre-silence", type=float, default=0.25, help="Silence before the burst in seconds (default 0.25)")
    p.add_argument("--post-silence", type=float, default=0.25, help="Silence after the burst in seconds (default 0.25)")
    p.add_argument("--rate", type=int, default=44100, help="Sample rate (default 44100)")
    p.add_argument("--amplitude", type=float, default=0.8, help="Amplitude 0.0-1.0 (default 0.8)")
    p.add_argument("--out", type=str, default=DEFAULT_OUT, help="Output WAV filename")
    p.add_argument("--play", action="store_true", help="Play the generated WAV after writing it")

    args = p.parse_args()

    try:
        code = parse_code(args.code)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if len(code) != EXPECTED_LEN:
        print(f"Warning: a real MODAT burst is {EXPECTED_LEN} tones long; "
              f"'{code}' is {len(code)}. Proceeding anyway.")

    samples = build_burst(
        code, args.rate, args.tone_dur, args.gap,
        args.pre_silence, args.post_silence, args.amplitude,
    )

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    write_wav(args.out, samples, args.rate)
    total_len = len(samples) / args.rate

    print(f"Wrote {args.out}")
    for ch in code:
        print(f"  {ch}: {DIGIT_FREQ[ch]} Hz")
    print(f"  Tone duration: {args.tone_dur}s, gap: {args.gap}s")
    print(f"  Total length: {total_len:.2f}s")

    if args.play:
        play_file(args.out)


if __name__ == "__main__":
    main()

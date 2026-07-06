#!/usr/bin/env python3
"""
Batch-generate QCII page WAVs from the Motorola General Encoding Plan
(Table 1) + Reed tone groups (see docs/tone_charts.md), confirmed
against the worked example on batlabs.com/qcii.html (QCII address 635 -> A =
Reed group 2 tone 3 = 669.9 Hz, B = Reed group 1 tone 5 = 433.7 Hz):

  - Digit 1 of the 3-digit QCII address selects which Reed GROUP tone A comes
    from and which Reed group tone B comes from (Table 1). Groups 1-5 only
    -- groups 6, 10, 11 belong to a separate high-capacity letter-prefix
    scheme (Table 3) not implemented here.
  - Digit 2 selects the tone POSITION within tone A's group.
  - Digit 3 selects the tone POSITION within tone B's group.

A/B pairs must NOT be built by grabbing two adjacent tones from the same
group's frequency list -- those are only 8-40 Hz apart and effectively
undecodable. Real pairs come from Table 1's group assignment.

Two modes:
  --mode representative (default): one pair per first-digit (11 samples),
    using tone position 2 for A and position 8 for B (arbitrary but fixed,
    chosen only so A != B).
  --mode full: every digit2 x digit3 position combination for every
    first-digit (11 x 10 x 10 = 1100 samples) -- the complete set of
    QCII addresses buildable from Table 1's base groups (1-5). Some same-group
    first-digits (1, 2, 4, 5, A) will produce closely-spaced or identical
    A/B pairs when digit2 and digit3 land near each other -- that's an
    inherent property of the real tone plan, not a generation error.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from qcii_tone_gen import build_page, write_wav, default_output_dir  # noqa: E402

REED_GROUPS = {
    1: [349.0, 368.5, 389.0, 410.8, 433.7, 457.9, 483.5, 510.5, 539.0, 330.5],
    2: [600.9, 634.5, 669.9, 707.3, 746.8, 788.5, 832.5, 879.0, 928.1, 569.1],
    3: [288.5, 296.5, 304.7, 313.0, 953.7, 979.9, 1006.9, 1034.7, 1063.2, 1092.4],
    4: [339.6, 358.6, 378.6, 399.8, 422.1, 445.7, 470.5, 496.8, 524.6, 321.7],
    5: [584.8, 617.4, 651.9, 688.3, 726.8, 767.4, 810.2, 855.5, 903.2, 553.9],
}

# Table 1: first QCII address digit -> (group for tone A, group for tone B)
GROUP_ASSIGNMENT = {
    "1": (1, 1),
    "2": (2, 2),
    "3": (1, 2),
    "4": (4, 4),
    "5": (5, 5),
    "6": (2, 1),
    "7": (4, 5),
    "8": (5, 4),
    "9": (2, 4),
    "0": (4, 2),
    "A": (3, 3),
}

POSITION_DIGITS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]

SAMPLE_RATE = 44100
A_DUR = 1.0
B_DUR = 3.0
GAP = 0.0
WARBLE_DUR = 3.0
WARBLE_SEG = 0.25
PRE_SILENCE = 0.25
POST_SILENCE = 0.25
AMPLITUDE = 0.8


def tone_at_position(group, position_digit):
    index = 9 if position_digit == "0" else int(position_digit) - 1
    return REED_GROUPS[group][index]


def write_page(out_dir, capcode, a_freq, b_freq, c_freq=None, d_freq=None):
    samples = build_page(
        a_freq=a_freq, b_freq=b_freq, sample_rate=SAMPLE_RATE,
        a_duration=A_DUR, b_duration=B_DUR,
        gap_duration=GAP,
        warble_duration=WARBLE_DUR, warble_segment=WARBLE_SEG,
        pre_silence=PRE_SILENCE, post_silence=POST_SILENCE,
        amplitude=AMPLITUDE,
        c_freq=c_freq, d_freq=d_freq,
    )
    filename = f"capcode_{capcode}_A{a_freq}_B{b_freq}.wav"
    write_wav(os.path.join(out_dir, filename), samples, SAMPLE_RATE)
    return filename


def generate_representative(out_dir, c_freq=None, d_freq=None):
    a_pos, b_pos = "2", "8"
    count = 0
    for first_digit, (group_a, group_b) in GROUP_ASSIGNMENT.items():
        a_freq = tone_at_position(group_a, a_pos)
        b_freq = tone_at_position(group_b, b_pos)
        capcode = f"{first_digit}{a_pos}{b_pos}"
        filename = write_page(out_dir, capcode, a_freq, b_freq, c_freq, d_freq)
        count += 1
        print(f"Wrote {filename}  (QCII address {capcode}: group A={group_a} -> {a_freq} Hz, "
              f"group B={group_b} -> {b_freq} Hz, separation {abs(a_freq - b_freq):.1f} Hz)")
    return count


def generate_full(out_dir, c_freq=None, d_freq=None):
    count = 0
    for first_digit, (group_a, group_b) in GROUP_ASSIGNMENT.items():
        for a_pos in POSITION_DIGITS:
            for b_pos in POSITION_DIGITS:
                a_freq = tone_at_position(group_a, a_pos)
                b_freq = tone_at_position(group_b, b_pos)
                capcode = f"{first_digit}{a_pos}{b_pos}"
                write_page(out_dir, capcode, a_freq, b_freq, c_freq, d_freq)
                count += 1
        print(f"Group-assignment {first_digit} (A<-group{group_a}, B<-group{group_b}): "
              f"100 QCII addresses written")
    return count


def main():
    p = argparse.ArgumentParser(description="Batch-generate QCII page WAVs from Table 1.")
    p.add_argument("--mode", choices=["representative", "full"], default="representative",
                    help="representative: 11 samples (one per first-digit). "
                         "full: 1100 samples (every digit2 x digit3 combination).")
    p.add_argument("--c", type=float, default=None,
                    help="Independent warble tone C frequency (Hz). Default: reuse A/B.")
    p.add_argument("--d", type=float, default=None,
                    help="Independent warble tone D frequency (Hz). Default: reuse A/B.")
    args = p.parse_args()

    out_dir = default_output_dir()
    os.makedirs(out_dir, exist_ok=True)

    if args.mode == "full":
        count = generate_full(out_dir, args.c, args.d)
    else:
        count = generate_representative(out_dir, args.c, args.d)

    print(f"\nDone: {count} tone-pair samples written to {os.path.abspath(out_dir)}")


if __name__ == "__main__":
    main()

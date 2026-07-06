#!/usr/bin/env python3
"""
Talk Permit Tone (TPT) Generator
----------------------------------
Generates a WAV file for a Talk Permit Tone — the "beep(s)" heard on
trunked radios confirming the trunking handshake succeeded and it's safe
to start talking. Without it, keying up before the system has granted a
channel clips the first syllable ("false-keying"). MOTOTRBO radios can
also produce a TPT-equivalent on conventional (non-trunked) channels,
where it just means "you are now transmitting" rather than confirming a
trunking grant.

Variants (--variant):

  p25-classic (default): a single frequency (not a sweep), played as
  three short pulses with two short silences between them:
    910 Hz 30ms -> 20ms silence -> 910 Hz 30ms -> 20ms silence -> 910 Hz 50ms
  This exact value set is a widely-referenced custom-tone example, not a
  formally published ITU/TIA spec.

  p25-mototrbo: a 4-note musical chirp (G6/C6/G6/E6), no gaps between
  notes, same purpose as p25-classic but a newer/nicer-sounding
  implementation:
    1569 Hz, 1046 Hz, 1569 Hz, 1317 Hz, each 40ms
  Confirmed by multiple independent sources (kg4cyx.net, DMR user
  forums). Motorola CPS rounds these to 1570/1050/1570/1320 Hz when
  programming custom tones into compatible radios.

  iden-nextel: the same 3-pulse/2-gap shape as p25-classic, at a
  different frequency:
    1800 Hz 30ms -> 20ms silence -> 1800 Hz 30ms -> 20ms silence -> 1800 Hz 50ms
  CAVEAT: this exact value comes from a single non-authoritative source
  (a blog post, not an official iDEN spec). It's also a *higher* pitch
  than P25's 910 Hz, which contradicts other descriptions of the
  iDEN/Nextel chirp as "lower-pitched than P25" — treat this as a
  plausible lead, not settled fact.

  p25-clear-alert: NOT IMPLEMENTED. This is a real, configurable
  Motorola feature (a beep on TX/RX of an unencrypted channel), but the
  actual frequency varies by radio model/system config with no single
  documented spec (scattered mentions of ~500/1000/1011 Hz, no
  consistent value) — selecting it prints an error rather than guessing.

Note: some radios instead play a distinct low "bonk" tone when the
trunking handshake fails (system busy, repeater out of range) rather
than granting a TPT. No specific documented frequency/duration for that
failure tone was available, so it isn't implemented here either.

Usage:
  python3 tpt_tone_gen.py
  python3 tpt_tone_gen.py --variant p25-mototrbo --play
  python3 tpt_tone_gen.py --variant iden-nextel --play
"""

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qcii_tone_gen import tone, silence, write_wav, default_output_dir  # noqa: E402
from playback import play_file  # noqa: E402


DEFAULT_OUT = os.path.join(default_output_dir(), "tpt_page.wav")

DEFAULT_FREQ = {
    "p25-classic": 910,
    "iden-nextel": 1800,
}

MOTOTRBO_NOTES = [1569, 1046, 1569, 1317]

VARIANTS = ["p25-classic", "p25-mototrbo", "iden-nextel", "p25-clear-alert"]


def build_pulse_tpt(freq, pulse1_dur, gap1, pulse2_dur, gap2, pulse3_dur,
                     sample_rate, pre_silence, post_silence, amplitude):
    """Shared 3-pulse/2-gap shape used by p25-classic and iden-nextel."""
    parts = []
    if pre_silence > 0:
        parts.append(silence(pre_silence, sample_rate))

    parts.append(tone(freq, pulse1_dur, sample_rate, amplitude))
    if gap1 > 0:
        parts.append(silence(gap1, sample_rate))
    parts.append(tone(freq, pulse2_dur, sample_rate, amplitude))
    if gap2 > 0:
        parts.append(silence(gap2, sample_rate))
    parts.append(tone(freq, pulse3_dur, sample_rate, amplitude))

    if post_silence > 0:
        parts.append(silence(post_silence, sample_rate))

    return np.concatenate(parts)


def build_mototrbo_chirp(note_dur, sample_rate, pre_silence, post_silence, amplitude):
    parts = []
    if pre_silence > 0:
        parts.append(silence(pre_silence, sample_rate))

    for freq in MOTOTRBO_NOTES:
        parts.append(tone(freq, note_dur, sample_rate, amplitude))

    if post_silence > 0:
        parts.append(silence(post_silence, sample_rate))

    return np.concatenate(parts)


def main():
    p = argparse.ArgumentParser(description="Generate a Talk Permit Tone (TPT) WAV file.")
    p.add_argument("--variant", type=str, default="p25-classic", choices=VARIANTS,
                   help="TPT variant to generate (default p25-classic)")
    p.add_argument("--freq", type=float, default=None,
                   help="Tone frequency in Hz for p25-classic/iden-nextel (default 910 / 1800 respectively)")
    p.add_argument("--pulse1-dur", type=float, default=0.03, help="First pulse duration in seconds (default 0.03, p25-classic/iden-nextel only)")
    p.add_argument("--gap1", type=float, default=0.02, help="Silence after first pulse in seconds (default 0.02, p25-classic/iden-nextel only)")
    p.add_argument("--pulse2-dur", type=float, default=0.03, help="Second pulse duration in seconds (default 0.03, p25-classic/iden-nextel only)")
    p.add_argument("--gap2", type=float, default=0.02, help="Silence after second pulse in seconds (default 0.02, p25-classic/iden-nextel only)")
    p.add_argument("--pulse3-dur", type=float, default=0.05, help="Third pulse duration in seconds (default 0.05, p25-classic/iden-nextel only)")
    p.add_argument("--note-dur", type=float, default=0.04, help="Duration of each of the 4 notes in seconds (default 0.04, p25-mototrbo only)")
    p.add_argument("--pre-silence", type=float, default=0.25, help="Silence before the tone in seconds (default 0.25)")
    p.add_argument("--post-silence", type=float, default=0.25, help="Silence after the tone in seconds (default 0.25)")
    p.add_argument("--rate", type=int, default=44100, help="Sample rate (default 44100)")
    p.add_argument("--amplitude", type=float, default=0.8, help="Peak amplitude 0.0-1.0 (default 0.8)")
    p.add_argument("--out", type=str, default=None, help="Output WAV filename (default output/tpt_page.wav, or output/tpt_<variant>_page.wav for non-default variants)")
    p.add_argument("--play", action="store_true", help="Play the generated WAV after writing it")

    args = p.parse_args()

    if args.variant == "p25-clear-alert":
        print("Error: p25-clear-alert is not implemented — no reliably documented "
              "frequency/timing exists for it (varies by radio model/system config). "
              "See the module docstring for details.")
        sys.exit(1)

    out = args.out
    if out is None:
        out = DEFAULT_OUT if args.variant == "p25-classic" else \
            os.path.join(default_output_dir(), f"tpt_{args.variant.replace('-', '_')}_page.wav")

    if args.variant == "p25-mototrbo":
        samples = build_mototrbo_chirp(
            args.note_dur, args.rate, args.pre_silence, args.post_silence, args.amplitude,
        )
    else:
        freq = args.freq if args.freq is not None else DEFAULT_FREQ[args.variant]
        samples = build_pulse_tpt(
            freq, args.pulse1_dur, args.gap1, args.pulse2_dur, args.gap2, args.pulse3_dur,
            args.rate, args.pre_silence, args.post_silence, args.amplitude,
        )

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    write_wav(out, samples, args.rate)
    total_len = len(samples) / args.rate

    print(f"Wrote {out}")
    print(f"  Variant: {args.variant}")
    if args.variant == "p25-mototrbo":
        for i, freq in enumerate(MOTOTRBO_NOTES, start=1):
            print(f"  Note {i}: {freq} Hz for {args.note_dur}s")
    else:
        print(f"  Pulse 1: {freq} Hz for {args.pulse1_dur}s")
        print(f"  Gap 1: {args.gap1}s")
        print(f"  Pulse 2: {freq} Hz for {args.pulse2_dur}s")
        print(f"  Gap 2: {args.gap2}s")
        print(f"  Pulse 3: {freq} Hz for {args.pulse3_dur}s")
    print(f"  Total length: {total_len:.2f}s")

    if args.play:
        play_file(out)


if __name__ == "__main__":
    main()

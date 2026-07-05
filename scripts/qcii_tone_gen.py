#!/usr/bin/env python3
"""
QCII Two-Tone Page + Warble Tail Generator
--------------------------------------------
Generates a WAV file matching a Motorola Quick Call II "D" style page:
  A-tone -> B-tone (standard 1/3 sequential page) -> hi-lo warble tail

Tone set (edit as needed):
  A tone = 1122.5 Hz  (page)
  B tone = 1433.4 Hz  (page)
  C tone = warble tone 1 (defaults to A if not given)
  D tone = warble tone 2 (defaults to B if not given)

By default the warble tail alternates between the A and B tones (matching
real-world QC-D behavior on many consoles). Pass --c/--d to make the warble
use a completely independent tone pair instead of reusing A/B.

Usage:
  python3 qcii_tone_gen.py
  python3 qcii_tone_gen.py --a 1122.5 --b 1433.4 --out my_page.wav
  python3 qcii_tone_gen.py --a 1122.5 --b 1433.4 --c 1500 --d 800 --out my_page.wav
"""

import argparse
import os
import sys
import numpy as np
import wave
import struct


def default_output_dir():
    """Directory generated WAVs are written to by default: normally the
    repo-root output/ folder next to scripts/. When frozen into a single
    executable (PyInstaller etc.), __file__ resolves inside a temporary
    extraction folder that's deleted when the process exits, so anchor to
    the executable's own directory instead."""
    if getattr(sys, "frozen", False):
        return os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "output")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output")


DEFAULT_OUT = os.path.join(default_output_dir(), "qcii_tone_page.wav")


def tone(freq, duration_s, sample_rate, amplitude=0.8, fade_ms=5):
    """Generate a sine tone with short fade in/out to avoid audible clicks."""
    n_samples = int(duration_s * sample_rate)
    t = np.arange(n_samples) / sample_rate
    wave_data = amplitude * np.sin(2 * np.pi * freq * t)

    fade_samples = int((fade_ms / 1000.0) * sample_rate)
    fade_samples = min(fade_samples, n_samples // 2) if n_samples > 1 else 0
    if fade_samples > 0:
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        wave_data[:fade_samples] *= fade_in
        wave_data[-fade_samples:] *= fade_out

    return wave_data


def silence(duration_s, sample_rate):
    return np.zeros(int(duration_s * sample_rate))


def warble_tail(freq_a, freq_b, total_duration_s, segment_s, sample_rate, amplitude=0.8):
    """Alternate between freq_a and freq_b (hi-lo warble) for total_duration_s."""
    segments = []
    n_segments = int(round(total_duration_s / segment_s))
    for i in range(n_segments):
        f = freq_a if i % 2 == 0 else freq_b
        segments.append(tone(f, segment_s, sample_rate, amplitude, fade_ms=3))
    return np.concatenate(segments) if segments else np.array([])


def build_page(a_freq, b_freq, sample_rate,
                a_duration, b_duration,
                gap_duration,
                warble_duration, warble_segment,
                pre_silence, post_silence,
                amplitude,
                c_freq=None, d_freq=None):
    parts = []
    if pre_silence > 0:
        parts.append(silence(pre_silence, sample_rate))

    # Standard QCII page: A tone, then B tone
    parts.append(tone(a_freq, a_duration, sample_rate, amplitude))
    if gap_duration > 0:
        parts.append(silence(gap_duration, sample_rate))
    parts.append(tone(b_freq, b_duration, sample_rate, amplitude))

    # Warble tail (QC "D" style alerting tail).
    # Uses C/D tones if provided, otherwise falls back to reusing A/B.
    if warble_duration > 0:
        warble_freq_1 = c_freq if c_freq is not None else a_freq
        warble_freq_2 = d_freq if d_freq is not None else b_freq
        parts.append(warble_tail(warble_freq_1, warble_freq_2, warble_duration,
                                  warble_segment, sample_rate, amplitude))

    if post_silence > 0:
        parts.append(silence(post_silence, sample_rate))

    return np.concatenate(parts)


def write_wav(filename, samples, sample_rate):
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767).astype(np.int16)
    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())


def main():
    p = argparse.ArgumentParser(description="Generate a QCII two-tone page + warble tail WAV file.")
    p.add_argument("--a", type=float, default=1122.5, help="A tone frequency in Hz (default 1122.5)")
    p.add_argument("--b", type=float, default=1433.4, help="B tone frequency in Hz (default 1433.4)")
    p.add_argument("--c", type=float, default=None, help="Warble tone 1 (C) frequency in Hz. Defaults to A tone if not given.")
    p.add_argument("--d", type=float, default=None, help="Warble tone 2 (D) frequency in Hz. Defaults to B tone if not given.")
    p.add_argument("--a-dur", type=float, default=1.0, help="A tone duration in seconds (default 1.0)")
    p.add_argument("--b-dur", type=float, default=3.0, help="B tone duration in seconds (default 3.0, standard QCII 1/3)")
    p.add_argument("--gap", type=float, default=0.0, help="Gap between A and B tones in seconds (default 0.0)")
    p.add_argument("--warble-dur", type=float, default=3.0, help="Total warble tail duration in seconds (default 3.0, 0 to disable)")
    p.add_argument("--warble-seg", type=float, default=0.25, help="Duration of each warble hi/lo segment in seconds (default 0.25)")
    p.add_argument("--pre-silence", type=float, default=0.25, help="Silence before the page in seconds (default 0.25)")
    p.add_argument("--post-silence", type=float, default=0.25, help="Silence after the page in seconds (default 0.25)")
    p.add_argument("--rate", type=int, default=44100, help="Sample rate (default 44100)")
    p.add_argument("--amplitude", type=float, default=0.8, help="Amplitude 0.0-1.0 (default 0.8)")
    p.add_argument("--out", type=str, default=DEFAULT_OUT, help="Output WAV filename")

    args = p.parse_args()

    samples = build_page(
        a_freq=args.a, b_freq=args.b, sample_rate=args.rate,
        a_duration=args.a_dur, b_duration=args.b_dur,
        gap_duration=args.gap,
        warble_duration=args.warble_dur, warble_segment=args.warble_seg,
        pre_silence=args.pre_silence, post_silence=args.post_silence,
        amplitude=args.amplitude,
        c_freq=args.c, d_freq=args.d,
    )

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    write_wav(args.out, samples, args.rate)
    total_len = len(samples) / args.rate
    warble_f1 = args.c if args.c is not None else args.a
    warble_f2 = args.d if args.d is not None else args.b
    warble_source = "C/D" if (args.c is not None or args.d is not None) else "A/B (default)"

    print(f"Wrote {args.out}")
    print(f"  A tone: {args.a} Hz for {args.a_dur}s")
    print(f"  B tone: {args.b} Hz for {args.b_dur}s")
    print(f"  Warble tail: {args.warble_dur}s alternating {warble_f1}/{warble_f2} Hz "
          f"in {args.warble_seg}s segments (source: {warble_source})")
    print(f"  Total length: {total_len:.2f}s")


if __name__ == "__main__":
    main()

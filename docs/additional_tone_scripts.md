# Additional Tone-Signaling Scripts

This repo's core focus is QCII (see the root [README](../README.md)). The
four scripts below generate WAV files for other radio signaling formats
that came up alongside that work. They're kept separate here rather than
folded into the main README since they're auxiliary/experimental additions,
not part of QCII itself.

All four follow the same conventions as the core QCII scripts: they reuse
`tone`/`silence`/`write_wav`/`default_output_dir` from
[`scripts/qcii_tone_gen.py`](../scripts/qcii_tone_gen.py), default their
output into the repo-root `output/` folder, and support `--play` via the
shared [`scripts/playback.py`](../scripts/playback.py) helper (Linux needs
`paplay`/`aplay`/`ffplay`; macOS/Windows use the OS player automatically).

## MODAT

[`scripts/modat_tone_gen.py`](../scripts/modat_tone_gen.py) generates a
Motorola MODAT tone burst — a legacy 7-tone sequential ANI/status
signaling format used on MT500/MX300/Syntor/MICOR/ASTRO-era radios to
send a unit ID and emergency/status condition ahead of a voice
transmission. 11 tones total (digits 0-9 at 637.5-1987.5 Hz in 150 Hz
steps, plus `R` = 487.5 Hz for repeat), each ~40ms, back-to-back with no
documented inter-tone gap. Sourced from batboard.batlabs.com MODAT format
threads and sigidwiki.com/wiki/MODAT.

**Scope note:** the algorithm Motorola radios use to encode a 4-digit
unit ID (0000-8999) into the transmitted 7-tone burst is not publicly
documented — field reports show inconsistent tone counts (6 vs 7) for
the same ID. This script does not attempt that encoding; it takes the
literal tone sequence to transmit, as a string of characters `0`-`9` and
`R`. A real MODAT burst is 7 tones long — a different length just prints
a warning and still generates.

```bash
# Generate a WAV to the default location (output/modat_page.wav)
python3 scripts/modat_tone_gen.py --code 1981R12

# Generate and immediately play it back
python3 scripts/modat_tone_gen.py --code 1981R12 --play

# Custom output path
python3 scripts/modat_tone_gen.py --code 1981R12 --out output/my_modat.wav

# Slower tones for easier listening/debugging (default is 40ms per spec)
python3 scripts/modat_tone_gen.py --code 1981R12 --tone-dur 0.2 --play
```

| Flag | Meaning | Default |
|---|---|---|
| `--code` | Tone sequence to transmit (`0`-`9`, `R`) | required |
| `--tone-dur` | Duration of each tone (s) | 0.04 |
| `--gap` | Silence between tones (s) | 0.0 |
| `--pre-silence` / `--post-silence` | Padding before/after the burst (s) | 0.25 / 0.25 |
| `--out` | Output WAV path | `output/modat_page.wav` |
| `--play` | Play the WAV after writing it | off |

## SELCAL

[`scripts/selcal_tone_gen.py`](../scripts/selcal_tone_gen.py) generates a
SELCAL tone sequence — the ICAO Annex 10 Vol II Section 5.2.4 / ARINC
714A aircraft selective-calling system used by ground stations to call a
specific aircraft over HF/VHF radio without the crew having to monitor
the channel continuously. A code is 4 letters written as two pairs (e.g.
`AB-CD`); each pair is transmitted as a single pulse of its two tones
sounding *simultaneously* (not sequentially), 1.0±0.25s per pulse with a
0.2±0.1s gap between them. 16 tone letters total (`A`-`S`, skipping
`I`/`N`/`O`), 312.6-1479.1 Hz. Sourced from ICAO Annex 10 Vol II Section
5.2.4, en.wikipedia.org/wiki/SELCAL, and code7700.com/selcal.htm.

**Convention vs. requirement:** the two letters within each pair being in
alphabetical order, and no letter repeating across the 4-letter code, is
a call-sign assignment convention, not a physical constraint — an
out-of-order pair just prints a warning and still generates, but invalid
letters, repeats, or the wrong number of letters are hard errors.

```bash
# Generate a WAV to the default location (output/selcal_page.wav)
python3 scripts/selcal_tone_gen.py --code AB-CD

# Dash is optional — same thing
python3 scripts/selcal_tone_gen.py --code ABCD

# Generate and immediately play it back
python3 scripts/selcal_tone_gen.py --code AB-CD --play

# Slower/faster pulses than the ICAO nominal (1.0s pulse, 0.2s gap)
python3 scripts/selcal_tone_gen.py --code AB-CD --pulse-dur 1.5 --pulse-gap 0.3 --play
```

| Flag | Meaning | Default |
|---|---|---|
| `--code` | 4-letter SELCAL code, e.g. `AB-CD` or `ABCD` (`A-S` excluding `I`/`N`/`O`) | required |
| `--pulse-dur` | Duration of each pulse (s) | 1.0 |
| `--pulse-gap` | Silence between the two pulses (s) | 0.2 |
| `--pre-silence` / `--post-silence` | Padding before/after the call (s) | 0.25 / 0.25 |
| `--out` | Output WAV path | `output/selcal_page.wav` |
| `--play` | Play the WAV after writing it | off |

## Five-Tone (Select-5)

[`scripts/select5_tone_gen.py`](../scripts/select5_tone_gen.py) generates
a five-tone sequential selective-calling burst — the European/Motorola
family of formats (ZVEI, CCIR, EEA and variants) still in everyday use by
German BOS/Feuerwehr rescue services and other European dispatch systems,
unlike QCII (US-only, largely retired outside North America). A call is
normally 5 tones, back-to-back, each 40-100ms depending on format. Digit
0-9 tables match the ones already in
[`docs/tone_charts.md`](tone_charts.md), cross-checked
against sigidwiki.com/wiki/ZVEI_Selcall and sigidwiki.com/wiki/CCIR_Selcall.

Per-format default tone duration:

| Format(s) | Default tone duration |
|---|---|
| ZVEI1, ZVEI2, ZVEI3, PZVEI, DZVEI, PDZVEI | 70ms (max inter-tone gap tolerance 15ms) |
| CCIR1, PCCIR | 100ms |
| CCIR2 | 70ms |
| EEA | 40ms |

**Control tones:** `A`-`F` (group/reset/repeat; digit `E` is the
conventional "repeat previous digit" tone) are only reliably documented
for the ZVEI family, and are supported here for
ZVEI1/ZVEI2/ZVEI3/PZVEI/DZVEI/PDZVEI (ZVEI3 only defines `A`/`E`). Public
sources disagree or are incomplete on CCIR/EEA control-tone frequencies,
so those formats accept digits 0-9 only — passing `A`-`F` there is a hard
error rather than a guess. The script does not auto-apply the
repeat-digit convention (e.g. rewriting `12334` to `123E4`); type `E`
yourself where wanted.

```bash
# ZVEI1 (German BOS/Feuerwehr standard), 5-digit call
python3 scripts/select5_tone_gen.py --format ZVEI1 --code 12345

# Generate and immediately play it back
python3 scripts/select5_tone_gen.py --format ZVEI1 --code 12345 --play

# CCIR1 (UK-common format)
python3 scripts/select5_tone_gen.py --format CCIR1 --code 98765

# Using the repeat tone 'E' manually (ZVEI formats only), e.g. "12334" -> "123E4"
python3 scripts/select5_tone_gen.py --format ZVEI1 --code 123E4 --play
```

| Flag | Meaning | Default |
|---|---|---|
| `--format` | `ZVEI1`, `ZVEI2`, `ZVEI3`, `PZVEI`, `DZVEI`, `PDZVEI`, `CCIR1`, `CCIR2`, `PCCIR`, `EEA` | required |
| `--code` | Tone sequence, e.g. `12345` (`0`-`9`; `A`-`F` on ZVEI formats only) | required |
| `--tone-dur` | Duration of each tone (s) | per-format (see table above) |
| `--gap` | Silence between tones (s) | 0.0 |
| `--pre-silence` / `--post-silence` | Padding before/after the call (s) | 0.25 / 0.25 |
| `--out` | Output WAV path | `output/select5_<format>_page.wav` |
| `--play` | Play the WAV after writing it | off |

## Talk Permit Tone (TPT)

[`scripts/tpt_tone_gen.py`](../scripts/tpt_tone_gen.py) generates a Talk
Permit Tone — the "beep(s)" heard on trunked radios confirming the
trunking handshake succeeded and it's safe to start talking. Without it,
keying up before the system has granted a channel clips the first
syllable ("false-keying"). MOTOTRBO radios can also produce a
TPT-equivalent on conventional (non-trunked) channels, where it just
means "you are now transmitting" rather than confirming a trunking grant.

Some radios instead play a distinct low "bonk" tone when the trunking
handshake fails (system busy, repeater out of range) rather than granting
a TPT — no documented frequency/duration for that failure tone was
available, so it isn't implemented.

| `--variant` | Shape | Notes |
|---|---|---|
| `p25-classic` (default) | 910 Hz, 30ms → 20ms silence → 30ms → 20ms silence → 50ms | Widely-referenced custom-tone example, not a formally published ITU/TIA spec |
| `p25-mototrbo` | 1569/1046/1569/1317 Hz (G6/C6/G6/E6), 40ms each, no gaps | Confirmed by multiple independent sources; Motorola CPS rounds these to 1570/1050/1570/1320 Hz |
| `iden-nextel` | Same shape as `p25-classic`, at 1800 Hz | Single non-authoritative source; note this is actually a *higher* pitch than P25's 910 Hz, which contradicts other descriptions of it as "lower-pitched" — treat as a lead, not settled fact |
| `p25-clear-alert` | Not implemented | Real Motorola feature (unencrypted-channel warning beep), but no single documented frequency/timing exists across radio models/configs — selecting it errors rather than guesses |

```bash
# Default: classic P25 3-beep TPT (910 Hz)
python3 scripts/tpt_tone_gen.py --play

# MOTOTRBO 4-note musical chirp
python3 scripts/tpt_tone_gen.py --variant p25-mototrbo --play

# iDEN/Nextel-style chirp (same shape as classic, at 1800 Hz)
python3 scripts/tpt_tone_gen.py --variant iden-nextel --play

# Tweak timing/pitch
python3 scripts/tpt_tone_gen.py --variant p25-mototrbo --note-dur 0.06 --out output/my_chirp.wav
python3 scripts/tpt_tone_gen.py --variant p25-classic --freq 1000 --pulse3-dur 0.08
```

| Flag | Meaning | Default |
|---|---|---|
| `--variant` | `p25-classic`, `p25-mototrbo`, `iden-nextel`, `p25-clear-alert` | `p25-classic` |
| `--freq` | Tone frequency (Hz), `p25-classic`/`iden-nextel` only | 910 / 1800 respectively |
| `--pulse1-dur` / `--gap1` / `--pulse2-dur` / `--gap2` / `--pulse3-dur` | Pulse/gap timing (s), `p25-classic`/`iden-nextel` only | 0.03 / 0.02 / 0.03 / 0.02 / 0.05 |
| `--note-dur` | Duration of each of the 4 notes (s), `p25-mototrbo` only | 0.04 |
| `--pre-silence` / `--post-silence` | Padding before/after the tone (s) | 0.25 / 0.25 |
| `--out` | Output WAV path | `output/tpt_page.wav` (or `output/tpt_<variant>_page.wav`) |
| `--play` | Play the WAV after writing it | off |

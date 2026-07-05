# Two-Tone / Multi-Tone Paging Reference Charts

Source: Midian Electronics, Inc. "Motorola Two Tone & Four Tone Paging" reference
sheet (widely mirrored, e.g. sigidwiki.com). Reproduced here so tone values are
available offline without re-fetching. Values are the industry-standard
frequencies for each signaling format; some manufacturers deviate slightly (noted
where the source document calls it out).

## Motorola General Encoding Plan (Table 1)

Which Reed group each of Tone A / Tone B is pulled from, keyed by the first digit
of the pager code:

| 1st digit of pager code | Group for Tone A | Group for Tone B |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 2 | 2 |
| 3 | 1 | 2 |
| 4 | 4 | 4 |
| 5 | 5 | 5 |
| 6 | 2 | 1 |
| 7 | 4 | 5 |
| 8 | 5 | 4 |
| 9 | 2 | 4 |
| 0 | 4 | 2 |
| A | 3 | 3 |

### How a 3-digit QCII address becomes an A/B tone pair

Confirmed via batlabs.com/qcii.html, worked example QCII address 635:

- **Digit 1** selects the group for tone A and the group for tone B (table
  above). Digit 6 -> tone A from Group 2, tone B from Group 1.
- **Digit 2** selects the tone *position* (1-9, 0) within tone A's group.
  Digit 3 -> position 3 in Group 2 = 669.9 Hz.
- **Digit 3** selects the tone position within tone B's group. Digit 5 ->
  position 5 in Group 1 = 433.7 Hz.
- Result: Tone A = 669.9 Hz, Tone B = 433.7 Hz.

**A/B pairs are never two adjacent tones from the same group's frequency
list** — those sit only 8-40 Hz apart in the Reed tables and would be
unreadable by a real decoder. Digit 1 exists specifically to keep A and B
far enough apart (same-group self-pairs like digit 1/2/4/5/A only work
because digit 2 and digit 3 pick *different positions* within that group,
e.g. position 2 vs position 8, not neighbors like position 1 vs 2).

Groups 6, 10, and 11 are not reachable through this base Table 1 scheme —
they belong to a separate high-capacity letter-prefix format (Table 3,
below) that hasn't been fully worked out here. Don't assume a same-group
or adjacent-tone pairing is valid for those groups without confirming the
real addressing rule first.

## Motorola Quick Call 1 "Two Plus Two" (Code Type "Y")

| Code | Freq (A) | Code | Freq (B) | Code | Freq (Z) |
|---|---|---|---|---|---|
| DA | 398.1 | DB | 412.1 | DZ | 384.6 |
| EA | 441.6 | EB | 457.1 | EZ | 426.6 |
| FA | 489.8 | FB | 507.0 | FZ | 473.2 |
| GA | 543.3 | GB | 562.3 | GZ | 524.8 |
| HA | 602.6 | HB | 623.7 | HZ | 582.1 |
| JA | 668.3 | JB | 691.8 | JZ | 645.7 |
| KA | 741.3 | KB | 767.4 | KZ | 716.7 |
| LA | 822.2 | LB | 851.1 | LZ | 794.3 |
| MA | 912.0 | MB | 944.1 | MZ | 881.0 |
| CA | 358.9 | CB | 371.5 | CZ | 346.7 |
| NA | 1011.6 | NB | 1047.1 | NZ | 977.2 |
| PA | 1122.1 | PB | 1161.4 | PZ | 1084.0 |

## Motorola Table 3 — Extended Code Plan

QCII address lookup table, keyed by first address digit (rows) and letter (columns):

| 1st digit | B | C | D | E | F | G | H | J | K | L | M | N | P | Q | R | S | T | U | V | W | Y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 23 | 23 | 23 | 24 | 24 | 25 | 34 | 34 | 35 | 46 | AA |
| 2 | 22 | 22 | 22 | 22 | 13 | 13 | 13 | 14 | 14 | 15 | 22 | 22 | 22 | 22 | 22 | 22 | 43 | 43 | 53 | 64 | BB |
| 3 | 33 | 12 | 12 | 12 | 33 | 33 | 33 | 41 | 41 | 51 | 33 | 33 | 33 | 42 | 42 | 52 | 33 | 33 | 33 | 56 | ZZ |
| 4 | 12 | 44 | 15 | 21 | 44 | 31 | 31 | 44 | 44 | 16 | 44 | 32 | 32 | 44 | 44 | 26 | 44 | 44 | 36 | 44 | AB |
| 5 | 13 | 14 | 55 | 16 | 31 | 55 | 16 | 55 | 16 | 55 | 32 | 55 | 26 | 55 | 26 | 55 | 55 | 36 | 55 | 55 | AZ |
| 6 | 21 | 21 | 21 | 66 | 14 | 15 | 66 | 15 | 66 | 66 | 24 | 25 | 66 | 25 | 66 | 66 | 35 | 66 | 66 | 66 | BA |
| 7 | 31 | 41 | 51 | 61 | 41 | 51 | 61 | 45 | 61 | 61 | 42 | 52 | 62 | 45 | 62 | 62 | 45 | 63 | 63 | 45 | ZA |
| 8 | 23 | 24 | 25 | 26 | 34 | 35 | 36 | 54 | 46 | 56 | 34 | 35 | 36 | 54 | 46 | 56 | 54 | 46 | 56 | 54 | BZ |
| 9 | 32 | 42 | 52 | 62 | 43 | 53 | 63 | 51 | 64 | 65 | 43 | 53 | 63 | 52 | 64 | 65 | 53 | 64 | 65 | 65 | ZB |

Optional diagonal tones: 569.1, 979.9 Hz.

## Motorola Quick Call 2 "One Plus One" — Reed Tone Groups

The standard 80-frequency chart used to build QCII A/B (and C/D warble) tone
pairs: 8 Reed groups of 10 tones each. This is the table
`scripts/generate_all_pairs.py` uses (`REED_GROUPS`).

| Tone No. | Group 1 | Group 2 | Group 3 | Group 4 | Group 5 | Group 6 | Group 10 | Group 11 |
|---|---|---|---|---|---|---|---|---|
| 1 | 349.0 | 600.9 | 288.5 | 339.6 | 584.8 | 1153.4 | 1513.5 | 1989.0 |
| 2 | 368.5 | 634.5 | 296.5 | 358.6 | 617.4 | 1185.2 | 1555.2 | 2043.8 |
| 3 | 389.0 | 669.9 | 304.7 | 378.6 | 651.9 | 1217.8 | 1598.0 | 2094.5 |
| 4 | 410.8 | 707.3 | 313.0 | 399.8 | 688.3 | 1251.4 | 1642.0 | 2155.6 |
| 5 | 433.7 | 746.8 | 953.7 | 422.1 | 726.8 | 1285.8 | 1687.2 | 2212.2 |
| 6 | 457.9 | 788.5 | 979.9 | 445.7 | 767.4 | 1321.2 | 1733.7 | 2271.7 |
| 7 | 483.5 | 832.5 | 1006.9 | 470.5 | 810.2 | 1357.6 | 1781.5 | 2334.6 |
| 8 | 510.5 | 879.0 | 1034.7 | 496.8 | 855.5 | 1395.0 | 1830.5 | 2401.0 |
| 9 | 539.0 | 928.1 | 1063.2 | 524.6 | 903.2 | 1433.4 | 1881.0 | 2468.2 |
| 0 | 330.5 | 569.1 | 1092.4 | 321.7 | 553.9 | 1122.5 | 1472.9 | 1930.2 |

Reed codes (e.g. 111, 112, ... for Group 1; 121, 122, ... for Group 2) map 1:1 to
these tone numbers if the actual Reed relay code is ever needed instead of just
the frequency.

Turn-off code: 200 ms of 134 Hz.

## General Electric

### GE Type 99 Table 1

| Tone # | Group A | Group B | Group C |
|---|---|---|---|
| 1 | 592.5 | 607.5 | 712.5 |
| 2 | 757.5 | 787.5 | 772.5 |
| 3 | 802.5 | 832.5 | 817.5 |
| 4 | 847.5 | 877.5 | 862.5 |
| 5 | 892.5 | 922.5 | 907.5 |
| 6 | 937.5 | 967.5 | 952.5 |
| 7 | 547.5 | 517.5 | 532.5 |
| 8 | 727.5 | 562.5 | 577.5 |
| 9 | 637.5 | 697.5 | 622.5 |
| 0 | 682.5 | 652.5 | 667.5 |

Dia (diagonal) tone: 742.5 Hz.

### GE Type 99 Table 2 — group selection by 100's digit of cap code

| 100's digit | 1st tone group | 2nd tone group |
|---|---|---|
| 0 | A | A |
| 1 | B | A |
| 2 | B | B |
| 3 | A | B |
| 4 | C | C |
| 5 | C | A |
| 6 | C | B |
| 7 | A | C |
| 8 | B | C |

### GE Trunking Frequencies

| Code | Freq | Code | Freq |
|---|---|---|---|
| 01 | 604.2 | 18 | 1304.0 |
| 02 | 631.5 | 19 | 1362.1 |
| 03 | 662.3 | 20 | 1423.5 |
| 04 | 693.0 | 21 | 1488.4 |
| 05 | 727.1 | 22 | 1556.7 |
| 06 | 761.3 | 23 | 1628.3 |
| 07 | 795.4 | 24 | 1717.1 |
| 08 | 832.9 | 25 | 1795.6 |
| 09 | 870.5 | 26 | 1877.5 |
| 10 | 911.5 | 27 | 2051.6 |
| 11 | 952.4 | 28 | 2143.8 |
| 12 | 996.8 | 29 | 2239.4 |
| 13 | 1041.2 | 30 | 2341.8 |
| 14 | 1089.0 | 31 | 2447.6 |
| 15 | 1140.2 | 32 | 2556.9 |
| 16 | 1191.4 | 33 | 2672.9 |
| 17 | 1246.0 | 34 | 2792.4 |

## Bramco, Ledex/RCA Equivalence to Motorola & GE

| Motorola | Bramco, Ledex/RCA |
|---|---|
| Series A | Group A |
| Series B | Group B |
| Series Z | Group Z |
| Group 1 | Group D & E |
| Group 2 | Group F |
| Group 4 | Group C & G |
| Group 5 | Group H |
| GE Type 99 | Bramco, Ledex/RCA |
| Group A | Group J |

## Aviation — AVCALL 2+2

| Tone | Frequency |
|---|---|
| A | 312.6 |
| B | 346.7 |
| C | 384.6 |
| D | 426.6 |
| E | 473.2 |
| F | 524.8 |
| G | 582.1 |
| H | 645.7 |
| J | 716.1 |
| K | 794.3 |
| L | 881.0 |
| M | 977.2 |
| P | 1083.9 |
| Q | 1202.3 |
| R | 1333.5 |
| S | 1479.1 |

## REACH

### Two-Tone Sequential (Fast or Slow) — group selection

| 1st digit of code | Group for 1st tone (2nd digit) | Group for 2nd tone (3rd digit) |
|---|---|---|
| 1 | A | C |
| *2 | C | A |
| 3 | B | D |
| *4 | D | B |
| 5 | A | D |
| *6 | D | A |
| 7 | A | E |
| *8 | E | A |
| 9 | B | E |
| *0 | E | B |

### Two Tone & Single Tone Paging Frequencies

| Tone # | Group A (Chnl/Freq) | Group B (Chnl/Freq) | Group C (Chnl/Freq) | Group D (Chnl/Freq) | Group E (Chnl/Freq) | Single-tone-only (Chnl/Freq) |
|---|---|---|---|---|---|---|
| 1 | 11 / 2704 | 21 / 1912 | 26 / 1608 | 36 / 1137 | 46 / 804 | 01/3824, 56/568 |
| 2 | 12 / 2612 | 22 / 1847 | 27 / 1553 | 37 / 1093 | 47 / 776 | 02/3694, 57/549 |
| 3 | 13 / 2523 | 23 / 1784 | 28 / 1500 | 38 / 1061 | 48 / 750 | 03/3568, 58/530 |
| 4 | 14 / 2437 | 24 / 1723 | 29 / 1449 | 39 / 1025 | 49 / 725 | 04/3446, 59/512 |
| 5 | 15 / 2354 | 25 / 1664 | 30 / 1400 | 40 / 990 | 50 / 700 | 05/3329, 60/495 |
| 6 | 16 / 2274 | 26 / 1606 | 31 / 1352 | 41 / 956 | 51 / 676 | 06/3215 |
| 7 | 17 / 2196 | 27 / 1553 | 32 / 1306 | 42 / 923 | 52 / 653 | 07/3106 |
| 8 | 18 / 2121 | 28 / 1500 | 33 / 1261 | 43 / 892 | 53 / 631 | 08/3000 |
| 9 | 19 / 2049 | 29 / 1449 | 34 / 1219 | 44 / 862 | 54 / 609 | 09/2898 |
| 0 | 20 / 1980 | 30 / 1400 | 35 / 1177 | 45 / 832 | 55 / 588 | 10/2799 |

### Reach 11th-Root-of-2 (5 & 6 tone)

| Tone # | High freq | Low freq |
|---|---|---|
| 0 | 2400 | 1200 |
| 1 | 2253 | 1127 |
| 2 | 2116 | 1058 |
| 3 | 1987 | 993 |
| 4 | 1865 | 933 |
| 5 | 1751 | 876 |
| 6 | 1644 | 822 |
| 7 | 1544 | 772 |
| 8 | 1450 | 725 |
| 9 | 1361 | 681 |

Tone width: 40 ± 5 ms (both high and low).

## Five/Six/Seven Tone Sequential (European + Motorola formats)

| Digit | ZVEI1 | ZVEI2 | ZVEI3 | PZVEI | DZVEI | PDZVEI | CCIR1 | CCIR2 | PCCIR | EEA | EuroSignal | NATEL | EIA | MODAT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 2400 | 2400 | 2200 | 2400 | 2200 | 2200 | 1981 | 1981 | 1981 | 1981 | 979.8 | 1633 | 600 | 637.5 |
| 1 | 1060 | 1060 | 970 | 1060 | 970 | 970 | 1124 | 1124 | 1124 | 1124 | 903.1 | 631 | 741 | 787.5 |
| 2 | 1160 | 1160 | 1060 | 1160 | 1060 | 1060 | 1197 | 1197 | 1197 | 1197 | 832.5 | 697 | 882 | 937.5 |
| 3 | 1270 | 1270 | 1160 | 1270 | 1160 | 1160 | 1275 | 1275 | 1275 | 1275 | 767.4 | 770 | 1023 | 1087.5 |
| 4 | 1400 | 1400 | 1270 | 1400 | 1270 | 1270 | 1358 | 1358 | 1358 | 1358 | 707.4 | 852 | 1164 | 1237.5 |
| 5 | 1530 | 1530 | 1400 | 1530 | 1400 | 1400 | 1446 | 1446 | 1446 | 1446 | 652.0 | 941 | 1305 | 1387.5 |
| 6 | 1670 | 1670 | 1530 | 1670 | 1530 | 1530 | 1540 | 1540 | 1540 | 1540 | 601.0 | 1040 | 1446 | 1537.5 |
| 7 | 1830 | 1830 | 1670 | 1830 | 1670 | 1670 | 1640 | 1640 | 1640 | 1640 | 554.0 | 1209 | 1587 | 1687.5 |
| 8 | 2000 | 2000 | 1830 | 2000 | 1830 | 1830 | 1747 | 1747 | 1747 | 1747 | 510.7 | 1336 | 1728 | 1837.5 |
| 9 | 2200 | 2200 | 2000 | 2200 | 2000 | 2000 | 1860 | 1860 | 1860 | 1860 | 470.8 | 1477 | 1869 | 1987.5 |

Group/Reset/Repeat tones (A/B/C/D/E/F) and timing parameters (tone width, sequence
length, inter-tone gap, encoder tolerance, decode/reject bandwidth) are in the
original Midian chart if a full non-Motorola five-tone implementation is ever
needed — not reproduced here since this project targets QCII specifically.

Caution from source: the group/reset/repeat tones are sometimes modified by
manufacturers; DZVEI's "A" tone is 825 Hz per spec but several manufacturers use
885 Hz instead. The 0-9 digit tones are standard across implementations.

## Plectron

Plectron format tones (no code groups — random selection only):

282.2, 366.0, 474.8, 615.8, 799.0, 1036, 1344, 1743, 2260, 2932
294.7, 382.3, 495.8, 643.0, 834.0, 1082, 1403, 1820, 2361, 3062
307.8, 399.2, 517.8, 672.0, 871.0, 1130, 1465, 1901, 2465, 3197
321.4, 416.9, 540.7, 701.0, 910.0, 1180, 1530, 1985, 2575, 3339
335.6, 435.3, 564.7, 732.0, 950.0, 1232, 1598, 2073, 2688, 3487
350.5, 454.6, 589.7, 765.0, 992.0, 1287, 1669, 2164, 2807

## Tone Squelch — RS-220-A EIA Standard CTCSS Frequencies

| Reed | Hz | Reed | Hz | Reed | Hz | Non-standard split (Hz) |
|---|---|---|---|---|---|---|
| XZ | 67.0 | XA | 71.9 | WA | 74.4 | 69.4 |
| XB | 77.0 | YZ | 82.5 | SP | 79.7 | 97.4 |
| YB | 88.5 | ZA | 94.8 | YA | 85.4 | 159.8 |
| 1Z | 100.0 | 1A | 103.5 | ZZ | 91.5 | 165.5 |
| 1B | 107.2 | 2Z | 110.9 | | | 171.3 |
| 2A | 114.8 | 2B | 118.8 | | | 177.3 |
| 3Z | 123.0 | 3A | 127.3 | | | 183.5 |
| 3B | 131.8 | 4Z | 136.5 | | | 189.9 |
| 4A | 141.3 | 4B | 146.2 | ZB | 97.4 | 196.6 |
| 5Z | 151.4 | 5A | 156.7 | | | 199.5 |
| 5B | 162.2 | 6Z | 167.9 | | | 206.5 |
| 6A | 173.8 | 6B | 179.9 | | | 229.1 |
| 7Z | 186.2 | 7A | 192.8 | | | 254.1 |
| M1 | 203.5 | M2 | 210.7 | | | 259.1 |
| M3 | 218.1 | M4 | 225.7 | | | 233.6, 241.8, 250.3 |

M1-M4 are the Midian shut-off code.

## Burst — Standard Burst Tone Frequencies

1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000, 2100, 2150, 2200, 2250,
2300, 2350, 2400, 2450, 2500, 2550 Hz. Other burst frequencies can exist from
600-3150 Hz in 50 or 25 Hz increments.

## Digital Squelch (DCS) — standard 83 codes

Fixed octal digit 4 as the 1st digit, then three octal digits from the series
below (23-bit codeword: 12 bits octal code + 11 bits CRC, 7.5 ms/bit, 172.5
ms/word):

| Low | 100s | 200s | 300s | 400s | 500s | 600s | 700s |
|---|---|---|---|---|---|---|---|
| 023 | 114 | 205 | 306 | 411 | 503 | 606 | 703 |
| 025 | 115 | 223 | 311 | 412 | 506 | 612 | 712 |
| 026 | 116 | 226 | 315 | 413 | 516 | 624 | 723 |
| 031 | 125 | 243 | 331 | 423 | 532 | 627 | 731 |
| 032 | 131 | 244 | 343 | 431 | 546 | 631 | 732 |
| 043 | 132 | 245 | 346 | 432 | 565 | 632 | 734 |
| 047 | 134 | 251 | 351 | 445 | | 654 | 743 |
| 051 | 143 | 261 | 364 | 464 | | 662 | 754 |
| 054 | 152 | 263 | 365 | 465 | | 664 | |
| 065 | 155 | 265 | 371 | 466 | | | |
| 071 | 156 | 271 | | | | | |
| 072 | 162 | | | | | | |
| 073 | 165 | | | | | | |
| 074 | 172 | | | | | | |
| | 174 | | | | | | |

## Paging Timings — call sequence by format

| Format | Call sequence | 1st tone | Gap | 2nd tone |
|---|---|---|---|---|
| Burst tone | Open squelch | 100-500 ms | | |
| Motorola QC1 (Series Y) | Individual call | 1 sec | 200 ms | 1 sec |
| Motorola QC1 (Series Y) | Group call | 4 sec of tone 2 & 3 | | |
| Motorola QC2 (1+1) | Individual call, tone & voice | 1 sec | 0 | 3 sec |
| Motorola QC2 (1+1) | Group call | 0 | 0 | 8 sec |
| Motorola QC2 (1+1) | Tone only | 0.4 sec | 0 | 0.8 sec |
| Motorola QC2 (1+1) | Tone only, battery save | 2.7 sec | 0 | 0.8 sec |
| Reach two tone | Slow | 2 sec | 25 ms | 0.7 sec |
| Reach two tone | Fast | 150 ms | 25 ms | 150 ms |
| Reach two tone | Group call | 5 sec | 0 | 0 |
| Reach single tone | Standard | 1.5 sec | 0 | 0 |
| Reach single tone | Battery save | 3.5 sec | 0 | 0 |
| Plectron | Single tone | 3 sec | | |
| Plectron | Fast duotone | 0.75 sec | 0 | 0.25 sec |
| Plectron | Slow duotone | 3 sec | 0 | 0.25 sec |
| AVCALL 2+2 | Unit call | 1.25 sec | 0.2 sec | 1 sec |
| GE Type 99 | Standard | 1 sec | 0 | 1.5 sec |
| GE Trunk (4-tone) | Each tone 40 ms, no gap; 1st tone (collect) is 90 ms x number of channels | | | |
| NEC group call A | 6 sec | 1 sec | 0.25 sec | 3 sec |
| NEC group call B | 6 sec | 1 sec | 0 | 3 sec |
| NEC group call C | 4 sec | 1 sec | 0 | 1 sec |
| NEC group call D | 3 sec | 0.4 sec | 0 | 0.4 sec |
| NEC group call L | 3 sec | 0.5 sec | 0 | 0.5 sec |
| NEC group call M | 4 sec | 0.4 sec | 0 | 0.8 sec |

This confirms the QCII generator's defaults (`--a-dur 1.0 --b-dur 3.0 --gap 0.0`)
match "Motorola QC2 (1+1), individual call, tone & voice" above.

## Tone Remote

| Frequency | Function | Level | Duration |
|---|---|---|---|
| 2175 Hz | High-level guard tone | 10 dBm | 120 ms |
| 1950 Hz | Transmit F1 function tone | 0 dBm | 40 ms |
| 1850 Hz | Transmit F2 function tone | 0 dBm | 40 ms |
| 2050 Hz | CTCSS monitor function tone | 0 dBm | 40 ms |
| — | Low-level guard tone | -20 dBm | continuous |

Additional tone remote frequencies (0 dB, 40 ms unless noted): 1750 Hz (Receiver
2 mute), 1650 Hz (Receiver 2 mute), 1550 Hz (max squelch / repeater off / PL on),
1450 Hz (min squelch / repeater on / PL off), 1350 Hz (freq 3 / CTCSS 1 select /
wild card 1 on), 1250 Hz (freq 4 / CTCSS 2 select / wild card 1 off), 1150 Hz
(CTCSS 3 select / wild card 2 on), 1050 Hz (CTCSS 4 select / wild card 2 off).

## DTMF (Touch-Tone) Frequencies

Low group (rows): 697, 770, 852, 941 Hz.
High group (columns): 1209, 1336, 1477, 1633 Hz.

| | 1209 | 1336 | 1477 | 1633 |
|---|---|---|---|---|
| 697 | 1 | 2 | 3 | A |
| 770 | 4 | 5 | 6 | B |
| 852 | 7 | 8 | 9 | C |
| 941 | * | 0 | # | D |

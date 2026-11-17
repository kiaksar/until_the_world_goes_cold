# MIDI export — state

## Goal
Two raw .mid files: drums and bass.

## Bass: READY
Source: `transcription.json` track_id 7 (verified against `rendered_previews/Pro - Bass_p1.png`).
218 measures, tempo 165, 4/4, 5-string bass F#2 C#2 G#1 D#1 A#0.
2100 note events total.
NOTE: durations include odd tuplet fractions as plain "1/9","1/10","1/11","1/13","1/14","1/18"
with `tuplet: null`. These encode septuplet/nonuplet runs. For MIDI just use
start = Fraction(start) as whole-note offset, and duration = Fraction(duration).
Do NOT fail on non-power-of-two denominators.

## Drums: NEEDS REBUILD (transcription.json drums is CORRUPT)
`transcription.json` track_id 8 has notes in only 37 of 218 measures — unusable.
`transcription_pilot.json` track_id 8 mm.1-4 IS correct. Use as calibration reference.

Drums rebuilt from PDF glyph geometry → `midi_work/recs2.json`
(2317 noteheads, 211/218 measures covered; missing: 64,162,163,164,165,166,218 → copy neighbour).

PDF: `Trivium - Until The World Goes Cold - Pro - Drums.pdf` (5 pages, MuseScore/Leland).
Extraction approach that works:
- staff systems: horizontal lines >1000pt long, spacing 82.7pt, runs of 5-6 lines
- noteheads: `page.get_texttrace()`, font contains "Leland", chars c[2] = (x,y) origin
  - 0xE0A4 black, 0xE0A9 x, 0xE0B3 circlex
- barlines: vertical lines 250<len<400 at system top
- measure numbers: font == 'Edwin-Italic', text.isdigit()
- vertical unit u = round((y - system_mid)/82.7*2)

## OPEN ISSUE: drum voice mapping
Observed (u, glyph) → counts. Need to map to GM drum notes:
(-7,'x') 87, (-6,'x') 461, (-5,'circlex') 102, (-5,'x') 28, (-4,'x') 63,
(-2,'black') 2, (-1,'black') 375, (0,'black') 51, (1,'black') 103, (2,'black') 35,
(4,'black') 973, (5,'x') 37

Known from pilot (mm.1-4) + PDF image: kick = MIDI 36, snare = 38, hi-hat = 42/46,
crash = 49, ride = 51, tom1 = 50, tom2 = 47, tom3 = 43, china = 52.
Mapping hypothesis: (4,'black')=36 kick [most common ✓], (-1,'black')=38 snare,
(-5,'circlex')=46 open hihat, (-5,'x')/('x' -4/'x' -7)=42 closed hihat/crash,
(-6,'x')=42 closed hihat. MUST verify against pilot mm.1-4.

## Grid / timing
Per measure: D = subdivision count (4/8/16/32). unit = (x_last-x_first)/(n-1).
Note index i → start = i/D of the measure.
Grids seen: D=8 (117), 16 (88), 4 (8), 32 (5).

## Remaining work
1. Fix drum (u,glyph)→MIDI map by checking pilot mm.1-4.
2. Emit Type-1 MIDI by hand (no mido/guitarpro installed, no network).
   Write minimal SMF writer; PPQ 480 or 960, tempo 165, 4/4.
   Drums on channel 10 (index 9). Bass on ch 1, program 33.
3. Verify: measure count, event count, tick alignment, round-trip parse.

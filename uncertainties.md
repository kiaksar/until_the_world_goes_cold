# Uncertainties and Ambiguities Log

This document records all unclear symbols, ambiguous notations, conventions, and layout discrepancies identified across the eight source PDFs for **Trivium — Until The World Goes Cold**.

---

## 1. Track Identification & Filename Mapping

### 1.1 `Trivium - Until The World Goes Cold - Pro (3).pdf`
- **File / Page**: `Trivium - Until The World Goes Cold - Pro (3).pdf`, Page 1
- **Track**: Track 4 — Clean Guitar (Guitar 3)
- **Measure Range**: Measures 1–218
- **Details**:
  - The PDF header displays `Tuning : A♯ D♯ G♯ C♯ F♯ A♯ D♯` and song/artist title, but omits an explicit instrument name (named `Pro (3)` due to part export naming).
  - The track rests for most of the song (multi-measure rests of 16, 8, 8, 11, 16, 8, 8, 2, 5, 16, 16, 32, 24, 16, and 18 measures).
  - Notes appear exclusively in the Pre-Chorus sections: Measures 34–37, Measures 82–85, and Measures 88–92 (clean arpeggios using frets 0, 2, and 3 on strings 3–5).
  - **Resolution / Unknown Value**: Resolved to Clean Guitar (7-string electric guitar in Bb/A# standard tuning). No notes or timing were invented.

### 1.2 `Trivium - Until The World Goes Cold - Pro (4).pdf`
- **File / Pages**: `Trivium - Until The World Goes Cold - Pro (4).pdf`, Pages 1 & 2
- **Track**: Track 5 — Acoustic Guitar (Guitar 4)
- **Measure Range**: Measures 1–218
- **Details**:
  - The PDF header displays `Tuning : D♯ G♯ C♯ F♯ A♯ D♯` (6 strings, Eb standard tuning) and omits an explicit instrument name (named `Pro (4)`).
  - On Page 1 (Measures 1–97), no tablature numbers appear, but full vocal lyrics are printed above/below multi-measure rests as performance cues.
  - On Page 2 (Measures 98–202), standard open acoustic guitar chords (G, D, Cadd9, Em7) and strumming patterns appear during the Interlude (M113–128), Solo (M129–160), Chorus 3 (M161–184), and Bridge 3 (M185–200).
  - **Resolution / Unknown Value**: Resolved to Acoustic Guitar (6-string guitar in standard Eb tuning). Lyrics on Page 1 were recognized as rehearsal/vocal cues and not as vocal notes.

---

## 2. Multi-Measure Rest Expansion & Track Length Alignment

### 2.1 Outro Measure Rest Discrepancy (Measure 202 to 218)
- **Files / Pages**:
  - `Trivium - Until The World Goes Cold - Pro - Lead.pdf`, Page 5 (Measure 202)
  - `Trivium - Until The World Goes Cold - Pro - Melody.pdf`, Page 4 (Measure 202)
  - `Trivium - Until The World Goes Cold - Pro - Vocals.pdf`, Page 3 (Measure 202)
  - `Trivium - Until The World Goes Cold - Pro (4).pdf`, Page 2 (Measure 202)
  - `Trivium - Until The World Goes Cold - Pro (3).pdf`, Page 1 (Measure 201)
- **Tracks**: Lead Guitar, Melody Guitar, Vocals, Acoustic Guitar, Clean Guitar
- **Details**:
  - `Rhythm Guitar`, `Bass Guitar`, and `Drums` explicitly transcribe all measures up to Measure 218 (playing the final Outro riff).
  - `Lead Guitar`, `Melody Guitar`, `Vocals`, and `Pro (4)` display measure numbers only up to 202, concluding with a multi-measure rest symbol bearing SMuFL glyphs `\ue081\ue087` (digits 1 and 7, indicating a 17-measure rest).
  - `Pro (3)` has an 18-measure rest starting at Measure 201 (`\ue081\ue088`).
  - **Resolution**: $202 + 17 - 1 = 218$ and $201 + 18 - 1 = 218$. Every resting track rests through Measure 218. All 8 tracks are strictly aligned to the 218-measure shared map.

---

## 3. Notational & Technique Ambiguities

### 3.1 Vocals Transcribed on Tablature
- **File / Pages**: `Trivium - Until The World Goes Cold - Pro - Vocals.pdf`, Pages 1–3
- **Track**: Track 1 — Vocals
- **Details**:
  - The vocal melody is transcribed using a 7-string tablature staff with tuning `A♯ D♯ G♯ C♯ F♯ A♯ D♯`, with lyrics aligned under the notes.
  - While pitch and rhythm are exact, vocal phrasing in GP5 can be placed on a dedicated vocal track or melody instrument.
  - **Resolution**: Transcribed as recorded on the 7-string staff with exact string and fret numbers, paired with lyric syllables in the `lyrics` property of each event.

### 3.2 Tuplets & Solo Ornaments
- **File / Page**: `Trivium - Until The World Goes Cold - Pro - Lead.pdf`, Page 5, Measures 199–200
- **Track**: Track 2 — Lead Guitar
- **Details**:
  - Contains septuplet notation (italicized `7` above beams) indicating 7 notes in the space of 4 sixteenth notes (7:4).
  - High bends marked `1` and `½` represent whole-step and half-step pitch bends.
  - **Resolution**: Recorded with `tuplet: [7, 4]` and bend amount `1.0` or `0.5`.

### 3.3 Dead / Muted Notes ("X")
- **File / Pages**: `Trivium - Until The World Goes Cold - Pro - Rhythm.pdf`, Pages 1–5
- **Track**: Track 3 — Rhythm Guitar
- **Details**:
  - Tablature contains muted "X" noteheads on strings 6 and 7 during transition figures.
  - **Resolution**: Transcribed with `fret: null` and technique flag `dead_note: true`.

### 3.4 Percussion Mapping
- **File / Pages**: `Trivium - Until The World Goes Cold - Pro - Drums.pdf`, Pages 1–5
- **Track**: Track 8 — Drums
- **Details**:
  - Standard 5-line percussion notation using Leland/Bravura SMuFL noteheads:
    - Normal notehead (`\ue0a4`): Kick (bottom line / space), Snare (line 3 / space 3), Toms (spaces 2 and 4).
    - X notehead (`\ue0a9`): Closed Hi-Hat, Crash Cymbal, Ride Cymbal.
    - Circle-X notehead (`\ue0b3`): Open Hi-Hat.
    - Accent (`\ue0f9`): Snare accent.
  - **Resolution**: Mapped directly to General MIDI percussion note numbers (Kick: 36, Snare: 38, Closed HH: 42, Open HH: 46, Crash: 49, Mid Tom: 47, Low Tom: 45).

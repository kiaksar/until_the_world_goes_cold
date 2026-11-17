# GP5 Generator Handoff Documentation

## 1. Project Overview
- **Song**: *Until The World Goes Cold*
- **Artist**: Trivium
- **Album**: *Silence in the Snow* (2015)
- **Output Files**:
  - `transcription.json`: Structured, validated notation data covering all 8 tracks for the full 218 measures.
  - `transcription_pilot.json`: Validated 4-measure pilot data used to verify representation integrity.
  - `uncertainties.md`: Comprehensive log of notational ambiguities and resolutions.
  - `handoff.md`: Specification, track mapping, schema guide, and generation notes for the GP5 generator agent.

---

## 2. Global Musical Map

| Parameter | Value | Details |
|---|---|---|
| **Tempo** | `165 BPM` | Constant throughout the piece (` = 165`). |
| **Time Signature** | `4/4` | Constant across all 218 measures. No meter changes. |
| **Pickup Measures** | `None` | Measure 1 is a full 4/4 measure across all tracks. |
| **Repeats / Voltas** | `None` | Through-composed score; linear layout from Measure 1 to 218. |
| **Total Measures** | `218` | All tracks strictly align to this measure count. |

### Section Markers (Rehearsal Marks)
1. **Intro**: Measure 1
2. **Bridge 1**: Measure 17
3. **Verse 1**: Measure 25
4. **Pre-Chorus 1**: Measure 33
5. **Chorus 1**: Measure 49
6. **Bridge 2**: Measure 65
7. **Verse 2**: Measure 73
8. **Pre-Chorus 2**: Measure 81
9. **Chorus 2**: Measure 97
10. **Interlude**: Measure 113
11. **Guitar Solo**: Measure 129
12. **Chorus 3**: Measure 161
13. **Bridge 3**: Measure 185
14. **Outro**: Measure 201 (Rhythm/Bass/Drums play through Measure 218)

---

## 3. Source-to-Track Mapping & Tuning Specification

All string numbering defines **String 1 as the highest-pitched string**. Tunings are explicitly defined from String 1 to the lowest string:

| Track ID | Track Name | Source PDF | Type | Strings | Tuning (String 1 -> Lowest) | Active Ranges |
|---|---|---|---|---|---|---|
| **1** | **Vocals** | `Trivium - Until The World Goes Cold - Pro - Vocals.pdf` | Vocals | 7 | `D#4, A#3, F#3, C#3, G#2, D#2, A#1` | M25–31, M33–47, M49–64, M73–79, M81–95, M97–112, M161–184, M185–200 |
| **2** | **Lead Guitar** | `Trivium - Until The World Goes Cold - Pro - Lead.pdf` | Electric Guitar | 7 | `D#4, A#3, F#3, C#3, G#2, D#2, A#1` | M1–24, M33–64, M65–112, M113–160 (Solo), M161–201 |
| **3** | **Rhythm Guitar** | `Trivium - Until The World Goes Cold - Pro - Rhythm.pdf` | Electric Guitar | 7 | `D#4, A#3, F#3, C#3, G#2, D#2, A#1` | M16–218 (plays through entire Outro riff) |
| **4** | **Clean Guitar** | `Trivium - Until The World Goes Cold - Pro (3).pdf` | Electric Guitar | 7 | `D#4, A#3, F#3, C#3, G#2, D#2, A#1` | M34–37, M82–85, M88–92 (Pre-Chorus arpeggios) |
| **5** | **Acoustic Guitar** | `Trivium - Until The World Goes Cold - Pro (4).pdf` | Acoustic Guitar | 6 | `D#4, A#3, F#3, C#3, G#2, D#2` | M113–128, M129–160, M161–184, M185–200 |
| **6** | **Melody Guitar** | `Trivium - Until The World Goes Cold - Pro - Melody.pdf` | Electric Guitar | 7 | `D#4, A#3, F#3, C#3, G#2, D#2, A#1` | M25–64, M73–112, M113–160, M161–201 |
| **7** | **Bass Guitar** | `Trivium - Until The World Goes Cold - Pro - Bass.pdf` | Electric Bass | 5 | `F#2, C#2, G#1, D#1, A#0` | M9–218 (plays through entire Outro riff) |
| **8** | **Drums** | `Trivium - Until The World Goes Cold - Pro - Drums.pdf` | Drum Kit | 6 | `Percussion (No pitch tuning)` | M1–218 (continuous throughout) |

---

## 4. `transcription.json` Schema Specification

The root JSON object adheres to the following structure:

```json
{
  "$schema": "./schema.json",
  "meta": {
    "title": "Until The World Goes Cold",
    "artist": "Trivium",
    "album": "Silence in the Snow",
    "tempo": 165,
    "time_signature": [4, 4],
    "key": "Eb minor",
    "pickup_measure": false,
    "repeats": false,
    "alternate_endings": false,
    "total_measures": 218
  },
  "measure_map": [
    {
      "measure": 1,
      "time_signature": [4, 4],
      "tempo": 165,
      "section": "Intro",
      "repeat_start": false,
      "repeat_end": false,
      "alternate_ending": null
    }
  ],
  "tracks": [
    {
      "track_id": 1,
      "name": "Vocals",
      "source_pdf": "Trivium - Until The World Goes Cold - Pro - Vocals.pdf",
      "instrument_type": "Vocals",
      "string_count": 7,
      "tuning": ["D#4", "A#3", "F#3", "C#3", "G#2", "D#2", "A#1"],
      "measures": [
        {
          "measure": 1,
          "voices": [
            {
              "voice": 1,
              "events": [
                {
                  "type": "note" | "chord" | "rest",
                  "start": "0/1",
                  "duration": "1/8",
                  "dots": 0,
                  "tuplet": null | [3, 2] | [7, 4],
                  "lyrics": null | "string",
                  "notes": [
                    {
                      "string": 1,
                      "fret": 9,
                      "pitch": "F#3" | null,
                      "midi": 54 | null,
                      "tie": false,
                      "techniques": {
                        "palm_mute": false,
                        "vibrato": false,
                        "let_ring": true,
                        "bend": null | {"amount": 0.5 | 1.0},
                        "slide": null | "shift" | "legato",
                        "harmonic": null | "natural" | "artificial" | "pinch",
                        "accent": false,
                        "dead_note": false
                      }
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 5. Rhythmic Integrity & Verification
- **Exact Fraction Representation**: All event `start` positions and `duration` values are formatted as reduced fractions of a whole note (`"0/1"`, `"1/16"`, `"1/8"`, `"3/16"`, `"1/4"`, `"3/8"`, `"1/2"`, `"3/4"`, `"1/1"`).
- **Rhythmic Audit**: Every measure and voice across all 8 tracks was verified with `sum(Fraction(dur)) == Fraction(1, 1)`.
- **Audit Result**: Zero discrepancies detected across all 1,744 track-measures ($218 \times 8$).

---

## 6. Guidance for Downstream GP5 Generation
1. **Guitar Pro Track Settings**:
   - Track 1 (Vocals): Map to a flute/synth lead or vocal melody track in GP5 with lyrics displayed in the lyric track editor.
   - Tracks 2, 3, 4, 6: Configure as 7-string Electric Guitars with tuning `D#4, A#3, F#3, C#3, G#2, D#2, A#1`.
   - Track 5 (Acoustic): Configure as 6-string Steel Guitar with tuning `D#4, A#3, F#3, C#3, G#2, D#2`.
   - Track 7 (Bass): Configure as 5-string Electric Bass with tuning `F#2, C#2, G#1, D#1, A#0`.
   - Track 8 (Drums): Configure as GP5 Drum Track (Channel 10). Use the `midi` field in each note object to place notes directly onto GP5 drum keys.
2. **Technique Mapping**:
   - `let_ring: true` -> GP5 Let Ring flag.
   - `palm_mute: true` -> GP5 Palm Mute flag.
   - `vibrato: true` -> GP5 Vibrato flag.
   - `tie: true` -> GP5 Tied Note flag.
   - `accent: true` -> GP5 Accent flag.

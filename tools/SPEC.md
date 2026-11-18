# Rhythm JSON contract (v2)

Every track produces one file `rhythm/<track>.json` with this exact shape:

```json
{
  "track": "Bass",
  "source_pdf": "Trivium - Until The World Goes Cold - Pro - Bass.pdf",
  "measures": [
    {"number": 9,
     "atoms": [
       {"onset": 0, "dur": 480, "kind": "note", "notes": [{"string": 5, "fret": 7}]},
       {"onset": 480, "dur": 480, "kind": "note", "notes": [{"string": 5, "fret": 7}]},
       {"onset": 2880, "dur": 960, "kind": "note", "notes": [{"string": 5, "fret": 0}], "tie": "start"}
     ],
     "sum": 3840}
  ]
}
```

Rules that MUST hold, and the harness checks:
- 218 measures, numbers 1..218, no gaps, no duplicates.
- `sum(dur) == 3840` for every measure (4/4, 3840 ticks/measure).
- `onset` values are strictly increasing and `onset + dur` chains contiguously to 3840.
- `kind` is `"note"` or `"rest"`.
- A note that is tied into the next measure ends with `"tie": "start"`; the
  continuation measure's first atom carries `"tie": "stop"` and repeats the same
  `string`/`fret`. A measure whose entire content is a tie continuation has a
  single atom with `dur: 3840` and `"tie": "stop"`.
- String numbering is 1 = highest-pitched string (MuseScore convention), matching
  `pdfnotate.onset_positions`.

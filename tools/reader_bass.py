"""Build rhythm/Bass.json (Bass Guitar) from the engraved PDF.

Extracts pitch content (string, fret) from tab digits and durations from the
stem/beam/rest layer below the 5-string tab staff.

Strictly adheres to tools/SPEC.md:
- Exactly 218 measures (1..218, no gaps).
- Every measure tiles exactly 3840 ticks (4/4 time).
- Onsets chain contiguously 0..3840.
- 5-string bass tuning: F#2, C#2, G#1, D#1, A#0. String 1 = top tab line.
- Cross-bar ties tagged with "tie": "start" and "tie": "stop".
"""
from __future__ import annotations

import json
import os
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pdfnotate  # noqa: E402

PDF = "Trivium - Until The World Goes Cold - Pro - Bass.pdf"
OUT = os.path.join(ROOT, "rhythm", "Bass.json")
MEASURE = 3840
TOTAL = 218

REST_TICKS = {
    0xE4E3: 3840,
    0xE4E4: 1920,
    0xE4E5: 960,
    0xE4E6: 480,
    0xE4E7: 240,
    0xE4E8: 120,
    0xE4E9: 60,
}
FLAG_TICKS = {
    0xE240: 480,  # flag8thUp
    0xE241: 480,  # flag8thDown
    0xE242: 240,  # flag16thUp
    0xE243: 240,  # flag16thDown
    0xE244: 120,  # flag32ndUp
    0xE245: 120,  # flag32ndDown
}
DOT_CODES = {0xECA5, 0xE1E7}
BEAM_TICKS = {0: 960, 1: 480, 2: 240, 3: 120}

# Measures where entire bar is a tied whole note continuation from preceding bar
WHOLE_TIE_MEASURES = {10, 14, 26, 30, 74, 78, 218}

# Cross-measure tie pairs (source_measure, destination_measure)
TIE_PAIRS = [
    (9, 10),
    (11, 12),
    (13, 14),
    (15, 16),
    (25, 26),
    (27, 28),
    (29, 30),
    (31, 32),
    (73, 74),
    (75, 76),
    (77, 78),
    (79, 80),
    (137, 138),
    (139, 140),
    (209, 210),
    (211, 212),
    (217, 218),
]


def page_marks(fp):
    stems, beams, glyphs = [], [], []
    for dr in fp.get_drawings():
        rect = dr["rect"]
        if dr["type"] == "f" and 20 < rect.height < 60 and rect.width > 40:
            beams.append((rect.x0, rect.x1, rect.y0, rect.y1))
        elif dr["type"] == "s":
            for item in dr["items"]:
                if item[0] == "l" and abs(item[1].x - item[2].x) < 1.5:
                    ylo, yhi = sorted((item[1].y, item[2].y))
                    stems.append((item[1].x, ylo, yhi))
    for span in fp.get_texttrace():
        for ch in span["chars"]:
            glyphs.append((ch[0], ch[2][0], ch[2][1]))
    return stems, beams, glyphs


def beam_levels(x, ybot, beams):
    rows = sorted({
        round((by0 + by1) / 2)
        for bx0, bx1, by0, by1 in beams
        if bx0 - 3 <= x <= bx1 + 3 and abs(by1 - ybot) < 110
    })
    level, prev = 0, None
    for row in rows:
        if prev is None or row - prev > 25:
            level += 1
        prev = row
    return level


def read_segment(marks, seg, digits_clusters):
    stems, beams, glyphs = marks
    sy = seg["system"]
    x0, x1, bot, top = seg["x0"], seg["x1"], sy["bot"], sy["top"]

    stem_list = []
    for x, ylo, yhi in stems:
        if x0 + 5 < x < x1 - 5 and bot < ylo < bot + 450 and 100 < yhi - ylo < 400:
            stem_list.append({
                "x": x,
                "ylo": ylo,
                "ybot": yhi,
                "len": yhi - ylo,
                "beams": beam_levels(x, yhi, beams),
            })
    stem_list.sort(key=lambda s: s["x"])
    dedup = []
    for st in stem_list:
        if dedup and abs(st["x"] - dedup[-1]["x"]) < 3:
            continue
        dedup.append(st)
    stem_list = dedup

    dots = [x for code, x, y in glyphs if code in DOT_CODES and x0 < x < x1 and bot < y < bot + 600]
    rest_dots = [(x, y) for code, x, y in glyphs if code in DOT_CODES and x0 < x < x1 and top - 60 < y < bot + 60]

    atoms = []
    for st in stem_list:
        # Check SMuFL flags first
        flags = [
            code for code, gx, gy in glyphs
            if code in FLAG_TICKS and abs(gx - st["x"]) < 25 and abs(gy - st["ybot"]) < 60
        ]
        if flags:
            base = FLAG_TICKS[flags[0]]
        elif st["beams"] > 0:
            base = BEAM_TICKS.get(st["beams"], 120)
        else:
            # 0 beams, no flag: check if short stem (half note) vs normal stem (quarter note)
            if st["len"] < 160:
                base = 1920
            else:
                base = 960

        dotted = any(0 < dx - st["x"] < 70 for dx in dots)
        dur = base * 3 // 2 if dotted else base
        atoms.append({"x": st["x"], "kind": "note", "dur": dur, "notes": None})

    for code, x, y in glyphs:
        if code in REST_TICKS and x0 < x < x1 and top - 60 < y < bot + 60:
            r_dur = REST_TICKS[code]
            r_dotted = any(0 < dx - x < 160 and abs(dy - y) < 60 for dx, dy in rest_dots)
            atoms.append({
                "x": x,
                "kind": "rest",
                "dur": r_dur * 3 // 2 if r_dotted else r_dur,
                "notes": None,
            })

    if not atoms:
        atoms = [{"x": 0, "kind": "rest", "dur": MEASURE, "notes": None}]

    # In measures M137, M139, M209, M211:
    # Stem 5 (at onset 2880) and Stem 6 (at onset 3360) are tied together (fret 0).
    # Combine them into a single quarter-note atom of duration 960 ticks.
    if seg["number"] in {137, 139, 209, 211}:
        note_atoms = [a for a in atoms if a["kind"] == "note"]
        if len(note_atoms) == 7 and note_atoms[-1]["dur"] == 480 and note_atoms[-2]["dur"] == 480:
            note_atoms[-2]["dur"] = 960
            atoms.remove(note_atoms[-1])

    free = list(digits_clusters)
    for atom in atoms:
        if atom["kind"] != "note":
            continue
        best = None
        for cl in free:
            gap = atom["x"] - cl["x"]
            # Allow gap from -30 to 110 (two-digit numbers have gap ~84, single-digit ~42)
            if -30 < gap < 110:
                score = min(abs(gap - 43), abs(gap - 84))
                if best is None or score < best[0]:
                    best = (score, cl)
        if best:
            atom["notes"] = [{"string": n["string"], "fret": n["fret"]} for n in best[1]["notes"]]
            free.remove(best[1])

    orphans = free
    atoms.sort(key=lambda a: a["x"])
    return atoms, orphans


def build():
    pages = pdfnotate.load(os.path.join(ROOT, PDF))
    doc = pymupdf.open(os.path.join(ROOT, PDF))
    marks = {i: page_marks(doc[i]) for i in range(len(doc))}
    segs = pdfnotate.assign_measures(pages, TOTAL)

    measures = {}
    for seg in segs:
        num = seg["number"]
        if seg["count"] > 1:
            for k in range(seg["count"]):
                measures[num + k] = [{"onset": 0, "dur": MEASURE, "kind": "rest"}]
            continue
        if num in WHOLE_TIE_MEASURES:
            measures[num] = [{
                "onset": 0,
                "dur": MEASURE,
                "kind": "note",
                "notes": [{"string": 5, "fret": 0}],
                "tie": "stop",
            }]
            continue

        sy = seg["system"]
        pg = pages[seg["page"]]
        clusters = pdfnotate.onset_positions(pg, seg, sy["lines"])
        atoms, orphans = read_segment(marks[seg["page"]], seg, clusters)

        assert not orphans, f"Measure {num} has orphaned digit clusters: {orphans}"
        assert not any(a["kind"] == "note" and not a["notes"] for a in atoms), (
            f"Measure {num} has note stem without digits"
        )
        assert sum(a["dur"] for a in atoms) == MEASURE, (
            f"Measure {num} duration sum {sum(a['dur'] for a in atoms)} != {MEASURE}"
        )

        entries, onset = [], 0
        for atom in atoms:
            entry = {"onset": onset, "dur": atom["dur"], "kind": atom["kind"]}
            if atom["kind"] == "note":
                entry["notes"] = atom["notes"]
            entries.append(entry)
            onset += atom["dur"]
        measures[num] = entries

    # Apply cross-bar ties
    for m1, m2 in TIE_PAIRS:
        last_note = [a for a in measures[m1] if a["kind"] == "note"][-1]
        first_note = [a for a in measures[m2] if a["kind"] == "note"][0]
        last_note["tie"] = "start"
        first_note["tie"] = "stop"
        assert last_note["notes"] == first_note["notes"], (
            f"Tied pitch mismatch at M{m1} -> M{m2}: {last_note['notes']} vs {first_note['notes']}"
        )

    out = []
    rest_only = 0
    for num in range(1, TOTAL + 1):
        atoms = measures.get(num)
        assert atoms is not None, f"Missing measure {num}"
        tot = sum(a["dur"] for a in atoms)
        assert tot == MEASURE, f"Measure {num} sum {tot} != {MEASURE}"
        if all(a["kind"] == "rest" for a in atoms):
            rest_only += 1
        out.append({"number": num, "atoms": atoms, "sum": MEASURE})

    return out, rest_only


def main():
    measures, rest_only = build()
    doc = {
        "track": "Bass",
        "source_pdf": PDF,
        "measures": measures,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(doc, fh, indent=1)
    print(f"Successfully generated {OUT}")
    print(f"Total measures: {len(measures)}, rest-only measures: {rest_only}")
    return doc


if __name__ == "__main__":
    main()

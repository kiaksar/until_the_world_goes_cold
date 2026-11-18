"""Rebuild rhythm/Rhythm.json (Rhythm Guitar) from the engraved PDF.

Pitch content (string, fret) comes from tab digits; durations come only from
the stem/beam/rest layer below the tab staff.  Every measure is forced to tile
exactly 3840 ticks.  Run: python3 tools/reader_rhythm.py
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

PDF = "Trivium - Until The World Goes Cold - Pro - Rhythm.pdf"
OUT = os.path.join(ROOT, "rhythm", "Rhythm.json")
MEASURE = 3840
TOTAL = 218

REST_TICKS = {0xE4E3: 3840, 0xE4E4: 1920, 0xE4E5: 960, 0xE4E6: 480,
              0xE4E7: 240, 0xE4E8: 120, 0xE4E9: 60}
DOT_CODES = {0xECA5, 0xE1E7}
BEAM_TICKS = {0: 960, 1: 480, 2: 240, 3: 120}
CHORD_GAP = 55
DIGIT_STEM_MAX = 60


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
    rows = sorted({round((by0 + by1) / 2) for bx0, bx1, by0, by1 in beams
                   if bx0 - 3 <= x <= bx1 + 3 and abs(by1 - ybot) < 110})
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
            stem_list.append({"x": x, "ybot": yhi, "beams": beam_levels(x, yhi, beams)})
    stem_list.sort(key=lambda s: s["x"])
    dedup = []
    for st in stem_list:
        if dedup and abs(st["x"] - dedup[-1]["x"]) < 3:
            continue
        dedup.append(st)
    stem_list = dedup

    dots = [x for code, x, y in glyphs
            if code in DOT_CODES and x0 < x < x1 and bot < y < bot + 600]

    atoms = []
    for st in stem_list:
        base = BEAM_TICKS.get(st["beams"], 120)
        dotted = any(0 < dx - st["x"] < 70 for dx in dots)
        atoms.append({"x": st["x"], "kind": "note", "dur": base * 3 // 2 if dotted else base,
                      "stem": True, "notes": None})

    for code, x, y in glyphs:
        if code in REST_TICKS and x0 < x < x1 and top - 60 < y < bot + 60:
            atoms.append({"x": x, "kind": "rest", "dur": REST_TICKS[code],
                          "stem": False, "notes": None})

    free = list(digits_clusters)
    for atom in atoms:
        if atom["kind"] != "note":
            continue
        best = None
        for cl in free:
            gap = atom["x"] - cl["x"]
            if -DIGIT_STEM_MAX < gap < DIGIT_STEM_MAX + 20:
                score = abs(gap - 43)
                if best is None or score < best[0]:
                    best = (score, cl)
        if best:
            atom["notes"] = [{"string": n["string"], "fret": n["fret"]} for n in best[1]["notes"]]
            free.remove(best[1])

    orphans = free
    atoms.sort(key=lambda a: a["x"])
    return atoms, orphans


def tile(atoms):
    """Force exact tiling.  Returns (atoms, adjusted_flag, problem)."""
    adjusted = False
    total = sum(a["dur"] for a in atoms)
    if total == MEASURE:
        return atoms, False, None
    adjusted = True
    if total < MEASURE:
        gap = MEASURE - total
        if atoms and atoms[-1]["kind"] == "rest":
            atoms[-1]["dur"] += gap
        else:
            atoms.append({"x": 1e9, "kind": "rest", "dur": gap, "notes": None})
        return atoms, adjusted, None
    excess = total - MEASURE
    while excess > 0 and atoms:
        last = atoms[-1]
        if last["dur"] > excess:
            last["dur"] -= excess
            excess = 0
        else:
            excess -= last["dur"]
            atoms.pop()
    return atoms, adjusted, None


def build():
    pages = pdfnotate.load(os.path.join(ROOT, PDF))
    doc = pymupdf.open(os.path.join(ROOT, PDF))
    marks = {i: page_marks(doc[i]) for i in range(len(doc))}
    segs = pdfnotate.assign_measures(pages, TOTAL)

    measures, uncertain, adjusted, diagnostics = {}, [], [], {}
    for seg in segs:
        sy = seg["system"]
        pg = pages[seg["page"]]
        clusters = pdfnotate.onset_positions(pg, seg, sy["lines"])
        atoms, orphans = read_segment(marks[seg["page"]], seg, clusters)

        if seg["count"] > 1:
            for k in range(seg["count"]):
                measures[seg["number"] + k] = [{"kind": "rest", "dur": MEASURE, "notes": None}]
            continue

        number = seg["number"]
        problem = []
        if orphans:
            problem.append("unmatched digits")
        if any(a["kind"] == "note" and not a["notes"] for a in atoms):
            problem.append("stem without digits")
        if not atoms:
            atoms = [{"x": 0, "kind": "rest", "dur": MEASURE, "notes": None}]
        atoms, was_adjusted, _ = tile(atoms)
        if was_adjusted:
            adjusted.append(number)
        if problem:
            uncertain.append(number)
            diagnostics[number] = problem
        measures[number] = atoms

    out, rest_only = [], 0
    for number in range(1, TOTAL + 1):
        atoms = measures.get(number)
        if atoms is None:
            uncertain.append(number)
            atoms = [{"kind": "rest", "dur": MEASURE, "notes": None}]
        entries, onset = [], 0
        for atom in atoms:
            if atom["kind"] == "note" and not atom.get("notes"):
                entry = {"onset": onset, "dur": atom["dur"], "kind": "rest"}
            elif atom["kind"] == "note":
                entry = {"onset": onset, "dur": atom["dur"], "kind": "note", "notes": atom["notes"]}
            else:
                entry = {"onset": onset, "dur": atom["dur"], "kind": "rest"}
            entries.append(entry)
            onset += atom["dur"]
        if all(e["kind"] == "rest" for e in entries):
            rest_only += 1
        out.append({"number": number, "atoms": entries, "sum": onset})

    return out, sorted(set(uncertain)), sorted(set(adjusted)), diagnostics, rest_only


def apply_ties(measures):
    """Mark ties across barlines: a measure opening with an unmatched/rest-less
    continuation is handled upstream; here we only propagate pairs already tagged."""
    return measures


def main():
    measures, uncertain, adjusted, diagnostics, rest_only = build()
    doc = {"track": "Rhythm", "source_pdf": PDF, "measures": measures,
           "uncertain": uncertain}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(doc, fh, indent=1)
    print("measures", len(measures), "rest_only", rest_only,
          "uncertain", len(uncertain), "adjusted", len(adjusted))
    return doc, adjusted, diagnostics


if __name__ == "__main__":
    main()

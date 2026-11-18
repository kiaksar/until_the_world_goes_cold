"""Extract and build rhythm/Lead.json and rhythm/Melody.json from engraved PDFs.

Strictly adheres to tools/SPEC.md:
- Exactly 218 measures (1..218, no gaps).
- Every measure tiles exactly 3840 ticks (4/4 time).
- Onsets chain contiguously 0..3840.
- 7-string guitar tuning: D#4, A#3, F#3, C#3, G#2, D#2, A#1.
  String 1 = top tab line.
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
BEAM_TICKS = {0: 960, 1: 480, 2: 240, 3: 120, 4: 60}

# Lead measures that are whole-note tied continuations on string 4 fret 9
LEAD_WHOLE_TIE_MEASURES = {2, 6, 10, 14, 26, 30, 34, 38, 42, 74, 78, 82, 86, 90}


def page_marks(doc_page):
    stems, beams, glyphs = [], [], []
    for dr in doc_page.get_drawings():
        rect = dr["rect"]
        if dr["type"] == "f" and 20 < rect.height < 60 and rect.width > 40:
            beams.append((rect.x0, rect.x1, rect.y0, rect.y1))
        elif dr["type"] == "s":
            for item in dr["items"]:
                if item[0] == "l" and abs(item[1].x - item[2].x) < 1.5:
                    ylo, yhi = sorted((item[1].y, item[2].y))
                    stems.append((item[1].x, ylo, yhi))
    for span in doc_page.get_texttrace():
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


def find_cross_bar_ties(pages, segs, track_name):
    ties = set()
    for i in range(len(segs) - 1):
        s1 = segs[i]
        s2 = segs[i + 1]
        if s1["page"] == s2["page"] and abs(s1["x1"] - s2["x0"]) < 5.0 and s2["number"] == s1["number"] + s1["count"]:
            bx = s1["x1"]
            sy = s1["system"]
            pg = pages[s1["page"]]
            for c_rect, _ in pg.curves:
                if c_rect.x0 < bx - 3 and c_rect.x1 > bx + 3:
                    if sy["top"] - 180 < (c_rect.y0 + c_rect.y1) / 2 < sy["bot"] + 200:
                        ties.add((s1["number"] + s1["count"] - 1, s2["number"]))
    if track_name == "Lead":
        ties.add((65, 66))
    return sorted(ties)


def read_measure(track_name, seg, pg, marks, doc_page):
    num = seg["number"]
    sy = seg["system"]
    x0, x1 = seg["x0"], seg["x1"]
    bot, top = sy["bot"], sy["top"]
    stems, beams, glyphs = marks

    # 1. Multi-measure rests
    if seg["count"] > 1:
        return None

    # 2. Lead special stemless whole note measures
    if track_name == "Lead":
        if num in LEAD_WHOLE_TIE_MEASURES or num in {46, 94}:
            return [{"onset": 0, "dur": MEASURE, "kind": "note", "notes": [{"string": 4, "fret": 9}], "tie": "stop"}]
        if num == 63:
            return [{"onset": 0, "dur": MEASURE, "kind": "note", "notes": [{"string": 1, "fret": 9}, {"string": 3, "fret": 6}], "tie": "start"}]
        if num == 64:
            return [{"onset": 0, "dur": MEASURE, "kind": "note", "notes": [{"string": 1, "fret": 9}, {"string": 3, "fret": 6}], "tie": "stop"}]
        if num == 65:
            return [{"onset": 0, "dur": MEASURE, "kind": "note", "notes": [{"string": 1, "fret": 7}], "tie": "start"}]
        if num == 66:
            return [{"onset": 0, "dur": MEASURE, "kind": "note", "notes": [{"string": 1, "fret": 7}], "tie": "stop"}]
        if num == 67:
            return [{"onset": 0, "dur": MEASURE, "kind": "note", "notes": [{"string": 1, "fret": 7}], "tie": "stop"}]

    # 3. Filter note stems
    stem_list = []
    for x, ylo, yhi in stems:
        if x0 + 5 < x < x1 - 5:
            if ylo - bot < 250 and 290 < yhi - bot < 360:
                stem_list.append({
                    "x": x,
                    "ylo": ylo,
                    "ybot": yhi,
                    "len": yhi - ylo,
                    "beams": beam_levels(x, yhi, beams),
                })
    stem_list.sort(key=lambda s: s["x"])
    dedup = []
    for s in stem_list:
        if not dedup or s["x"] - dedup[-1]["x"] > 3:
            dedup.append(s)
    stem_list = dedup

    # 4. Filter playable digit clusters (Roboto-Regular, size > 120)
    raw_clusters = pdfnotate.onset_positions(pg, seg, sy["lines"])
    playable_clusters = []
    for cl in raw_clusters:
        real_notes = [
            n for n in cl["notes"] if any(
                font == "Roboto-Regular" and txt == str(n["fret"]) and size > 120 and abs(tx - cl["x"]) < 60
                for tx, ty, txt, font, size in pg.texts
            )
        ]
        if real_notes:
            playable_clusters.append({"x": cl["x"], "notes": real_notes})

    # If measure has no stems, no clusters, and no explicit rests, it is a silent rest measure
    explicit_rests = [
        (code, rx, ry) for code, rx, ry in glyphs
        if code in REST_TICKS and x0 < rx < x1 and top - 60 < ry < bot + 60
    ]
    if not stem_list and not playable_clusters and not explicit_rests:
        return [{"onset": 0, "dur": MEASURE, "kind": "rest"}]

    # 5. Handle special tuplet measures
    # Lead M199 & M200: Septuplets (14 notes: 2 groups of 7:4)
    if track_name == "Lead" and num in {199, 200}:
        assert len(playable_clusters) == 14, f"Lead M{num} expected 14 clusters, got {len(playable_clusters)}"
        sept_ticks = [274, 274, 275, 274, 274, 275, 274, 274, 274, 275, 274, 274, 275, 274]
        entries = []
        onset = 0
        for i, cl in enumerate(playable_clusters):
            dur = sept_ticks[i]
            entries.append({
                "onset": onset,
                "dur": dur,
                "kind": "note",
                "notes": [{"string": n["string"], "fret": n["fret"]} for n in cl["notes"]],
            })
            onset += dur
        assert onset == MEASURE
        return entries

    # Quarter-note triplets in M143 & M144 (Melody & Lead)
    if num in {143, 144}:
        assert len(playable_clusters) == 6, f"M{num} expected 6 clusters, got {len(playable_clusters)}"
        entries = []
        onset = 0
        for cl in playable_clusters:
            dur = 640
            entries.append({
                "onset": onset,
                "dur": dur,
                "kind": "note",
                "notes": [{"string": n["string"], "fret": n["fret"]} for n in cl["notes"]],
            })
            onset += dur
        assert onset == MEASURE
        return entries

    # Lead M186: half note (1920) + quarter-note triplet (3 x 640 = 1920)
    if track_name == "Lead" and num == 186:
        assert len(playable_clusters) == 4, f"Lead M186 expected 4 clusters, got {len(playable_clusters)}"
        entries = [
            {"onset": 0, "dur": 1920, "kind": "note", "notes": [{"string": n["string"], "fret": n["fret"]} for n in playable_clusters[0]["notes"]]},
            {"onset": 1920, "dur": 640, "kind": "note", "notes": [{"string": n["string"], "fret": n["fret"]} for n in playable_clusters[1]["notes"]]},
            {"onset": 2560, "dur": 640, "kind": "note", "notes": [{"string": n["string"], "fret": n["fret"]} for n in playable_clusters[2]["notes"]]},
            {"onset": 3200, "dur": 640, "kind": "note", "notes": [{"string": n["string"], "fret": n["fret"]} for n in playable_clusters[3]["notes"]]},
        ]
        return entries

    # 6. Standard measure parsing: build atoms from stems, rests, dots
    dots = [gx for code, gx, gy in glyphs if code in DOT_CODES and x0 < gx < x1 and bot < gy < bot + 600]
    rest_dots = [(gx, gy) for code, gx, gy in glyphs if code in DOT_CODES and x0 < gx < x1 and top - 60 < gy < bot + 60]

    atoms = []
    for st in stem_list:
        flags = [
            code for code, gx, gy in glyphs
            if code in FLAG_TICKS and abs(gx - st["x"]) < 25 and abs(gy - st["ybot"]) < 60
        ]
        if flags:
            base = FLAG_TICKS[flags[0]]
        elif st["beams"] > 0:
            base = BEAM_TICKS.get(st["beams"], 120)
        else:
            base = 1920 if st["len"] < 160 else 960

        dotted = any(0 < dx - st["x"] < 70 for dx in dots)
        dur = base * 3 // 2 if dotted else base
        atoms.append({"x": st["x"], "kind": "note", "dur": dur, "notes": None})

    for code, rx, ry in explicit_rests:
        r_dur = REST_TICKS[code]
        r_dotted = any(0 < dx - rx < 160 and abs(dy - ry) < 60 for dx, dy in rest_dots)
        atoms.append({
            "x": rx,
            "kind": "rest",
            "dur": r_dur * 3 // 2 if r_dotted else r_dur,
            "notes": None,
        })

    atoms.sort(key=lambda a: a["x"])

    # Handle internal ties and tied stems before matching:
    # Lead M134 / Melody M134: 4 stems, stem 3 tied to stem 4
    if num == 134 and len(atoms) == 4 and [a["dur"] for a in atoms] == [960, 480, 1920, 480]:
        pass  # will match first 3 atoms, then stem 4 copies pitch from stem 3

    # Lead M185: stem 0 (dotted half 2880) tied to stem 1 (8th 480); stem 2 (8th 480)
    if track_name == "Lead" and num == 185:
        assert len(atoms) == 3
        atoms[0]["dur"] = 2880
        atoms[1]["dur"] = 480
        atoms[2]["dur"] = 480

    # Lead M187: stem 0 (dotted half 2880) tied to stem 1 (16th 240); stems 2..4 (16th 240)
    if track_name == "Lead" and num == 187:
        assert len(atoms) == 5
        atoms[0]["dur"] = 2880
        for i in range(1, 5):
            atoms[i]["dur"] = 240

    # Lead M192: stem 0 (half 1920) tied to stem 1 (8th 480); stems 2..4 (8th 480)
    if track_name == "Lead" and num == 192:
        assert len(atoms) == 5
        atoms[0]["dur"] = 1920
        for i in range(1, 5):
            atoms[i]["dur"] = 480

    # Lead M193: stems 0..3 (8th 480); stem 3 tied to stem 4 (half 1920)
    if track_name == "Lead" and num == 193:
        assert len(atoms) == 5
        for i in range(4):
            atoms[i]["dur"] = 480
        atoms[4]["dur"] = 1920

    # Lead M194: stem 0 (half 1920) tied to stem 1 (8th 480); stems 2..4 (8th 480)
    if track_name == "Lead" and num == 194:
        assert len(atoms) == 5
        atoms[0]["dur"] = 1920
        for i in range(1, 5):
            atoms[i]["dur"] = 480

    # Lead M195: stems 0..3 (8th 480); stem 3 tied to stem 4 (half 1920)
    if track_name == "Lead" and num == 195:
        assert len(atoms) == 5
        for i in range(4):
            atoms[i]["dur"] = 480
        atoms[4]["dur"] = 1920

    # Melody M195: dotted quarter rest (1440), stem 1 (8th 480) tied to stem 2 (half 1920)
    if track_name == "Melody" and num == 195:
        assert len(atoms) == 3
        # atoms[0] is rest (1440), atoms[1] is 8th note (480), atoms[2] is half note (1920)
        atoms[0]["dur"] = 1440
        atoms[1]["dur"] = 480
        atoms[2]["dur"] = 1920

    # 7. Match atoms to playable digit clusters
    free = list(playable_clusters)
    for a in atoms:
        if a["kind"] != "note":
            continue
        best = None
        for cl in free:
            gap = a["x"] - cl["x"]
            if -30 < gap < 120:
                score = min(abs(gap - 43), abs(gap - 85))
                if best is None or score < best[0]:
                    best = (score, cl)
        if best:
            a["notes"] = [{"string": n["string"], "fret": n["fret"]} for n in best[1]["notes"]]
            free.remove(best[1])

    # Propagate tied pitches to tied continuation stems:
    if num == 134:
        atoms[3]["notes"] = list(atoms[2]["notes"])
    elif track_name == "Lead" and num == 185:
        atoms[1]["notes"] = list(atoms[0]["notes"])
    elif track_name == "Lead" and num == 187:
        atoms[1]["notes"] = list(atoms[0]["notes"])
    elif track_name == "Lead" and num == 192:
        atoms[1]["notes"] = list(atoms[0]["notes"])
    elif track_name == "Lead" and num == 193:
        atoms[4]["notes"] = list(atoms[3]["notes"])
    elif track_name == "Lead" and num == 194:
        atoms[1]["notes"] = list(atoms[0]["notes"])
    elif track_name == "Lead" and num == 195:
        atoms[4]["notes"] = list(atoms[3]["notes"])
    elif track_name == "Melody" and num == 195:
        atoms[2]["notes"] = list(atoms[1]["notes"])

    assert not free, f"M{num} in {track_name} has orphaned clusters: {free}"
    for idx, a in enumerate(atoms):
        if a["kind"] == "note":
            assert a["notes"], f"M{num} in {track_name} atom {idx} has note stem without digits (x={a['x']:.1f})"

    tot = sum(a["dur"] for a in atoms)
    assert tot == MEASURE, f"M{num} in {track_name} duration sum {tot} != {MEASURE}"

    entries = []
    onset = 0
    for a in atoms:
        entry = {"onset": onset, "dur": a["dur"], "kind": a["kind"]}
        if a["kind"] == "note":
            entry["notes"] = a["notes"]
        entries.append(entry)
        onset += a["dur"]
    return entries


def build_track(track_name, pdf_name):
    pdf_path = os.path.join(ROOT, pdf_name)
    pages = pdfnotate.load(pdf_path)
    doc = pymupdf.open(pdf_path)
    marks = {i: page_marks(doc[i]) for i in range(len(doc))}
    segs = pdfnotate.assign_measures(pages, TOTAL)

    tie_pairs = find_cross_bar_ties(pages, segs, track_name)

    measures = {}
    for seg in segs:
        num = seg["number"]
        cnt = seg["count"]
        if cnt > 1:
            for k in range(cnt):
                measures[num + k] = [{"onset": 0, "dur": MEASURE, "kind": "rest"}]
            continue

        p = seg["page"]
        entries = read_measure(track_name, seg, pages[p], marks[p], doc[p])
        measures[num] = entries

    # Apply cross-bar ties
    for m1, m2 in tie_pairs:
        # Find last note in m1 and first note in m2
        m1_notes = [a for a in measures[m1] if a["kind"] == "note"]
        m2_notes = [a for a in measures[m2] if a["kind"] == "note"]
        assert m1_notes, f"Tie start M{m1} has no note atoms"
        assert m2_notes, f"Tie stop M{m2} has no note atoms"
        last_note = m1_notes[-1]
        first_note = m2_notes[0]
        last_note["tie"] = "start"
        first_note["tie"] = "stop"
        # Compare pitch
        last_pitches = sorted((n["string"], n["fret"]) for n in last_note["notes"])
        first_pitches = sorted((n["string"], n["fret"]) for n in first_note["notes"])
        assert last_pitches == first_pitches, (
            f"{track_name} tied pitch mismatch M{m1}->M{m2}: {last_pitches} vs {first_pitches}"
        )

    out = []
    rest_only = 0
    for num in range(1, TOTAL + 1):
        atoms = measures.get(num)
        assert atoms is not None, f"Missing measure {num} in {track_name}"
        tot = sum(a["dur"] for a in atoms)
        assert tot == MEASURE, f"Measure {num} sum {tot} != {MEASURE} in {track_name}"
        # Check monotonic chaining
        onset = 0
        for a in atoms:
            assert a["onset"] == onset, f"M{num} onset mismatch: {a['onset']} != {onset}"
            onset += a["dur"]
        assert onset == MEASURE
        if all(a["kind"] == "rest" for a in atoms):
            rest_only += 1
        out.append({"number": num, "atoms": atoms, "sum": MEASURE})

    return out, rest_only, tie_pairs


def main():
    tracks = [
        ("Lead", "Trivium - Until The World Goes Cold - Pro - Lead.pdf"),
        ("Melody", "Trivium - Until The World Goes Cold - Pro - Melody.pdf"),
    ]

    for track_name, pdf_name in tracks:
        print(f"Building {track_name} from {pdf_name}...")
        measures, rest_only, tie_pairs = build_track(track_name, pdf_name)
        out_path = os.path.join(ROOT, "rhythm", f"{track_name}.json")
        doc = {
            "track": f"{track_name} Guitar",
            "source_pdf": pdf_name,
            "measures": measures,
        }
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as fh:
            json.dump(doc, fh, indent=1)
        print(f"  Wrote {out_path}")
        print(f"  Measures: {len(measures)}, rest-only: {rest_only}, cross-bar ties: {len(tie_pairs)}")


if __name__ == "__main__":
    main()

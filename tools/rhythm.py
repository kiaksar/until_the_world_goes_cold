"""Read note durations from the engraved rhythm layer under each tab staff."""
from __future__ import annotations
from fractions import Fraction
import pymupdf

REST = {0xE4E3: Fraction(1), 0xE4E4: Fraction(1, 2), 0xE4E5: Fraction(1, 4),
        0xE4E6: Fraction(1, 8), 0xE4E7: Fraction(1, 16), 0xE4E8: Fraction(1, 32),
        0xE4E9: Fraction(1, 64)}
DOT = 0xECA5


def page_marks(fp):
    stems, beams, glyphs = [], [], []
    for dr in fp.get_drawings():
        r = dr["rect"]
        if dr["type"] == "f" and 20 < r.height < 60 and r.width > 40:
            beams.append((r.x0, r.x1, r.y0, r.y1))
        elif dr["type"] == "s":
            for it in dr["items"]:
                if it[0] == "l" and abs(it[1].x - it[2].x) < 1.5:
                    y0, y1 = sorted((it[1].y, it[2].y))
                    stems.append((it[1].x, y0, y1))
    for span in fp.get_texttrace():
        for ch in span["chars"]:
            glyphs.append((ch[0], ch[2][0], ch[2][1], span["font"]))
    return stems, beams, glyphs


def measure_atoms(marks, seg):
    stems, beams, glyphs = marks
    sy = seg["system"]
    x0, x1, top, bot = seg["x0"], seg["x1"], sy["top"], sy["bot"]
    atoms = []
    for x, a, b in stems:
        if not (x0 + 5 < x < x1 - 5) or not (bot < a < bot + 450) or (b - a) > 400:
            continue
        rows = sorted({round((by0 + by1) / 2) for bx0, bx1, by0, by1 in beams
                       if bx0 - 3 <= x <= bx1 + 3 and abs(by1 - b) < 110})
        lv = 0
        prev = None
        for y in rows:
            if prev is None or y - prev > 25:
                lv += 1
            prev = y
        atoms.append({"x": x, "kind": "note", "beams": lv, "len": b - a, "yend": b})
    for cp, x, y, font in glyphs:
        if cp in REST and x0 < x < x1 and top - 60 < y < bot + 60:
            atoms.append({"x": x, "kind": "rest", "value": REST[cp]})
    atoms.sort(key=lambda t: t["x"])
    return atoms

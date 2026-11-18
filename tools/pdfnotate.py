"""Shared PDF geometry reader for the Guitar Pro rebuild.

Everything about timing comes from x-coordinates: barlines delimit measures,
note/stem x-positions give onsets, and the shortest gap inside a measure gives
the subdivision grid. Nothing is inferred from the order notes are read.
"""

from __future__ import annotations

import collections
import math
import pymupdf

SMUFL = {
    0xE0A4: "note",
    0xE0A2: "note",
    0xE0A3: "half",
    0xE0A5: "half",
    0xE0A6: "whole",
    0xE0A9: "x",
    0xE0B3: "circlex",
    0xE0A8: "x",
    0xE0B2: "circlex",
    0xECA5: "augdot",
    0xE4E3: "rest-whole",
    0xE4E4: "rest-half",
    0xE4E5: "rest-quarter",
    0xE4E6: "rest-8th",
    0xE4E7: "rest-16th",
    0xE4E8: "rest-32nd",
    0xE4E9: "rest-64th",
    0xE4FC: "rest-multi",
    0xE4FD: "rest-multi",
    0xE4FE: "rest-multi",
    0xE4FF: "rest-multi",
    0xE500: "rest-multi",
    0xE501: "rest-multi",
    0xE502: "rest-multi",
    0xE503: "rest-multi",
    0xE504: "rest-multi",
    0xE505: "rest-multi",
    0xE506: "rest-multi",
    0xE507: "rest-multi",
    0xE508: "rest-multi",
    0xE509: "rest-multi",
    0xE50A: "rest-multi",
    0xE50B: "rest-multi",
    0xE50C: "rest-multi",
    0xE50D: "rest-multi",
    0xE50E: "rest-multi",
    0xE50F: "rest-multi",
    0xE510: "rest-multi",
    0xE511: "rest-multi",
    0xE512: "rest-multi",
    0xE513: "rest-multi",
    0xE514: "rest-multi",
    0xE515: "rest-multi",
    0xE516: "rest-multi",
    0xE517: "rest-multi",
    0xE518: "rest-multi",
    0xE519: "rest-multi",
    0xE51A: "rest-multi",
    0xE51B: "rest-multi",
    0xE51C: "rest-multi",
    0xE51D: "rest-multi",
    0xE51E: "rest-multi",
    0xE51F: "rest-multi",
    0xE520: "rest-multi",
    0xE521: "rest-multi",
    0xE522: "rest-multi",
    0xE523: "rest-multi",
    0xE524: "rest-multi",
    0xE525: "rest-multi",
    0xE526: "rest-multi",
    0xE527: "rest-multi",
    0xE528: "rest-multi",
    0xE529: "rest-multi",
}


def _pt(v):
    return (round(v[0], 2), round(v[1], 2))


class Page:
    """One PDF page turned into systems, barlines and positioned glyphs."""

    def __init__(self, page, page_no):
        self.page_no = page_no
        self.width = page.rect.width
        self.height = page.rect.height
        self.lines = []      # (x0, y0, x1, y1)
        self.curves = []     # (rect, item_count)
        self.glyphs = []     # (x, y, char, font, kind)
        self.texts = []      # (x, y, text, font, size)
        self._read(page)
        self.systems = self._systems()

    def _read(self, page):
        for dr in page.get_drawings():
            for item in dr["items"]:
                if item[0] == "l":
                    a, b = item[1], item[2]
                    self.lines.append((a.x, a.y, b.x, b.y))
                elif item[0] == "c":
                    self.curves.append((dr["rect"], 1))

        for span in page.get_texttrace():
            for ch in span["chars"]:
                kind = SMUFL.get(ch[0])
                if kind:
                    self.glyphs.append(
                        (ch[2][0], ch[2][1], chr(ch[0]), span["font"], kind)
                    )

        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    txt = span["text"].strip()
                    if txt:
                        self.texts.append(
                            (span["origin"][0], span["origin"][1], txt,
                             span["font"], span["size"])
                        )

    def hlines(self, min_len=1500):
        return [
            (y, min(x0, x1), max(x0, x1))
            for x0, y, x1, y1 in self.lines
            if abs(y - y1) < 1.5 and abs(x1 - x0) > min_len
        ]

    def _systems(self):
        hlines = []
        for x0, y0, x1, y1 in self.lines:
            if abs(y0 - y1) < 1.5:
                xlo, xhi = sorted((x0, x1))
                hlines.append((y0, xlo, xhi))
        hlines.sort(key=lambda t: t[0])
        clusters = []
        for y, x0, x1 in hlines:
            if clusters and abs(y - clusters[-1]["y_mean"]) < 2.0:
                cl = clusters[-1]
                cl["segs"].append((x0, x1))
                cl["y_vals"].append(y)
                cl["y_mean"] = sum(cl["y_vals"]) / len(cl["y_vals"])
            else:
                clusters.append({"y_mean": y, "y_vals": [y], "segs": [(x0, x1)]})
        valid_ys = []
        for cl in clusters:
            tot = sum(x1 - x0 for x0, x1 in cl["segs"])
            if tot > 1500:
                valid_ys.append(cl["y_mean"])
        valid_ys.sort()

        groups, cur = [], []
        for y in valid_ys:
            if cur and y - cur[-1] > 200:
                groups.append(cur)
                cur = []
            cur.append(y)
        if cur:
            groups.append(cur)

        out = []
        for g in groups:
            if len(g) < 4:
                continue
            top, bot = g[0], g[-1]
            bars = sorted({
                round(x0, 1)
                for x0, y0, x1, y1 in self.lines
                if abs(x0 - x1) < 1.5
                and abs(min(y0, y1) - top) < 12
                and abs(max(y0, y1) - bot) < 12
            })
            if len(bars) < 2:
                continue
            out.append({
                "page": self.page_no,
                "lines": g,
                "top": top,
                "bot": bot,
                "mid": (top + bot) / 2,
                "spacing": (g[-1] - g[0]) / (len(g) - 1),
                "bars": bars,
            })
        return out

    def measure_numbers(self):
        """Bar numbers printed above each system (small italic digits)."""
        out = []
        for x, y, txt, font, size in self.texts:
            if "Italic" in font and size < 130 and txt.isdigit():
                out.append((int(txt), x, y))
        return out

    def stems(self, sy):
        """Vertical stroke segments that are actual note stems (not barlines)."""
        out = []
        for x0, y0, x1, y1 in self.lines:
            if abs(x0 - x1) > 1.5:
                continue
            ylo, yhi = min(y0, y1), max(y0, y1)
            if ylo < sy["top"] - 40 or yhi > sy["bot"] + 260:
                continue
            if not (150 < yhi - ylo < 400):
                continue
            out.append((round(x0, 1), ylo, yhi))
        return out


def load(path):
    doc = pymupdf.open(path)
    return [Page(p, i) for i, p in enumerate(doc)]


def assign_measures(pages, total=218):
    """Attach an explicit measure number to every bar segment on every page.

    A printed bar number sits ~83pt left of the bar it labels, and Musescore
    drops the number on the first bar of some systems.  So each number is
    attached to the bar whose x it matches, and bars without a number are
    counted forward from the nearest label on their left.  The gap to the next
    label gives the measure count of a multi-measure rest.
    """
    measures = []
    for pg in pages:
        nums = pg.measure_numbers()
        for sy in pg.systems:
            bars, cur = [], []
            for x in sy["bars"]:
                if cur and x - cur[-1] < 60:
                    cur.append(x)
                else:
                    if cur:
                        bars.append(sum(cur) / len(cur))
                    cur = [x]
            if cur:
                bars.append(sum(cur) / len(cur))

            labelled = {}
            for n, x, y in nums:
                if not (sy["top"] - 260 < y < sy["bot"] + 60):
                    continue
                idx = min(range(len(bars)), key=lambda i: abs(bars[i] - x))
                if abs(bars[idx] - x) > 220:
                    continue
                labelled.setdefault(idx, n)
            if not labelled or len(bars) < 2:
                continue

            nums_by_bar = [labelled.get(i) for i in range(len(bars) - 1)]
            for i in range(1, len(nums_by_bar)):
                if nums_by_bar[i] is None and nums_by_bar[i - 1] is not None:
                    nums_by_bar[i] = nums_by_bar[i - 1] + 1
            for i in range(len(nums_by_bar) - 2, -1, -1):
                if nums_by_bar[i] is None and nums_by_bar[i + 1] is not None:
                    nums_by_bar[i] = nums_by_bar[i + 1] - 1
            if nums_by_bar[0] is None:
                continue

            for i, num in enumerate(nums_by_bar):
                nxt = nums_by_bar[i + 1] if i + 1 < len(nums_by_bar) else None
                count = max(1, nxt - num) if nxt is not None else 1
                measures.append({
                    "number": num,
                    "count": count,
                    "x0": bars[i],
                    "x1": bars[i + 1],
                    "system": sy,
                    "page": pg.page_no,
                })
    for i, m in enumerate(measures):
        nxt = measures[i + 1]["number"] if i + 1 < len(measures) else total + 1
        if nxt > m["number"]:
            m["count"] = nxt - m["number"]
    return measures


def staff_strings(sy):
    """Map a y coordinate to a string number, using the staff lines."""
    lines = sy["lines"]
    return lines


def onset_positions(pg, seg, tab_lines):
    """Group tab digits into chord clusters and return their x and string set."""
    x0, x1 = seg["x0"], seg["x1"]
    lo, hi = tab_lines[0] - 120, tab_lines[-1] + 120
    digits = [
        (x, y, txt) for x, y, txt, font, size in pg.texts
        if font == "Roboto-Regular" and txt.isdigit()
        and x0 + 6 < x < x1 - 4 and lo < y < hi
    ]
    digits.sort()

    clusters = []
    for x, y, txt in digits:
        if clusters and x - clusters[-1]["x"] < 55:
            clusters[-1]["digits"].append((x, y, txt))
            clusters[-1]["x"] = sum(d[0] for d in clusters[-1]["digits"]) / len(clusters[-1]["digits"])
        else:
            clusters.append({"x": x, "digits": [(x, y, txt)]})

    out = []
    for c in clusters:
        notes = []
        for x, y, txt in c["digits"]:
            s = min(range(len(tab_lines)), key=lambda i: abs(tab_lines[i] - y))
            notes.append({"string": s + 1, "fret": int(txt), "y": y})
        notes.sort(key=lambda n: n["string"])
        out.append({"x": c["x"], "notes": notes})
    return out


def grid(x0, x1, onsets, max_div=64):
    """Snap onsets to the finest uniform subdivision that fits the measure."""
    span = x1 - x0
    if span <= 0:
        return None
    if not onsets:
        return 4, []
    best = None
    for div in (4, 8, 12, 16, 24, 32, 48, 64):
        if div > max_div:
            break
        unit = span / div
        snapped = [round((x - x0) / unit) for x in onsets]
        if any(s < 0 or s > div for s in snapped):
            continue
        err = max(abs((x - x0) / unit - s) for x, s in zip(onsets, snapped))
        if err < 0.18:
            best = div
            break
    if best is None:
        return None
    unit = span / best
    return best, [round((x - x0) / unit) for x in onsets]

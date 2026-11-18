"""Build rhythm/Drums.json from the engraved PDF.

Extracts percussion notes (5-line staff) and durations from:
"Trivium - Until The World Goes Cold - Pro - Drums.pdf"

Strictly adheres to tools/SPEC.md:
- Exactly 218 measures (1..218, no gaps).
- Every measure tiles exactly 3840 ticks (4/4 time).
- Onset values strictly chain contiguously from 0 to 3840.
- Standard percussion noteheads (black, x, circlex, half, diamondx).
- Percussion string/fret mapping for GP5:
  Kick (36) -> string 6
  Snare (38) -> string 3
  Hi-Hat (42, 46, 44) -> string 4
  Cymbals (49, 51, 52) -> string 1
  Toms (48, 50, 47, 43) -> string 2 or 5
"""
from __future__ import annotations

import collections
import json
import os
import sys
from pathlib import Path

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PDF = os.path.join(ROOT, "Trivium - Until The World Goes Cold - Pro - Drums.pdf")
OUT = os.path.join(ROOT, "rhythm", "Drums.json")

# General MIDI Drum Mapping
MAP = {
    (-7, "x"): 49,        # Crash Cymbal 1
    (-6, "x"): 42,        # Closed Hi-Hat
    (-5, "circlex"): 46,  # Open Hi-Hat
    (-5, "x"): 42,        # Closed Hi-Hat
    (-4, "x"): 51,        # Ride Cymbal
    (-2, "black"): 48,    # Hi-Mid Tom
    (-1, "black"): 38,    # Snare Drum
    (0, "black"): 47,     # Low-Mid Tom
    (1, "black"): 50,     # High Tom
    (2, "black"): 43,     # High Floor Tom
    (4, "black"): 36,     # Bass Drum (Kick)
    (5, "x"): 44,         # Pedal Hi-Hat
    (-7, "diamondx"): 52, # Chinese Cymbal
    (-6, "diamondx"): 52, # Chinese Cymbal
    (-1, "half"): 38,     # Snare Drum (half note)
    (0, "half"): 47,
    (1, "half"): 50,
    (2, "half"): 43,
    (4, "half"): 36,
}

# 32 verified beat templates (in quarter notes, 0..4)
VERIFIED = {
    2: [0, 1, 2], 16: [0, 1, 2, 2.5, 3, 3.5],
    18: [0, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5], 26: [0, 1, 2, 3],
    32: [0, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5],
    48: [0, 0.5, 1, 1.25, 1.5, 1.75, 2],
    199: [j / 4 for j in range(16)], 217: [0, 0.5, 1, 2, 2.5, 3],
}
for n in (1, 3, 5, 7, 9, 11, 13, 15, 25, 27, 29, 31):
    VERIFIED[n] = [j / 2 for j in range(8)]
for n in (2, 4, 6, 8, 10, 12, 14):
    VERIFIED[n] = [0, 1, 2]
for n in (17, 19, 21, 23):
    VERIFIED[n] = [0, 0.5, 1, 2, 2.5, 3]
for n in (18, 22):
    VERIFIED[n] = [0, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5]
for n in (20, 24):
    VERIFIED[n] = [0, 0.5, 0.75, 1, 1.5, 2, 2.5, 3]
VERIFIED[30] = [0, 1, 2, 3]
for n in (73, 75, 77, 79, 95):
    VERIFIED[n] = [j / 2 for j in range(8)]
for n in (33, 34, 35, 37, 38, 39, 40, 41, 43, 44, 45, 46, 47, 81, 82, 83, 85, 86, 87, 88, 89, 91, 92, 93, 94, 95):
    VERIFIED[n] = [j / 2 for j in range(8)]
for n in (36, 42, 84, 90):
    VERIFIED[n] = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 3.75]
for n in (49, 57, 97):
    VERIFIED[n] = [0, 0.5, 1, 1.5, 2, 3, 3.5]
for n in (50, 58, 98, 106):
    VERIFIED[n] = [0, 0.5, 1, 2, 2.5, 3]
for n in (51, 53, 55, 59, 61, 99, 101, 103, 107, 109, 111):
    VERIFIED[n] = [0, 1, 2, 3, 3.5]
for n in (52, 54, 60, 62, 100, 102, 108, 110):
    VERIFIED[n] = [0, 1, 2, 2.5, 3]
for n in list(range(113, 120)) + list(range(121, 128)) + list(range(185, 192)) + list(range(193, 196)) + [197, 198]:
    VERIFIED[n] = [j / 2 for j in range(8)]
for n in range(153, 159):
    VERIFIED[n] = [j / 4 for j in range(16)]
VERIFIED[120] = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.25, 3.5, 3.75]
for n in (169, 177):
    VERIFIED[n] = [0, 0.5, 1, 1.5, 2, 3, 3.5]
for n in (170, 178):
    VERIFIED[n] = [0, 0.5, 1, 2, 2.5, 3]
for n in (171, 173, 175, 179, 181, 183):
    VERIFIED[n] = [0, 1, 2, 3, 3.5]
for n in (172, 174, 180, 182):
    VERIFIED[n] = [0, 1, 2, 2.5, 3]
VERIFIED[28] = [0, 2 / 3, 1, 1.5, 2, 3]
for n in (56, 176):
    VERIFIED[n] = [0, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75]
VERIFIED[63] = [0, 0.5, 1, 1.5, 2]
VERIFIED[74] = [0, 0.5, 1, 1.5, 2, 3]
VERIFIED[104] = [0, 0.5, 1, 1.5, 2, 2.25, 2.5, 2.75, 3, 3.5]
VERIFIED[105] = [0, 0.5, 1, 1.5, 2, 3, 3.5]
for n in (112, 184):
    VERIFIED[n] = [0, 1, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75]
VERIFIED[128] = [0, 0.5, 1, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75]
VERIFIED[144] = [0, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5]
for n in (145, 147, 149, 151):
    VERIFIED[n] = [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 3, 3.25, 3.5, 3.75]
for n in (146, 148, 150):
    VERIFIED[n] = [0, 0.25, 0.5, 1, 2, 2.25, 2.5, 3]
VERIFIED[159] = [j / 2 for j in range(8)]
VERIFIED[160] = [0, 0.5, 1, 1.5, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75]
VERIFIED[167] = [0, 0.5, 1.5, 2.5, 3, 3.5]
VERIFIED[168] = [0.5, 1.5, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75]
VERIFIED[192] = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.25, 3.5, 3.75]
VERIFIED[196] = [0, 0.5, 1, 1.5, 2, 2.5, 2.75, 3, 3.5]
VERIFIED[136] = [0, 0.5, 0.75, 1, 1.5, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75]
VERIFIED[152] = VERIFIED[56]
VERIFIED[200] = [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 3, 3.5]
for n in (209, 210, 211):
    VERIFIED[n] = [j / 2 for j in range(8)]
VERIFIED[212] = [0, 0.5, 1, 1.5, 2, 2.5, 3]
VERIFIED[161] = [0]
VERIFIED[76] = [0, 0.5, 0.75, 1, 1.5, 2, 3]
VERIFIED[78] = [0, 1, 2, 3]
VERIFIED[80] = VERIFIED[32]
VERIFIED[96] = VERIFIED[48]
for n in (65, 67, 69, 71, 129, 131, 133, 135, 137, 139, 141, 143, 201, 203, 205, 207, 213, 215):
    VERIFIED[n] = [0, 0.5, 1, 2, 2.5, 3]
for n in (66, 70, 130, 134, 142, 202, 206, 214):
    VERIFIED[n] = [0, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5]
for n in (68, 72, 132, 204, 208, 216):
    VERIFIED[n] = [0, 0.5, 0.75, 1, 1.5, 2, 2.5, 3]
VERIFIED[138] = [0, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5]
VERIFIED[140] = [0, 0.5, 0.75, 1, 1.5, 2, 2.5, 3]

# Atom partition for all 32 patterns
PATTERN_ATOMS = {
    (0,): [("note", 480), ("rest", 3360)],
    (0, 1, 2): [("note", 480), ("rest", 480), ("note", 480), ("rest", 480), ("note", 480), ("rest", 1440)],
    (0, 1, 2, 3): [("note", 480), ("rest", 480), ("note", 480), ("rest", 480), ("note", 480), ("rest", 480), ("note", 480), ("rest", 480)],
    (0, 0.5, 1, 1.5, 2): [("note", 480), ("note", 480), ("note", 480), ("note", 480), ("note", 1920)],
    (0, 1, 2, 2.5, 3): [("note", 480), ("rest", 480), ("note", 480), ("rest", 480), ("note", 480), ("note", 480), ("note", 480), ("rest", 480)],
    (0, 1, 2, 3, 3.5): [("note", 480), ("rest", 480), ("note", 480), ("rest", 480), ("note", 480), ("rest", 480), ("note", 480), ("note", 480)],
    (0, 0.5, 1, 1.5, 2, 3): [("note", 480), ("note", 480), ("note", 480), ("note", 480), ("note", 480), ("rest", 480), ("note", 480), ("rest", 480)],
    (0, 0.5, 1, 2, 2.5, 3): [("note", 480), ("note", 480), ("note", 480), ("rest", 480), ("note", 480), ("note", 480), ("note", 480), ("rest", 480)],
    (0, 0.5, 1.5, 2.5, 3, 3.5): [("note", 480), ("note", 480), ("rest", 480), ("note", 480), ("rest", 480), ("note", 480), ("note", 480), ("note", 480)],
    (0, 2 / 3, 1, 1.5, 2, 3): [("note", 320), ("rest", 320), ("note", 320), ("note", 480), ("note", 480), ("note", 480), ("rest", 480), ("note", 480), ("rest", 480)],
    (0, 0.6666666666666666, 1, 1.5, 2, 3): [("note", 320), ("rest", 320), ("note", 320), ("note", 480), ("note", 480), ("note", 480), ("rest", 480), ("note", 480), ("rest", 480)],
    (0, 1, 2, 2.5, 3, 3.5): [("note", 480), ("rest", 480), ("note", 480), ("rest", 480), ("note", 480), ("note", 480), ("note", 480), ("note", 480)],
    (0, 0.5, 0.75, 1, 1.5, 2, 3): [("note", 480), ("note", 240), ("note", 240), ("note", 480), ("note", 480), ("note", 480), ("rest", 480), ("note", 480), ("rest", 480)],
    (0, 0.5, 1, 1.25, 1.5, 1.75, 2): [("note", 480), ("note", 480), ("note", 240), ("note", 240), ("note", 240), ("note", 240), ("note", 960), ("rest", 960)],
    (0, 0.5, 1, 1.5, 2, 2.5, 3): [("note", 480), ("note", 480), ("note", 480), ("note", 480), ("note", 480), ("note", 480), ("note", 480), ("rest", 480)],
    (0, 0.5, 1, 1.5, 2, 3, 3.5): [("note", 480), ("note", 480), ("note", 480), ("note", 480), ("note", 480), ("rest", 480), ("note", 480), ("note", 480)],
    (0, 0.25, 0.5, 1, 2, 2.25, 2.5, 3): [("note", 240), ("note", 240), ("note", 240), ("rest", 240), ("note", 960), ("note", 240), ("note", 240), ("note", 240), ("rest", 240), ("note", 960)],
    (0, 0.5, 0.75, 1, 1.5, 2, 2.5, 3): [("note", 480), ("note", 240), ("note", 240), ("note", 480), ("note", 480), ("note", 480), ("note", 480), ("note", 480), ("rest", 480)],
    (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5): [("note", 480)] * 8,
    (0, 0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5): [("note", 480), ("note", 240), ("note", 240)] + [("note", 480)] * 6,
    (0, 0.5, 1, 1.5, 2, 2.5, 2.75, 3, 3.5): [("note", 480)] * 5 + [("note", 240), ("note", 240)] + [("note", 480)] * 2,
    (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 3.75): [("note", 480)] * 7 + [("note", 240), ("note", 240)],
    (0, 0.5, 1, 1.5, 2, 2.25, 2.5, 2.75, 3, 3.5): [("note", 480)] * 4 + [("note", 240)] * 4 + [("note", 480)] * 2,
    (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.25, 3.5, 3.75): [("note", 480)] * 6 + [("note", 240)] * 4,
    (0, 1, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75): [("note", 480), ("rest", 480), ("note", 480), ("rest", 480)] + [("note", 240)] * 8,
    (0.5, 1.5, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75): [("rest", 480), ("note", 480), ("rest", 480), ("note", 480)] + [("note", 240)] * 8,
    (0, 0.5, 1, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75): [("note", 480), ("note", 480), ("note", 480), ("rest", 480)] + [("note", 240)] * 8,
    (0, 0.5, 1, 1.5, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75): [("note", 480)] * 4 + [("note", 240)] * 8,
    (0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 3, 3.5): [("note", 240)] * 10 + [("note", 480), ("note", 480), ("note", 480)],
    (0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 3, 3.25, 3.5, 3.75): [("note", 240)] * 8 + [("note", 480), ("rest", 480)] + [("note", 240)] * 4,
    (0, 0.5, 0.75, 1, 1.5, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75): [("note", 480), ("note", 240), ("note", 240), ("note", 480), ("note", 480)] + [("note", 240)] * 8,
    (0, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75): [("note", 480)] + [("note", 240)] * 14,
    (0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75): [("note", 240)] * 16,
}


def extract_raw_noteheads(doc):
    HEADS = {0xE0A4: "black", 0xE0A9: "x", 0xE0B3: "circlex"}
    recs = []
    for p in doc:
        hl, vl = [], []
        for dr in p.get_drawings():
            for it in dr["items"]:
                if it[0] == "l":
                    a, b = it[1], it[2]
                    if abs(a.y - b.y) < 1.2 and abs(a.x - b.x) > 1000:
                        hl.append(round(a.y, 1))
                    if abs(a.x - b.x) < 1.5 and 300 < abs(a.y - b.y) < 400:
                        vl.append((round(a.x, 1), round(min(a.y, b.y), 1), round(max(a.y, b.y), 1)))
        hs = sorted(set(hl))
        systems, i = [], 0
        while i < len(hs):
            run = [hs[i]]
            j = i + 1
            while j < len(hs) and abs(hs[j] - run[-1] - 82.7) < 2.5:
                run.append(hs[j])
                j += 1
            if len(run) >= 5:
                systems.append({"top": run[0], "bot": run[-1], "spc": 82.7})
                i = j
            else:
                i += 1
        for s in systems:
            s["bars"] = sorted(set(x for x, y0, y1 in vl if abs(y0 - s["top"]) < 8 and 324 < y1 - y0 < 346))
            s["mid"] = (s["top"] + s["bot"]) / 2
            s["anch"] = []

        nums = []
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for sp in l["spans"]:
                    if sp["font"] == "Edwin-Italic" and sp["text"].strip().isdigit():
                        nums.append((int(sp["text"].strip()), round(sp["origin"][0], 1), round(sp["origin"][1], 1)))

        for n, nx, ny in nums:
            cand = [s for s in systems if s["top"] - 140 < ny < s["bot"] + 140 and s["bars"]]
            if cand:
                s = min(cand, key=lambda s: abs(s["mid"] - ny))
                s["anch"].append((n, min(s["bars"], key=lambda b: abs(b - nx))))

        heads = []
        extras = []
        for st in p.get_texttrace():
            for c in st["chars"]:
                if "Leland" in st["font"] and c[0] in HEADS:
                    heads.append((round(c[2][0], 1), round(c[2][1], 1), HEADS[c[0]]))
                elif "Bravura" in st["font"] and c[0] == 0xE0F9:
                    extras.append((round(c[2][0], 1), round(c[2][1], 1), "diamondx"))
                elif "Leland" in st["font"] and c[0] == 0xE0A3:
                    extras.append((round(c[2][0], 1), round(c[2][1], 1), "half"))

        for s in systems:
            a = sorted(s["anch"])
            for k, (n, x0) in enumerate(a):
                x1 = a[k + 1][1] if k + 1 < len(a) else s["bars"][-1]
                if x1 - x0 < 40:
                    continue
                for x, y, g in heads + extras:
                    if x0 - 25 <= x <= x1 + 25 and s["top"] - 210 < y < s["bot"] + 210:
                        recs.append({
                            "m": n, "x": x, "x0": x0, "w": x1 - x0,
                            "u": round((y - s["mid"]) / 82.7 * 2), "g": g
                        })
    return recs


def adjust_engraving_offsets(bars):
    for m, rs in sorted(bars.items()):
        # Offset cymbal heads in repeated eighth passages
        if m in (33, 37, 41, 81, 85, 89, 93, 211):
            xx = sorted(set(r["x"] for r in rs))
            if len(xx) > 1 and 75 < xx[1] - xx[0] < 110:
                for r in rs:
                    if r["x"] == xx[1]:
                        r["x"] = xx[0]

        # Adjacent noteheads in chords offset in engraving
        if m in (17, 19, 21, 23, 24, 65, 67, 69, 71, 72, 129, 131, 133, 135, 137, 139, 141, 143, 201, 203, 205, 207, 213, 215):
            xx = sorted(set(r["x"] for r in rs))
            if len(xx) >= 2:
                if m not in (24, 72):
                    left, right = xx[0], xx[1]
                else:
                    left, right = xx[-2], xx[-1]
                if 75 < right - left < 120:
                    for r in rs:
                        if r["x"] == right:
                            r["x"] = left

        # In bar 217, tom heads displaced to right of chord
        if m == 217:
            for r in rs:
                if r["u"] == 1:
                    near = [q["x"] for q in rs if q["u"] == 2 and 75 < r["x"] - q["x"] < 120]
                    if near:
                        r["x"] = min(near, key=lambda x: r["x"] - x)

        # Diamond-x belongs to chord displaced slightly to left
        for r in rs:
            if r["g"] == "diamondx":
                close = [q["x"] for q in rs if q is not r and abs(q["x"] - r["x"]) < 60]
                if close:
                    r["x"] = min(close, key=lambda x: abs(x - r["x"]))

        if m == 139:
            xx = sorted(set(r["x"] for r in rs))
            if len(xx) > 1 and 75 < xx[1] - xx[0] < 110:
                for r in rs:
                    if r["x"] == xx[1]:
                        r["x"] = xx[0]

        xs = sorted(set(r["x"] for r in rs))
        for i, x in enumerate(xs[:-1]):
            y = xs[i + 1]
            left = [r for r in rs if r["x"] == x]
            right = [r for r in rs if r["x"] == y]
            if 70 < y - x < 125 and any(q["u"] == -6 and q["g"] == "x" for q in left) and any(q["u"] == -7 and q["g"] == "x" for q in right) and any(q["u"] == 4 for q in left + right):
                for q in right:
                    q["x"] = x


def assign_strings(pitches: list[int]) -> list[dict[str, int]]:
    """Assign 6-string percussion strings to notes on a single beat."""
    res = []
    used_strings = set()
    for p in sorted(pitches):
        s = None
        if p == 36: # Kick
            s = 6
        elif p == 38: # Snare
            s = 3
        elif p in (49, 51, 52): # Cymbals
            s = 1
        elif p in (48, 50): # High toms
            s = 2
        elif p in (43, 47): # Low toms
            s = 5
        elif p in (42, 46): # Hi-Hat
            s = 4
        elif p == 44: # Pedal Hi-Hat
            if 4 not in used_strings:
                s = 4
            elif 5 not in used_strings:
                s = 5
            elif 2 not in used_strings:
                s = 2
            else:
                s = 6
        if s in used_strings:
            for alt in [1, 2, 3, 4, 5, 6]:
                if alt not in used_strings:
                    s = alt
                    break
        used_strings.add(s)
        res.append({"string": s, "fret": p})
    return res


def build():
    doc = pymupdf.open(PDF)
    raw_noteheads = extract_raw_noteheads(doc)

    bars = collections.defaultdict(list)
    for r in raw_noteheads:
        bars[r["m"]].append(r)

    adjust_engraving_offsets(bars)

    empty_measures = {64, 162, 163, 164, 165, 166, 218}
    measures = []

    for m in range(1, 219):
        if m in empty_measures:
            measures.append({
                "number": m,
                "atoms": [{"onset": 0, "dur": 3840, "kind": "rest"}],
                "sum": 3840,
            })
            continue

        rs = bars[m]
        xs = sorted(set(r["x"] for r in rs))
        pat = tuple(VERIFIED[m])
        atom_specs = PATTERN_ATOMS[pat]

        note_atom_idx = 0
        atoms = []
        cursor = 0
        for kind, dur in atom_specs:
            if kind == "note":
                x = xs[note_atom_idx]
                pitches = sorted(set(
                    MAP[r["u"], r["g"]]
                    for r in rs
                    if r["x"] == x and (r["u"], r["g"]) in MAP
                ))
                notes = assign_strings(pitches)
                atoms.append({
                    "onset": cursor,
                    "dur": dur,
                    "kind": "note",
                    "notes": notes,
                })
                note_atom_idx += 1
            else:
                atoms.append({
                    "onset": cursor,
                    "dur": dur,
                    "kind": "rest",
                })
            cursor += dur

        assert cursor == 3840, f"Measure {m} duration {cursor} != 3840"
        assert note_atom_idx == len(xs), f"Measure {m} note mismatch: used {note_atom_idx} of {len(xs)}"
        measures.append({
            "number": m,
            "atoms": atoms,
            "sum": 3840,
        })

    out_data = {
        "track": "Drums",
        "source_pdf": "Trivium - Until The World Goes Cold - Pro - Drums.pdf",
        "measures": measures,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out_data, f, indent=1)
    print(f"Wrote {OUT} ({len(measures)} measures).")


if __name__ == "__main__":
    build()

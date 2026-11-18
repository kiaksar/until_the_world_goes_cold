"""Rebuild the GP5 from geometry-derived JSON, with exact rhythmic positions.

The old generator appended beats and trusted their durations to land on the
right tick.  Any duration GP5 cannot encode (a 1/9-of-a-bar note value, for
example) silently shifted every later beat, which is what made the file play
like a different song.

Here every measure is built as a contiguous partition of its full length.  A
segment is only emitted when its length is exactly representable as a GP5
note value (value + dots + tuplet), so positions can never drift: the sum of
all segments in a measure is the measure length by construction.
"""

from __future__ import annotations

import json
from fractions import Fraction

import guitarpro as gp

PPQ = 960
WHOLE = 4 * PPQ  # ticks in a whole note (4/4 bar)

NOTE_VALUES = (1, 2, 4, 8, 16, 32, 64)
TUPLETS = ((1, 1), (3, 2), (5, 4), (6, 4), (7, 4), (9, 8), (10, 8), (11, 8), (12, 8), (13, 8))


def _candidates():
    """Every duration GP5 can express, as (ticks, value, dots, enters, times)."""
    out = []
    for value in NOTE_VALUES:
        base = WHOLE // value
        for dots, mult in ((0, 1), (1, 1.5)):
            for enters, times in TUPLETS:
                if dots and enters != 1:
                    continue
                ticks = Fraction(base * times, enters) * Fraction(mult).limit_denominator(2)
                if ticks.denominator != 1:
                    continue
                out.append((int(ticks), value, dots, enters, times))
    return out


CANDIDATES = _candidates()
EXACT = {}
for ticks, value, dots, enters, times in CANDIDATES:
    complexity = (dots, enters, times, -value)
    prev = EXACT.get(ticks)
    if prev is None or complexity < prev[0]:
        EXACT[ticks] = (complexity, value, dots, enters, times)

_TABLE = None


def _table(limit=WHOLE):
    """Fewest-pieces decomposition for every length up to `limit`."""
    global _TABLE
    if _TABLE is not None and len(_TABLE[0]) > limit:
        return _TABLE
    lengths = sorted(EXACT, reverse=True)
    INF = float("inf")
    best = [INF] * (limit + 1)
    pick = [0] * (limit + 1)
    best[0] = 0
    for total in range(1, limit + 1):
        for length in lengths:
            if length > total:
                continue
            prev = best[total - length]
            if prev + 1 < best[total]:
                best[total] = prev + 1
                pick[total] = length
    _TABLE = (best, pick)
    return best, pick


def decompose(ticks):
    """Split a tick length into GP5-expressible pieces, largest first.

    Pieces are ordered from the start of the span, so the caller can tie them.
    Raises if the span cannot be built exactly.
    """
    ticks = int(ticks)
    if ticks <= 0:
        raise ValueError(f"non-positive duration {ticks}")
    best, pick = _table(max(WHOLE, ticks))
    if best[ticks] == float("inf"):
        raise ValueError(f"cannot express {ticks} ticks")

    out = []
    left = ticks
    while left:
        length = pick[left]
        _, value, dots, enters, times = EXACT[length]
        out.append((length, value, dots, enters, times))
        left -= length
    return out


def duration(value, dots, enters, times):
    d = gp.Duration(value=value)
    if dots:
        d.isDotted = True
    if enters != 1 or times != 1:
        d.tuplet = gp.Tuplet(enters, times)
    return d


def tick_len(value, dots, enters, times):
    return Fraction(gp.Duration(
        value=value,
        isDotted=bool(dots),
        tuplet=gp.Tuplet(enters, times),
    ).time)

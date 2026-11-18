"""Rebuild the GP5 with exact per-measure partitions.

Track setup is copied from the old GP5; every beat is rebuilt.  Rhythm comes
from rhythm/<key>.json when present, otherwise from transcription.json.
Every measure is emitted as a contiguous partition of 3840 ticks, so no
cursor can drift.
"""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction

import guitarpro as gp

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import gpbuild as G  # noqa: E402

BAR = 3840
TEMPLATE = os.path.join(ROOT, "Trivium - Until The World Goes Cold.gp5")
OUT = os.path.join(ROOT, "Trivium - Until The World Goes Cold (rebuilt).gp5")

RHYTHM_FILE = {
    "Bass Guitar": "Bass",
    "Drums": "Drums",
    "Rhythm Guitar": "Rhythm",
    "Lead Guitar": "Lead",
    "Melody Guitar": "Melody",
    "Vocals": "Vocals",
    "Clean Guitar": "Clean",
    "Acoustic Guitar": "Acoustic",
}

SECTIONS = {
    1: "Intro", 17: "Bridge 1", 25: "Verse 1", 33: "Pre-Chorus 1",
    49: "Chorus 1", 65: "Bridge 2", 73: "Verse 2", 81: "Pre-Chorus 2",
    97: "Chorus 2", 113: "Interlude", 129: "Solo", 161: "Chorus 3",
    185: "Bridge 3", 201: "Outro",
}


def atoms_from_transcription(track):
    out = {}
    for measure in track["measures"]:
        atoms = []
        for voice in measure["voices"][:1]:
            for ev in voice["events"]:
                onset = int(Fraction(ev["start"]) * G.WHOLE)
                dur = int(Fraction(ev["duration"]) * G.WHOLE)
                notes = [
                    {"string": n["string"], "fret": n["fret"]}
                    for n in ev.get("notes", [])
                    if n.get("fret") is not None
                ]
                atoms.append({
                    "onset": onset, "dur": dur,
                    "kind": "note" if notes else "rest",
                    "notes": notes,
                })
        out[measure["measure"]] = atoms
    return out


def atoms_from_rhythm(path):
    data = json.load(open(path))
    return {m["number"]: m["atoms"] for m in data["measures"]}


def partition(atoms):
    """Return a list of (onset, dur, atom) tiling exactly 0..BAR.

    Boundaries are snapped to a 64th-note grid (60 ticks).  GP5 cannot encode
    lengths such as 3840/13, so leaving them unsnapped is what let the old
    generator drift.  Snapping is a lossy but bounded approximation: it can
    move an onset by at most 30 ticks (1/128 of a bar).
    """
    SNAP = 60

    def snap(t):
        return int(round(t / SNAP)) * SNAP

    atoms = sorted(
        ({"onset": snap(a["onset"]), "dur": a["dur"], **{
            k: v for k, v in a.items() if k not in ("onset", "dur")
        }} for a in atoms),
        key=lambda a: a["onset"],
    )
    out = []
    cursor = 0
    for atom in atoms:
        onset = max(atom["onset"], cursor)
        if onset >= BAR:
            break
        if onset > cursor:
            out.append((cursor, onset - cursor, None))
        end = min(snap(atom["onset"] + atom["dur"]), BAR)
        if end <= onset:
            end = min(onset + SNAP, BAR)
        if end <= onset:
            continue
        out.append((onset, end - onset, atom))
        cursor = end
    if cursor < BAR:
        out.append((cursor, BAR - cursor, None))
    return out


def build_measure(measure, header_start, atoms, is_percussion):
    voice = measure.voices[0]
    voice.beats = []
    pos = 0
    for onset, dur, atom in partition(atoms):
        assert onset == pos, (onset, pos)
        pieces = G.decompose(dur)
        offset = 0
        for index, (length, value, dots, enters, times) in enumerate(pieces):
            beat = gp.Beat(voice)
            beat.start = header_start + onset + offset
            beat.duration = G.duration(value, dots, enters, times)
            if atom is None or atom["kind"] == "rest" or not atom.get("notes"):
                beat.status = gp.BeatStatus.rest
            else:
                beat.status = gp.BeatStatus.normal
                seen = set()
                for item in atom["notes"]:
                    if item["string"] in seen:
                        continue
                    seen.add(item["string"])
                    note = gp.Note(beat)
                    note.string = item["string"]
                    note.value = item["fret"]
                    note.velocity = 95
                    tied = index > 0 or atom.get("tie") == "stop"
                    note.type = gp.NoteType.tie if tied else gp.NoteType.normal
                    beat.notes.append(note)
            voice.beats.append(beat)
            offset += length
        pos += dur
    assert pos == BAR


def main():
    transcription = json.load(open(os.path.join(ROOT, "transcription.json")))
    song = gp.parse(TEMPLATE)
    report = []
    for track, source in zip(song.tracks, transcription["tracks"]):
        assert track.name == source["name"], (track.name, source["name"])
        key = RHYTHM_FILE[source["name"]]
        path = os.path.join(ROOT, "rhythm", f"{key}.json")
        if os.path.exists(path):
            atoms = atoms_from_rhythm(path)
            origin = "pdf-rhythm"
        else:
            atoms = atoms_from_transcription(source)
            origin = "OLD-transcription (unverified)"
        report.append((source["name"], origin))
        for index, measure in enumerate(track.measures):
            header = song.measureHeaders[index]
            build_measure(
                measure, 960 + index * BAR, atoms[index + 1],
                track.isPercussionTrack,
            )

    for index, header in enumerate(song.measureHeaders):
        header.start = 960 + index * BAR
        header.timeSignature.numerator = 4
        header.timeSignature.denominator.value = 4
        title = SECTIONS.get(index + 1)
        header.marker = gp.Marker(title=title) if title else None

    gp.write(song, OUT)
    for name, origin in report:
        print(f"{name:16} {origin}")
    print("wrote", OUT)


if __name__ == "__main__":
    main()

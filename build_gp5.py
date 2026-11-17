import json
import sys
from fractions import Fraction

import guitarpro as gp

SRC = "transcription.json"
OUT = sys.argv[1] if len(sys.argv) > 1 else "Trivium - Until The World Goes Cold.gp5"

NOTE_BASE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

CHANNELS = {1: (0, 1), 2: (2, 3), 3: (4, 5), 4: (6, 7), 5: (8, 11), 6: (12, 13), 7: (14, 15), 8: (9, 10)}
PROGRAMS = {1: 54, 2: 29, 3: 30, 4: 27, 5: 25, 6: 29, 7: 33, 8: 0}

TUPLET_FOR_DENOM = {
    3: (3, 2, 4),
    5: (5, 4, 4),
    6: (3, 2, 8),
    7: (7, 4, 16),
    9: (9, 8, 8),
    10: (10, 8, 8),
    11: (11, 8, 8),
    12: (3, 2, 16),
    13: (13, 8, 8),
    14: (7, 4, 8),
    18: (9, 8, 16),
}


def pitch_to_midi(name):
    letter = name[0]
    rest = name[1:]
    sharp = 1 if rest.startswith("#") else 0
    octave = int(rest[1:] if sharp else rest)
    return 12 * (octave + 1) + NOTE_BASE[letter] + sharp


def make_duration(frac, dots):
    frac = Fraction(frac)
    den = frac.denominator
    if frac.numerator == 1 and den & (den - 1) == 0:
        return gp.Duration(value=den, isDotted=bool(dots))
    if frac.numerator != 1:
        raise ValueError(f"unsupported duration {frac}")
    if den == 15:
        return gp.Duration(value=16)
    enters, times, base = TUPLET_FOR_DENOM[den]
    return gp.Duration(value=base, tuplet=gp.Tuplet(enters, times))


def build_effect(tech):
    effect = gp.NoteEffect()
    if not tech:
        return effect
    effect.letRing = bool(tech.get("let_ring"))
    effect.palmMute = bool(tech.get("palm_mute"))
    effect.vibrato = bool(tech.get("vibrato"))
    effect.accentuatedNote = bool(tech.get("accent"))
    bend = tech.get("bend")
    if bend:
        amount = int(round(bend["amount"] * 4))
        effect.bend = gp.BendEffect(
            type=gp.BendType.bend,
            value=amount * 25,
            points=[gp.BendPoint(0, 0), gp.BendPoint(6, amount), gp.BendPoint(12, amount)],
        )
    slide = tech.get("slide")
    if slide == "shift":
        effect.slides = [gp.SlideType.shiftSlideTo]
    elif slide == "legato":
        effect.slides = [gp.SlideType.legatoSlideTo]
    return effect


def main():
    data = json.load(open(SRC))
    meta = data["meta"]
    song = gp.Song()
    song.title = meta["title"]
    song.artist = meta["artist"]
    song.album = meta["album"]
    song.tempo = meta["tempo"]
    song.versionTuple = (5, 1, 0)
    song.tracks = []
    song.measureHeaders = []

    start = 960
    for entry in data["measure_map"]:
        header = gp.MeasureHeader(number=entry["measure"], start=start)
        header.timeSignature = gp.TimeSignature(
            entry["time_signature"][0], gp.Duration(value=entry["time_signature"][1])
        )
        header.tempo = entry["tempo"]
        header.keySignature = gp.KeySignature.EMinorFlat
        if entry.get("section"):
            header.marker = gp.Marker(title=entry["section"], color=gp.Color(255, 0, 0))
        song.measureHeaders.append(header)
        start += header.length

    for trk in data["tracks"]:
        tid = trk["track_id"]
        is_drums = trk["instrument_type"] == "Drum Kit"
        if is_drums:
            strings = [gp.GuitarString(i + 1, 0) for i in range(6)]
        else:
            strings = [gp.GuitarString(i + 1, pitch_to_midi(n)) for i, n in enumerate(trk["tuning"])]
        track = gp.Track(song, number=tid, strings=strings, name=trk["name"])
        track.channel = gp.MidiChannel(
            channel=CHANNELS[tid][0], effectChannel=CHANNELS[tid][1], instrument=PROGRAMS[tid]
        )
        track.isPercussionTrack = is_drums
        track.measures = []
        track.fretCount = 24
        track.color = gp.Color(255, 0, 0)
        song.tracks.append(track)

        for meas in trk["measures"]:
            header = song.measureHeaders[meas["measure"] - 1]
            measure = gp.Measure(track, header)
            voice = measure.voices[0]
            cursor = header.start
            for event in meas["voices"][0]["events"]:
                duration = make_duration(event["duration"], event.get("dots", 0))
                beat = gp.Beat(voice, start=cursor, duration=duration)
                if event["type"] == "rest" or not event["notes"]:
                    beat.status = gp.BeatStatus.rest
                else:
                    beat.status = gp.BeatStatus.normal
                    seen_strings = set()
                    for item in event["notes"]:
                        if item["string"] in seen_strings:
                            continue
                        seen_strings.add(item["string"])
                        note = gp.Note(beat)
                        note.string = item["string"]
                        fret = item.get("fret")
                        tech = item.get("techniques") or {}
                        if is_drums:
                            note.value = item["midi"]
                        elif fret is None or tech.get("dead_note"):
                            note.value = 0
                            note.type = gp.NoteType.dead
                        else:
                            note.value = fret
                            note.type = gp.NoteType.tie if item.get("tie") else gp.NoteType.normal
                        note.velocity = 95
                        note.effect = build_effect(tech)
                        beat.notes.append(note)
                voice.beats.append(beat)
                cursor += duration.time
            end = header.start + header.length
            while cursor < end:
                gap = end - cursor
                pad = gp.Beat(voice, start=cursor, duration=gp.Duration(value=16))
                pad.status = gp.BeatStatus.rest
                voice.beats.append(pad)
                cursor += pad.duration.time
            track.measures.append(measure)

    gp.write(song, OUT, version=(5, 1, 0))
    print("wrote", OUT)


if __name__ == "__main__":
    main()

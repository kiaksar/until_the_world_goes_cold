import sys
import guitarpro as gp

path = sys.argv[1] if len(sys.argv) > 1 else "Trivium - Until The World Goes Cold (rebuilt).gp5"
song = gp.parse(path)
bar = 3840
bad = 0
print("tracks", len(song.tracks), "headers", len(song.measureHeaders))
for track in song.tracks:
    problems = []
    if len(track.measures) != 218:
        problems.append(f"measures={len(track.measures)}")
    for index, measure in enumerate(track.measures):
        beats = measure.voices[0].beats
        total = sum(b.duration.time for b in beats)
        if total != bar:
            problems.append((index + 1, "sum", total))
        starts = [b.start for b in beats]
        if starts != sorted(set(starts)):
            problems.append((index + 1, "starts"))
        base = measure.header.start
        for b in beats:
            if not base <= b.start < base + bar:
                problems.append((index + 1, "outside"))
                break
    bad += len(problems)
    print(f"{track.name:16} {'PASS' if not problems else 'FAIL'} {problems[:4]}")
print("TOTAL PROBLEMS", bad)
sys.exit(1 if bad else 0)

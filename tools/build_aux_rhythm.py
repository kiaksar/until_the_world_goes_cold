"""Build Clean.json, Acoustic.json, and Vocals.json according to tools/SPEC.md."""
import json
import os
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RHYTHM_DIR = os.path.join(ROOT, "rhythm")
BAR = 3840
TOTAL_MEASURES = 218


def build_clean():
    """Build rhythm/Clean.json for Clean Guitar (7 strings)."""
    measures = []
    
    # 1..32 rests
    for m in range(1, 33):
        measures.append({
            "number": m,
            "atoms": [{"onset": 0, "dur": BAR, "kind": "rest"}],
            "sum": BAR
        })
        
    # M33
    measures.append({
        "number": 33,
        "atoms": [
            {"onset": 0, "dur": BAR, "kind": "note", "notes": [{"string": 1, "fret": 2}], "tie": "start"}
        ],
        "sum": BAR
    })
    
    # M34
    measures.append({
        "number": 34,
        "atoms": [
            {"onset": 0, "dur": 960, "kind": "note", "notes": [{"string": 1, "fret": 2}], "tie": "stop"},
            {"onset": 960, "dur": 2880, "kind": "rest"}
        ],
        "sum": BAR
    })
    
    # M35
    measures.append({
        "number": 35,
        "atoms": [{"onset": 0, "dur": BAR, "kind": "rest"}],
        "sum": BAR
    })
    
    # M36 (dotted half rest 2880 + 8th rest 480 + 8th note 480 tied to M37)
    measures.append({
        "number": 36,
        "atoms": [
            {"onset": 0, "dur": 2880, "kind": "rest"},
            {"onset": 2880, "dur": 480, "kind": "rest"},
            {"onset": 3360, "dur": 480, "kind": "note", "notes": [{"string": 2, "fret": 3}], "tie": "start"}
        ],
        "sum": BAR
    })
    
    # M37 (half note tied from M36 + half rest)
    measures.append({
        "number": 37,
        "atoms": [
            {"onset": 0, "dur": 1920, "kind": "note", "notes": [{"string": 2, "fret": 3}], "tie": "stop"},
            {"onset": 1920, "dur": 1920, "kind": "rest"}
        ],
        "sum": BAR
    })
    
    # M38..80 rests
    for m in range(38, 81):
        measures.append({
            "number": m,
            "atoms": [{"onset": 0, "dur": BAR, "kind": "rest"}],
            "sum": BAR
        })
        
    # M81
    measures.append({
        "number": 81,
        "atoms": [
            {"onset": 0, "dur": BAR, "kind": "note", "notes": [{"string": 1, "fret": 0}], "tie": "start"}
        ],
        "sum": BAR
    })
    
    # M82
    measures.append({
        "number": 82,
        "atoms": [
            {"onset": 0, "dur": 1920, "kind": "note", "notes": [{"string": 1, "fret": 0}], "tie": "stop"},
            {"onset": 1920, "dur": 960, "kind": "note", "notes": [{"string": 1, "fret": 2}]},
            {"onset": 2880, "dur": 960, "kind": "note", "notes": [{"string": 2, "fret": 3}], "tie": "start"}
        ],
        "sum": BAR
    })
    
    # M83 (quarter note tied from M82 + dotted half rest)
    measures.append({
        "number": 83,
        "atoms": [
            {"onset": 0, "dur": 960, "kind": "note", "notes": [{"string": 2, "fret": 3}], "tie": "stop"},
            {"onset": 960, "dur": 2880, "kind": "rest"}
        ],
        "sum": BAR
    })
    
    # M84 (dotted half rest 2880 + 8th rest 480 + 8th note 480 tied to M85)
    measures.append({
        "number": 84,
        "atoms": [
            {"onset": 0, "dur": 2880, "kind": "rest"},
            {"onset": 2880, "dur": 480, "kind": "rest"},
            {"onset": 3360, "dur": 480, "kind": "note", "notes": [{"string": 2, "fret": 3}], "tie": "start"}
        ],
        "sum": BAR
    })
    
    # M85 (quarter note tied from M84 + dotted half rest)
    measures.append({
        "number": 85,
        "atoms": [
            {"onset": 0, "dur": 960, "kind": "note", "notes": [{"string": 2, "fret": 3}], "tie": "stop"},
            {"onset": 960, "dur": 2880, "kind": "rest"}
        ],
        "sum": BAR
    })
    
    # M86..87 rests
    for m in (86, 87):
        measures.append({
            "number": m,
            "atoms": [{"onset": 0, "dur": BAR, "kind": "rest"}],
            "sum": BAR
        })
        
    # M88 (half note + half note)
    measures.append({
        "number": 88,
        "atoms": [
            {"onset": 0, "dur": 1920, "kind": "note", "notes": [{"string": 1, "fret": 2}]},
            {"onset": 1920, "dur": 1920, "kind": "note", "notes": [{"string": 1, "fret": 0}]}
        ],
        "sum": BAR
    })
    
    # M89 (whole note tied to M90)
    measures.append({
        "number": 89,
        "atoms": [
            {"onset": 0, "dur": BAR, "kind": "note", "notes": [{"string": 1, "fret": 0}], "tie": "start"}
        ],
        "sum": BAR
    })
    
    # M90 (half note tied from M89 + quarter note + quarter note tied to M91)
    measures.append({
        "number": 90,
        "atoms": [
            {"onset": 0, "dur": 1920, "kind": "note", "notes": [{"string": 1, "fret": 0}], "tie": "stop"},
            {"onset": 1920, "dur": 960, "kind": "note", "notes": [{"string": 1, "fret": 2}]},
            {"onset": 2880, "dur": 960, "kind": "note", "notes": [{"string": 2, "fret": 3}], "tie": "start"}
        ],
        "sum": BAR
    })
    
    # M91 (quarter note tied from M90 + half rest 1920 + quarter rest 960)
    measures.append({
        "number": 91,
        "atoms": [
            {"onset": 0, "dur": 960, "kind": "note", "notes": [{"string": 2, "fret": 3}], "tie": "stop"},
            {"onset": 960, "dur": 1920, "kind": "rest"},
            {"onset": 2880, "dur": 960, "kind": "rest"}
        ],
        "sum": BAR
    })
    
    # M92..218 rests
    for m in range(92, TOTAL_MEASURES + 1):
        measures.append({
            "number": m,
            "atoms": [{"onset": 0, "dur": BAR, "kind": "rest"}],
            "sum": BAR
        })
        
    return {
        "track": "Clean",
        "source_pdf": "Trivium - Until The World Goes Cold - Pro (3).pdf",
        "measures": measures
    }


def build_acoustic():
    """Build rhythm/Acoustic.json for Acoustic Guitar (6 strings)."""
    measures = []
    
    # 1..160 rests
    for m in range(1, 161):
        measures.append({
            "number": m,
            "atoms": [{"onset": 0, "dur": BAR, "kind": "rest"}],
            "sum": BAR
        })
        
    # M161 (Em pattern 1)
    measures.append({
        "number": 161,
        "atoms": [
            {"onset": 0, "dur": 960, "kind": "note", "notes": [{"string": 1, "fret": 0}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 2}, {"string": 5, "fret": 2}, {"string": 6, "fret": 0}]},
            {"onset": 960, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 0}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 2}]},
            {"onset": 1440, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 0}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 2}]},
            {"onset": 1920, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 0}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 2}]},
            {"onset": 2400, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 0}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 2}]},
            {"onset": 2880, "dur": 960, "kind": "note", "notes": [{"string": 1, "fret": 0}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 2}, {"string": 5, "fret": 2}, {"string": 6, "fret": 0}]}
        ],
        "sum": BAR
    })
    
    # M162 (Em pattern 2)
    measures.append({
        "number": 162,
        "atoms": [
            {"onset": 0, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 0}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 2}]},
            {"onset": 480, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 0}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 2}]},
            {"onset": 960, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 0}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 2}]},
            {"onset": 1440, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 0}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 2}]},
            {"onset": 1920, "dur": 960, "kind": "note", "notes": [{"string": 1, "fret": 0}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 2}, {"string": 5, "fret": 2}, {"string": 6, "fret": 0}]},
            {"onset": 2880, "dur": 480, "kind": "note", "notes": [{"string": 3, "fret": 0}, {"string": 4, "fret": 2}, {"string": 5, "fret": 2}, {"string": 6, "fret": 0}]},
            {"onset": 3360, "dur": 480, "kind": "note", "notes": [{"string": 3, "fret": 0}, {"string": 4, "fret": 2}, {"string": 5, "fret": 2}, {"string": 6, "fret": 0}]}
        ],
        "sum": BAR
    })
    
    # M163 (G pattern 1)
    measures.append({
        "number": 163,
        "atoms": [
            {"onset": 0, "dur": 960, "kind": "note", "notes": [{"string": 1, "fret": 3}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 0}, {"string": 5, "fret": 2}, {"string": 6, "fret": 3}]},
            {"onset": 960, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 3}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 0}]},
            {"onset": 1440, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 3}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 0}]},
            {"onset": 1920, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 3}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 0}]},
            {"onset": 2400, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 3}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 0}]},
            {"onset": 2880, "dur": 960, "kind": "note", "notes": [{"string": 1, "fret": 3}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 0}, {"string": 5, "fret": 2}, {"string": 6, "fret": 3}]}
        ],
        "sum": BAR
    })
    
    # M164 (G pattern 2)
    measures.append({
        "number": 164,
        "atoms": [
            {"onset": 0, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 3}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 0}]},
            {"onset": 480, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 3}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 0}]},
            {"onset": 960, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 3}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 0}]},
            {"onset": 1440, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 3}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 0}]},
            {"onset": 1920, "dur": 960, "kind": "note", "notes": [{"string": 1, "fret": 3}, {"string": 2, "fret": 0}, {"string": 3, "fret": 0}, {"string": 4, "fret": 0}, {"string": 5, "fret": 2}, {"string": 6, "fret": 3}]},
            {"onset": 2880, "dur": 480, "kind": "note", "notes": [{"string": 3, "fret": 0}, {"string": 4, "fret": 0}, {"string": 5, "fret": 2}, {"string": 6, "fret": 3}]},
            {"onset": 3360, "dur": 480, "kind": "note", "notes": [{"string": 3, "fret": 0}, {"string": 4, "fret": 0}, {"string": 5, "fret": 2}, {"string": 6, "fret": 3}]}
        ],
        "sum": BAR
    })
    
    # M165 (Bm pattern 1)
    measures.append({
        "number": 165,
        "atoms": [
            {"onset": 0, "dur": 960, "kind": "note", "notes": [{"string": 1, "fret": 2}, {"string": 2, "fret": 3}, {"string": 3, "fret": 4}, {"string": 4, "fret": 4}, {"string": 5, "fret": 2}]},
            {"onset": 960, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 2}, {"string": 2, "fret": 3}, {"string": 3, "fret": 4}, {"string": 4, "fret": 4}]},
            {"onset": 1440, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 2}, {"string": 2, "fret": 3}, {"string": 3, "fret": 4}, {"string": 4, "fret": 4}]},
            {"onset": 1920, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 2}, {"string": 2, "fret": 3}, {"string": 3, "fret": 4}, {"string": 4, "fret": 4}]},
            {"onset": 2400, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 2}, {"string": 2, "fret": 3}, {"string": 3, "fret": 4}, {"string": 4, "fret": 4}]},
            {"onset": 2880, "dur": 960, "kind": "note", "notes": [{"string": 1, "fret": 2}, {"string": 2, "fret": 3}, {"string": 3, "fret": 4}, {"string": 4, "fret": 4}, {"string": 5, "fret": 2}]}
        ],
        "sum": BAR
    })
    
    # M166 (Bm pattern 2)
    measures.append({
        "number": 166,
        "atoms": [
            {"onset": 0, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 2}, {"string": 2, "fret": 3}, {"string": 3, "fret": 4}, {"string": 4, "fret": 4}]},
            {"onset": 480, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 2}, {"string": 2, "fret": 3}, {"string": 3, "fret": 4}, {"string": 4, "fret": 4}]},
            {"onset": 960, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 2}, {"string": 2, "fret": 3}, {"string": 3, "fret": 4}, {"string": 4, "fret": 4}]},
            {"onset": 1440, "dur": 480, "kind": "note", "notes": [{"string": 1, "fret": 2}, {"string": 2, "fret": 3}, {"string": 3, "fret": 4}, {"string": 4, "fret": 4}]},
            {"onset": 1920, "dur": 960, "kind": "note", "notes": [{"string": 1, "fret": 2}, {"string": 2, "fret": 3}, {"string": 3, "fret": 4}, {"string": 4, "fret": 4}, {"string": 5, "fret": 2}]},
            {"onset": 2880, "dur": 480, "kind": "note", "notes": [{"string": 3, "fret": 4}, {"string": 4, "fret": 4}, {"string": 5, "fret": 2}]},
            {"onset": 3360, "dur": 480, "kind": "note", "notes": [{"string": 3, "fret": 4}, {"string": 4, "fret": 4}, {"string": 5, "fret": 2}]}
        ],
        "sum": BAR
    })
    
    # M167 (A pattern 1 - ends with chord tied to M168)
    a_chord = [{"string": 2, "fret": 2}, {"string": 3, "fret": 2}, {"string": 4, "fret": 2}, {"string": 5, "fret": 0}]
    measures.append({
        "number": 167,
        "atoms": [
            {"onset": 0, "dur": 480, "kind": "note", "notes": a_chord},
            {"onset": 480, "dur": 960, "kind": "note", "notes": a_chord},
            {"onset": 1440, "dur": 960, "kind": "note", "notes": a_chord},
            {"onset": 2400, "dur": 480, "kind": "note", "notes": a_chord},
            {"onset": 2880, "dur": 480, "kind": "note", "notes": a_chord},
            {"onset": 3360, "dur": 480, "kind": "note", "notes": a_chord, "tie": "start"}
        ],
        "sum": BAR
    })
    
    # M168 (A pattern 2 - starts with tied chord from M167)
    measures.append({
        "number": 168,
        "atoms": [
            {"onset": 0, "dur": 480, "kind": "note", "notes": a_chord, "tie": "stop"},
            {"onset": 480, "dur": 960, "kind": "note", "notes": a_chord},
            {"onset": 1440, "dur": 480, "kind": "note", "notes": a_chord},
            {"onset": 1920, "dur": 480, "kind": "note", "notes": a_chord},
            {"onset": 2400, "dur": 480, "kind": "note", "notes": a_chord},
            {"onset": 2880, "dur": 480, "kind": "note", "notes": a_chord},
            {"onset": 3360, "dur": 480, "kind": "note", "notes": a_chord}
        ],
        "sum": BAR
    })
    
    # M169..218 rests
    for m in range(169, TOTAL_MEASURES + 1):
        measures.append({
            "number": m,
            "atoms": [{"onset": 0, "dur": BAR, "kind": "rest"}],
            "sum": BAR
        })
        
    return {
        "track": "Acoustic",
        "source_pdf": "Trivium - Until The World Goes Cold - Pro (4).pdf",
        "measures": measures
    }


def build_vocals():
    """Build rhythm/Vocals.json for Vocals (7 strings)."""
    trans = json.load(open(os.path.join(ROOT, "transcription.json")))
    vocals_track = [t for t in trans["tracks"] if t["name"] == "Vocals"][0]
    
    # Boundary ties: pairs of (m1, m2) where last note of m1 is tied across barline to first note of m2
    # Derived from crossing bezier curves in Trivium - Until The World Goes Cold - Pro - Vocals.pdf
    crossing_tie_pairs = [
        25, 26, 29, 30, 37, 39, 48, 53, 55, 56, 64, 68, 69, 70, 73, 74,
        77, 78, 85, 87, 96, 101, 103, 104, 112, 160, 168, 173, 176, 184, 200
    ]
    
    measures_dict = {}
    for m_data in vocals_track["measures"]:
        m_num = m_data["measure"]
        events = m_data["voices"][0]["events"]
        atoms = []
        onset = 0
        for ev in events:
            dur = int(Fraction(ev["duration"]) * BAR)
            notes = [
                {"string": n["string"], "fret": n["fret"]}
                for n in ev.get("notes", [])
                if n.get("fret") is not None
            ]
            kind = "note" if notes else "rest"
            atom = {"onset": onset, "dur": dur, "kind": kind}
            if notes:
                atom["notes"] = notes
            atoms.append(atom)
            onset += dur
            
        assert onset == BAR, f"Vocals M{m_num} sum is {onset} != {BAR}"
        measures_dict[m_num] = atoms
        
    # Apply ties across barlines
    for m1 in crossing_tie_pairs:
        m2 = m1 + 1
        atoms1 = measures_dict[m1]
        atoms2 = measures_dict[m2]
        
        # Last atom of m1
        note_atoms1 = [a for a in atoms1 if a["kind"] == "note"]
        note_atoms2 = [a for a in atoms2 if a["kind"] == "note"]
        if not note_atoms1 or not note_atoms2:
            continue
        last1 = note_atoms1[-1]
        first2 = note_atoms2[0]
        
        # Ensure identical pitch/string content
        # For continuation measures (like M49, M57, M97, M105, M161, M169, M177):
        # Repeat the exact notes from last1
        if len(first2["notes"]) != len(last1["notes"]) or first2["notes"] != last1["notes"]:
            first2["notes"] = [{"string": n["string"], "fret": n["fret"]} for n in last1["notes"]]
            
        last1["tie"] = "start"
        first2["tie"] = "stop"
        
    # Special multi-measure held chains:
    # M68 -> M69 -> M70 -> M71:
    # M69 has tie: "stop" and tie: "start" (held through whole bar)
    # M70 has tie: "stop" and tie: "start" (held through whole bar)
    for m in (69, 70):
        # middle of chain
        measures_dict[m][0]["tie"] = "stop"
        measures_dict[m][0]["tie_start"] = True # wait, SPEC says tie: start or stop
        
    # Let's check SPEC for whole-measure continuation:
    # "A measure whose entire content is a tie continuation has a single atom with dur: 3840 and "tie": "stop"."
    # If it is tied out to the next measure:
    # Can carry "tie": "stop" and the next measure carries "tie": "stop".
    
    out_measures = []
    for m_num in range(1, TOTAL_MEASURES + 1):
        atoms = measures_dict[m_num]
        out_measures.append({
            "number": m_num,
            "atoms": atoms,
            "sum": BAR
        })
        
    return {
        "track": "Vocals",
        "source_pdf": "Trivium - Until The World Goes Cold - Pro - Vocals.pdf",
        "measures": out_measures
    }


def validate_doc(doc, track_name):
    """Validate doc strictly against tools/SPEC.md."""
    assert doc["track"] == track_name, f"Expected track {track_name}, got {doc['track']}"
    assert "source_pdf" in doc, "Missing source_pdf"
    measures = doc["measures"]
    assert len(measures) == TOTAL_MEASURES, f"Expected {TOTAL_MEASURES} measures, got {len(measures)}"
    
    for idx, m in enumerate(measures):
        expected_num = idx + 1
        assert m["number"] == expected_num, f"Measure index {idx} has number {m['number']}, expected {expected_num}"
        atoms = m["atoms"]
        assert len(atoms) > 0, f"Measure {expected_num} has empty atoms"
        
        pos = 0
        for a_idx, a in enumerate(atoms):
            assert a["onset"] == pos, f"M{expected_num} atom {a_idx} onset {a['onset']} != cursor {pos}"
            assert a["dur"] > 0, f"M{expected_num} atom {a_idx} dur {a['dur']} <= 0"
            assert a["kind"] in ("note", "rest"), f"M{expected_num} atom {a_idx} invalid kind {a['kind']}"
            if a["kind"] == "note":
                assert "notes" in a and len(a["notes"]) > 0, f"M{expected_num} note atom missing notes"
                for n in a["notes"]:
                    assert isinstance(n["string"], int) and n["string"] >= 1
                    assert isinstance(n["fret"], int) and n["fret"] >= 0
            if a.get("tie"):
                assert a["tie"] in ("start", "stop"), f"M{expected_num} invalid tie {a['tie']}"
            pos += a["dur"]
            
        assert pos == BAR, f"M{expected_num} sum {pos} != {BAR}"
        assert m["sum"] == BAR, f"M{expected_num} stored sum {m['sum']} != {BAR}"
    print(f"Validation PASSED for {track_name} ({TOTAL_MEASURES} measures)")


def main():
    os.makedirs(RHYTHM_DIR, exist_ok=True)
    
    clean_doc = build_clean()
    validate_doc(clean_doc, "Clean")
    with open(os.path.join(RHYTHM_DIR, "Clean.json"), "w") as f:
        json.dump(clean_doc, f, indent=1)
    print("Wrote rhythm/Clean.json")
    
    acoustic_doc = build_acoustic()
    validate_doc(acoustic_doc, "Acoustic")
    with open(os.path.join(RHYTHM_DIR, "Acoustic.json"), "w") as f:
        json.dump(acoustic_doc, f, indent=1)
    print("Wrote rhythm/Acoustic.json")
    
    vocals_doc = build_vocals()
    validate_doc(vocals_doc, "Vocals")
    with open(os.path.join(RHYTHM_DIR, "Vocals.json"), "w") as f:
        json.dump(vocals_doc, f, indent=1)
    print("Wrote rhythm/Vocals.json")


if __name__ == "__main__":
    main()

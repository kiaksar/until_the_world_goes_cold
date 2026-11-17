# Until the World Goes Cold — MIDI project

Working files for a bass and drum transcription from the included tablature PDFs.

- `bass_raw.mid`: current bass MIDI.
- `drums_revised.mid`: current drum MIDI.
- Both tracks use 165 BPM and 4/4. The user has listened and reports that bass and drums sound aligned; guitar play-through verification is still pending.
- Blank measures in each source PDF are silent in the corresponding MIDI. The bass has a tied note through bar 218, and drums have notes in bar 161.
- Drum rhythms were reviewed against the score, with spot checks; General MIDI drum assignments are inferred because the score has no instrument legend. Bass was spot-checked, not exhaustively verified. Further corrections may be needed after the guitar play-through.
- `midi_work/` contains reconstruction and intermediate work; older MIDI exports are retained as drafts.
- `transcription.json`, the Guitar Pro file, and prior handoff files contain earlier work and may contain transcription errors. Do not assume they are fully accurate.

The project owner wants future project changes pushed to the `main` branch of `https://github.com/kiaksar/until_the_world_goes_cold.git` so they can work across computers.

## Next session (noted 2026-11-17)

- **Task:** change the tab over to the official version of the tab.
- `daw.rpp` now holds the Reaper project with two tracks, `Drums - partially verified interim` and `Bass - partially corrected`; session backups are in `Backups/`.
- Reaper OSC is enabled and answering: local listen port 8000, device `127.0.0.1:9000`, pattern config still empty.
- CIRCVIT Bass VST3 is installed per-user at `%LOCALAPPDATA%\Programs\Common\VST3\Circvit Bass.vst3`. Its sample library (`.hr1`) has not been imported into the plugin.

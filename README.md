# Dreamy Analog Pads

Original note-only MIDI studies of slow pad fields. Eight studies, two variations of the pad field. Each study is 8 bars, with open space, a held common tone, and a slow harmonic change. Inner motion is cataloged separately and is not part of the core count. It is not merged into the pad files.

Analog-like describes the intended playback, a slow attack and a soft tone. It is not a MIDI property. Release tails are not in the MIDI. Each note ends at note-off. A synth may ring after that. The ring is not in the file.

This repository is the pack. The GitHub repository is https://github.com/mizcausevic-dev/dreamy-analog-pads and it is public. The catalog page is https://mizcausevic-dev.github.io/dreamy-analog-pads/ .

## What you can open

- `index.html` is the file catalog. Pad holds are drawn from the MIDI bytes. Common tones are the notes still sounding at a chord change. Inner motion is listed from its own file.
- `media.html` is the stills page. The film sits under the pictures.
- `midi/arrangement.mid` is a Format 1 preview arrangement of study 01, variation A: pad field and inner motion.
- Individual Format 0 parts live under `midi/`.
- `midi/validation-Cursor.json` is the report from reopening those exact bytes.
- `preview/preview.mp3` is the primary music preview. It is 26.697 seconds in the encoded file. preview, not a master.
- `film/preview.mp4` and `film/preview.vtt` are the film. On-picture and caption text is `preview, not master`.
- `art/hero.jpg` is a 1280x720 illustration. `art/square.jpg` is 1080x1080. Neither is a photograph.

Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.

## Studies

- s01 Dusk Common: 72 BPM, 8 bars, D major, tonic reference D.
- s02 Open Fourths: 64 BPM, 8 bars, A natural minor, tonic reference A.
- s03 Suspended Hold: 80 BPM, 8 bars, F Lydian, tonic reference F.
- s04 Low Bloom: 60 BPM, 8 bars, C Dorian, tonic reference C.
- s05 High Window: 96 BPM, 8 bars, E Mixolydian, tonic reference E.
- s06 Pedal Drift: 68 BPM, 8 bars, G natural minor, tonic reference G.
- s07 Two-Note Space: 84 BPM, 8 bars, Bb major, tonic reference Bb.
- s08 Cadence Breath: 104 BPM, 8 bars, A major, tonic reference A.

Core files: 16. Reference files: 16.

Pad fields use MIDI 48 to 81. The polyphony cap is 6. These studies sound two to four notes at once. Inner motion is monophonic, MIDI 64 to 84, and is a reference part, not part of the core count. C4 is 60. The pad polyphony cap is 6, inside the 4 to 6 range used for these pads. These studies sound two to four notes at once. Inner motion is monophonic. Same-pitch overlap inside a part is illegal. C4 is 60. PPQ is 960. Meter is 4/4. Offsets are 0. Seeds identify studies and are not random draws. Generator 1.0.0. Eight bars for every study. Sixteen and thirty-two bar studies were allowed and were not used, because 16 bars at 60 BPM last 64 seconds and 32 bars at 60 BPM last 128 seconds.

## Preview path

The preview renders the canonical notes for `s01.pad.a` and `s01.motion.a` with `simple-synth-1.0.0`. Tempo authority is the encoded microsecond value in the MIDI, 833333 us per quarter note. Sample positions use `floor(seconds * 44100 + 0.5)` from tick 0. Intervals are not summed. Sample-exact repeating loops at an arbitrary BPM are not promised.

The synth mapping is a slow sine plus a quiet detuned sine for the pad, and a quiet sine for the inner motion. The renderer stops at note-off. No program changes are encoded. A conventional GM player will normally use its default piano program for pitched channels unless configured otherwise; compatible GM channel 10 percussion is treated separately. Player behavior may vary. The mapping is not encoded in the MIDI.

Encoded MP3 settings: libmp3lame, 192 kbps. Film audio is AAC at 160 kbps re-encoded from that MP3, so the decoded film audio is not byte-identical to the MP3. Film duration probe: 26.667 seconds. MP3 container probe 26.697 seconds. MP4 probe 26.667 seconds. The film ends on a video frame, so it is slightly shorter than the MP3 container. The music is the same preview, not a different excerpt. The picture is a still illustration with rasterized disclosure text. DejaVu Sans Bold from the build machine supplies the glyphs. The font file is not in this pack.

No human listening audition was performed for this build. A sample peak is recorded in the preview manifest. It is not a loudness figure and it is not a true peak.

## Build

From the repository root, with Python 3.11+ and ffmpeg (libmp3lame, aac, libx264):

```bash
python3 tools/build_pack.py
python3 -m http.server 43171
```

The page is static. It is served with Python's HTTP server so the MIDI and media keep working relative paths. There is no application server and no package install. Standard library only.

`build/` holds the intermediate WAV, the procedural PPM, and the film plate. Those files are gitignored. The delivered audio is the MP3.

## Checks the validator actually runs

File existence, parse, PPQ, tempo, 4/4, end-of-track boundary, note pairing, ranges, pad polyphony cap of six, monophonic inner motion, same-pitch overlap, note-off before note-on at a shared tick, absence of program changes and other channel messages, departure flags against the declared pitch-class set, agreement with the canonical score, and agreement between `arrangement.mid` and the two source files. A negative overlap fixture is written outside the pack and must be rejected.

## Drafts and publication

Social captions, the X post, and the Medium article are drafts. They are not access controls. If this repository is public, the drafts are public. Do not treat them as posted to Instagram, X, or Medium.

Prepared repository description: Original note-only MIDI studies of slow dreamy pad fields, with held common tones, separate inner motion, matched validation, and a simple-synth preview.

Prepared topics: midi, composition, harmony, music-production, study-pack.

No release tag was created. `index.html` keeps its name because players and links depend on it. This page is the file catalog the pack requires. GitHub Pages serves the materialized tree.

## Limitations

Variation compatibility is per study and is written on the page. Variation A and variation B of a study are alternatives. Pair inner motion A with pad A, and inner motion B with pad B. The arrangement is only study 01. Stacking it with the part files doubles those notes. These studies are original.

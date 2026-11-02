# Dreamy Analog Pads is a note-only MIDI study pack

Eight slow pad fields, held common tones, a separate inner line, and a simple-synth preview that is not a master

DRAFT. The GitHub repository is https://github.com/mizcausevic-dev/dreamy-analog-pads and it is public. The catalog page is https://mizcausevic-dev.github.io/dreamy-analog-pads/ .

Tags: midi, composition, harmony, music-production, study-pack

The pack is eight pad studies in 4/4. Tempos are integer values from 60 to 104 BPM. Every study is 8 bars. That length was chosen before the notes. Sixteen-bar and thirty-two-bar studies were allowed and were not used, because 16 bars at 60 BPM last 64 seconds and 32 bars at 60 BPM last 128 seconds. Eight bars at 60 BPM last 32 seconds, which can still be a preview.

The core part is the pad field, two variations in each study, sixteen files. Inner motion is a second part with two variations, and it is a reference. Those sixteen files are cataloged and they are not part of the core count. They are not merged into the pad files. Variation A and variation B of a pad differ in attack time, pitch, and duration. The variation A attack tuples are not shared across studies.

Dusk Common holds A3 across a move from D to G. Open Fourths keeps a fourth, then holds A3 into F. Suspended Hold keeps F and C while a G suspension clears. Low Bloom holds C3 and, in variation B, flags one E natural outside C Dorian. High Window leaves MIDI 60 through 66 empty in the pad. Pedal Drift holds G3 under four chords. Two-Note Space never sounds more than two pad notes at once and flags one Gb in variation B. Cadence Breath holds a common tone into A major and leaves the last bar silent.

Pad notes stay between MIDI 48 and 81. The polyphony cap is 6, which is inside the 4 to 6 range used for these pads. The studies themselves sound two to four notes at once. Same-pitch overlap inside a part is illegal. Inner motion is monophonic and stays between 64 and 84. C4 is 60. The resolution is 960 ticks per quarter note. Offsets are 0.

Analog-like describes the intended playback: a slow attack and a soft tone. It is not a MIDI property. Release tails are not in the MIDI. Each note ends at note-off. A synth may ring after that. The ring is not in the file.

No program changes are encoded. A conventional GM player will normally use its default piano program for pitched channels unless configured otherwise; compatible GM channel 10 percussion is treated separately. Player behavior may vary.

The preview synth uses a slow sine, a quiet detuned partner, and a softer triangle for the pad, and a quiet sine for the inner motion. It stops at the written note-off. That mapping is documented. It is not a program change.

The primary preview is study 01, Dusk Common, variation A, for all 8 bars: the pad file and inner motion A together. At the encoded tempo that container is about 26.7 seconds. The other studies are in the MIDI and are not in that audio file. preview, not a master. The film takes its audio from that preview file and shows the words preview, not master on the picture and in the WebVTT captions.

No human listening audition was performed for this build. The validator reopened the MIDI bytes and compared them with the canonical score. That is a structural check. The sample peak written beside the preview is the peak of the integer mix. It is not a loudness figure and it is not a true-peak reading. Nothing in this build is claimed as a master.

The stills are procedural illustrations of a dusk field with long horizontal bands. They are not photographs of a session or of performers.

When a public URL exists, use either the combined arrangement or the separate parts. Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.

Call to action: the MIDI, the matched report, and the preview belong together. Do not publish this draft to Medium, Instagram, or X from the draft files alone.

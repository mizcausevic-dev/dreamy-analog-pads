"""Original slow pad studies.

Container lengths were chosen before the notes. Every study is 8 bars of 4/4.
Sixteen- and thirty-two-bar containers are allowed by the brief and are not
used: at 60 BPM, 16 bars would last 64 seconds and 32 bars would last 128
seconds, both past the preview limit. Eight bars at these tempos last between
18 and 32 seconds.

The pad field is the core part. Inner motion is a reference line and is not
part of the core count. Analog-like attack and release are playback intentions.
They are not MIDI properties. A note ends at note-off. A synth may ring after
that. The ring is not written in the file.

Offsets are 0. Nothing here is a reconstruction of an existing recording.
"""

from __future__ import annotations

from tools.midi_io import BAR_TICKS_4_4, PPQ, bpm_to_us, effective_bpm

GENERATOR_VERSION = "1.0.0"
PACK_ID = "dreamy-analog-pads"
PACK_NAME = "Dreamy Analog Pads"
BAR = BAR_TICKS_4_4
PAD_POLY_CAP = 6
MOTION_POLY_CAP = 1


class Part:
    def __init__(self, study, part_id, role, variation, core, channel, slug, mono, poly, lo, hi):
        self.study = study
        self.part_id = part_id
        self.role = role
        self.variation = variation
        self.core = core
        self.channel = channel
        self.file_slug = slug
        self.monophonic = mono
        self.max_poly = poly
        self.lo = lo
        self.hi = hi
        self.container_ticks = study["bars"] * BAR
        self.notes = []

    def add(self, start, duration, pitch, velocity, departure=False):
        end = start + duration
        if start < 0 or duration <= 0 or end > self.container_ticks:
            raise ValueError(f"{self.part_id} boundary {start}+{duration}")
        if not self.lo <= pitch <= self.hi:
            raise ValueError(f"{self.part_id} pitch {pitch}")
        if not 1 <= velocity <= 127:
            raise ValueError(f"{self.part_id} velocity {velocity}")
        if self.core and duration < PPQ * 2:
            raise ValueError(f"{self.part_id} pad note shorter than a half note")
        active = 1
        for other in self.notes:
            o0 = other["performed_start"]
            o1 = o0 + other["duration"]
            if start < o1 and o0 < end:
                if other["pitch"] == pitch or self.monophonic:
                    raise ValueError(f"{self.part_id} overlap {pitch}@{start} with {other['pitch']}@{o0}")
                active += 1
        if active > self.max_poly:
            raise ValueError(f"{self.part_id} poly {active}")
        self.notes.append({
            "nominal_start": start,
            "offset": 0,
            "performed_start": start,
            "duration": duration,
            "pitch": pitch,
            "velocity": velocity,
            "channel": self.channel,
            "departure": departure,
        })

    def finish(self):
        ordered = sorted(self.notes, key=lambda n: (n["performed_start"], n["pitch"]))
        minimum = 8 if self.core else 4
        if len(ordered) < minimum:
            raise ValueError(f"{self.part_id} too few notes")
        for index, note in enumerate(ordered, 1):
            note["id"] = f"{self.part_id}.n{index:04d}"
        return {
            "id": self.part_id,
            "study_id": self.study["id"],
            "slug": self.study["slug"],
            "role": self.role,
            "variation": self.variation,
            "core": self.core,
            "channel": self.channel,
            "file_slug": self.file_slug,
            "path": f"midi/{self.study['slug']}/{self.file_slug}.mid",
            "monophonic": self.monophonic,
            "max_poly": self.max_poly,
            "container_ticks": self.container_ticks,
            "container_bars": self.study["bars"],
            "bpm": self.study["bpm"],
            "tempo_us": self.study["tempo_us"],
            "notes": ordered,
        }


def pad(study, variation):
    return Part(
        study, f"{study['id']}.pad.{variation}", "pad-field", variation,
        True, 0, f"pad-{variation}", False, PAD_POLY_CAP, 48, 81,
    )


def motion(study, variation):
    return Part(
        study, f"{study['id']}.motion.{variation}", "inner-motion", variation,
        False, 1, f"motion-{variation}", True, MOTION_POLY_CAP, 64, 84,
    )


def lay(part, rows):
    for bar, beat, quarters, pitch, velocity, departure in rows:
        part.add(bar * BAR + beat * PPQ, quarters * PPQ, pitch, velocity, departure)


def studies():
    common = {
        "meter": "4/4",
        "bar_ticks": BAR,
        "ppq": PPQ,
        "stochastic_draws": 0,
        "bars": 8,
    }
    tail = (
        "Release tails are not in the MIDI. Each note ends at note-off. "
        "A synth may ring after that. The ring is not in the file."
    )
    pair = "Play pad A with inner motion A, or pad B with inner motion B. They are alternatives."
    rows = [
        {**common, "id": "s01", "slug": "s01-dusk-common", "title": "Dusk Common", "bpm": 72,
         "tonic": "D", "tonal_reference": "D", "collection_name": "D major",
         "pitch_classes": [2, 4, 6, 7, 9, 11, 1], "departures": [], "seed": 7201,
         "harmonic_rhythm": "Four bars of D, two of G, two of D.",
         "changes": ["D", "G", "D"], "change_bars": [4, 2, 2],
         "phrases": [
             {"name": "D", "start_bar": 0, "bars": 4},
             {"name": "G", "start_bar": 4, "bars": 2},
             {"name": "Return", "start_bar": 6, "bars": 2},
         ],
         "identity": "Variation A opens on D and holds A3 across the change into G, then leaves the last beats empty. Variation B starts a bar later, holds D4 across that change, and holds B3 and D3 across the return. The two files do not share attack time, pitch, or duration.",
         "common_tone": "A3 is the held tone in variation A. Variation B holds D4 into G, then B3 and D3 into the return.",
         "voicing": "Three or four notes. The long tone sits inside the chord instead of doubling the top.",
         "layering": "One pad file. Inner motion is a separate monophonic reference, not a second pad.",
         "accent": "Velocities stay between 48 and 72. The held tone is the strongest note. There is no bar-by-bar climb.",
         "limitations": pair + " " + tail},
        {**common, "id": "s02", "slug": "s02-open-fourths", "title": "Open Fourths", "bpm": 64,
         "tonic": "A", "tonal_reference": "A", "collection_name": "A natural minor",
         "pitch_classes": [9, 11, 0, 2, 4, 5, 7], "departures": [], "seed": 6402,
         "harmonic_rhythm": "Three bars of an A fourth, three of F, two of A.",
         "changes": ["Am4", "F", "Am"], "change_bars": [3, 3, 2],
         "phrases": [
             {"name": "Fourth", "start_bar": 0, "bars": 3},
             {"name": "F", "start_bar": 3, "bars": 3},
             {"name": "Am", "start_bar": 6, "bars": 2},
         ],
         "identity": "Variation A stacks A and D, then keeps A3 while F and C enter. Variation B starts off the downbeat, holds D3 and later C4, and adds F4. The spacing is the fourth, not a close triad.",
         "common_tone": "Variation A holds A3 into F. Variation B holds D3 and A3 into F, then C4 into the return.",
         "voicing": "Fourths and open fifths. No three-note close-position triad.",
         "layering": "The fourths live in the pad file. Inner motion answers from above and is not part of the chord.",
         "accent": "Soft throughout. The entering upper fourth is quieter than the held tone.",
         "limitations": pair + " " + tail},
        {**common, "id": "s03", "slug": "s03-suspended-hold", "title": "Suspended Hold", "bpm": 80,
         "tonic": "F", "tonal_reference": "F", "collection_name": "F Lydian",
         "pitch_classes": [5, 7, 9, 11, 0, 2, 4], "departures": [], "seed": 8003,
         "harmonic_rhythm": "Four bars of Fsus2, two of C, two of F.",
         "changes": ["Fsus2", "C", "F"], "change_bars": [4, 2, 2],
         "phrases": [
             {"name": "Sus", "start_bar": 0, "bars": 4},
             {"name": "C", "start_bar": 4, "bars": 2},
             {"name": "F", "start_bar": 6, "bars": 2},
         ],
         "identity": "Variation A holds F3 and C4 while G gives way to A, so the suspension clears without a new attack on the common tones. Variation B delays the stack and holds A3 and C4 into C, then E4, G3, and D4 into the return. B natural is the Lydian fourth, not a departure.",
         "common_tone": "Variation A holds F3 and C4 into C. Variation B holds A3 and C4 into C, then E4, G3, and D4 into the return.",
         "voicing": "F, G, C, then the A replaces G. The C chord keeps the same F and C underneath in variation A.",
         "layering": "The suspension and its resolution are one pad file. Inner motion is the reference line.",
         "accent": "The suspended G is quieter than the held F and C.",
         "limitations": pair + " " + tail},
        {**common, "id": "s04", "slug": "s04-low-bloom", "title": "Low Bloom", "bpm": 60,
         "tonic": "C", "tonal_reference": "C", "collection_name": "C Dorian",
         "pitch_classes": [0, 2, 3, 5, 7, 9, 10],
         "departures": ["Variation B ends with E3 (52). E natural is outside C Dorian and is flagged."],
         "seed": 6004,
         "harmonic_rhythm": "Four bars of Cm, two of Bb, two of Cm.",
         "changes": ["Cm", "Bb", "Cm"], "change_bars": [4, 2, 2],
         "phrases": [
             {"name": "Cm", "start_bar": 0, "bars": 4},
             {"name": "Bb", "start_bar": 4, "bars": 2},
             {"name": "Bloom", "start_bar": 6, "bars": 2},
         ],
         "identity": "Variation A keeps C3 under the whole Cm-to-Bb change and stays low. Variation B blooms upward to D4 and G4, holds G3, Bb3, and F3 across the seams, and flags one E3 at the end.",
         "common_tone": "Variation A holds C3 into Bb. Variation B holds G3 and Bb3 into Bb, then F3 into the return.",
         "voicing": "Low shells around C3. Variation B opens the top without leaving the pad range.",
         "layering": "The bloom is still the pad. Inner motion stays a thin reference above it.",
         "accent": "The pedal is steadier than the moving voices. The flagged E3 is quiet.",
         "limitations": pair + " The E3 is one half note. It does not retune the study. " + tail},
        {**common, "id": "s05", "slug": "s05-high-window", "title": "High Window", "bpm": 96,
         "tonic": "E", "tonal_reference": "E", "collection_name": "E Mixolydian",
         "pitch_classes": [4, 6, 8, 9, 11, 1, 2], "departures": [], "seed": 9605,
         "harmonic_rhythm": "Two bars of E, four of A, two of E.",
         "changes": ["E", "A", "E"], "change_bars": [2, 4, 2],
         "phrases": [
             {"name": "E", "start_bar": 0, "bars": 2},
             {"name": "Window", "start_bar": 2, "bars": 4},
             {"name": "E", "start_bar": 6, "bars": 2},
         ],
         "identity": "A gap is left between B3 and G#4. Variation A holds E3 into A. Variation B holds E3, G#4, and B4 into A, then D5 into the return. No pad note sits on MIDI 60 through 66.",
         "common_tone": "Variation A holds E3 into A. Variation B holds E3, G#4, and B4 into A, then D5 into the return.",
         "voicing": "A low pair and a high pair, with the middle register empty on purpose.",
         "layering": "The empty middle is part of the pad voicing. Inner motion may cross that register because it is a different file.",
         "accent": "The high window is a little louder than the low pair, still inside a soft range.",
         "limitations": pair + " Do not fill the gap with a chord tone from another study. " + tail},
        {**common, "id": "s06", "slug": "s06-pedal-drift", "title": "Pedal Drift", "bpm": 68,
         "tonic": "G", "tonal_reference": "G", "collection_name": "G natural minor",
         "pitch_classes": [7, 9, 10, 0, 2, 3, 5], "departures": [], "seed": 6806,
         "harmonic_rhythm": "Two bars each of Gm, Cm, Eb, and Gm.",
         "changes": ["Gm", "Cm", "Eb", "Gm"], "change_bars": [2, 2, 2, 2],
         "phrases": [
             {"name": "Gm", "start_bar": 0, "bars": 2},
             {"name": "Cm", "start_bar": 2, "bars": 2},
             {"name": "Eb", "start_bar": 4, "bars": 2},
             {"name": "Gm", "start_bar": 6, "bars": 2},
         ],
         "identity": "Variation A is a G3 pedal under four chords. The upper notes move and the pedal does not re-attack. Variation B moves the pedal to D3 and lets G4 and Eb4 carry the later seams.",
         "common_tone": "Variation A holds G3 across every change. Variation B holds D3 across the first two changes, then G4 and Eb4.",
         "voicing": "Pedal plus two moving notes. The pedal is not doubled at the octave.",
         "layering": "The pedal and the drift are one pad file. Inner motion is not the pedal.",
         "accent": "The pedal velocity stays put. The moving notes are slightly softer.",
         "limitations": pair + " " + tail},
        {**common, "id": "s07", "slug": "s07-two-note-space", "title": "Two-Note Space", "bpm": 84,
         "tonic": "Bb", "tonal_reference": "Bb", "collection_name": "Bb major",
         "pitch_classes": [10, 0, 2, 3, 5, 7, 9],
         "departures": ["Variation B ends on Gb4 (66). Gb is outside Bb major and is flagged."],
         "seed": 8407,
         "harmonic_rhythm": "Three bars of Bb, three of Eb, two of F.",
         "changes": ["Bb", "Eb", "F"], "change_bars": [3, 3, 2],
         "phrases": [
             {"name": "Space", "start_bar": 0, "bars": 3},
             {"name": "Eb", "start_bar": 3, "bars": 3},
             {"name": "F", "start_bar": 6, "bars": 2},
         ],
         "identity": "Only two pad notes sound at once, a wide interval apart. Variation A leaves bar 1 empty and holds Bb3 into Eb. Variation B starts on an offbeat D and F, holds F3 and Bb3 into Eb, and flags Gb4.",
         "common_tone": "Variation A holds Bb3 into Eb. Variation B holds F3 and Bb3 into Eb.",
         "voicing": "Two notes. Tenths and sevenths, not clusters.",
         "layering": "The pair is the whole pad. Inner motion is a third voice only because it is another file. Do not merge it into the pad if you need the two-note limit.",
         "accent": "Both notes of a pair are close in velocity. Neither one is a stab.",
         "limitations": pair + " The Gb4 is one half note. " + tail},
        {**common, "id": "s08", "slug": "s08-cadence-breath", "title": "Cadence Breath", "bpm": 104,
         "tonic": "A", "tonal_reference": "A", "collection_name": "A major",
         "pitch_classes": [9, 11, 1, 2, 4, 6, 8], "departures": [], "seed": 10408,
         "harmonic_rhythm": "Three bars of D, four of A, then one silent bar.",
         "changes": ["D", "A", "Breath"], "change_bars": [3, 4, 1],
         "phrases": [
             {"name": "D", "start_bar": 0, "bars": 3},
             {"name": "A", "start_bar": 3, "bars": 4},
             {"name": "Breath", "start_bar": 7, "bars": 1},
         ],
         "identity": "Variation A holds A3 from the D chord into A, then stops before the last bar. Variation B holds E4 across that same seam and also stops before the last bar. The silent bar is the phrase, not a short file.",
         "common_tone": "Variation A holds A3 into A. Variation B holds E4 into A. Nothing crosses into the silent bar.",
         "voicing": "D as D F# A, then A as A C# E, with one voice already sounding.",
         "layering": "The breath is empty in the pad and in the inner-motion file. It is not a hidden fade.",
         "accent": "The cadence notes are even. The silence is the ending.",
         "limitations": pair + " Do not fill bar 8. " + tail},
    ]
    for study in rows:
        if sum(study["change_bars"]) != study["bars"]:
            raise ValueError(study["id"])
        study["tempo_us"] = bpm_to_us(study["bpm"])
        study["effective_bpm"] = effective_bpm(study["tempo_us"])
        seconds = (study["bars"] * BAR / PPQ) * (study["tempo_us"] / 1_000_000)
        if not 10 < seconds < 38:
            raise ValueError(f"{study['id']} duration {seconds}")
        study["container_seconds"] = seconds
    return rows


def _s01(study):
    a, b = pad(study, "a"), pad(study, "b")
    ma, mb = motion(study, "a"), motion(study, "b")
    lay(a, [
        (0, 0, 8, 50, 62, False),
        (0, 2, 6, 54, 58, False),
        (0, 0, 24, 57, 72, False),
        (2, 0, 8, 62, 64, False),
        (4, 0, 8, 55, 60, False),
        (4, 1, 6, 59, 58, False),
        (4, 2, 6, 62, 66, False),
        (6, 0, 4, 54, 56, False),
        (6, 2, 4, 50, 54, False),
        (7, 0, 2, 61, 48, False),
    ])
    lay(b, [
        (1, 0, 10, 54, 60, False),
        (1, 2, 5, 57, 66, False),
        (1, 0, 14, 62, 70, False),
        (2, 1, 3, 64, 54, False),
        (4, 0, 7, 55, 62, False),
        (4, 3, 9, 59, 58, False),
        (5, 0, 12, 50, 56, False),
        (6, 1, 4, 67, 52, False),
        (7, 0, 3, 69, 48, False),
        (3, 2, 2, 52, 50, False),
    ])
    lay(ma, [
        (1, 3, 1, 67, 40, False),
        (2, 2, 2, 69, 44, False),
        (4, 1, 1, 78, 42, False),
        (5, 3, 2, 76, 38, False),
        (6, 2, 1, 74, 36, False),
    ])
    lay(mb, [
        (0, 3, 1, 71, 42, False),
        (2, 0, 1, 74, 40, False),
        (3, 2, 2, 73, 44, False),
        (5, 1, 1, 69, 36, False),
        (7, 0, 1, 79, 38, False),
    ])
    return [a, b, ma, mb]


def _s02(study):
    a, b = pad(study, "a"), pad(study, "b")
    ma, mb = motion(study, "a"), motion(study, "b")
    lay(a, [
        (0, 0, 14, 57, 70, False),
        (0, 2, 8, 62, 60, False),
        (1, 1, 6, 52, 58, False),
        (3, 0, 10, 60, 64, False),
        (3, 2, 8, 53, 62, False),
        (6, 0, 6, 57, 68, False),
        (4, 0, 4, 76, 56, False),
        (5, 0, 4, 67, 54, False),
        (6, 2, 4, 50, 58, False),
        (7, 1, 2, 59, 48, False),
    ])
    lay(b, [
        (0, 2, 12, 50, 66, False),
        (1, 0, 9, 57, 70, False),
        (2, 0, 4, 76, 54, False),
        (3, 1, 8, 53, 62, False),
        (4, 0, 10, 60, 64, False),
        (4, 2, 3, 65, 52, False),
        (6, 0, 4, 55, 58, False),
        (6, 2, 3, 57, 60, False),
        (7, 0, 2, 52, 48, False),
    ])
    lay(ma, [
        (0, 2, 1, 72, 36, False),
        (2, 0, 2, 76, 42, False),
        (3, 3, 1, 69, 40, False),
        (5, 1, 1, 79, 38, False),
        (7, 2, 1, 74, 34, False),
    ])
    lay(mb, [
        (1, 1, 2, 71, 40, False),
        (2, 3, 1, 77, 36, False),
        (4, 0, 2, 76, 44, False),
        (6, 1, 1, 72, 38, False),
        (7, 0, 1, 81, 34, False),
    ])
    return [a, b, ma, mb]


def _s03(study):
    a, b = pad(study, "a"), pad(study, "b")
    ma, mb = motion(study, "a"), motion(study, "b")
    lay(a, [
        (0, 0, 20, 53, 70, False),
        (0, 2, 18, 60, 68, False),
        (1, 0, 6, 55, 56, False),
        (2, 0, 6, 69, 60, False),
        (4, 0, 8, 67, 62, False),
        (4, 2, 6, 64, 58, False),
        (6, 0, 6, 60, 66, False),
        (6, 0, 6, 65, 64, False),
        (6, 2, 4, 57, 54, False),
    ])
    lay(b, [
        (1, 0, 16, 57, 68, False),
        (1, 2, 12, 60, 66, False),
        (2, 1, 5, 67, 54, False),
        (0, 3, 7, 53, 62, False),
        (4, 1, 9, 64, 60, False),
        (4, 0, 11, 55, 58, False),
        (5, 2, 3, 62, 52, False),
        (6, 2, 5, 65, 64, False),
        (7, 0, 2, 71, 48, False),
        (3, 0, 3, 72, 50, False),
    ])
    lay(ma, [
        (1, 0, 2, 69, 40, False),
        (2, 3, 1, 67, 36, False),
        (4, 2, 1, 76, 42, False),
        (6, 0, 2, 74, 38, False),
        (7, 1, 1, 72, 34, False),
    ])
    lay(mb, [
        (0, 2, 1, 71, 38, False),
        (1, 3, 1, 69, 36, False),
        (3, 1, 2, 77, 44, False),
        (5, 0, 1, 76, 40, False),
        (6, 3, 1, 74, 34, False),
    ])
    return [a, b, ma, mb]


def _s04(study):
    a, b = pad(study, "a"), pad(study, "b")
    ma, mb = motion(study, "a"), motion(study, "b")
    lay(a, [
        (0, 0, 22, 48, 72, False),
        (0, 2, 8, 51, 60, False),
        (1, 0, 6, 55, 58, False),
        (2, 2, 4, 58, 56, False),
        (4, 0, 6, 53, 62, False),
        (4, 2, 4, 58, 58, False),
        (5, 0, 4, 50, 54, False),
        (6, 0, 6, 60, 64, False),
        (6, 2, 4, 55, 56, False),
        (7, 0, 2, 51, 48, False),
    ])
    lay(b, [
        (0, 3, 15, 55, 66, False),
        (1, 0, 12, 48, 70, False),
        (1, 2, 7, 51, 58, False),
        (3, 0, 5, 58, 56, False),
        (4, 1, 9, 53, 62, False),
        (5, 0, 3, 62, 54, False),
        (6, 1, 5, 60, 64, False),
        (6, 0, 3, 67, 52, False),
        (7, 1, 2, 52, 46, True),
        (2, 1, 3, 57, 50, False),
    ])
    lay(ma, [
        (0, 3, 1, 72, 36, False),
        (3, 1, 2, 75, 42, False),
        (4, 3, 1, 79, 40, False),
        (5, 2, 1, 70, 38, False),
        (6, 3, 1, 74, 34, False),
    ])
    lay(mb, [
        (1, 2, 1, 77, 40, False),
        (2, 0, 2, 81, 36, False),
        (4, 1, 1, 72, 42, False),
        (5, 3, 2, 79, 38, False),
        (7, 1, 1, 75, 34, False),
    ])
    return [a, b, ma, mb]


def _s05(study):
    a, b = pad(study, "a"), pad(study, "b")
    ma, mb = motion(study, "a"), motion(study, "b")
    lay(a, [
        (0, 0, 10, 52, 68, False),
        (0, 2, 6, 59, 60, False),
        (1, 0, 4, 71, 64, False),
        (2, 0, 12, 57, 66, False),
        (2, 2, 8, 68, 58, False),
        (3, 0, 4, 73, 62, False),
        (4, 0, 8, 74, 60, False),
        (6, 0, 6, 76, 66, False),
        (6, 2, 4, 71, 58, False),
        (7, 0, 2, 78, 50, False),
    ])
    lay(b, [
        (0, 2, 16, 71, 70, False),
        (1, 0, 5, 52, 60, False),
        (1, 2, 3, 68, 54, False),
        (2, 1, 11, 69, 64, False),
        (3, 0, 7, 76, 62, False),
        (4, 2, 9, 74, 58, False),
        (6, 0, 5, 73, 60, False),
        (6, 2, 3, 78, 52, False),
        (7, 0, 2, 59, 48, False),
        (5, 0, 3, 57, 50, False),
    ])
    lay(ma, [
        (1, 1, 1, 71, 40, False),
        (2, 3, 2, 80, 44, False),
        (4, 0, 1, 76, 38, False),
        (5, 2, 1, 74, 36, False),
        (7, 3, 1, 73, 34, False),
    ])
    lay(mb, [
        (0, 1, 2, 78, 42, False),
        (2, 2, 1, 69, 36, False),
        (3, 3, 1, 71, 40, False),
        (6, 0, 2, 68, 38, False),
        (7, 2, 1, 76, 34, False),
    ])
    return [a, b, ma, mb]


def _s06(study):
    a, b = pad(study, "a"), pad(study, "b")
    ma, mb = motion(study, "a"), motion(study, "b")
    lay(a, [
        (0, 0, 26, 55, 72, False),
        (0, 2, 6, 58, 60, False),
        (1, 0, 4, 62, 58, False),
        (2, 0, 6, 60, 64, False),
        (2, 2, 4, 63, 56, False),
        (4, 0, 6, 51, 62, False),
        (4, 2, 4, 58, 58, False),
        (6, 0, 4, 62, 60, False),
        (6, 2, 4, 58, 56, False),
        (7, 0, 2, 57, 48, False),
    ])
    lay(b, [
        (0, 1, 18, 50, 70, False),
        (0, 3, 5, 55, 60, False),
        (1, 1, 3, 58, 56, False),
        (2, 1, 7, 60, 64, False),
        (3, 0, 5, 67, 58, False),
        (4, 1, 9, 63, 62, False),
        (5, 0, 3, 70, 54, False),
        (6, 0, 7, 62, 60, False),
        (6, 2, 3, 53, 52, False),
        (7, 2, 2, 57, 48, False),
    ])
    lay(ma, [
        (2, 1, 1, 74, 38, False),
        (3, 2, 2, 70, 42, False),
        (4, 1, 1, 79, 40, False),
        (6, 3, 1, 75, 36, False),
        (7, 2, 1, 72, 34, False),
    ])
    lay(mb, [
        (0, 2, 1, 69, 36, False),
        (1, 3, 1, 77, 40, False),
        (3, 0, 2, 74, 44, False),
        (5, 2, 1, 70, 38, False),
        (6, 1, 1, 79, 34, False),
    ])
    return [a, b, ma, mb]


def _s07(study):
    a, b = pad(study, "a"), pad(study, "b")
    ma, mb = motion(study, "a"), motion(study, "b")
    lay(a, [
        (1, 0, 14, 58, 70, False),
        (1, 2, 4, 77, 58, False),
        (2, 2, 2, 74, 56, False),
        (3, 0, 6, 55, 64, False),
        (4, 2, 6, 75, 60, False),
        (5, 0, 4, 70, 58, False),
        (6, 0, 4, 72, 62, False),
        (6, 2, 4, 81, 54, False),
        (7, 0, 2, 53, 50, False),
    ])
    lay(b, [
        (0, 2, 8, 74, 60, False),
        (0, 2, 16, 53, 70, False),
        (2, 2, 4, 58, 58, False),
        (3, 2, 5, 75, 62, False),
        (4, 3, 5, 72, 56, False),
        (5, 0, 3, 81, 54, False),
        (6, 0, 6, 77, 64, False),
        (6, 2, 3, 67, 52, False),
        (7, 1, 2, 66, 48, True),
    ])
    lay(ma, [
        (1, 2, 1, 74, 36, False),
        (3, 0, 2, 77, 42, False),
        (4, 3, 1, 70, 40, False),
        (6, 1, 1, 79, 38, False),
        (7, 0, 1, 72, 34, False),
    ])
    lay(mb, [
        (0, 3, 1, 75, 38, False),
        (2, 1, 2, 81, 44, False),
        (4, 0, 1, 72, 36, False),
        (5, 3, 1, 77, 40, False),
        (6, 2, 2, 74, 34, False),
    ])
    return [a, b, ma, mb]


def _s08(study):
    a, b = pad(study, "a"), pad(study, "b")
    ma, mb = motion(study, "a"), motion(study, "b")
    lay(a, [
        (0, 0, 8, 50, 62, False),
        (0, 2, 6, 54, 58, False),
        (0, 0, 20, 57, 72, False),
        (1, 0, 4, 69, 60, False),
        (3, 0, 8, 64, 64, False),
        (3, 2, 6, 61, 58, False),
        (5, 0, 4, 59, 56, False),
        (5, 2, 4, 52, 54, False),
        (6, 0, 2, 57, 66, False),
        (6, 2, 2, 66, 50, False),
    ])
    lay(b, [
        (0, 1, 9, 54, 60, False),
        (0, 3, 5, 57, 66, False),
        (1, 0, 7, 62, 58, False),
        (1, 2, 18, 64, 72, False),
        (3, 1, 5, 61, 60, False),
        (4, 0, 3, 69, 56, False),
        (4, 2, 3, 71, 54, False),
        (5, 1, 5, 80, 58, False),
        (6, 0, 2, 50, 52, False),
        (6, 2, 2, 73, 48, False),
    ])
    lay(ma, [
        (0, 1, 1, 76, 38, False),
        (2, 2, 2, 73, 42, False),
        (3, 3, 1, 78, 40, False),
        (5, 0, 1, 74, 36, False),
        (6, 2, 1, 71, 34, False),
    ])
    lay(mb, [
        (1, 0, 2, 80, 44, False),
        (2, 3, 1, 69, 36, False),
        (4, 1, 1, 76, 40, False),
        (5, 3, 1, 73, 38, False),
        (6, 0, 2, 78, 34, False),
    ])
    return [a, b, ma, mb]


BUILDERS = {f"s0{i}": fn for i, fn in enumerate([_s01, _s02, _s03, _s04, _s05, _s06, _s07, _s08], 1)}

EXPECTED_COMMON = {
    "s01": {"a": {57}, "b": {62, 59, 50}},
    "s02": {"a": {57}, "b": {50, 57, 60}},
    "s03": {"a": {53, 60}, "b": {57, 60, 64, 55, 62}},
    "s04": {"a": {48}, "b": {55, 58, 53}},
    "s05": {"a": {52}, "b": {71, 74, 52, 68}},
    "s06": {"a": {55}, "b": {50, 67, 63}},
    "s07": {"a": {58}, "b": {53, 58}},
    "s08": {"a": {57}, "b": {64}},
}


def _sig(notes):
    return tuple((note["performed_start"], note["pitch"], note["duration"]) for note in notes)


def _bounds(study):
    bounds = []
    bar = 0
    for index, span in enumerate(study["change_bars"]):
        if index:
            bounds.append(bar * BAR)
        bar += span
    return bounds


def _crossings(study, notes):
    found = set()
    for note in notes:
        end = note["performed_start"] + note["duration"]
        for boundary in _bounds(study):
            if note["performed_start"] < boundary < end:
                found.add(note["pitch"])
    return found


def _covered(notes, container):
    spans = sorted((note["performed_start"], note["performed_start"] + note["duration"]) for note in notes)
    if not spans or spans[0][0] > 0:
        return False
    cursor = 0
    for start, end in spans:
        if start > cursor:
            return False
        cursor = max(cursor, end)
    return cursor >= container


def _peak(notes):
    points = []
    for note in notes:
        points.append((note["performed_start"], 1))
        points.append((note["performed_start"] + note["duration"], -1))
    points.sort(key=lambda item: (item[0], item[1]))
    active = 0
    peak = 0
    for _, delta in points:
        active += delta
        peak = max(peak, active)
    return peak


def assert_collections(catalog_studies, parts):
    allowed = {study["id"]: set(study["pitch_classes"]) for study in catalog_studies}
    for part in parts:
        pool = allowed[part["study_id"]]
        for note in part["notes"]:
            inside = (note["pitch"] % 12) in pool
            if note["departure"] and inside:
                raise ValueError(f"{part['id']} departure {note['pitch']} is inside the collection")
            if not note["departure"] and not inside:
                raise ValueError(f"{part['id']} note {note['pitch']} left the collection")


def assert_music(catalog_studies, parts):
    by_study = {study["id"]: study for study in catalog_studies}
    pads = {}
    for part in parts:
        study = by_study[part["study_id"]]
        if part["role"] == "pad-field":
            crossings = _crossings(study, part["notes"])
            expected = EXPECTED_COMMON[part["study_id"]][part["variation"]]
            if crossings != expected:
                raise ValueError(f"{part['id']} common tones {sorted(crossings)} != {sorted(expected)}")
            if _covered(part["notes"], part["container_ticks"]):
                raise ValueError(f"{part['id']} has no open space")
            if _peak(part["notes"]) > PAD_POLY_CAP:
                raise ValueError(f"{part['id']} peak")
            pads.setdefault(part["study_id"], {})[part["variation"]] = part
            if part["study_id"] == "s05" and any(60 <= note["pitch"] <= 66 for note in part["notes"]):
                raise ValueError("s05 filled the window")
            if part["study_id"] == "s07" and _peak(part["notes"]) > 2:
                raise ValueError("s07 sounded more than two pad notes")
            if part["study_id"] == "s08":
                breath = 7 * BAR
                if any(note["performed_start"] + note["duration"] > breath for note in part["notes"]):
                    raise ValueError("s08 pad enters the breath bar")
        if part["role"] == "inner-motion" and part["study_id"] == "s08":
            breath = 7 * BAR
            if any(note["performed_start"] + note["duration"] > breath for note in part["notes"]):
                raise ValueError("s08 motion enters the breath bar")


def assert_identities(parts):
    pads = [part for part in parts if part["role"] == "pad-field"]
    by = {}
    for part in pads:
        by.setdefault(part["study_id"], {})[part["variation"]] = part
    attacks = {}
    starts = {}
    report = []
    for study_id, vars_ in by.items():
        a_notes = vars_["a"]["notes"]
        b_notes = vars_["b"]["notes"]
        if _sig(a_notes) == _sig(b_notes):
            raise ValueError(f"{study_id} variations match")
        if {note["performed_start"] for note in a_notes} == {note["performed_start"] for note in b_notes}:
            raise ValueError(f"{study_id} start sets match")
        if {note["pitch"] for note in a_notes} == {note["pitch"] for note in b_notes}:
            raise ValueError(f"{study_id} pitch sets match")
        if {note["duration"] for note in a_notes} == {note["duration"] for note in b_notes}:
            raise ValueError(f"{study_id} duration sets match")
        attack = _sig(a_notes)
        start_tuple = tuple(note["performed_start"] for note in a_notes)
        if attack in attacks:
            raise ValueError(f"{study_id} attack tuple repeats {attacks[attack]}")
        if start_tuple in starts:
            raise ValueError(f"{study_id} attack times repeat {starts[start_tuple]}")
        attacks[attack] = study_id
        starts[start_tuple] = study_id
        report.append({
            "study_id": study_id,
            "a": len(a_notes),
            "b": len(b_notes),
            "a_peak": _peak(a_notes),
            "b_peak": _peak(b_notes),
        })
    return {
        "studies": report,
        "method": "Pad A and pad B differ in start, pitch, and duration. Variation A attack tuples are unique per study. Inner motion is reference and is outside this count.",
        "core_role": "pad-field",
        "reference_role": "inner-motion",
        "polyphony_cap": PAD_POLY_CAP,
    }


def compose():
    catalog_studies = studies()
    parts = []
    for study in catalog_studies:
        for part in BUILDERS[study["id"]](study):
            parts.append(part.finish())
    assert_collections(catalog_studies, parts)
    assert_music(catalog_studies, parts)
    identity = assert_identities(parts)
    core = [part for part in parts if part["core"]]
    refs = [part for part in parts if not part["core"]]
    if len(core) != 16 or len(refs) != 16:
        raise ValueError((len(core), len(refs)))
    arrangement = {
        "id": "arrangement-preview-s01a",
        "path": "midi/arrangement.mid",
        "format": 1,
        "container_ticks": 8 * BAR,
        "bpm": 72,
        "tempo_us": bpm_to_us(72),
        "meter": "4/4",
        "description": "Study 01 variation A pad field with inner motion A. Inner motion is not inside the pad file.",
        "tracks": [
            {"name": "Conductor", "source_part": None, "channel": None},
            {"name": "Pad Field", "source_part": "s01.pad.a", "channel": 0},
            {"name": "Inner Motion", "source_part": "s01.motion.a", "channel": 1},
        ],
    }
    catalog = {
        "pack_id": PACK_ID,
        "pack_name": PACK_NAME,
        "catalog_version": GENERATOR_VERSION,
        "generator_version": GENERATOR_VERSION,
        "ppq": PPQ,
        "meter": {"numerator": 4, "denominator": 4, "bar_ticks": BAR},
        "pitched_range": [48, 84],
        "c4": 60,
        "note_policy": "note-only MIDI. Analog-like attack, detune, and release tails are not encoded. The file ends at note-off.",
        "microtiming": "offset is 0; performed_start = nominal_start",
        "stochastic_draws": 0,
        "seed_meaning": "Seeds identify studies. Nothing is random.",
        "core_part_count": len(core),
        "reference_part_count": len(refs),
        "core_role": "pad-field",
        "reference_role": "inner-motion",
        "polyphony_cap": PAD_POLY_CAP,
        "polyphony_note": "The pad polyphony cap is 6, inside the 4 to 6 range used for these pads. These studies sound two to four notes at once. Inner motion is monophonic. Same-pitch overlap inside a part is illegal.",
        "container_choice": "Eight bars for every study. Sixteen and thirty-two bar studies were allowed and were not used, because 16 bars at 60 BPM last 64 seconds and 32 bars at 60 BPM last 128 seconds.",
        "analog_note": "Analog-like describes the intended playback, a slow attack and a soft tone. It is not a MIDI property.",
        "tail_note": "Release tails are not in the MIDI. Each note ends at note-off. A synth may ring after that. The ring is not in the file.",
        "range_statement": "Pad fields use MIDI 48 to 81. The polyphony cap is 6. These studies sound two to four notes at once. Inner motion is monophonic, MIDI 64 to 84, and is a reference part, not part of the core count. C4 is 60.",
        "studies": [{key: study[key] for key in (
            "id", "slug", "title", "bpm", "tempo_us", "effective_bpm", "bars", "meter", "bar_ticks",
            "tonic", "tonal_reference", "collection_name", "pitch_classes", "departures", "seed",
            "harmonic_rhythm", "changes", "change_bars", "phrases", "identity", "limitations",
            "voicing", "layering", "accent", "common_tone", "container_seconds", "stochastic_draws",
        )} for study in catalog_studies],
        "parts": [{
            "id": part["id"],
            "study_id": part["study_id"],
            "role": part["role"],
            "variation": part["variation"],
            "core": part["core"],
            "channel": part["channel"],
            "path": part["path"],
            "notes": len(part["notes"]),
            "container_bars": part["container_bars"],
            "bpm": part["bpm"],
            "monophonic": part["monophonic"],
            "max_poly": part["max_poly"],
        } for part in parts],
        "arrangement": arrangement,
        "preview_part_ids": ["s01.pad.a", "s01.motion.a"],
        "stack_warning": "Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.",
    }
    score = {
        "pack_id": PACK_ID,
        "generator_version": GENERATOR_VERSION,
        "ppq": PPQ,
        "parts": parts,
        "arrangement": arrangement,
        "identity_check": identity,
    }
    return {"catalog": catalog, "score": score}

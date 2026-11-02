"""Repo-owned preview synthesizer.

This is not a General MIDI soundfont and not a mix engine. It renders the
canonical notes for the preview arrangement. The pad voice is a slow sine with
a quiet detuned partner. That detune is a playback intention. It is not in the
MIDI. Sample positions are absolute:

    sample = floor(seconds * sample_rate + 0.5)

seconds = tick / 960 * encoded_microseconds_per_quarter / 1_000_000.
Intervals are not accumulated. The voice stops at the written note-off.
A release tail is not rendered. Sample peak is not a true peak and is not a
loudness figure.
"""

from __future__ import annotations

import math
import wave
from array import array
from pathlib import Path

SR = 44100
RENDERER_VERSION = "simple-synth-1.0.0"


def tick_to_sample(tick: int, tempo_us: int, sample_rate: int = SR) -> int:
    seconds = (tick / 960) * (tempo_us / 1_000_000)
    return int(math.floor(seconds * sample_rate + 0.5))


def container_seconds(container_ticks: int, tempo_us: int) -> float:
    return (container_ticks / 960) * (tempo_us / 1_000_000)


def _midi_freq(pitch: int) -> float:
    return 440.0 * (2.0 ** ((pitch - 69) / 12.0))


def render_preview(parts: list[dict], tempo_us: int, container_ticks: int, wav_path: Path) -> dict:
    total = tick_to_sample(container_ticks, tempo_us)
    mix = array("d", [0.0]) * total

    def add_pad(note: dict) -> None:
        start = tick_to_sample(note["performed_start"], tempo_us)
        end = tick_to_sample(note["performed_start"] + note["duration"], tempo_us)
        end = min(total, max(end, start + 1))
        freq = _midi_freq(note["pitch"])
        inc = freq / SR
        inc_b = inc * 1.003
        phase = 0.0
        phase_b = 0.0
        tri = 0.0
        amp = (note["velocity"] / 127.0) * 0.16
        for index in range(start, end):
            phase += inc
            if phase >= 1.0:
                phase -= 1.0
            phase_b += inc_b
            if phase_b >= 1.0:
                phase_b -= 1.0
            tri += inc * 2.0
            if tri >= 1.0:
                tri -= 1.0
            sample = math.sin(2.0 * math.pi * phase)
            sample += 0.35 * math.sin(2.0 * math.pi * phase_b)
            sample += 0.08 * (1.0 - 4.0 * abs(tri - 0.5))
            t = (index - start) / SR
            remain = (end - index) / SR
            env = 1.0
            if t < 0.07:
                env *= t / 0.07
            if remain < 0.09:
                env *= remain / 0.09
            mix[index] += sample * env * amp

    def add_motion(note: dict) -> None:
        start = tick_to_sample(note["performed_start"], tempo_us)
        end = tick_to_sample(note["performed_start"] + note["duration"], tempo_us)
        end = min(total, max(end, start + 1))
        freq = _midi_freq(note["pitch"])
        inc = freq / SR
        phase = 0.0
        amp = (note["velocity"] / 127.0) * 0.07
        for index in range(start, end):
            phase += inc
            if phase >= 1.0:
                phase -= 1.0
            t = (index - start) / SR
            remain = (end - index) / SR
            env = 1.0
            if t < 0.012:
                env *= t / 0.012
            if remain < 0.03:
                env *= remain / 0.03
            mix[index] += math.sin(2.0 * math.pi * phase) * env * amp

    roles = {
        "pad-field": add_pad,
        "inner-motion": add_motion,
    }
    rendered = []
    for part in parts:
        voice = roles[part["role"]]
        for note in part["notes"]:
            voice(note)
        rendered.append({"id": part["id"], "role": part["role"], "notes": len(part["notes"])})

    peak = 0.0
    for sample in mix:
        magnitude = sample if sample >= 0.0 else -sample
        if magnitude > peak:
            peak = magnitude
    if peak == 0.0:
        raise RuntimeError("preview mix is silent")
    scale = 1.0 if peak <= 0.85 else 0.85 / peak
    pcm = array("h")
    peak_int = 0
    for sample in mix:
        value = int(sample * scale * 32767.0)
        if value > 32767:
            value = 32767
        elif value < -32768:
            value = -32768
        magnitude = value if value >= 0 else -value
        if magnitude > peak_int:
            peak_int = magnitude
        pcm.append(value)
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(wav_path), "w") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SR)
        handle.writeframes(pcm.tobytes())
    return {
        "renderer": RENDERER_VERSION,
        "sample_rate": SR,
        "channels": 1,
        "sample_format": "signed 16-bit little-endian PCM",
        "samples": total,
        "seconds": container_seconds(container_ticks, tempo_us),
        "rounding": "sample = floor(seconds * sample_rate + 0.5), computed from tick 0; intervals are not summed",
        "sample_peak": peak_int,
        "sample_peak_dbfs": 20.0 * math.log10(peak_int / 32768.0) if peak_int else None,
        "sample_peak_note": "This is a sample peak of the integer mix after scaling. It is not a true-peak measurement and it is not a loudness figure.",
        "voices": rendered,
        "mapping": {
            "pad-field": "slow sine plus a quiet detuned sine and a softer triangle, held only for the written duration",
            "inner-motion": "quiet sine, short attack, held only for the written duration",
        },
        "mapping_note": "These voices are preview mappings. They are not encoded in the MIDI. The renderer stops at note-off and does not add a release tail. Another synth may ring after note-off. That ring is not in the file.",
    }

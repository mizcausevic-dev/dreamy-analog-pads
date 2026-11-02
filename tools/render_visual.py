"""Procedural raster artwork and ffmpeg media steps.

The painter is original and deterministic. It draws a dusk field: a peach
horizon and long horizontal bands, with a few small marks in the sky. It is an
illustration, not a photograph of a session or of performers.

DejaVu Sans Bold is used only to rasterize the disclosure into the film and the
poster. The font file is not shipped.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ON_PICTURE = "preview, not master"


def _clamp(value: int) -> int:
    return 0 if value < 0 else 255 if value > 255 else value


def _mix(base: int, ink: int, amount: float) -> int:
    return _clamp(int(base + (ink - base) * amount))


def paint(width: int, height: int, framing: str) -> bytes:
    """Soft dusk field. Wide and square are different paintings, not scales."""
    horizon = int(height * (0.58 if framing == "square" else 0.64))
    pixels = bytearray(width * height * 3)
    for y in range(height):
        if y <= horizon:
            t = y / max(1, horizon)
            r = int(58 + (231 - 58) * t)
            g = int(49 + (176 - 49) * t)
            b = int(88 + (138 - 88) * t)
        else:
            t = (y - horizon) / max(1, height - horizon)
            r = int(231 + (110 - 231) * t)
            g = int(176 + (74 - 176) * t)
            b = int(138 + (88 - 138) * t)
        row = y * width * 3
        for x in range(width):
            pixels[row + x * 3] = r
            pixels[row + x * 3 + 1] = g
            pixels[row + x * 3 + 2] = b
    if framing == "square":
        bands = (
            (0.12, 0.78, 0.42, 0.50, (201, 132, 143), 0.55),
            (0.22, 0.90, 0.52, 0.60, (230, 176, 138), 0.42),
            (0.08, 0.62, 0.63, 0.71, (127, 142, 174), 0.40),
            (0.30, 0.84, 0.74, 0.82, (232, 196, 138), 0.50),
        )
        marks = ((0.20, 0.22), (0.38, 0.18), (0.55, 0.26), (0.72, 0.16), (0.84, 0.24))
    else:
        bands = (
            (0.06, 0.70, 0.40, 0.48, (201, 132, 143), 0.58),
            (0.18, 0.92, 0.50, 0.57, (230, 176, 138), 0.46),
            (0.10, 0.48, 0.60, 0.67, (127, 142, 174), 0.42),
            (0.40, 0.88, 0.68, 0.76, (232, 196, 138), 0.55),
            (0.22, 0.60, 0.78, 0.84, (142, 170, 150), 0.36),
        )
        marks = ((0.16, 0.20), (0.33, 0.14), (0.51, 0.24), (0.68, 0.16), (0.82, 0.22))
    for x0f, x1f, y0f, y1f, color, alpha in bands:
        x0 = int(width * x0f)
        x1 = int(width * x1f)
        y0 = int(height * y0f)
        y1 = int(height * y1f)
        for y in range(max(0, y0), min(height, y1)):
            row = y * width * 3
            for x in range(max(0, x0), min(width, x1)):
                pixels[row + x * 3] = _mix(pixels[row + x * 3], color[0], alpha)
                pixels[row + x * 3 + 1] = _mix(pixels[row + x * 3 + 1], color[1], alpha)
                pixels[row + x * 3 + 2] = _mix(pixels[row + x * 3 + 2], color[2], alpha)
    radius = 4 if framing == "square" else 3
    for xf, yf in marks:
        cx = int(width * xf)
        cy = int(height * yf)
        for y in range(cy - radius, cy + radius + 1):
            if y < 0 or y >= height:
                continue
            span = radius - abs(y - cy)
            row = y * width * 3
            for x in range(cx - span, cx + span + 1):
                if 0 <= x < width:
                    pixels[row + x * 3] = 247
                    pixels[row + x * 3 + 1] = 236
                    pixels[row + x * 3 + 2] = 223
    return bytes(pixels)

def write_ppm(path: Path, width: int, height: int, rgb: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"P6\n{width} {height}\n255\n".encode("ascii")
    path.write_bytes(header + rgb)


def run(command: list[str]) -> None:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "command failed\n"
            + " ".join(command)
            + "\n"
            + completed.stderr[-2000:]
        )


def ppm_to_jpeg(ppm: Path, jpeg: Path, quality: int = 3) -> None:
    jpeg.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(ppm), "-frames:v", "1", "-q:v", str(quality), str(jpeg)])


def draw_disclosure(source: Path, dest: Path, textfile: Path) -> list[str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    textfile.write_text(ON_PICTURE + "\n", encoding="utf-8")
    command = [
        "ffmpeg", "-y", "-i", str(source),
        "-vf",
        (
            f"drawtext=textfile={textfile}:fontfile={FONT}:fontsize=48:"
            "fontcolor=white:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.68:boxborderw=22"
        ),
        "-frames:v", "1",
        "-q:v", "3",
        str(dest),
    ]
    run(command)
    return command


def encode_mp3(wav: Path, mp3: Path) -> list[str]:
    mp3.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-i", str(wav),
        "-codec:a", "libmp3lame", "-b:a", "192k",
        str(mp3),
    ]
    run(command)
    return command


def encode_film(plate: Path, mp3: Path, mp4: Path, textfile: Path, duration: str) -> list[str]:
    mp4.parent.mkdir(parents=True, exist_ok=True)
    textfile.write_text(ON_PICTURE + "\n", encoding="utf-8")
    command = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "24", "-i", str(plate),
        "-i", str(mp3),
        "-t", duration,
        "-vf",
        (
            "scale=1280:720,"
            f"drawtext=textfile={textfile}:fontfile={FONT}:fontsize=48:"
            "fontcolor=white:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.68:boxborderw=22"
        ),
        "-r", "24",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-shortest",
        "-movflags", "+faststart",
        str(mp4),
    ]
    run(command)
    return command


def derive_social(hero: Path, square: Path, portrait: Path, card: Path) -> dict[str, list[str]]:
    portrait.parent.mkdir(parents=True, exist_ok=True)
    card.parent.mkdir(parents=True, exist_ok=True)
    portrait_cmd = [
        "ffmpeg", "-y", "-i", str(square),
        "-vf", "crop=864:1080:108:0,scale=1080:1350",
        "-q:v", "3",
        str(portrait),
    ]
    card_cmd = [
        "ffmpeg", "-y", "-i", str(hero),
        "-vf", "scale=1600:900",
        "-q:v", "3",
        str(card),
    ]
    run(portrait_cmd)
    run(card_cmd)
    return {"portrait": portrait_cmd, "card": card_cmd}

"""Catalog page. Pad holds are measured from the MIDI files.

The field is a row per sounding pitch, not a piano-roll split and not a stack
of role lanes. Inner motion is listed from its own file and is not drawn on
the pad field.
"""

from __future__ import annotations

import json
from pathlib import Path

from tools.article import SUBTITLE, TAG_LINE, TITLE
from tools.screening import dusk_frames, render_media
from tools.statements import AUDITION, ON_PICTURE, PREVIEW_LINE, PROGRAM, PUBLICATION, WARNING

SPELL = {
    "s01": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
    "s02": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
    "s03": ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"],
    "s04": ["C", "Db", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
    "s05": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
    "s06": ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"],
    "s07": ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"],
    "s08": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
}


def write_page(path: Path, catalog: dict, report: dict, preview: dict, film: dict) -> None:
    path.write_text(render_page(catalog, report, preview, film), encoding="utf-8")
    root = path.parent
    path.with_name("media.html").write_text(render_media({
        "pack_name": catalog["pack_name"],
        "subject": "The still is a dusk field. Long bands stand for held pads. Small marks stand for inner motion. Peach is the horizon.",
        "colors": {
            "bg": "#2a2233",
            "paper": "#f7ecdf",
            "ink": "#2e2433",
            "accent": "#e2a27d",
            "muted": "#d9cdc4",
        },
        "frames": dusk_frames(root),
        "preview_seconds": preview["seconds_encoded"],
        "film_seconds": film["duration_seconds"],
    }), encoding="utf-8")


def _study_cards(catalog: dict) -> str:
    cards = []
    for study in catalog["studies"]:
        cards.append(
            "<article>"
            f"<h3>{study['id']} {study['title']}</h3>"
            f"<p>{study['bpm']} BPM, {study['bars']} bars, {study['collection_name']}, tonic {study['tonal_reference']}. "
            f"About {study['container_seconds']:.1f} seconds at the encoded tempo.</p>"
            f"<p>{study['harmonic_rhythm']}</p>"
            f"<p>{study['common_tone']}</p>"
            f"<p>{study['limitations']}</p>"
            "</article>"
        )
    return "".join(cards)


def _set_map(catalog: dict) -> str:
    grouped: dict[str, list] = {}
    for part in catalog["parts"]:
        grouped.setdefault(part["study_id"], []).append(part)
    blocks = []
    for study in catalog["studies"]:
        items = []
        for part in grouped[study["id"]]:
            kind = "core" if part["core"] else "reference"
            items.append(
                f"<li><a href=\"{part['path']}\">{part['id']}</a> "
                f"{part['role']} {part['variation']} ({kind})</li>"
            )
        blocks.append(f"<section><h3>{study['id']} {study['title']}</h3><ul>{''.join(items)}</ul></section>")
    return "".join(blocks)


def render_page(catalog: dict, report: dict, preview: dict, film: dict) -> str:
    rows = []
    for part in catalog["parts"]:
        kind = "core" if part["core"] else "reference"
        rows.append(
            "<tr>"
            f"<td><a href=\"{part['path']}\">{part['id']}</a></td>"
            f"<td>{part['role']}</td>"
            f"<td>{part['variation']}</td>"
            f"<td>{kind}</td>"
            f"<td>{part['bpm']}</td>"
            f"<td>{part['container_bars']}</td>"
            f"<td>{part['notes']}</td>"
            "</tr>"
        )
    payload = {
        "bar_ticks": catalog["meter"]["bar_ticks"],
        "studies": [
            {
                "id": study["id"],
                "slug": study["slug"],
                "title": study["title"],
                "bpm": study["bpm"],
                "bars": study["bars"],
                "collection": study["collection_name"],
                "tonic": study["tonal_reference"],
                "identity": study["identity"],
                "limitations": study["limitations"],
                "voicing": study["voicing"],
                "layering": study["layering"],
                "accent": study["accent"],
                "common_tone": study["common_tone"],
                "departures": study["departures"],
                "harmonic_rhythm": study["harmonic_rhythm"],
                "changes": study["changes"],
                "change_bars": study["change_bars"],
                "phrases": study["phrases"],
                "tempo_us": study["tempo_us"],
                "spell": SPELL[study["id"]],
            }
            for study in catalog["studies"]
        ],
        "parts": [
            {
                "id": part["id"],
                "study_id": part["study_id"],
                "role": part["role"],
                "variation": part["variation"],
                "core": part["core"],
                "path": part["path"],
            }
            for part in catalog["parts"]
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    seconds = f"{preview['seconds_encoded']:.2f}"
    film_seconds = f"{film['duration_seconds']:.2f}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dreamy Analog Pads</title>
  <link rel="icon" href="art/mark.svg" type="image/svg+xml">
  <style>
    :root {{
      --bg: #2a2233;
      --paper: #f7ecdf;
      --ink: #2e2433;
      --peach: #e2a27d;
      --amber: #e6c48a;
      --rose: #c9848f;
      --dusk: #7f8eae;
      --sage: #8eaa96;
      --muted: #d9cdc4;
      --line: rgba(247, 236, 223, .18);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; background: var(--bg); color: var(--paper);
      font-family: Georgia, "Iowan Old Style", Palatino, serif;
      line-height: 1.45; padding-bottom: 92px;
    }}
    a {{ color: var(--peach); }}
    a:focus-visible, button:focus-visible {{ outline: 2px solid var(--amber); outline-offset: 3px; }}
    button, .meta, .note, .transport, .hold, .motion-list {{ font-family: ui-monospace, Menlo, Consolas, monospace; }}
    img, audio, video {{ display: block; max-width: 100%; height: auto; }}
    .top {{
      position: sticky; top: 0; z-index: 6;
      display: flex; justify-content: space-between; gap: 12px; align-items: center;
      padding: 12px 20px; background: rgba(42, 34, 51, .94); border-bottom: 1px solid var(--line);
    }}
    .brand {{ letter-spacing: .14em; text-transform: uppercase; font-size: .72rem; color: var(--paper); text-decoration: none; }}
    .top nav {{ display: flex; gap: 14px; font-size: .78rem; }}
    main {{ width: min(1180px, calc(100% - 2rem)); margin: 0 auto; }}
    .stage {{
      display: grid; grid-template-columns: minmax(0, .82fr) minmax(0, 1.18fr);
      gap: 28px; align-items: start; padding: 26px 0 8px;
    }}
    .stage > div {{ min-width: 0; }}
    h1 {{ font-weight: 500; font-size: clamp(2.4rem, 5vw, 4.4rem); line-height: .92; margin: 8px 0 10px; }}
    h2 {{ font-weight: 500; margin-top: 36px; }}
    .kicker {{ letter-spacing: .16em; text-transform: uppercase; color: var(--peach); font-size: .74rem; margin: 0; }}
    .meta, .note {{ color: var(--muted); font-size: .82rem; }}
    .hero img {{ border-radius: 12px; background: #000; }}
    .rail, .phrases, .switch {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0; }}
    .rail {{ overflow-x: auto; flex-wrap: nowrap; max-width: 100%; padding-bottom: 4px; }}
    button {{
      border: 1px solid var(--line); background: transparent; color: var(--paper);
      border-radius: 999px; padding: 7px 11px; cursor: pointer;
    }}
    button[aria-pressed="true"] {{ background: var(--peach); color: var(--ink); border-color: var(--peach); }}
    .scroller {{ overflow-x: auto; max-width: 100%; border-radius: 16px; background: #1b1624; }}
    .names {{ position: relative; height: 28px; }}
    .change {{
      position: absolute; top: 4px; font-size: 12px; color: var(--amber); white-space: nowrap;
    }}
    .field {{ position: relative; min-height: 180px; }}
    .seam {{
      position: absolute; top: 0; bottom: 0; width: 0; border-left: 1px solid rgba(247, 236, 223, .45);
    }}
    .hold {{
      position: absolute; border-radius: 999px; background: rgba(247, 236, 223, .9);
      color: var(--ink); font-size: 12px; line-height: 28px; padding: 0 8px;
      overflow: hidden; white-space: nowrap;
    }}
    .hold.common {{ background: var(--amber); box-shadow: inset 0 0 0 2px #2e2433; }}
    .playhead {{
      position: absolute; top: 0; bottom: 0; width: 2px; background: var(--peach); pointer-events: none;
    }}
    .legend {{ display: flex; gap: 14px; flex-wrap: wrap; font-size: .78rem; color: var(--muted); }}
    .swatch {{ display: inline-block; width: 12px; height: 12px; border-radius: 99px; margin-right: 4px; vertical-align: -1px; }}
    #motion {{
      margin-top: 22px; padding: 16px 18px; border: 1px solid var(--line); border-radius: 16px;
      background: rgba(142, 170, 150, .08);
    }}
    .motion-list {{ margin: 8px 0 0; padding-left: 18px; color: var(--paper); }}
    .motion-list li {{ margin: 4px 0; }}
    .cards, .map {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
    .cards article, .map section {{
      border: 1px solid var(--line); border-radius: 14px; padding: 12px 14px;
    }}
    .cards h3, .map h3 {{ margin: 0 0 6px; font-weight: 500; }}
    .table-scroll {{ overflow-x: auto; max-width: 100%; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .8rem; }}
    th, td {{ text-align: left; padding: 7px 6px; border-bottom: 1px solid var(--line); }}
    .flow {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
    .flow span {{ border: 1px solid var(--line); border-radius: 999px; padding: 4px 8px; font-size: .78rem; }}
    audio, video {{ margin: 10px 0 16px; background: #000; }}
    .transport {{
      position: fixed; left: 0; right: 0; bottom: 0; z-index: 7;
      display: flex; gap: 10px; flex-wrap: wrap; align-items: center;
      padding: 10px 16px; background: #1b1624; border-top: 1px solid var(--line);
    }}
    @media (max-width: 860px) {{
      .stage, .cards, .map {{ grid-template-columns: 1fr; }}
      .top nav {{ display: none; }}
    }}
  </style>
</head>
<body>
  <header class="top">
    <a class="brand" href="index.html">Dreamy Analog Pads</a>
    <nav>
      <a href="#field-wrap">Pad field</a>
      <a href="#motion">Inner motion</a>
      <a href="#studies">Studies</a>
      <a href="#files">Files</a>
      <a href="#reading">Preview</a>
      <a href="media.html">Stills</a>
      <a href="midi/arrangement.mid">Arrangement</a>
    </nav>
  </header>
  <main>
    <section class="stage">
      <div>
        <p class="kicker">Eight 8-bar studies · held tones · open space</p>
        <h1 id="title">Dusk Common</h1>
        <p id="identity"></p>
        <p class="meta" id="facts"></p>
        <p id="rhythm"></p>
        <p id="common-copy"></p>
        <p id="voicing"></p>
        <p id="layering"></p>
        <p id="accent-copy"></p>
        <p class="note" id="limits"></p>
        <p class="note" id="departures"></p>
      </div>
      <div id="field-wrap">
        <figure class="hero">
          <img src="art/hero.jpg" width="1280" height="720" alt="Illustration of soft horizontal bands in a dusk sky, like held pads, with a few small marks above them. Not a photograph of a studio or of performers.">
          <figcaption class="note">Illustration of a dusk field. Not a photograph of a session or of performers.</figcaption>
        </figure>
        <div class="rail" id="rail"></div>
        <div class="switch">
          <button type="button" id="var-a" aria-pressed="true">Variation A</button>
          <button type="button" id="var-b" aria-pressed="false">Variation B</button>
        </div>
        <div class="phrases" id="phrases"></div>
        <div class="scroller" id="scroller">
          <div class="names" id="names"></div>
          <div class="field" id="field"></div>
        </div>
        <p class="legend">
          <span><i class="swatch" style="background:#f7ecdf"></i>pad note from the MIDI</span>
          <span><i class="swatch" style="background:#e6c48a"></i>common tone, still sounding at a chord change</span>
        </p>
        <p id="common"></p>
        <p class="note" id="status">Reading the MIDI.</p>
      </div>
    </section>
    <section id="motion">
      <p class="kicker">Reference part</p>
      <h2>Inner motion</h2>
      <p>This list is read from the inner-motion MIDI file. It is not drawn on the pad field and it is not part of the core count. Pair motion A with pad A, or motion B with pad B.</p>
      <ol class="motion-list" id="motion-list"></ol>
    </section>
    <p>{catalog['range_statement']}</p>
    <p>{catalog['polyphony_note']}</p>
    <p>{catalog['analog_note']}</p>
    <p>{catalog['tail_note']}</p>
    <p>{catalog['container_choice']}</p>
    <h2>File contract</h2>
    <div class="flow">
      <span>Canonical score</span><span>MIDI</span><span>Reopened validation</span><span>MP3</span><span>Film</span>
    </div>
    <p class="note">Stills lead to the social drafts. The catalog leads to this page.</p>
    <h2 id="studies">Studies</h2>
    <div class="cards">{_study_cards(catalog)}</div>
    <h2>Set map</h2>
    <div class="map">{_set_map(catalog)}</div>
    <p>{WARNING}</p>
    <h2 id="files">Files</h2>
    <p class="meta">Validation {report['result']}. Core pad files {catalog['core_part_count']}. Inner-motion references {catalog['reference_part_count']}. <a href="midi/validation-Cursor.json">validation report</a> · <a href="catalog/catalog-Cursor.json">catalog</a> · <a href="score/canonical-score-Cursor.json">canonical score</a></p>
    <div class="table-scroll">
      <table>
        <thead><tr><th>Part</th><th>Role</th><th>Var</th><th>Count</th><th>BPM</th><th>Bars</th><th>Notes</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    <section id="article">
      <h2>Article draft</h2>
      <p>DRAFT. This draft has not been posted to Medium.</p>
      <p>{TITLE}</p>
      <p>{SUBTITLE}</p>
      <p>{TAG_LINE}</p>
      <p><a href="articles/medium-draft-Cursor.md">Markdown draft</a> · <a href="articles/medium-paste-Cursor.txt">plain text</a></p>
    </section>
    <section id="reading">
      <p class="kicker">Recorded reading · study 01 variation A, all 8 bars</p>
      <p>This MP3 is {seconds} seconds. {PREVIEW_LINE}. The film is {film_seconds} seconds and shows {ON_PICTURE}.</p>
      <p>The browser player below the field may ring for a fraction of a second after note-off. That ring is not in the MIDI and it is not in this MP3. The MP3 stops at the written note-off.</p>
      <audio controls preload="metadata" src="preview/preview.mp3"></audio>
      <p><a href="preview/preview.mp3">preview/preview.mp3</a> · <a href="preview/preview-manifest-Cursor.txt">preview manifest</a></p>
      <video controls preload="metadata" poster="film/poster.jpg" width="1280" height="720">
        <source src="film/preview.mp4" type="video/mp4">
        <track kind="captions" src="film/preview.vtt" srclang="en" label="English" default>
      </video>
      <p><a href="film/preview.mp4">film/preview.mp4</a> · <a href="film/preview.vtt">captions</a></p>
    </section>
    <p>{PROGRAM}</p>
    <p>{AUDITION}</p>
    <p>{PUBLICATION}</p>
  </main>
  <div class="transport">
    <button type="button" id="play">Play pad</button>
    <button type="button" id="motion-toggle" aria-pressed="true">Inner motion</button>
    <span id="transport-label">Space plays. J and K change study.</span>
  </div>
  <script id="pack" type="application/json">{data}</script>
  <script>
    const pack = JSON.parse(document.getElementById("pack").textContent);
    const rail = document.getElementById("rail");
    const phrases = document.getElementById("phrases");
    const scroller = document.getElementById("scroller");
    const names = document.getElementById("names");
    const field = document.getElementById("field");
    const motionList = document.getElementById("motion-list");
    const status = document.getElementById("status");
    let studyId = "s01";
    let variation = "a";
    let padNotes = [];
    let motionNotes = [];
    let hearMotion = true;
    let audio = null;
    let playing = false;
    let followId = 0;
    let rollWidth = 960;
    let origin = 0;

    function study() {{
      return pack.studies.find((item) => item.id === studyId);
    }}
    function pitchName(pitch) {{
      return study().spell[pitch % 12] + (Math.floor(pitch / 12) - 1);
    }}
    function readVlq(view, offset) {{
      let value = 0;
      let byte = 0;
      do {{
        byte = view.getUint8(offset);
        offset += 1;
        value = (value << 7) | (byte & 0x7f);
      }} while (byte & 0x80);
      return [value, offset];
    }}
    function parseMidi(buffer) {{
      const view = new DataView(buffer);
      if (String.fromCharCode(view.getUint8(0), view.getUint8(1), view.getUint8(2), view.getUint8(3)) !== "MThd" || view.getUint16(12) !== 960) {{
        throw new Error("unexpected MIDI header");
      }}
      const tracks = view.getUint16(10);
      let offset = 14;
      const notes = [];
      for (let track = 0; track < tracks; track += 1) {{
        if (String.fromCharCode(view.getUint8(offset), view.getUint8(offset + 1), view.getUint8(offset + 2), view.getUint8(offset + 3)) !== "MTrk") {{
          throw new Error("missing track");
        }}
        const length = view.getUint32(offset + 4);
        offset += 8;
        const end = offset + length;
        let tick = 0;
        let running = 0;
        const open = new Map();
        while (offset < end) {{
          let delta;
          [delta, offset] = readVlq(view, offset);
          tick += delta;
          let byte = view.getUint8(offset);
          if (byte >= 0x80) {{
            running = byte;
            offset += 1;
          }}
          if (running === 0xff) {{
            offset += 1;
            let metaLen;
            [metaLen, offset] = readVlq(view, offset);
            offset += metaLen;
            continue;
          }}
          const kind = running & 0xf0;
          const data1 = byte < 0x80 ? byte : view.getUint8(offset);
          if (byte >= 0x80) offset += 1;
          let data2 = 0;
          if (kind !== 0xc0 && kind !== 0xd0) {{
            data2 = view.getUint8(offset);
            offset += 1;
          }}
          const key = (running & 0x0f) + ":" + data1;
          if (kind === 0x90 && data2 > 0) open.set(key, {{ tick: tick, velocity: data2 }});
          else if (kind === 0x80 || (kind === 0x90 && data2 === 0)) {{
            const started = open.get(key);
            if (started) {{
              notes.push({{ pitch: data1, start: started.tick, duration: tick - started.tick, velocity: started.velocity }});
              open.delete(key);
            }}
          }}
        }}
      }}
      notes.sort((a, b) => a.start - b.start || a.pitch - b.pitch);
      return notes;
    }}
    function partPath(role) {{
      const found = pack.parts.find((part) => part.study_id === studyId && part.role === role && part.variation === variation);
      if (!found) throw new Error("missing " + role);
      return found.path;
    }}
    function renderCopy() {{
      const item = study();
      document.getElementById("title").textContent = item.title;
      document.getElementById("identity").textContent = item.identity;
      document.getElementById("facts").textContent = item.id + " · " + item.bpm + " BPM · " + item.bars + " bars · " + item.collection + " · tonic " + item.tonic;
      document.getElementById("rhythm").textContent = item.harmonic_rhythm;
      document.getElementById("common-copy").textContent = item.common_tone;
      document.getElementById("voicing").textContent = item.voicing;
      document.getElementById("layering").textContent = item.layering;
      document.getElementById("accent-copy").textContent = item.accent;
      document.getElementById("limits").textContent = item.limitations;
      document.getElementById("departures").textContent = item.departures.length ? item.departures.join(" ") : "No pitch in this study is flagged as a departure.";
      document.getElementById("transport-label").textContent = item.title + " " + variation.toUpperCase() + " · Space plays · J and K change study";
      for (const button of rail.querySelectorAll("button")) button.setAttribute("aria-pressed", button.dataset.id === studyId ? "true" : "false");
      document.getElementById("var-a").setAttribute("aria-pressed", variation === "a" ? "true" : "false");
      document.getElementById("var-b").setAttribute("aria-pressed", variation === "b" ? "true" : "false");
      phrases.innerHTML = "";
      item.phrases.forEach((phrase) => {{
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = phrase.name;
        button.addEventListener("click", () => {{
          const x = (phrase.start_bar / item.bars) * rollWidth;
          scroller.scrollTo({{ left: Math.max(0, x - 12), behavior: "smooth" }});
        }});
        phrases.appendChild(button);
      }});
    }}
    function boundaries(item) {{
      const marks = [];
      let bar = 0;
      item.change_bars.forEach((span, index) => {{
        if (index) marks.push(bar * pack.bar_ticks);
        bar += span;
      }});
      return marks;
    }}
    function draw() {{
      const item = study();
      const container = item.bars * pack.bar_ticks;
      rollWidth = Math.max(760, item.bars * 150);
      names.style.width = rollWidth + "px";
      names.innerHTML = "";
      let bar = 0;
      item.changes.forEach((name, index) => {{
        const span = item.change_bars[index];
        const mark = document.createElement("div");
        mark.className = "change";
        mark.textContent = name;
        mark.style.left = (bar / item.bars) * rollWidth + "px";
        names.appendChild(mark);
        bar += span;
      }});
      const pitches = [...new Set(padNotes.map((note) => note.pitch))].sort((a, b) => b - a);
      const rowH = 36;
      field.style.width = rollWidth + "px";
      field.style.height = Math.max(160, pitches.length * rowH + 20) + "px";
      field.innerHTML = "";
      const seams = boundaries(item);
      seams.forEach((tick) => {{
        const line = document.createElement("div");
        line.className = "seam";
        line.style.left = (tick / container) * rollWidth + "px";
        field.appendChild(line);
      }});
      const head = document.createElement("div");
      head.id = "playhead";
      head.className = "playhead";
      head.style.left = "0px";
      field.appendChild(head);
      const heldNames = [];
      padNotes.forEach((note) => {{
        const end = note.start + note.duration;
        const held = seams.some((tick) => note.start < tick && end > tick);
        if (held) heldNames.push(pitchName(note.pitch));
        const row = pitches.indexOf(note.pitch);
        const block = document.createElement("div");
        block.className = "hold" + (held ? " common" : "");
        block.textContent = pitchName(note.pitch) + (held ? " held" : "");
        block.title = pitchName(note.pitch) + " · velocity " + note.velocity;
        block.dataset.start = String(note.start);
        block.dataset.end = String(end);
        block.style.left = (note.start / container) * rollWidth + "px";
        block.style.width = Math.max(36, (note.duration / container) * rollWidth - 6) + "px";
        block.style.top = (8 + row * rowH) + "px";
        block.style.height = (rowH - 8) + "px";
        field.appendChild(block);
      }});
      const unique = [...new Set(heldNames)];
      document.getElementById("common").textContent = unique.length
        ? "Common tones read from this MIDI file: " + unique.join(", ") + ". Each one is still sounding when a chord changes."
        : "No note in this MIDI file is still sounding when a chord changes.";
      motionList.innerHTML = "";
      motionNotes.forEach((note) => {{
        const li = document.createElement("li");
        const barNumber = Math.floor(note.start / pack.bar_ticks) + 1;
        const beat = Math.floor((note.start % pack.bar_ticks) / 960) + 1;
        const quarters = note.duration / 960;
        li.textContent = "Bar " + barNumber + ", beat " + beat + ", " + pitchName(note.pitch) + ", " + quarters + (quarters === 1 ? " quarter" : " quarters");
        motionList.appendChild(li);
      }});
      status.textContent = padNotes.length + " pad notes from the MIDI. " + motionNotes.length + " inner-motion notes are listed apart from the field.";
    }}
    async function loadStudy() {{
      stopPlayback();
      renderCopy();
      status.textContent = "Reading the MIDI.";
      motionList.innerHTML = "";
      try {{
        const padRes = await fetch(partPath("pad-field"));
        const motionRes = await fetch(partPath("inner-motion"));
        if (!padRes.ok || !motionRes.ok) throw new Error("MIDI request failed");
        padNotes = parseMidi(await padRes.arrayBuffer());
        motionNotes = parseMidi(await motionRes.arrayBuffer());
        draw();
      }} catch (error) {{
        padNotes = [];
        motionNotes = [];
        status.textContent = "The MIDI did not load. " + error.message;
      }}
    }}
    function freq(pitch) {{
      return 440 * Math.pow(2, (pitch - 69) / 12);
    }}
    function schedule(ctx, note, whenOrigin, amount, slow) {{
      const item = study();
      const seconds = (tick) => tick / 960 * item.tempo_us / 1000000;
      const when = whenOrigin + seconds(note.start);
      const duration = Math.max(0.05, seconds(note.duration));
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = slow ? "triangle" : "sine";
      osc.frequency.value = freq(note.pitch);
      const level = amount * (note.velocity / 100);
      const attack = slow ? Math.min(0.08, duration * 0.25) : Math.min(0.02, duration * 0.2);
      gain.gain.setValueAtTime(0.0001, when);
      gain.gain.exponentialRampToValueAtTime(Math.max(0.0002, level), when + attack);
      gain.gain.exponentialRampToValueAtTime(0.0001, when + duration + 0.12);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(when);
      osc.stop(when + duration + 0.13);
    }}
    function stopPlayback() {{
      playing = false;
      cancelAnimationFrame(followId);
      if (audio) audio.close();
      audio = null;
      document.getElementById("play").textContent = "Play pad";
    }}
    function playPad() {{
      if (!padNotes.length) return;
      stopPlayback();
      const ctx = new AudioContext();
      audio = ctx;
      playing = true;
      document.getElementById("play").textContent = "Stop";
      origin = ctx.currentTime + 0.05;
      padNotes.forEach((note) => schedule(ctx, note, origin, 0.05, true));
      if (hearMotion) motionNotes.forEach((note) => schedule(ctx, note, origin, 0.03, false));
      const item = study();
      const container = item.bars * 4 * 60 / item.bpm;
      const follow = () => {{
        if (!playing || !audio) return;
        const elapsed = audio.currentTime - origin;
        const head = document.getElementById("playhead");
        if (head) head.style.left = Math.max(0, Math.min(rollWidth, (elapsed / container) * rollWidth)) + "px";
        if (elapsed < container + 0.2) followId = requestAnimationFrame(follow);
        else stopPlayback();
      }};
      follow();
    }}
    function stepStudy(direction) {{
      const index = pack.studies.findIndex((item) => item.id === studyId);
      studyId = pack.studies[(index + direction + pack.studies.length) % pack.studies.length].id;
      loadStudy();
    }}
    pack.studies.forEach((item) => {{
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.id = item.id;
      button.textContent = item.id.slice(1) + " " + item.title;
      button.addEventListener("click", () => {{ studyId = item.id; loadStudy(); }});
      rail.appendChild(button);
    }});
    document.getElementById("var-a").addEventListener("click", () => {{ variation = "a"; loadStudy(); }});
    document.getElementById("var-b").addEventListener("click", () => {{ variation = "b"; loadStudy(); }});
    document.getElementById("play").addEventListener("click", () => {{ if (playing) stopPlayback(); else playPad(); }});
    document.getElementById("motion-toggle").addEventListener("click", () => {{
      hearMotion = !hearMotion;
      document.getElementById("motion-toggle").setAttribute("aria-pressed", hearMotion ? "true" : "false");
    }});
    window.addEventListener("keydown", (event) => {{
      const tag = document.activeElement && document.activeElement.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      if (event.code === "Space") {{
        if (tag === "BUTTON" || tag === "A" || tag === "VIDEO" || tag === "AUDIO") return;
        event.preventDefault();
        if (playing) stopPlayback(); else playPad();
      }} else if (event.key === "j" || event.key === "J") stepStudy(-1);
      else if (event.key === "k" || event.key === "K") stepStudy(1);
    }});
    loadStudy();
  </script>
</body>
</html>
"""

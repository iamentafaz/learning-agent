from datetime import date
from html import escape
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import webbrowser

from .config import Settings
from .schemas import DailyLesson
from .service import generate_daily_lesson

STYLE = """
:root{color-scheme:light;--ink:#15253a;--muted:#526377;--line:#e4eaf1;--blue:#3268e8;--paper:#f3f6fa;--lav:#eef1ff}*{box-sizing:border-box}body{margin:0;color:var(--ink);background:var(--paper);font:17px/1.7 system-ui,-apple-system,"Segoe UI",Arial,sans-serif}header{display:flex;align-items:center;justify-content:space-between;padding:18px clamp(18px,5vw,64px);background:#fff;border-bottom:1px solid var(--line)}.brand{display:flex;align-items:center;gap:12px;font-weight:750}.mark{display:grid;place-items:center;width:38px;height:38px;border-radius:12px;background:#eaf0ff;color:var(--blue);font-size:20px}.badge{color:#328160;background:#e8f6ef;border-radius:99px;padding:6px 11px;font-size:13px;font-weight:650}main{width:min(1240px,calc(100% - 36px));margin:38px auto}.intro{display:flex;align-items:end;justify-content:space-between;gap:20px;margin-bottom:22px}h1{margin:0;font-size:clamp(32px,4vw,46px);letter-spacing:-.045em;line-height:1.15}.subtitle{margin:8px 0 0;color:var(--muted)}select,button{border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--ink);padding:12px 15px;font:inherit;font-size:16px}select{min-width:185px}button{border-color:var(--blue);background:var(--blue);color:white;font-weight:650;cursor:pointer}button:hover{background:#2455c9}.workspace{display:grid;grid-template-columns:minmax(0,1fr) 280px;gap:18px;align-items:start}.lesson,.side-card{background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:0 8px 28px #192f4a0a}.lesson{padding:clamp(22px,4vw,42px)}.lesson-date{color:var(--muted);font-size:15px}.opening{font-size:20px;max-width:780px;margin:18px 0 28px}.section{border-top:1px solid var(--line);padding:26px 0}.section h2{font-size:26px;letter-spacing:-.02em;margin:0 0 14px}.eyebrow{font-size:14px;text-transform:uppercase;letter-spacing:.1em;color:var(--blue);font-weight:700}.vocab-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}.vocab-card,.question,.worked,.story-copy{background:#f8faff;border:1px solid #e8edf5;border-radius:12px;padding:16px}.vocab-card h3{margin:0 0 3px;font-size:21px}.pron{color:var(--muted);font-size:15px}.vocab-card p{margin:9px 0}.recall{font-size:15px;color:#53657d;border-top:1px solid var(--line);padding-top:9px}.worked{margin:16px 0}.question{margin:10px 0}.question summary{cursor:pointer;font-weight:650}.answer{margin-top:10px;color:#53657d}.story-copy{white-space:pre-wrap;line-height:1.75}.reflection{margin-top:16px}.reflection li{margin:8px 0}.side-card{padding:20px}.side-card h2{margin:0 0 12px;font-size:19px}.side-card p{color:var(--muted);font-size:15px;margin:0 0 14px}.side-card button{width:100%}.hint{margin-top:14px!important;font-size:14px!important}.notice{margin-top:16px;padding:12px 14px;border:1px solid #f2d4ac;border-radius:10px;background:#fff8ee;color:#825012;overflow-wrap:anywhere}.empty{padding:70px 24px;text-align:center;color:var(--muted)}.legacy-block{padding:12px 16px;margin:10px 0;background:#f8faff;border-radius:10px;white-space:pre-wrap}.legacy-block h2{margin:0 0 8px;color:var(--ink)}@media(max-width:820px){.intro{align-items:start;flex-direction:column}.workspace{grid-template-columns:1fr}.vocab-grid{grid-template-columns:1fr}.lesson{padding:22px}}
html,body{height:100%;overflow:hidden}body{display:flex;flex-direction:column}header{flex:0 0 auto}main{flex:1;min-height:0;display:flex;flex-direction:column;margin:0 auto;padding:30px 0;width:min(1240px,calc(100% - 36px))}.intro{flex:0 0 auto}.workspace{flex:1;min-height:0}.lesson{height:100%;min-height:0;overflow-y:auto;overscroll-behavior:contain;scrollbar-gutter:stable}.side-card{position:sticky;top:16px;align-self:start}@media(max-width:820px){main{padding:18px 0}.workspace{grid-template-columns:1fr;grid-template-rows:auto minmax(0,1fr)}.side-card{grid-row:1;position:static}.lesson{grid-row:2;height:100%;min-height:0}}
"""


class _LegacyReader(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[tuple[str, str]] = []
        self.tag: str | None = None
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if self.tag is None and tag in {"h1", "h2", "p", "li"}:
            self.tag, self.parts = tag, []
        elif tag == "br" and self.tag:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self.tag == tag:
            text = "".join(self.parts).strip()
            if text:
                self.blocks.append((tag, text))
            self.tag, self.parts = None, []

    def handle_data(self, data: str) -> None:
        if self.tag:
            self.parts.append(data)


def _lesson_days(output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    days = {p.stem.removeprefix("lesson-") for p in output_dir.glob("lesson-????-??-??.html")}
    days.update(p.stem.removeprefix("lesson-") for p in output_dir.glob("lesson-????-??-??.json"))
    return sorted(days, reverse=True)


def _render_lesson(lesson: DailyLesson, lesson_date: date) -> str:
    vocab = "".join(
        f'<article class="vocab-card"><h3>{escape(item.word.title())}</h3><div class="pron">/{escape(item.pronunciation)}/</div><p>{escape(item.meaning)}</p><p><em>{escape(item.example)}</em></p><div class="recall">Recall: {escape(item.recall_prompt)}</div></article>'
        for item in lesson.vocabulary
    )
    questions = "".join(
        f'<details class="question"><summary>{escape(q.question)}</summary><div class="answer"><strong>Answer:</strong> {escape(q.answer)}<br><strong>Why:</strong> {escape(q.explanation)}</div></details>'
        for q in lesson.maths.questions
    )
    reflection = "".join(f"<li>{escape(item)}</li>" for item in lesson.story.reflection_questions)
    story = escape(lesson.story.story)
    return f'''<div class="lesson-date">{lesson_date.strftime("%A, %d %B %Y")}</div><p class="opening">{escape(lesson.opening)}</p>
<section class="section"><div class="eyebrow">5 minutes · English</div><h2>Vocabulary</h2><div class="vocab-grid">{vocab}</div></section>
<section class="section"><div class="eyebrow">15 minutes · Class 10 maths</div><h2>{escape(lesson.maths.title)}</h2><p>{escape(lesson.maths.explanation)}</p><div class="worked"><strong>Worked example</strong><br>{escape(lesson.maths.worked_example)}</div>{questions}</section>
<section class="section"><div class="eyebrow">{lesson.story.reading_minutes} minutes · Story &amp; puzzle</div><h2>{escape(lesson.story.title)}</h2><div class="story-copy">{story}</div><div class="reflection"><strong>Reflect</strong><ol>{reflection}</ol></div></section>
<p><strong>{escape(lesson.closing)}</strong></p>'''


def _render_legacy(path: Path) -> str:
    parser = _LegacyReader()
    parser.feed(path.read_text(encoding="utf-8"))
    rendered = []
    section_open = False
    for tag, text in parser.blocks:
        safe = escape(text).replace("\n", "<br>")
        if tag == "h1":
            rendered.append(f'<h2>{safe}</h2>')
        elif tag == "h2":
            if section_open:
                rendered.append("</section>")
            rendered.append(f'<section class="section"><h2>{safe}</h2>')
            section_open = True
        elif tag == "p":
            rendered.append(f'<p class="legacy-block">{safe}</p>')
        else:
            rendered.append(f'<div class="legacy-block">{safe}</div>')
    if section_open:
        rendered.append("</section>")
    return "".join(rendered)


def _page(output_dir: Path, selected: str | None, message: str = "") -> bytes:
    days = _lesson_days(output_dir)
    if selected not in days:
        selected = days[0] if days else None
    options = "".join(f'<option value="{day}"{" selected" if day == selected else ""}>{date.fromisoformat(day).strftime("%d %b %Y")}</option>' for day in days)
    selector = f'<form><select name="lesson" aria-label="Saved lessons" onchange="this.form.submit()">{options}</select></form>' if days else ""
    content = '<div class="empty">Generate your first lesson and it will appear here.</div>'
    if selected:
        json_path = output_dir / f"lesson-{selected}.json"
        html_path = output_dir / f"lesson-{selected}.html"
        if json_path.exists():
            lesson = DailyLesson.model_validate_json(json_path.read_text(encoding="utf-8"))
            content = _render_lesson(lesson, date.fromisoformat(selected))
        elif html_path.exists():
            content = _render_legacy(html_path)
    notice = f'<div class="notice">{escape(message)}</div>' if message else ""
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Learning Studio</title><style>{STYLE}</style></head><body><header><div class="brand"><span class="mark">✦</span><span>Learning Studio</span></div><span class="badge">Private · local app</span></header><main><section class="intro"><div><h1>Your learning space</h1><p class="subtitle">Daily lessons in English, maths, and creative thinking.</p></div>{selector}</section><div class="workspace"><article class="lesson">{content}</article><aside class="side-card"><h2>Daily lesson</h2><p>Generate a 30-minute lesson and read it right here.</p><form action="/generate" method="post"><button type="submit">Generate today's lesson</button></form><p class="hint">Uses your configured OpenAI API key. The app does not send email.</p>{notice}</aside></div></main></body></html>'''.encode()


def serve_ui(settings: Settings, host: str = "127.0.0.1", port: int = 8765, open_browser: bool = True) -> None:
    output_dir = settings.output_dir.resolve()

    class Handler(BaseHTTPRequestHandler):
        def _respond(self, status: int, body: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                selected = parse_qs(parsed.query).get("lesson", [None])[0]
                self._respond(200, _page(output_dir, selected))
            else:
                self._respond(404, b"Not found")

        def do_POST(self) -> None:
            if urlparse(self.path).path != "/generate":
                self._respond(404, b"Not found")
                return
            length = int(self.headers.get("Content-Length", "0"))
            if length:
                self.rfile.read(min(length, 4096))
            try:
                path = generate_daily_lesson(settings, send=False, render_html_file=False)
                day = path.stem.removeprefix("lesson-")
                self.send_response(303)
                self.send_header("Location", f"/?lesson={day}")
                self.send_header("Content-Length", "0")
                self.end_headers()
            except Exception as error:
                self._respond(500, _page(output_dir, None, str(error)))

        def log_message(self, format: str, *args) -> None:
            print(f"{self.log_date_time_string()} {format % args}")

    address = f"http://{host}:{port}/"
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Learning Studio is running at {address}")
    print("Keep this terminal open while you use the app. Press Ctrl+C to stop it.")
    if open_browser:
        webbrowser.open(address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLearning Studio stopped.")
    finally:
        server.server_close()




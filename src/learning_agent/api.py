"""Small authenticated HTTP bridge for an n8n instance running in Docker."""
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json

from .config import Settings
from .schemas import DailyLesson
from .service import generate_daily_lesson


def serve_api(settings: Settings, host: str = "0.0.0.0", port: int = 8766) -> None:
    if not settings.api_token:
        raise ValueError("LEARNING_AGENT_API_TOKEN is missing. Set a long random token in .env.")

    class Handler(BaseHTTPRequestHandler):
        def _reply(self, status: int, body: dict) -> None:
            payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:
            if self.path == "/health":
                self._reply(200, {"status": "ok"})
            else:
                self._reply(404, {"error": "Not found"})

        def do_POST(self) -> None:
            if self.path != "/api/generate":
                self._reply(404, {"error": "Not found"})
                return
            supplied = self.headers.get("Authorization", "")
            expected = f"Bearer {settings.api_token}"
            if not hmac.compare_digest(supplied, expected):
                self._reply(401, {"error": "Unauthorized"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 128_000:
                    self._reply(413, {"error": "Request body must be between 1 and 128000 bytes"})
                    return
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError("Expected a JSON object")
                topics = _clean_items(data.get("topic_articles", []))
                vocabulary = _clean_items(data.get("vocabulary_articles", []))
                path = generate_daily_lesson(
                    settings, send=False, render_html_file=False,
                    topic_articles=topics, vocabulary_articles=vocabulary
                )
                lesson = DailyLesson.model_validate_json(path.read_text(encoding="utf-8"))
                from .render import render_html

                self._reply(200, {
                    "date": date.today().isoformat(),
                    "subject_line": lesson.subject_line,
                    "html": render_html(lesson, date.today()),
                    "lesson": lesson.model_dump(mode="json"),
                })
            except (ValueError, json.JSONDecodeError) as error:
                self._reply(400, {"error": str(error)})
            except Exception as error:
                self._reply(500, {"error": str(error)})

        def log_message(self, format: str, *args) -> None:
            print(f"{self.log_date_time_string()} {format % args}")

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Learning Agent API listening at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLearning Agent API stopped.")
    finally:
        server.server_close()


def _clean_items(value) -> list[dict[str, str]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("RSS article fields must be arrays")
    cleaned = []
    for item in value[:30]:
        if not isinstance(item, dict):
            continue
        cleaned.append({
            key: str(item.get(key, ""))[:3000]
            for key in ("title", "summary", "url")
        })
    return cleaned

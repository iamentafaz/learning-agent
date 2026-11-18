import argparse

from .config import get_settings
from .database import initialise_database
from .service import generate_daily_lesson
from .webapp import serve_ui
from .api import serve_api


def main() -> None:
    parser = argparse.ArgumentParser(description="Personal Learning Agent")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init", help="Create the local SQLite database")
    generate = subparsers.add_parser("generate", help="Generate today's lesson")
    mode = generate.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Create HTML but do not send email")
    mode.add_argument("--send", action="store_true", help="Create and email the lesson")
    serve = subparsers.add_parser("serve", help="Open the local lesson library in a browser")
    serve.add_argument("--host", default="127.0.0.1", help="Local address to bind (default: 127.0.0.1)")
    serve.add_argument("--port", type=int, default=8765, help="Port to use (default: 8765)")
    serve.add_argument("--no-browser", action="store_true", help="Do not open a browser automatically")
    api = subparsers.add_parser("api", help="Run the authenticated HTTP API for n8n")
    api.add_argument("--host", default="0.0.0.0", help="Address to bind (default: 0.0.0.0 for Docker access)")
    api.add_argument("--port", type=int, default=8766, help="Port to use (default: 8766)")
    args = parser.parse_args()
    settings = get_settings()
    if args.command == "init":
        initialise_database(settings.database_url)
        print("Database initialised.")
        return
    if args.command == "serve":
        serve_ui(settings, host=args.host, port=args.port, open_browser=not args.no_browser)
        return
    if args.command == "api":
        serve_api(settings, host=args.host, port=args.port)
        return
    path = generate_daily_lesson(settings, send=args.send)
    print(f"Lesson ready: {path}")


if __name__ == "__main__":
    main()

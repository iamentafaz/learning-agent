from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from .config import Settings
from .database import DeliveryLog, initialise_database, make_engine
from .emailer import send_html_email
from .render import render_html
from .schemas import DailyLesson
from .selector import record_lesson_selection, select_due_vocabulary_words, select_maths_topic, select_story, select_vocabulary
from .teacher import build_lesson


def generate_daily_lesson(settings: Settings, send: bool = False, render_html_file: bool = True, *, topic_articles=None, vocabulary_articles=None) -> Path:
    """Generate today's lesson, saving structured JSON and optionally an HTML file."""
    initialise_database(settings.database_url)
    today = date.today()
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = settings.output_dir / f"lesson-{today.isoformat()}.json"
    html_path = settings.output_dir / f"lesson-{today.isoformat()}.html"
    engine = make_engine(settings.database_url)

    with Session(engine) as session:
        existing = session.query(DeliveryLog).filter_by(delivered_on=today).first()
        if existing:
            if json_path.exists():
                lesson = DailyLesson.model_validate_json(json_path.read_text(encoding="utf-8"))
                if render_html_file and not html_path.exists():
                    html = render_html(lesson, today)
                    html_path.write_text(html, encoding="utf-8")
                return html_path if render_html_file else json_path
            return Path(existing.html_path)

        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is missing. Add it to .env before generating a lesson.")
        vocabulary = select_vocabulary(session, today)
        due_words = select_due_vocabulary_words(session, today)
        topic = select_maths_topic(session)
        story = select_story(session)
        lesson = build_lesson(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            learner_name=settings.learner_name,
            vocabulary=vocabulary,
            topic=topic,
            story=story,
            topic_articles=topic_articles,
            vocabulary_articles=vocabulary_articles,
            due_words=due_words,
        )
        json_path.write_text(lesson.model_dump_json(indent=2), encoding="utf-8")
        if render_html_file or send:
            html = render_html(lesson, today)
            html_path.write_text(html, encoding="utf-8")
            if send:
                send_html_email(settings, lesson.subject_line, html)
        selected_vocabulary = [(item.word.lower(), item.meaning, item.example) for item in lesson.vocabulary]
        record_lesson_selection(session, selected_vocabulary, today)
        session.add(DeliveryLog(delivered_on=today, subject=lesson.subject_line, html_path=str(html_path)))
        session.commit()
        return html_path if render_html_file else json_path

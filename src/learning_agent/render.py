from datetime import date
from html import escape

from .schemas import DailyLesson


def render_html(lesson: DailyLesson, lesson_date: date) -> str:
    vocab = "".join(
        f"<li><strong>{escape(item.word.title())}</strong> <em>/{escape(item.pronunciation)}/</em><br>"
        f"{escape(item.meaning)}<br><span>{escape(item.example)}</span><br>"
        f"<small>Recall: {escape(item.recall_prompt)}</small></li>"
        for item in lesson.vocabulary
    )
    questions = "".join(
        f"<li><strong>{escape(q.question)}</strong><details><summary>Check answer</summary>"
        f"{escape(q.answer)}<br>{escape(q.explanation)}</details></li>"
        for q in lesson.maths.questions
    )
    reflections = "".join(f"<li>{escape(question)}</li>" for question in lesson.story.reflection_questions)
    return f"""<!doctype html><html><head><meta charset='utf-8'><style>
body{{font-family:Arial,sans-serif;background:#f6f7fb;color:#1f2937;line-height:1.55;margin:0}}
main{{max-width:680px;margin:24px auto;background:white;padding:32px;border-radius:12px}}
h1{{color:#1d4ed8}} h2{{margin-top:32px;color:#111827}} li{{margin:14px 0}} span,small{{color:#4b5563}}
details{{margin-top:8px;background:#eff6ff;padding:8px;border-radius:6px}} .meta{{color:#6b7280}}
</style></head><body><main>
<h1>Your 30-minute learning session</h1><p class='meta'>{lesson_date.strftime('%A, %d %B %Y')}</p>
<p>{escape(lesson.opening)}</p>
<h2>1. English vocabulary · 5 minutes</h2><ol>{vocab}</ol>
<h2>2. Maths: {escape(lesson.maths.title)} · 15 minutes</h2><p>{escape(lesson.maths.explanation)}</p>
<p><strong>Worked example:</strong> {escape(lesson.maths.worked_example)}</p><ol>{questions}</ol>
<h2>3. {escape(lesson.story.title)} · {lesson.story.reading_minutes} minutes</h2>
<p>{escape(lesson.story.story).replace(chr(10), '<br>')}</p><p><strong>Reflect:</strong></p><ol>{reflections}</ol>
<hr><p>{escape(lesson.closing)}</p></main></body></html>"""

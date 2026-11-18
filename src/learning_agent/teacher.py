import json

from openai import OpenAI

from .schemas import DailyLesson


SYSTEM_PROMPT = """You are a warm, precise personal teacher for an adult learner in India.
Create exactly a 30-minute daily lesson: 5 minutes vocabulary, 15 minutes Class 10 maths,
and 10 minutes an original brain-stimulating story or puzzle. Use clear English, never talk
down to the learner, and keep the maths rigorous. Do not claim a story is factual or copied.
Return only JSON that follows the supplied schema."""


def build_lesson(*, api_key: str, model: str, learner_name: str, vocabulary, topic, story, topic_articles=None, vocabulary_articles=None, due_words=None) -> DailyLesson:
    due_words = due_words or set()
    vocab_text = "\n".join(
        f"- {word}: {meaning}; example seed: {example}" + (" [due for review]" if word in due_words else "")
        for word, meaning, example in vocabulary
    )
    title, genre, story_seed = story
    user_prompt = f"""Learner: {learner_name}

Vocabulary to teach (use exactly these three):
{vocab_text}

Maths topic: {topic.title}
Maths focus: {topic.focus}
Teach one small concept suitable for a 15-minute session. Include one worked example and 2-3
progressive questions with correct, concise solutions.

Story title: {title}
Genre: {genre}
Original-story seed: {story_seed}
Write a 5-10 minute original story or puzzle, then include reflection questions. Avoid graphic,
disturbing or copyrighted material."""

    if topic_articles or vocabulary_articles:
        topic_text = "\n".join(
            f"- {item.get('title', '')}: {item.get('summary', '')} ({item.get('url', '')})"
            for item in (topic_articles or [])[:12]
        ) or "No topic articles supplied."
        word_text = "\n".join(
            f"- {item.get('title', '')}: {item.get('summary', '')}"
            for item in (vocabulary_articles or [])[:12]
        ) or "No vocabulary feed items supplied."
        user_prompt += f"""

Optional RSS material supplied by the learner's n8n workflow:
Learning-topic articles:
{topic_text}

Vocabulary-feed items:
{word_text}

Use topic articles as timely examples or story inspiration when relevant, while keeping the
assigned Class 10 maths topic and accuracy. For vocabulary, due review words take priority. A
clear candidate word in a vocabulary RSS item may replace a not-yet-due seed word; use the RSS
word exactly and write its meaning, pronunciation, example, and recall prompt. Do not invent facts
from article snippets."""

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "daily_lesson",
                "strict": True,
                "schema": DailyLesson.model_json_schema(),
            }
        },
    )
    return DailyLesson.model_validate(json.loads(response.output_text))

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .content import MATHS_CURRICULUM, STORY_PROMPTS, VOCABULARY, MathTopic
from .database import LearningState, VocabularyReview


def select_maths_topic(session: Session) -> MathTopic:
    state = session.scalar(select(LearningState).limit(1))
    assert state is not None
    return MATHS_CURRICULUM[state.maths_topic_index % len(MATHS_CURRICULUM)]


def select_vocabulary(session: Session, today: date) -> list[tuple[str, str, str]]:
    due_words = set(session.scalars(
        select(VocabularyReview.word).where(VocabularyReview.next_review_on <= today)
    ).all())
    ordered = [item for item in VOCABULARY if item[0] in due_words]
    ordered.extend(item for item in VOCABULARY if item[0] not in due_words)
    return ordered[:3]


def select_due_vocabulary_words(session: Session, today: date) -> set[str]:
    return set(session.scalars(
        select(VocabularyReview.word).where(VocabularyReview.next_review_on <= today)
    ).all())


def select_story(session: Session):
    state = session.scalar(select(LearningState).limit(1))
    assert state is not None
    return STORY_PROMPTS[state.lesson_count % len(STORY_PROMPTS)]


def record_lesson_selection(session: Session, vocabulary: list[tuple[str, str, str]], today: date) -> None:
    intervals = [1, 3, 7, 14, 30]
    for word, _, _ in vocabulary:
        review = session.scalar(select(VocabularyReview).where(VocabularyReview.word == word))
        if review is None:
            review = VocabularyReview(word=word, times_seen=0, next_review_on=today)
            session.add(review)
        review.times_seen += 1
        review.next_review_on = today + timedelta(days=intervals[min(review.times_seen - 1, len(intervals) - 1)])

    state = session.scalar(select(LearningState).limit(1))
    assert state is not None
    state.lesson_count += 1
    state.maths_topic_index = (state.maths_topic_index + 1) % len(MATHS_CURRICULUM)

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class LearningState(Base):
    __tablename__ = "learning_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    maths_topic_index: Mapped[int] = mapped_column(Integer, default=0)
    lesson_count: Mapped[int] = mapped_column(Integer, default=0)


class VocabularyReview(Base):
    __tablename__ = "vocabulary_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    word: Mapped[str] = mapped_column(String(100), unique=True)
    times_seen: Mapped[int] = mapped_column(Integer, default=0)
    next_review_on: Mapped[date] = mapped_column(Date)


class DeliveryLog(Base):
    __tablename__ = "delivery_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    delivered_on: Mapped[date] = mapped_column(Date, unique=True)
    subject: Mapped[str] = mapped_column(String(255))
    html_path: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def make_engine(database_url: str):
    return create_engine(database_url)


def initialise_database(database_url: str) -> None:
    engine = make_engine(database_url)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        if session.scalar(select(LearningState).limit(1)) is None:
            session.add(LearningState())
            session.commit()

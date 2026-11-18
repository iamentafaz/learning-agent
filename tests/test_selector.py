from datetime import date

from sqlalchemy.orm import Session

from learning_agent.database import initialise_database, make_engine
from learning_agent.selector import record_lesson_selection, select_maths_topic, select_story, select_vocabulary


def test_selection_and_progression(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'test.db'}"
    initialise_database(database_url)
    with Session(make_engine(database_url)) as session:
        vocab = select_vocabulary(session, date(2026, 10, 30))
        assert len(vocab) == 3
        assert select_maths_topic(session).title == "Real Numbers"
        assert select_story(session)[0] == "The Missing Minute"
        record_lesson_selection(session, vocab, date(2026, 10, 30))
        session.commit()
    with Session(make_engine(database_url)) as session:
        assert select_maths_topic(session).title == "Polynomials"

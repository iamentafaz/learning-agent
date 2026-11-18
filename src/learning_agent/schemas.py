from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class VocabularyLesson(StrictModel):
    word: str
    pronunciation: str
    meaning: str
    example: str
    recall_prompt: str


class MathQuestion(StrictModel):
    question: str
    answer: str
    explanation: str


class MathLesson(StrictModel):
    title: str
    explanation: str
    worked_example: str
    questions: list[MathQuestion] = Field(min_length=2, max_length=3)


class StoryLesson(StrictModel):
    title: str
    reading_minutes: int = Field(ge=5, le=10)
    story: str
    reflection_questions: list[str] = Field(min_length=2, max_length=3)


class DailyLesson(StrictModel):
    subject_line: str
    opening: str
    vocabulary: list[VocabularyLesson] = Field(min_length=3, max_length=3)
    maths: MathLesson
    story: StoryLesson
    closing: str

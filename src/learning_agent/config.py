from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    learner_name: str
    recipient_email: str | None
    smtp_host: str | None
    smtp_port: int
    smtp_username: str | None
    smtp_password: str | None
    smtp_from_email: str | None
    database_url: str
    output_dir: Path
    api_token: str | None


def get_settings() -> Settings:
    load_dotenv()
    root = Path.cwd()
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-6-luna"),
        learner_name=os.getenv("LEARNER_NAME", "Learner"),
        recipient_email=os.getenv("RECIPIENT_EMAIL"),
        smtp_host=os.getenv("SMTP_HOST"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_username=os.getenv("SMTP_USERNAME"),
        smtp_password=os.getenv("SMTP_PASSWORD"),
        smtp_from_email=os.getenv("SMTP_FROM_EMAIL"),
        database_url="sqlite:///learning.db",
        output_dir=root / "output",
        api_token=os.getenv("LEARNING_AGENT_API_TOKEN"),
    )

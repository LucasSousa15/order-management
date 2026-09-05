from dataclasses import dataclass
from os import getenv
from pathlib import Path

from dotenv import load_dotenv


ROOT_ENV_FILE = Path(__file__).resolve().parents[5] / ".env"


@dataclass(frozen=True, slots=True)
class DatabaseSettings:
    url: str


def load_database_settings() -> DatabaseSettings:
    load_dotenv(dotenv_path=ROOT_ENV_FILE, override=False)

    database_url = getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL must be set in the root .env file "
            "or in the process environment."
        )

    return DatabaseSettings(url=database_url)


database_settings = load_database_settings()

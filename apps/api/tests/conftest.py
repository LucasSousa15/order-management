from os import environ, getenv
from pathlib import Path

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from sqlalchemy.engine import make_url


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ALEMBIC_CONFIG_FILE = PROJECT_ROOT / "alembic.ini"


def configure_test_database() -> str:
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    development_database_url = getenv("DATABASE_URL")
    test_database_url = getenv("TEST_DATABASE_URL")

    if not test_database_url:
        raise RuntimeError("TEST_DATABASE_URL must be set to run the test suite.")

    database_name = make_url(test_database_url).database
    if not database_name or not database_name.endswith("_test"):
        raise RuntimeError("The test database name must end with '_test'.")

    if test_database_url == development_database_url:
        raise RuntimeError("Test and development database URLs must be different.")

    environ["DATABASE_URL"] = test_database_url
    return test_database_url


configure_test_database()


def pytest_sessionstart() -> None:
    alembic_config = Config(str(ALEMBIC_CONFIG_FILE))
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")

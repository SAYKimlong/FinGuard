import pytest
from pydantic import ValidationError

from app.config import Settings


def production_settings(**overrides):
    values = {
        "APP_ENV": "production",
        "DEBUG": False,
        "SECRET_KEY": "test-only-random-secret-value-with-more-than-32-chars",
        "DATABASE_URL": "postgresql+asyncpg://prod_user:unique-password@db.example.invalid/finguard",
        "DATABASE_URL_SYNC": "postgresql+psycopg://prod_user:unique-password@db.example.invalid/finguard",
    }
    values.update(overrides)
    return Settings(**values)


def test_production_configuration_accepts_unique_secret_and_database_credentials():
    settings = production_settings()
    assert settings.APP_ENV == "production"
    assert settings.DEBUG is False


@pytest.mark.parametrize(
    "overrides",
    [
        {"SECRET_KEY": "change-me-to-a-random-secret-key"},
        {"SECRET_KEY": "short"},
        {"DEBUG": True},
        {"DATABASE_URL": "postgresql+asyncpg://finguard:finguard@localhost:5555/finguard"},
        {"DATABASE_URL_SYNC": "postgresql+psycopg://finguard:finguard@localhost:5555/finguard"},
    ],
)
def test_production_configuration_rejects_known_unsafe_defaults(overrides):
    with pytest.raises(ValidationError):
        production_settings(**overrides)

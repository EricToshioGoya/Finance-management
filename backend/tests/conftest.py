import os
import subprocess
import uuid
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.config import Settings
from app.main import create_app


@pytest.fixture(scope="session")
def application():
    """A real isolated PostgreSQL database; never truncate the development DB."""
    settings = Settings()
    database_name = "finnova_test_" + uuid.uuid4().hex
    original = make_url(settings.database_url.get_secret_value())
    admin = create_engine(original.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    url = original.set(database=database_name).render_as_string(hide_password=False)
    test_settings = settings.model_copy(update={"database_url": type(settings.database_url)(url)})
    try:
        subprocess.run(
            ["alembic", "upgrade", "head"],
            check=True,
            env={**os.environ, "FINNOVA_DATABASE_URL": url},
            capture_output=True,
        )
        app = create_app(test_settings)
        yield app
        app.state.engine.dispose()
    finally:
        with admin.connect() as connection:
            connection.execute(text(f'DROP DATABASE "{database_name}" WITH (FORCE)'))
        admin.dispose()


@pytest.fixture
def app(application):
    application.state.clock = lambda: datetime.now(UTC)
    with application.state.engine.begin() as db:
        db.execute(
            text(
                "TRUNCATE users, auth_sessions, refresh_tokens, auth_rate_buckets, "
                "auth_login_attempts CASCADE"
            )
        )
    return application


@pytest.fixture
def client(app):
    with TestClient(app, base_url="https://localhost:8443") as instance:
        yield instance

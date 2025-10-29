from __future__ import annotations

from collections.abc import Iterator
import os

os.environ.setdefault("POSTGRES_URL", "sqlite+pysqlite:///./tests.db")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from apps.api.db.base import Base
from apps.api.db.session import SessionLocal, engine, get_session
from apps.api.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_database() -> Iterator[None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_tables() -> Iterator[None]:
    yield
    table_names = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables)
    if not table_names:
        return
    with engine.begin() as connection:
        if engine.dialect.name == "sqlite":
            for table in Base.metadata.sorted_tables:
                connection.execute(text(f'DELETE FROM "{table.name}"'))
        else:
            connection.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))


@pytest.fixture()
def db_session() -> Iterator[Session]:
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session) -> Iterator[TestClient]:  # type: ignore[override]
    def override_get_session() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

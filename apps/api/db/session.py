from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from apps.api.config import settings

engine_kwargs: dict[str, object] = {"pool_pre_ping": True}
connect_args: dict[str, object] = {}

if settings.postgres_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    if settings.postgres_url.endswith(":memory:"):
        engine_kwargs["poolclass"] = StaticPool

engine = create_engine(settings.postgres_url, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

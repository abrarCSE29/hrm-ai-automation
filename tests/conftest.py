import os

os.environ.setdefault("ENVIRONMENT", "dev")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("GROQ_API_KEY", "test-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

settings.DATABASE_URL = "sqlite:///:memory:"

import app.db.session as db_session
import app.tools.execution as exec_mod

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, future=True)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

db_session.engine = engine
db_session.SessionLocal = TestingSessionLocal
exec_mod.SessionLocal = TestingSessionLocal

import app.db.models  # noqa: F401
from app.db.base import Base

Base.metadata.create_all(bind=engine)


import pytest


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # clean tables
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()


@pytest.fixture(autouse=True)
def _clean_tables():
    session = TestingSessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()
    yield

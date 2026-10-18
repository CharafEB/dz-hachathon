"""
conftest.py — shared pytest fixtures that ensure each test module gets its own
               independent in-memory SQLite database, preventing cross-module
               dependency-override conflicts.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from database import Base, get_db
from api import app


@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client(db_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

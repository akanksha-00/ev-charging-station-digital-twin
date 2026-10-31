import pytest
from fastapi.testclient import TestClient
from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import Session

from database import database_url, get_db
from main import app


@pytest.fixture(scope="session")
def test_engine():
    test_url = database_url.set(database="ev_charging_twin_test")
    engine = create_engine(test_url, pool_pre_ping=True)

    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def client(test_engine):
    with test_engine.connect() as connection:
        transaction = connection.begin()

        def override_get_db():
            with Session(
                bind=connection,
                join_transaction_mode="create_savepoint",
            ) as session:
                yield session
        
        app.dependency_overrides[get_db] = override_get_db
        
        try:
            with TestClient(app) as test_client:
                yield test_client
        finally:
            app.dependency_overrides.pop(get_db, None)
            transaction.rollback()
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.models import User
from app.auth import get_current_user, require_officer, require_citizen_or_officer
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestingSessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def mock_officer():
    return User(
        id="test-officer-uuid",
        username="officer_test",
        display_name="Inspector Sharma",
        password_hash="fakehash",
        role="officer",
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )

@pytest.fixture(scope="function")
def client(db_session, mock_officer):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: mock_officer
    app.dependency_overrides[require_officer] = lambda: mock_officer
    app.dependency_overrides[require_citizen_or_officer] = lambda: mock_officer

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

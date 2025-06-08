import sys
import os
# Add the project's root directory (backend) to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sa
from sqlalchemy.exc import ProgrammingError

from app.main import app
from app.api import deps
from app.db.session import Base

# --- Test Database Setup ---
# Use a separate database for testing
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://forest_user:forest_password@localhost:5432/forest_carbon_db_test")

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    
    with engine.connect() as connection:
        # Manually create schemas for postgres
        connection.execute(sa.schema.CreateSchema("user_mgmt", if_not_exists=True))
        connection.execute(sa.schema.CreateSchema("project_mgmt", if_not_exists=True))
        connection.execute(sa.schema.CreateSchema("carbon_mgmt", if_not_exists=True))
        connection.execute(sa.schema.CreateSchema("p2p_marketplace", if_not_exists=True))
        connection.execute(sa.schema.CreateSchema("analytics", if_not_exists=True))
        
        # Enable PostGIS extension
        try:
            connection.execute(sa.text("CREATE EXTENSION IF NOT EXISTS postgis"))
        except ProgrammingError:
            # may already be there in template1
            pass
        connection.commit()

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

# --- Fixture to override get_db dependency ---
@pytest.fixture(scope="function", autouse=True)
def override_get_db(db_session):
    def _override_get_db():
            yield db_session

    app.dependency_overrides[deps.get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def test_user(db_session):
    from app import crud, models
    from app.schemas import UserCreate
    import uuid

    email = "test@example.com"
    user_id = uuid.uuid4()
    
    user = crud.user.get_by_email(db_session, email=email)
    if not user:
         user = crud.user.create_from_auth0(db_session, user_in=models.User(id=user_id, email=email))
    
    return user

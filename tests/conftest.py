import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sqlalchemy as sa
from sqlalchemy.exc import ProgrammingError

from app.main import app
from app.api import deps
from app.db.session import Base

# --- Test Database Setup ---
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql://forest_user:forest_password@localhost:5432/forest_carbon_db_test")

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    
    with engine.connect() as connection:
        connection.execute(sa.schema.CreateSchema("user_mgmt", if_not_exists=True))
        connection.execute(sa.schema.CreateSchema("project_mgmt", if_not_exists=True))
        connection.execute(sa.schema.CreateSchema("carbon_mgmt", if_not_exists=True))
        connection.execute(sa.schema.CreateSchema("p2p_marketplace", if_not_exists=True))
        connection.execute(sa.schema.CreateSchema("analytics", if_not_exists=True))
        
        try:
            connection.execute(sa.text("CREATE EXTENSION IF NOT EXISTS postgis"))
        except ProgrammingError:
            pass # Extension may already exist
        
        # Use commit with newer SQLAlchemy versions
        if hasattr(connection, 'commit'):
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
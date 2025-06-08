from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import schemas, models
from unittest.mock import MagicMock
import uuid

def test_get_user_me(client: TestClient, db_session: Session, monkeypatch):
    # Mock the get_current_user dependency to return a test user
    mock_user_id = uuid.uuid4()
    mock_user = models.User(id=mock_user_id, email="test@example.com", is_active=True)
    
    def mock_get_current_user():
        return mock_user

    monkeypatch.setattr("app.api.deps.get_current_user", mock_get_current_user)
    
    response = client.get("/api/v1/users/me")
    
    assert response.status_code == 200
    user = schemas.User(**response.json())
    assert user.email == mock_user.email
    assert user.id == mock_user.id

def test_create_project_for_user(client: TestClient, db_session: Session, monkeypatch):
    # Mock the get_current_user dependency
    creator_id = uuid.uuid4()
    mock_user = models.User(id=creator_id, email="creator@example.com", is_active=True)
    
    # We need to add the user to the session for the test to work
    db_session.add(mock_user)
    db_session.commit()

    def mock_get_current_user():
        return mock_user
    
    monkeypatch.setattr("app.api.deps.get_current_user", mock_get_current_user)

    project_in = {"name": "Test Project", "project_type": "Forestry"}
    response = client.post("/api/v1/projects/", json=project_in)
    
    assert response.status_code == 200
    project = schemas.Project(**response.json())
    assert project.name == "Test Project"
    assert project.owner_id == mock_user.id 
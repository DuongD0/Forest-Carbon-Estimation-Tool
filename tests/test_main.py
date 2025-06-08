from fastapi.testclient import TestClient

def test_read_root(client: TestClient):
    """
    Test that the root endpoint returns a successful response.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Forest Carbon Credit Estimation Tool API. Docs at /docs or /redoc."} 
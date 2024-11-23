from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_serve_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    
def test_get_completion():
    response = client.get("/chatprompt/?user_prompt=Hello from testing")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_get_places():
    response = client.get("/get_places/")
    assert response.status_code == 200






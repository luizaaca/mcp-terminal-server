
import pytest
from mcp.server.fastmcp import TestClient
import uuid

from mcp_terminal_server.mcp.server import mcp_server

client = TestClient(mcp_server)

@pytest.mark.asyncio
async def test_create_session():
    session_id = str(uuid.uuid4())
    response = client.post("/create_session", json={"session_id": session_id})
    assert response.status_code == 200
    assert response.json()["session_id"] == session_id

@pytest.mark.asyncio
async def test_execute_command():
    session_id = str(uuid.uuid4())
    client.post("/create_session", json={"session_id": session_id})

    with client.websocket_connect(f"/execute_command?command=echo%20hello&session_id={session_id}") as websocket:
        response = websocket.receive_json()
        assert "hello" in response

@pytest.mark.asyncio
async def test_change_directory():
    session_id = str(uuid.uuid4())
    client.post("/create_session", json={"session_id": session_id})
    response = client.post("/change_directory", json={"path": "src", "session_id": session_id})
    assert response.status_code == 200
    assert "src" in response.json()["current_directory"]

@pytest.mark.asyncio
async def test_get_current_directory():
    session_id = str(uuid.uuid4())
    client.post("/create_session", json={"session_id": session_id})
    response = client.post("/get_current_directory", json={"session_id": session_id})
    assert response.status_code == 200
    assert response.json()["current_directory"] is not None

@pytest.mark.asyncio
async def test_get_command_history():
    session_id = str(uuid.uuid4())
    client.post("/create_session", json={"session_id": session_id})
    with client.websocket_connect(f"/execute_command?command=echo%20history_test&session_id={session_id}") as websocket:
        websocket.receive_json()

    response = client.post("/get_command_history", json={"session_id": session_id})
    assert response.status_code == 200
    history = response.json()["history"]
    assert isinstance(history, list)
    assert len(history) > 0
    assert "history_test" in history[0]["command"]

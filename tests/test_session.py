import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from src.mcp_terminal_server.core.session import SessionManager, Session


@pytest.fixture
def session_manager():
    return SessionManager()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


def test_create_and_get_session(session_manager):
    session = session_manager.create_session("session-1")
    assert isinstance(session, Session)
    assert session_manager.get_session("session-1") == session


def test_create_session_with_auto_id(session_manager):
    session1 = session_manager.create_session()
    session2 = session_manager.create_session()

    assert session1.session_id != session2.session_id
    assert session1.session_id in session_manager.sessions
    assert session2.session_id in session_manager.sessions


def test_get_nonexistent_session(session_manager):
    assert session_manager.get_session("nonexistent") is None


def test_session_initialization():
    session = Session("test-session")

    assert session.session_id == "test-session"
    assert session.current_working_directory == Path.cwd()
    assert isinstance(session.environment_variables, dict)
    assert len(session.active_processes) == 0
    assert session.websocket is None


def test_active_processes_management(session_manager):
    session = session_manager.create_session("session-process")

    # Add mock process
    mock_process = Mock()
    session.active_processes["cmd_123"] = mock_process

    assert len(session.active_processes) == 1
    assert session.active_processes["cmd_123"] == mock_process

    # Remove process
    del session.active_processes["cmd_123"]
    assert len(session.active_processes) == 0


@pytest.mark.asyncio
async def test_close_session_with_active_processes(session_manager):
    session = session_manager.create_session("session-close")

    # Add mock process
    mock_process = AsyncMock()
    session.active_processes["cmd_123"] = mock_process

    # Close session
    session_manager.close_session("session-close")

    # Verify terminate was called
    mock_process.terminate.assert_called_once()

    # Verify session was removed
    assert session_manager.get_session("session-close") is None


def test_close_nonexistent_session(session_manager):
    # Should not raise when closing a nonexistent session
    session_manager.close_session("nonexistent")
    # Test passes if no exception is raised

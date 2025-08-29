import pytest
import asyncio
import platform
from pathlib import Path
from unittest.mock import patch, AsyncMock

from src.mcp_terminal_server.core.executor import CommandExecutor
from src.mcp_terminal_server.core.session import Session


@pytest.fixture
def executor():
    """Fixture to create a CommandExecutor instance."""
    return CommandExecutor()


@pytest.fixture
def test_session(tmp_path):
    """Fixture to create a test session."""
    session = Session("test-session", str(tmp_path))
    return session


@pytest.mark.asyncio
async def test_execute_simple_command(executor, test_session):
    """Tests execution of a simple command."""
    exit_code, output = await executor.execute_command("echo 'Hello World'", test_session)

    assert exit_code == 0
    assert "Hello World" in output


@pytest.mark.asyncio
async def test_execute_command_with_error(executor, test_session):
    """Tests execution of a command that returns an error."""
    # Command that fails (exit code != 0)
    exit_code, output = await executor.execute_command("exit 1", test_session)

    assert exit_code == 1


@pytest.mark.asyncio
async def test_execute_command_with_stderr(executor, test_session):
    """Tests capturing standard error output."""
    if platform.system() == "Windows":
        command = 'echo "Error message" 1>&2'
    else:
        command = 'echo "Error message" >&2'

    exit_code, output = await executor.execute_command(command, test_session)

    assert exit_code == 0
    assert "Error message" in output
    assert "[STDERR]" in output


@pytest.mark.asyncio
async def test_invalid_command(executor, test_session):
    """Tests execution of an invalid command."""
    exit_code, output = await executor.execute_command("invalid_command_xyz", test_session)

    # Invalid command should return an error code
    assert exit_code != 0
    assert "invalid_command_xyz" in output or "not found" in output or "not recognized" in output


@pytest.mark.asyncio
async def test_process_registration_and_cleanup(executor, test_session):
    """Tests processes are registered and removed correctly from the session."""
    # Ensure there are no active processes initially
    assert len(test_session.active_processes) == 0

    # Execute command
    await executor.execute_command("echo 'test'", test_session)

    # After execution, there should be no active processes
    assert len(test_session.active_processes) == 0


@pytest.mark.asyncio
async def test_read_stream_with_none():
    """Tests the _read_stream method with stream None."""
    executor = CommandExecutor()

    result = await executor._read_stream(None)
    assert result == b""


@pytest.mark.asyncio
async def test_read_stream_with_data():
    """Tests the _read_stream method with data."""
    executor = CommandExecutor()

    # Create a StreamReader mock
    mock_stream = AsyncMock()
    mock_stream.read.return_value = b"test data"

    result = await executor._read_stream(mock_stream)

    assert result == b"test data"
    mock_stream.read.assert_called_once()

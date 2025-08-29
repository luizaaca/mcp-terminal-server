import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_execute_command_success(mocker):
    """
    Tests successful execution of a non-destructive command.
    """
    # Arrange: Set up initial state and mocks
    command = "dir"
    session_id = "test-session-1"
    mock_session = MagicMock()
    expected_output = "file1.txt\ndirectory1"

    # Mock external dependencies to isolate the function under test
    mock_get_session = mocker.patch("mcp_terminal_server.main.session_manager.get_session", return_value=mock_session)
    mock_create_session = mocker.patch("mcp_terminal_server.main.session_manager.create_session")
    mock_needs_confirmation = mocker.patch("mcp_terminal_server.main.security_manager.needs_confirmation", return_value=False)
    mock_execute = mocker.patch("mcp_terminal_server.main.executor.execute_command", new_callable=AsyncMock, return_value=(0, expected_output))

    # Import the function to test *after* applying the patches
    from mcp_terminal_server.main import execute_command

    # Act: Execute the function
    result = await execute_command(command, session_id)

    # Assert: Verify the result and interactions are correct
    mock_get_session.assert_called_once_with(session_id)
    mock_create_session.assert_not_called()
    mock_needs_confirmation.assert_called_once_with(command)
    mock_execute.assert_awaited_once_with(command, mock_session)
    assert result == f"Exit Code: 0\nOutput:\n{expected_output}"


@pytest.mark.asyncio
async def test_execute_command_creates_new_session(mocker):
    """
    Tests that a new session is created when one does not exist.
    """
    # Arrange
    command = "dir"
    session_id = "new-session-id"
    mock_session = MagicMock()
    expected_output = "file1.txt"

    mocker.patch("mcp_terminal_server.main.session_manager.get_session", return_value=None)
    mock_create_session = mocker.patch("mcp_terminal_server.main.session_manager.create_session", return_value=mock_session)
    mocker.patch("mcp_terminal_server.main.security_manager.needs_confirmation", return_value=False)
    mock_execute = mocker.patch("mcp_terminal_server.main.executor.execute_command", new_callable=AsyncMock, return_value=(0, expected_output))

    from mcp_terminal_server.main import execute_command

    # Act
    result = await execute_command(command, session_id)

    # Assert
    mock_create_session.assert_called_once_with(session_id)
    mock_execute.assert_awaited_once_with(command, mock_session)
    assert result == f"Exit Code: 0\nOutput:\n{expected_output}"


@pytest.mark.asyncio
async def test_execute_command_destructive_blocked(mocker):
    """
    Tests that a destructive command is blocked if confirmation fails.
    """
    # Arrange
    command = "del *.tmp"
    session_id = "test-session-2"
    mock_session = MagicMock()
    confirmation_message = "Confirmation required for destructive command."

    mocker.patch("mcp_terminal_server.main.session_manager.get_session", return_value=mock_session)
    mock_confirm_command = mocker.patch("mcp_terminal_server.main.security_manager.confirm_command", return_value=(False, confirmation_message))
    mock_needs_confirmation = mocker.patch("mcp_terminal_server.main.security_manager.needs_confirmation", return_value=True)
    mock_execute = mocker.patch("mcp_terminal_server.main.executor.execute_command", new_callable=AsyncMock)

    from mcp_terminal_server.main import execute_command

    # Act
    result = await execute_command(command, session_id)

    # Assert
    mock_needs_confirmation.assert_called_once_with(command)
    mock_confirm_command.assert_called_once_with(command)
    mock_execute.assert_not_awaited()
    assert result == confirmation_message
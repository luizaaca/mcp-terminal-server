import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path
import tempfile

from src.mcp_terminal_server.main import execute_command, security_manager, session_manager, executor


@pytest.fixture
def mock_session():
    """Cria uma sessão mock para testes."""
    session = MagicMock()
    session.session_id = "test-session"
    return session


@pytest.fixture
def mock_security_manager():
    """Cria um SecurityManager mock que não requer confirmação."""
    security = MagicMock()
    security.needs_confirmation.return_value = False
    return security


@pytest.mark.asyncio
async def test_execute_command_success(mock_session):
    """Testa execução bem-sucedida de comando."""
    with patch('src.mcp_terminal_server.main.session_manager') as mock_session_mgr, \
         patch('src.mcp_terminal_server.main.security_manager') as mock_security_mgr, \
         patch('src.mcp_terminal_server.main.executor') as mock_executor:

        # Setup mocks
        mock_session_mgr.get_session.return_value = mock_session
        mock_security_mgr.needs_confirmation.return_value = False
        mock_executor.execute_command.return_value = (0, "Command output")

        # Execute
        result = await execute_command("echo 'test'", "test-session")

        # Verify
        assert "code 0" in result
        assert "Command output" in result
        mock_session_mgr.get_session.assert_called_with("test-session")
        mock_executor.execute_command.assert_called_with("echo 'test'", mock_session)


@pytest.mark.asyncio
async def test_execute_command_new_session():
    """Testa criação de nova sessão quando não existe."""
    with patch('src.mcp_terminal_server.main.session_manager') as mock_session_mgr, \
         patch('src.mcp_terminal_server.main.security_manager') as mock_security_mgr, \
         patch('src.mcp_terminal_server.main.executor') as mock_executor:

        # Setup mocks
        new_session = MagicMock()
        new_session.session_id = "new-session"
        mock_session_mgr.get_session.return_value = None
        mock_session_mgr.create_session.return_value = new_session
        mock_security_mgr.needs_confirmation.return_value = False
        mock_executor.execute_command.return_value = (0, "New session output")

        # Execute
        result = await execute_command("ls", "new-session")

        # Verify
        assert "code 0" in result
        mock_session_mgr.create_session.assert_called_with("new-session")
        mock_executor.execute_command.assert_called_with("ls", new_session)


@pytest.mark.asyncio
async def test_execute_command_requires_confirmation_approved():
    """Testa comando que requer confirmação e é aprovado."""
    with patch('src.mcp_terminal_server.main.session_manager') as mock_session_mgr, \
         patch('src.mcp_terminal_server.main.security_manager') as mock_security_mgr, \
         patch('src.mcp_terminal_server.main.executor') as mock_executor:

        # Setup mocks
        mock_session_mgr.get_session.return_value = MagicMock()
        mock_security_mgr.needs_confirmation.return_value = True
        mock_security_mgr.confirm_command.return_value = (True, "Approved")
        mock_executor.execute_command.return_value = (0, "Confirmed command output")

        # Execute
        result = await execute_command("sudo rm -rf /", "test-session")

        # Verify
        assert "code 0" in result
        mock_security_mgr.confirm_command.assert_called_with("sudo rm -rf /")


@pytest.mark.asyncio
async def test_execute_command_requires_confirmation_denied():
    """Testa comando que requer confirmação e é negado."""
    with patch('src.mcp_terminal_server.main.session_manager') as mock_session_mgr, \
         patch('src.mcp_terminal_server.main.security_manager') as mock_security_mgr:

        # Setup mocks
        mock_session_mgr.get_session.return_value = MagicMock()
        mock_security_mgr.needs_confirmation.return_value = True
        mock_security_mgr.confirm_command.return_value = (False, "Access denied")

        # Execute
        result = await execute_command("sudo reboot", "test-session")

        # Verify
        assert "Access denied" in result
        assert "sudo reboot" not in result  # Command should not be executed


@pytest.mark.asyncio
async def test_execute_command_with_error():
    """Testa execução de comando que retorna erro."""
    with patch('src.mcp_terminal_server.main.session_manager') as mock_session_mgr, \
         patch('src.mcp_terminal_server.main.security_manager') as mock_security_mgr, \
         patch('src.mcp_terminal_server.main.executor') as mock_executor:

        # Setup mocks
        mock_session_mgr.get_session.return_value = MagicMock()
        mock_security_mgr.needs_confirmation.return_value = False
        mock_executor.execute_command.return_value = (1, "Error: Command failed")

        # Execute
        result = await execute_command("invalid_command", "test-session")

        # Verify
        assert "code 1" in result
        assert "Command failed" in result


@pytest.mark.asyncio
async def test_execute_command_with_stderr():
    """Testa comando que produz saída de erro."""
    with patch('src.mcp_terminal_server.main.session_manager') as mock_session_mgr, \
         patch('src.mcp_terminal_server.main.security_manager') as mock_security_mgr, \
         patch('src.mcp_terminal_server.main.executor') as mock_executor:

        # Setup mocks
        mock_session_mgr.get_session.return_value = MagicMock()
        mock_security_mgr.needs_confirmation.return_value = False
        mock_executor.execute_command.return_value = (0, "Normal output\n[STDERR]\nError message")

        # Execute
        result = await execute_command("command_with_error", "test-session")

        # Verify
        assert "code 0" in result
        assert "Normal output" in result
        assert "[STDERR]" in result
        assert "Error message" in result


def test_components_initialization():
    """Testa se os componentes principais são inicializados corretamente."""
    # Import the actual components
    from src.mcp_terminal_server.main import security_manager, session_manager, executor

    # Verify types
    from src.mcp_terminal_server.core.security import SecurityManager
    from src.mcp_terminal_server.core.session import SessionManager
    from src.mcp_terminal_server.core.executor import CommandExecutor

    assert isinstance(security_manager, SecurityManager)
    assert isinstance(session_manager, SessionManager)
    assert isinstance(executor, CommandExecutor)


@pytest.mark.asyncio
async def test_execute_command_empty():
    """Testa execução de comando vazio."""
    with patch('src.mcp_terminal_server.main.session_manager') as mock_session_mgr, \
         patch('src.mcp_terminal_server.main.security_manager') as mock_security_mgr, \
         patch('src.mcp_terminal_server.main.executor') as mock_executor:

        # Setup mocks
        mock_session_mgr.get_session.return_value = MagicMock()
        mock_security_mgr.needs_confirmation.return_value = False
        mock_executor.execute_command.return_value = (0, "")

        # Execute
        result = await execute_command("", "test-session")

        # Verify
        assert "code 0" in result


@pytest.mark.asyncio
async def test_execute_command_exception_handling():
    """Testa tratamento de exceções durante execução."""
    with patch('src.mcp_terminal_server.main.session_manager') as mock_session_mgr, \
         patch('src.mcp_terminal_server.main.security_manager') as mock_security_mgr, \
         patch('src.mcp_terminal_server.main.executor') as mock_executor:

        # Setup mocks
        mock_session_mgr.get_session.return_value = MagicMock()
        mock_security_mgr.needs_confirmation.return_value = False
        mock_executor.execute_command.side_effect = Exception("Unexpected error")

        # Execute
        result = await execute_command("failing_command", "test-session")

        # Verify - should handle the exception gracefully
        assert isinstance(result, str)
        # The exact error message depends on how the executor handles exceptions

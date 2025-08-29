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
    """Cria um diretório temporário para testes."""
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


def test_multiple_sessions_isolation(session_manager, temp_dir):
    session1 = session_manager.create_session("session-1")
    session2 = session_manager.create_session("session-2")

    # Cada sessão deve ter seu próprio diretório de trabalho
    session1.change_directory(str(temp_dir))
    assert session1.current_working_directory == temp_dir
    assert session2.current_working_directory != temp_dir


def test_change_directory_relative(session_manager, temp_dir):
    session = session_manager.create_session("session-cd")
    initial_dir = session.current_working_directory

    # Criar subdiretório
    subdir = temp_dir / "subdir"
    subdir.mkdir()

    # Mudar para o diretório temporário
    session.change_directory(str(temp_dir))

    # Mudar para subdiretório relativo
    assert session.change_directory("subdir") is True
    assert session.current_working_directory == subdir

    # Voltar para o diretório inicial
    assert session.change_directory(str(initial_dir)) is True
    assert session.current_working_directory == initial_dir


def test_change_directory_absolute(session_manager, temp_dir):
    session = session_manager.create_session("session-abs")

    # Mudar para caminho absoluto
    assert session.change_directory(str(temp_dir)) is True
    assert session.current_working_directory == temp_dir


def test_change_directory_invalid(session_manager):
    session = session_manager.create_session("session-invalid")

    # Tentar mudar para diretório inexistente
    assert session.change_directory("non_existent_dir_12345") is False
    assert session.change_directory("") is False


def test_environment_variables(session_manager):
    session = session_manager.create_session("session-env")

    # Testar set e get de variável
    session.set_env_var("TEST_VAR", "test_value")
    assert session.get_env_var("TEST_VAR") == "test_value"

    # Testar variável inexistente
    assert session.get_env_var("NONEXISTENT") is None

    # Verificar que variáveis de ambiente são isoladas entre sessões
    session2 = session_manager.create_session("session-env2")
    assert session2.get_env_var("TEST_VAR") is None


def test_session_initialization():
    session = Session("test-session")

    assert session.session_id == "test-session"
    assert session.current_working_directory == Path.cwd()
    assert isinstance(session.environment_variables, dict)
    assert len(session.active_processes) == 0
    assert session.websocket is None


def test_active_processes_management(session_manager):
    session = session_manager.create_session("session-process")

    # Adicionar processo mock
    mock_process = Mock()
    session.active_processes["cmd_123"] = mock_process

    assert len(session.active_processes) == 1
    assert session.active_processes["cmd_123"] == mock_process

    # Remover processo
    del session.active_processes["cmd_123"]
    assert len(session.active_processes) == 0


@pytest.mark.asyncio
async def test_close_session_with_active_processes(session_manager):
    session = session_manager.create_session("session-close")

    # Adicionar processo mock
    mock_process = AsyncMock()
    session.active_processes["cmd_123"] = mock_process

    # Fechar sessão
    session_manager.close_session("session-close")

    # Verificar que terminate foi chamado
    mock_process.terminate.assert_called_once()

    # Verificar que sessão foi removida
    assert session_manager.get_session("session-close") is None


def test_close_nonexistent_session(session_manager):
    # Não deve dar erro ao tentar fechar sessão inexistente
    session_manager.close_session("nonexistent")
    # Test passa se não lançar exceção


def test_session_persistence_across_operations(session_manager, temp_dir):
    session = session_manager.create_session("persistent-session")

    # Modificar estado da sessão
    session.change_directory(str(temp_dir))
    session.set_env_var("PERSISTENT_VAR", "persistent_value")
    session.active_processes["test_cmd"] = Mock()

    # Recuperar sessão e verificar persistência
    retrieved_session = session_manager.get_session("persistent-session")
    assert retrieved_session.current_working_directory == temp_dir
    assert retrieved_session.get_env_var("PERSISTENT_VAR") == "persistent_value"
    assert "test_cmd" in retrieved_session.active_processes


def test_session_isolation_comprehensive(session_manager):
    session1 = session_manager.create_session("iso1")
    session2 = session_manager.create_session("iso2")

    # Modificar session1
    session1.set_env_var("VAR1", "value1")
    session1.active_processes["proc1"] = Mock()

    # Verificar isolamento
    assert session2.get_env_var("VAR1") is None
    assert "proc1" not in session2.active_processes
    assert len(session2.active_processes) == 0
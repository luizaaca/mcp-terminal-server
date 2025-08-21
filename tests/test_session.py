import pytest
from src.mcp_terminal_server.core.session import SessionManager, Session
from pathlib import Path

@pytest.fixture
def session_manager():
    return SessionManager()

def test_create_and_get_session(session_manager):
    session = session_manager.create_session("session-1")
    assert isinstance(session, Session)
    assert session_manager.get_session("session-1") == session

def test_change_directory(session_manager):
    session = session_manager.create_session("session-cd")
    initial_dir = session.current_working_directory
    
    # Testa mudar para um subdiretório (assumindo que 'src' existe)
    src_path = Path.cwd() / "src"
    if src_path.exists():
        assert session.change_directory("src") is True
        assert session.current_working_directory == src_path
    
    # Testa voltar para o diretório inicial
    assert session.change_directory(str(initial_dir)) is True
    assert session.current_working_directory == initial_dir

    # Testa mudar para um diretório inválido
    assert session.change_directory("non_existent_dir_12345") is False
import pytest
from src.mcp_terminal_server.core.security import SecurityManager

@pytest.fixture
def security_manager():
    """Fixture para criar uma instância do SecurityManager."""
    return SecurityManager()

def test_needs_confirmation_sudo(security_manager):
    assert security_manager.needs_confirmation("sudo rm -rf /") is True

def test_needs_confirmation_destructive(security_manager):
    assert security_manager.needs_confirmation("rm -rf /some/path") is True

def test_needs_confirmation_package_manager(security_manager):
    assert security_manager.needs_confirmation("pip install requests") is True

def test_does_not_need_confirmation(security_manager):
    assert security_manager.needs_confirmation("ls -la") is False

def test_confirm_command_yes(security_manager, monkeypatch):
    """Testa a confirmação do usuário com resposta afirmativa."""
    # Simula o usuário digitando 'y' e pressionando Enter
    monkeypatch.setattr('builtins.input', lambda: 'y')
    assert security_manager.confirm_command("sudo reboot") is True

def test_confirm_command_no(security_manager, monkeypatch):
    """Testa a confirmação do usuário com resposta negativa."""
    # Simula o usuário digitando 'n' e pressionando Enter
    monkeypatch.setattr('builtins.input', lambda: 'n')
    assert security_manager.confirm_command("sudo reboot") is False
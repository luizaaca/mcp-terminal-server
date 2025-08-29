import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from src.mcp_terminal_server.core.security import SecurityManager


@pytest.fixture
def security_manager():
    """Fixture para criar uma instância do SecurityManager."""
    return SecurityManager()


@pytest.fixture
def temp_config_file():
    """Cria um arquivo de configuração temporário para testes."""
    config_data = {
        "sudo_commands": ["sudo", "doas"],
        "destructive_commands": ["rm -rf", "del /F"],
        "package_managers": ["pip", "apt"]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_path = Path(f.name)

    yield temp_path
    temp_path.unlink()  # Cleanup


def test_security_manager_initialization_default():
    """Testa inicialização com arquivo padrão."""
    manager = SecurityManager()
    assert manager.config_path.name == "known_commands.json"
    assert isinstance(manager.known_commands, dict)


def test_security_manager_initialization_custom_config(temp_config_file):
    """Testa inicialização com arquivo de configuração customizado."""
    manager = SecurityManager(temp_config_file)
    assert manager.config_path == temp_config_file
    assert "sudo_commands" in manager.known_commands


def test_load_known_commands_success(temp_config_file):
    """Testa carregamento bem-sucedido do arquivo de configuração."""
    manager = SecurityManager(temp_config_file)
    commands = manager.known_commands

    assert "sudo_commands" in commands
    assert "destructive_commands" in commands
    assert "package_managers" in commands
    assert "sudo" in commands["sudo_commands"]


def test_load_known_commands_file_not_found():
    """Testa comportamento quando arquivo de configuração não existe."""
    non_existent = Path("/non/existent/path.json")
    manager = SecurityManager(non_existent)

    assert manager.known_commands == {}


def test_load_known_commands_invalid_json():
    """Testa comportamento com JSON inválido."""
    with patch('builtins.open', mock_open(read_data='invalid json')):
        manager = SecurityManager(Path("dummy.json"))
        assert manager.known_commands == {}


def test_needs_confirmation_empty_command(security_manager):
    """Testa comando vazio."""
    assert security_manager.needs_confirmation("") is False
    assert security_manager.needs_confirmation("   ") is False


def test_needs_confirmation_sudo_commands(security_manager):
    """Testa comandos que requerem privilégios elevados."""
    assert security_manager.needs_confirmation("sudo rm -rf /") is True
    assert security_manager.needs_confirmation("doas apt update") is True
    assert security_manager.needs_confirmation("runas cmd") is True


def test_needs_confirmation_destructive_commands(security_manager):
    """Testa comandos destrutivos."""
    assert security_manager.needs_confirmation("rm -rf /some/path") is True
    assert security_manager.needs_confirmation("del /F /S /Q C:\\") is True
    assert security_manager.needs_confirmation("format C:") is True


def test_needs_confirmation_package_managers(security_manager):
    """Testa comandos de gerenciadores de pacotes."""
    assert security_manager.needs_confirmation("pip install requests") is True
    assert security_manager.needs_confirmation("apt update") is True
    assert security_manager.needs_confirmation("yum install nginx") is True


def test_does_not_need_confirmation_safe_commands(security_manager):
    """Testa comandos seguros que não precisam de confirmação."""
    assert security_manager.needs_confirmation("ls -la") is False
    assert security_manager.needs_confirmation("echo 'hello'") is False
    assert security_manager.needs_confirmation("cd /tmp") is False
    assert security_manager.needs_confirmation("cat file.txt") is False


def test_confirm_command_yes(security_manager, monkeypatch):
    """Testa confirmação do usuário com resposta afirmativa."""
    monkeypatch.setattr('builtins.input', lambda: 'y')
    confirmed, message = security_manager.confirm_command("sudo reboot")

    assert confirmed is True
    assert "approved" in message.lower()


def test_confirm_command_yes_variations(security_manager, monkeypatch):
    """Testa variações de resposta afirmativa."""
    for response in ['yes', 'YES', 'Y', 'Yes']:
        monkeypatch.setattr('builtins.input', lambda r=response: r)
        confirmed, message = security_manager.confirm_command("sudo reboot")

        assert confirmed is True
        assert "approved" in message.lower()


def test_confirm_command_no(security_manager, monkeypatch):
    """Testa confirmação do usuário com resposta negativa."""
    monkeypatch.setattr('builtins.input', lambda: 'n')
    confirmed, message = security_manager.confirm_command("sudo reboot")

    assert confirmed is False
    assert "cancelled" in message.lower() or "confirmation" in message.lower()


def test_confirm_command_no_variations(security_manager, monkeypatch):
    """Testa variações de resposta negativa."""
    for response in ['no', 'NO', 'N', 'anything_else']:
        monkeypatch.setattr('builtins.input', lambda r=response: r)
        confirmed, message = security_manager.confirm_command("sudo reboot")

        assert confirmed is False


def test_confirm_command_input_error(security_manager, monkeypatch):
    """Testa erro na leitura de input."""
    monkeypatch.setattr('builtins.input', lambda: (_ for _ in ()).throw(Exception("Input error")))
    confirmed, message = security_manager.confirm_command("sudo reboot")

    assert confirmed is False
    assert "error" in message.lower()


def test_complex_commands_requiring_confirmation(security_manager):
    """Testa comandos complexos que devem requerer confirmação."""
    complex_commands = [
        "sudo pip install -r requirements.txt",
        "apt update && apt upgrade -y",
        "rm -rf /tmp/* && sudo reboot"
    ]

    for cmd in complex_commands:
        assert security_manager.needs_confirmation(cmd) is True


def test_commands_with_whitespace(security_manager):
    """Testa comandos com espaços em branco."""
    assert security_manager.needs_confirmation("  sudo rm -rf /  ") is True
    assert security_manager.needs_confirmation("pip install flask") is True
    assert security_manager.needs_confirmation("  ls -la  ") is False
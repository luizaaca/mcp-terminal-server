import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from src.mcp_terminal_server.core.security import SecurityManager


@pytest.fixture
def security_manager():
    """Fixture to create a SecurityManager instance."""
    return SecurityManager()


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file for tests."""
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
    """Tests initialization with default file."""
    manager = SecurityManager()
    assert manager.config_path.name == "known_commands.json"
    assert isinstance(manager.known_commands, dict)


def test_security_manager_initialization_custom_config(temp_config_file):
    """Tests initialization with a custom configuration file."""
    manager = SecurityManager(temp_config_file)
    assert manager.config_path == temp_config_file
    assert "sudo_commands" in manager.known_commands


def test_load_known_commands_success(temp_config_file):
    """Tests successful loading of the configuration file."""
    manager = SecurityManager(temp_config_file)
    commands = manager.known_commands

    assert "sudo_commands" in commands
    assert "destructive_commands" in commands
    assert "package_managers" in commands
    assert "sudo" in commands["sudo_commands"]


def test_load_known_commands_file_not_found():
    """Tests behavior when the configuration file does not exist."""
    non_existent = Path("/non/existent/path.json")
    manager = SecurityManager(non_existent)

    assert manager.known_commands == {}


def test_load_known_commands_invalid_json():
    """Tests behavior with invalid JSON."""
    with patch('builtins.open', mock_open(read_data='invalid json')):
        manager = SecurityManager(Path("dummy.json"))
        assert manager.known_commands == {}


def test_needs_confirmation_empty_command(security_manager):
    """Tests empty command."""
    assert security_manager.needs_confirmation("") is False
    assert security_manager.needs_confirmation("   ") is False


def test_needs_confirmation_sudo_commands(security_manager):
    """Tests commands that require elevated privileges."""
    assert security_manager.needs_confirmation("sudo rm -rf /") is True
    assert security_manager.needs_confirmation("doas apt update") is True
    assert security_manager.needs_confirmation("runas cmd") is True


def test_needs_confirmation_destructive_commands(security_manager):
    """Tests destructive commands."""
    assert security_manager.needs_confirmation("rm -rf /some/path") is True
    assert security_manager.needs_confirmation("del /F /S /Q C:\\") is True
    assert security_manager.needs_confirmation("format C:") is True


def test_needs_confirmation_package_managers(security_manager):
    """Tests package manager commands."""
    assert security_manager.needs_confirmation("pip install requests") is True
    assert security_manager.needs_confirmation("apt update") is True
    assert security_manager.needs_confirmation("yum install nginx") is True


def test_does_not_need_confirmation_safe_commands(security_manager):
    """Tests safe commands that don't require confirmation."""
    assert security_manager.needs_confirmation("ls -la") is False
    assert security_manager.needs_confirmation("echo 'hello'") is False
    assert security_manager.needs_confirmation("cd /tmp") is False
    assert security_manager.needs_confirmation("cat file.txt") is False


def test_confirm_command_yes(security_manager, monkeypatch):
    """Tests user confirmation with affirmative response."""
    monkeypatch.setattr('builtins.input', lambda: 'y')
    confirmed, message = security_manager.confirm_command("sudo reboot")

    assert confirmed is True
    assert "approved" in message.lower()


def test_confirm_command_yes_variations(security_manager, monkeypatch):
    """Tests variations of affirmative responses."""
    for response in ['yes', 'YES', 'Y', 'Yes']:
        monkeypatch.setattr('builtins.input', lambda r=response: r)
        confirmed, message = security_manager.confirm_command("sudo reboot")

        assert confirmed is True
        assert "approved" in message.lower()


def test_confirm_command_no(security_manager, monkeypatch):
    """Tests user confirmation with negative response."""
    monkeypatch.setattr('builtins.input', lambda: 'n')
    confirmed, message = security_manager.confirm_command("sudo reboot")

    assert confirmed is False
    assert "cancelled" in message.lower() or "confirmation" in message.lower()


def test_confirm_command_no_variations(security_manager, monkeypatch):
    """Tests variations of negative responses."""
    for response in ['no', 'NO', 'N', 'anything_else']:
        monkeypatch.setattr('builtins.input', lambda r=response: r)
        confirmed, message = security_manager.confirm_command("sudo reboot")

        assert confirmed is False


def test_confirm_command_input_error(security_manager, monkeypatch):
    """Tests input read error."""
    monkeypatch.setattr('builtins.input', lambda: (_ for _ in ()).throw(Exception("Input error")))
    confirmed, message = security_manager.confirm_command("sudo reboot")

    assert confirmed is False
    assert "error" in message.lower()


def test_complex_commands_requiring_confirmation(security_manager):
    """Tests complex commands that should require confirmation."""
    complex_commands = [
        "sudo pip install -r requirements.txt",
        "apt update && apt upgrade -y",
        "rm -rf /tmp/* && sudo reboot"
    ]

    for cmd in complex_commands:
        assert security_manager.needs_confirmation(cmd) is True


def test_commands_with_whitespace(security_manager):
    """Tests commands with surrounding whitespace."""
    assert security_manager.needs_confirmation("  sudo rm -rf /  ") is True
    assert security_manager.needs_confirmation("pip install flask") is True
    assert security_manager.needs_confirmation("  ls -la  ") is False
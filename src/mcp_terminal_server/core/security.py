import json
from pathlib import Path
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityManager:
    """
    Manages command execution security.
    """
    def __init__(self, config_path: Path = None):
        """
        Initialize the SecurityManager.

        Args:
            config_path (Path, optional): Path to the JSON configuration file.
                                          If None, uses 'known_commands.json' in the data directory.
        """
        if config_path is None:
            self.config_path = Path(__file__).parent.parent / "data" / "known_commands.json"
        else:
            self.config_path = config_path
        
        self.known_commands = self._load_known_commands()

    def _load_known_commands(self) -> Dict[str, List[str]]:
        """
        Load known commands list from a JSON file.
        """
        try:
            if not self.config_path.exists():
                logger.warning(f"Security configuration file not found: {self.config_path}")
                return {}
            
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                logger.info("Security configuration loaded successfully.")
                return data
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error loading security configuration file: {e}")
            return {}

    def needs_confirmation(self, command: str) -> bool:
        """
        Check if a command requires confirmation before execution.

        Args:
            command (str): The command to check.

        Returns:
            bool: True if the command requires confirmation, False otherwise.
        """
        if not command:
            return False

        # Check if the command starts with an elevation command
        sudo_commands = self.known_commands.get('sudo_commands', [])
        if any(command.strip().startswith(cmd) for cmd in sudo_commands):
            logger.warning(f"Command '{command}' requires elevated privileges.")
            return True

        # Check for destructive command parts
        destructive_commands = self.known_commands.get('destructive_commands', [])
        if any(part in command for part in destructive_commands):
            logger.warning(f"Command '{command}' contains potentially destructive parts.")
            return True
            
        # Check if it is a package manager invocation
        package_managers = self.known_commands.get('package_managers', [])
        command_parts = command.strip().split()
        if command_parts and command_parts[0] in package_managers:
            logger.warning(f"Command '{command}' uses a package manager.")
            return True

        return False

    def confirm_command(self, command: str) -> bool:
        """
        Prompt the user on the server terminal to confirm executing a command.

        Args:
            command (str): The command awaiting confirmation.

        Returns:
            bool: True if the user confirms, False otherwise.
        """
        try:
            # Print the confirmation prompt to the server console
            prompt = f"\n[CONFIRMATION REQUIRED]\nExecute the potentially dangerous command below?\n\n  > {command}\n\nType 'y' or 'yes' to confirm, or any other key to cancel: "
            print(prompt, end="", flush=True)
            
            # Read user input directly from the server terminal
            answer = input().lower().strip()
            
            if answer in ['y', 'yes']:
                logger.info(f"Execution of command '{command}' APPROVED by the user.")
                print("-" * 20)
                return True
            else:
                logger.warning(f"Execution of command '{command}' CANCELLED by the user.")
                print("-" * 20)
                return False
        except Exception as e:
            logger.error(f"Error while requesting confirmation: {e}")
            return False

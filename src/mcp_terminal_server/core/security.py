import json
from pathlib import Path
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityManager:
    """
    Gerencia a segurança da execução de comandos.
    """
    def __init__(self, config_path: Path = None):
        """
        Inicializa o SecurityManager.

        Args:
            config_path (Path, optional): Caminho para o arquivo de configuração JSON.
                                          Se None, usa 'known_commands.json' no diretório de dados.
        """
        if config_path is None:
            self.config_path = Path(__file__).parent.parent / "data" / "known_commands.json"
        else:
            self.config_path = config_path
        
        self.known_commands = self._load_known_commands()

    def _load_known_commands(self) -> Dict[str, List[str]]:
        """
        Carrega a lista de comandos conhecidos de um arquivo JSON.
        """
        try:
            if not self.config_path.exists():
                logger.warning(f"Arquivo de configuração de segurança não encontrado: {self.config_path}")
                return {}
            
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                logger.info("Configuração de segurança carregada com sucesso.")
                return data
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Erro ao carregar o arquivo de configuração de segurança: {e}")
            return {}

    def needs_confirmation(self, command: str) -> bool:
        """
        Verifica se um comando precisa de confirmação antes da execução.

        Args:
            command (str): O comando a ser verificado.

        Returns:
            bool: True se o comando precisar de confirmação, False caso contrário.
        """
        if not command:
            return False

        # Verifica se o comando inicia com um comando que requer elevação
        sudo_commands = self.known_commands.get('sudo_commands', [])
        if any(command.strip().startswith(cmd) for cmd in sudo_commands):
            logger.warning(f"Comando '{command}' requer elevação de privilégios.")
            return True

        # Verifica se o comando contém partes destrutivas
        destructive_commands = self.known_commands.get('destructive_commands', [])
        if any(part in command for part in destructive_commands):
            logger.warning(f"Comando '{command}' contém partes potencialmente destrutivas.")
            return True
            
        # Verifica se é um gerenciador de pacotes
        package_managers = self.known_commands.get('package_managers', [])
        command_parts = command.strip().split()
        if command_parts and command_parts[0] in package_managers:
            logger.warning(f"Comando '{command}' utiliza um gerenciador de pacotes.")
            return True

        return False

    def confirm_command(self, command: str) -> bool:
        """
        Solicita confirmação do usuário no terminal para executar um comando.

        Args:
            command (str): O comando que aguarda confirmação.

        Returns:
            bool: True se o usuário confirmar, False caso contrário.
        """
        try:
            # Imprime a solicitação de confirmação no console do servidor
            prompt = f"\n[CONFIRMAÇÃO NECESSÁRIA]\nExecutar o comando potencialmente perigoso abaixo?\n\n  > {command}\n\nDigite 's' ou 'y' para confirmar, ou qualquer outra tecla para cancelar: "
            print(prompt, end="", flush=True)
            
            # Lê a entrada do usuário diretamente do terminal
            answer = input().lower().strip()
            
            if answer in ['s', 'y', 'sim', 'yes']:
                logger.info(f"Execução do comando '{command}' APROVADA pelo usuário.")
                print("-" * 20)
                return True
            else:
                logger.warning(f"Execução do comando '{command}' CANCELADA pelo usuário.")
                print("-" * 20)
                return False
        except Exception as e:
            logger.error(f"Ocorreu um erro durante a solicitação de confirmação: {e}")
            return False

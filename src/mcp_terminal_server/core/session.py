import asyncio
import logging
import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class Session:
    """
    Representa uma única sessão de terminal, com seu próprio estado.
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.current_working_directory = Path.cwd()
        self.environment_variables: Dict[str, str] = os.environ.copy()
        self.active_processes: Dict[str, asyncio.subprocess.Process] = {} # Mapeia command_id para processo
        self.websocket: Optional[WebSocket] = None

    def set_env_var(self, key: str, value: str):
        """Define uma variável de ambiente para a sessão."""
        self.environment_variables[key] = value

    def get_env_var(self, key: str) -> Optional[str]:
        """Obtém uma variável de ambiente da sessão."""
        return self.environment_variables.get(key)

    def change_directory(self, new_dir: str) -> bool:
        """
        Altera o diretório de trabalho atual da sessão.
        Retorna True se bem-sucedido, False caso contrário.
        """
        try:
            # Tenta resolver o novo diretório em relação ao atual
            target_dir = self.current_working_directory / new_dir
            if target_dir.is_dir():
                self.current_working_directory = target_dir.resolve()
                return True
            # Se não for um diretório, tenta como caminho absoluto
            elif Path(new_dir).is_dir():
                self.current_working_directory = Path(new_dir).resolve()
                return True
        except Exception:
            return False
        return False

class SessionManager:
    """
    Gerencia múltiplas sessões de terminal.
    """
    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def create_session(self, session_id: Optional[str] = None) -> Session:
        """
        Cria uma nova sessão ou retorna uma existente.

        Args:
            session_id (str, optional): O ID da sessão a ser criada ou recuperada.
                                      Se None, um novo ID aleatório é gerado.

        Returns:
            Session: A instância da sessão nova ou existente.
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.sessions:
            self.sessions[session_id] = Session(session_id)
        
        return self.sessions[session_id]

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Recupera uma sessão pelo seu ID.

        Args:
            session_id (str): O ID da sessão.

        Returns:
            Session: A instância da sessão, ou None se não for encontrada.
        """
        return self.sessions.get(session_id)

    def close_session(self, session_id: str):
        """
        Fecha e limpa uma sessão, terminando todos os processos ativos.

        Args:
            session_id (str): O ID da sessão a ser fechada.
        """
        session = self.sessions.get(session_id)
        if session:
            # Itera sobre uma cópia dos itens para evitar problemas de modificação durante a iteração
            for command_id, process in list(session.active_processes.items()):
                try:
                    logger.info(f"Encerrando processo ativo (PID: {process.pid}) da sessão {session_id}.")
                    process.terminate()
                except ProcessLookupError:
                    # O processo pode já ter terminado
                    logger.debug(f"Processo (PID: {process.pid}) não encontrado, pode já ter sido encerrado.")
                except Exception as e:
                    logger.error(f"Erro ao encerrar processo (PID: {process.pid}): {e}")
            
            del self.sessions[session_id]
            logger.info(f"Sessão {session_id} fechada com sucesso.")

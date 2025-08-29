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
    Represents a single terminal session with its own state.
    """
    def __init__(self, session_id: str, initial_dir: Optional[str] = None):
        self.session_id = session_id
        self.current_working_directory = Path(initial_dir) if initial_dir else Path.cwd()
        self.environment_variables: Dict[str, str] = os.environ.copy()
        self.active_processes: Dict[str, asyncio.subprocess.Process] = {} # Maps command_id to process
        self.websocket: Optional[WebSocket] = None
    

class SessionManager:
    """
    Manages multiple terminal sessions.
    """
    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def create_session(self, session_id: Optional[str] = None) -> Session:
        """
        Create a new session or return an existing one.

        Args:
            session_id (str, optional): The session ID to create or retrieve.
                                      If None, a new random ID is generated.

        Returns:
            Session: The new or existing session instance.
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.sessions:
            self.sessions[session_id] = Session(session_id)
        
        return self.sessions[session_id]

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve a session by its ID.

        Args:
            session_id (str): The session ID.

        Returns:
            Session: The session instance, or None if not found.
        """
        return self.sessions.get(session_id)

    def close_session(self, session_id: str):
        """
        Close and clean up a session, terminating all active processes.

        Args:
            session_id (str): The ID of the session to close.
        """
        session = self.sessions.get(session_id)
        if session:
            # Iterate over a copy of the items to avoid modification issues while iterating
            for command_id, process in list(session.active_processes.items()):
                try:
                    logger.info(f"Shutting down active process (PID: {process.pid}) for session {session_id}.")
                    process.terminate()
                except ProcessLookupError:
                    # The process may have already exited
                    logger.debug(f"Process (PID: {process.pid}) not found, it may have already exited.")
                except Exception as e:
                    logger.error(f"Error shutting down process (PID: {process.pid}): {e}")
            
            del self.sessions[session_id]
            logger.info(f"Session {session_id} closed successfully.")

import asyncio
import logging
import uuid
from typing import Any, Dict

from ..core.database import DatabaseManager
from ..core.executor import CommandExecutor
from ..core.security import SecurityManager
from ..core.session import SessionManager
from .handlers import COMMAND_HANDLERS

logger = logging.getLogger(__name__)

class MCPServer:
    """
    MCP server that manages business logic and request lifecycle.
    """
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.security_manager = SecurityManager()
        self.session_manager = SessionManager()
        
        # The executor now passes the session_id to the stream callback
        self.executor = CommandExecutor(output_callback=self.stream_output)
        
        self._is_running = False

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single MCP request.
        """
        command_name = request.get("command")
        params = request.get("params", {})
        session_id = params.get("session_id", str(uuid.uuid4()))

        # Ensure a session exists
        if not session_id or not self.session_manager.get_session(session_id):
            self.session_manager.create_session(session_id)
            logger.info(f"New session created: {session_id}")
        
        params["session_id"] = session_id # Ensure session_id is present in params

        handler = COMMAND_HANDLERS.get(command_name)
        if handler:
            try:
                return await handler(self, params)
            except Exception as e:
                logger.error(f"Error processing command '{command_name}': {e}")
                return {"error": str(e)}
        else:
            return {"error": f"Unknown command: {command_name}"}

    async def stream_output(self, session_id: str, output: str):
        """
        Callback for executor output streaming.
        Sends data to the client via WebSocket if a connection is active.
        """
        session = self.session_manager.get_session(session_id)
        if session and hasattr(session, 'websocket') and session.websocket:
            try:
                await session.websocket.send_json({"type": "stream", "output": output})
            except Exception as e:
                logger.warning(f"Unable to send stream to session {session_id}: {e}")
        else:
            # Fallback to console if no websocket is available
            print(output, end='')    

# Example of how the server could be used (for testing purposes)
async def main():
    server = MCPServer()
    # Simulate creating a session
    session = server.session_manager.create_session("user123")

    # Simulate a request to list files
    request = {
        "command": "execute_command",
        "params": {
            "command": "ls -l" if os.name != 'nt' else 'dir',
            "session_id": session.session_id
        }
    }
    response = await server.handle_request(request)
    print("\n--- Server Response ---")
    print(response)
    
    # Simulate a request to change directory
    request_cd = {
        "command": "change_directory",
        "params": {"path": "..", "session_id": session.session_id}
    }
    response_cd = await server.handle_request(request_cd)
    print("\n--- Server Response (cd) ---")
    print(response_cd)

if __name__ == "__main__":
    import os
    asyncio.run(main())

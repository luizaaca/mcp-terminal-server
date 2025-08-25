import logging
from typing import Any, Dict

from ..core.session import Session

logger = logging.getLogger(__name__)

# Handlers for MCP server commands

async def execute_command_handler(server: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the 'execute_command' command.
    """
    command = params.get("command")
    session_id = params.get("session_id")

    if not command:
        return {"error": "Command not provided."}

    session = server.session_manager.get_session(session_id)
    if not session:
        return {"error": f"Session '{session_id}' not found."}

    # 1. Security check
    if server.security_manager.needs_confirmation(command):
        if not server.security_manager.confirm_command(command):
            return {"output": "Execution cancelled by user.", "exit_code": -1, "success": False}

    # 2. Command execution
    exit_code, full_output = await server.executor.execute_command(command, session)
    success = exit_code == 0

    # 3. Log to the database
    server.db_manager.log_command(
        session_id=session.session_id,
        command=command,
        output=full_output,
        exit_code=exit_code,
        success=success
    )

    return {"output": full_output, "exit_code": exit_code, "success": success}

async def change_directory_handler(server: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the 'change_directory' command.
    """
    path = params.get("path")
    session_id = params.get("session_id")
    session = server.session_manager.get_session(session_id)

    if not path or not session:
        return {"error": "Invalid parameters."}

    if session.change_directory(path):
        return {"current_directory": str(session.current_working_directory)}
    else:
        return {"error": f"Unable to change to directory: {path}"}

async def get_current_directory_handler(server: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the 'get_current_directory' command.
    """
    session_id = params.get("session_id")
    session = server.session_manager.get_session(session_id)
    if session:
        return {"current_directory": str(session.current_working_directory)}
    return {"error": "Session not found."}

async def get_command_history_handler(server: Any, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handler for the 'get_command_history' command.
    """
    session_id = params.get("session_id")
    limit = params.get("limit", 100)
    history = server.db_manager.get_history(session_id, limit)
    return {"history": history}

# Mapping of commands to handlers
COMMAND_HANDLERS = {
    "execute_command": execute_command_handler,
    "change_directory": change_directory_handler,
    "get_current_directory": get_current_directory_handler,
    "get_command_history": get_command_history_handler,
}

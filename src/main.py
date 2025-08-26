import logging
from mcp.server.fastmcp import FastMCP
from core.executor import CommandExecutor
from core.security import SecurityManager
from core.session import SessionManager

logger = logging.getLogger(__name__)

# Create an MCP server instance
mcp_server = FastMCP("terminal")

# Instantiate core components
security_manager = SecurityManager()
session_manager = SessionManager()

executor = CommandExecutor()

@mcp_server.tool()
async def execute_command(command: str, session_id: str) -> str:
    """
    Executes a shell command in the specified cmd.exe session and returns the output back.
    Args:
        command (str): The shell command to execute.
        session_id (str): The ID of the session to use in order to keep terminal session with environment variables, path etc.
    """

    logger.info(f"Received command to execute: {command} in session: {session_id}")
    session = session_manager.get_session(session_id)
    if not session:
        session = session_manager.create_session(session_id)
        logger.info(f"New session created: {session_id}")

    # Security check
    if security_manager.needs_confirmation(command):
        success, message = security_manager.confirm_command(command)
        if not success:
            logger.warning(f"Confirmation needed for command: {command}")
            return message

    # Run the command execution in the background
        exit_code, output = executor.execute_command(command, session)

    return f"The execution returned with code {exit_code}: {output}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp_server.run(transport='stdio')
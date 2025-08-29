import logging
import os
from mcp.server.fastmcp import FastMCP
from mcp_terminal_server.core.executor import CommandExecutor
from mcp_terminal_server.core.security import SecurityManager
from mcp_terminal_server.core.session import SessionManager

# # Create logs directory if it doesn't exist
# log_dir = "logs"
# if not os.path.exists(log_dir):
#     os.makedirs(log_dir)

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     filename=os.path.join(log_dir, "mcp_terminal_server.log"),
# )

logger = logging.getLogger(__name__)

# Create an MCP server instance
mcp_server = FastMCP("terminal", "A terminal MCP server")

# Instantiate core components
security_manager = SecurityManager()
session_manager = SessionManager()

executor = CommandExecutor()

@mcp_server.tool()
async def execute_command(command: str, session_id: str) -> str:
    r"""
    Executes a shell command in the specified windows cmd.exe session and returns the output back.

    KNOWLEDGE BASE:
    - Common tasks: file management, service operations, log analysis
    - Preferred naming: use lowercase with underscores
    - Always confirm destructive (deletion and update) operations or commands with side effects

    Command   Purpose                          How to get help          Example usage
    help      List internal CMD commands       help                     help dir
    
    Args:
        command (str): The cmd.exe command to execute.
        session_id (str): The ID of the session to use in order to keep terminal session with environment variables, path etc.

    Instruction:
        You must play the role of a windows system administrator and provide the correct commands to execute.
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
    exit_code, output = await executor.execute_command(command, session)

    return f"Exit Code: {exit_code}\nOutput:\n{output}"

if __name__ == "__main__":
    # Initialize and run the server
    mcp_server.run(transport='stdio')
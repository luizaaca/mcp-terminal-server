import logging
from mcp.server.fastmcp import FastMCP
from .core.executor import CommandExecutor
from .core.security import SecurityManager
from .core.session import SessionManager

logger = logging.getLogger(__name__)

# Create an MCP server instance
mcp_server = FastMCP(
    "terminal",
    "A terminal MCP server",
    "v0.1.0-beta"
)

# Instantiate core components
security_manager = SecurityManager()
session_manager = SessionManager()

executor = CommandExecutor()

@mcp_server.tool()
async def execute_command(command: str, session_id: str) -> str:
    r"""
    Executes a shell command in the specified windows cmd.exe session and returns the output back.    
    Args:
        command (str): The cmd.exe command to execute.
        session_id (str): The ID of the session to use in order to keep terminal session with environment variables, path etc.

    Instruction:
        You must play the role of a windows system administrator and provide the correct commands to execute.

    KNOWLEDGE BASE:
        - Default working directory: D:\
        - Common tasks: file management, service operations, log analysis
        - Preferred naming: use lowercase with underscores
        - Always confirm destructive (deletion and update) operations or commands with side effects

        +----------+-----------------------------------+-------------------------+-----------------------------------------------+
        | Command  | Purpose                           | How to get help         | Example usage                                 |
        +----------+-----------------------------------+-------------------------+-----------------------------------------------+
        | help     | List internal CMD commands        | help                    | help dir                                      |
        | dir      | List files and folders            | dir /? or help dir      | dir /b                                        |
        | cd       | Change directory                  | cd /? or help cd        | cd C:\Users                                   |
        | copy     | Copy files                        | copy /? or help copy    | copy a.txt d:\backup\                         |
        | move     | Move or rename files              | move /?                 | move a.txt d:\backup\                         |
        | del      | Delete files                      | del /?                  | del *.tmp                                     |
        | md       | Create folder                     | md /?                   | md newFolder                                  |
        | rd       | Remove folder                     | rd /?                   | rd /s /q oldFolder                            |
        | cls      | Clear the screen                  | cls /?                  | cls                                           |
        | exit     | Close CMD                         | exit /?                 | exit                                          |
        | ping     | Test connectivity with a host     | ping /?                 | ping google.com                               |
        | ipconfig | Show IP, mask, gateway            | ipconfig /?             | ipconfig /all                                 |
        | tracert  | Show route to a host              | tracert /?              | tracert google.com                            |
        | netstat  | Show connections and open ports   | netstat /?              | netstat -an                                   |
        | nslookup | Query DNS server                  | nslookup /?             | nslookup google.com                           |
        | tasklist | List running processes            | tasklist /?             | tasklist /fi "imagename eq chrome.exe"        |
        | taskkill | Kill processes                    | taskkill /?             | taskkill /im chrome.exe /f                    |
        | sc       | Manage Windows services           | sc /?                   | sc query                                      |
        | chkdsk   | Check and repair disk             | chkdsk /?               | chkdsk C: /f /r                               |
        | sfc      | Verify system file integrity      | sfc /?                  | sfc /scannow                                  |
        | shutdown | Shutdown or restart the computer  | shutdown /?             | shutdown /r /t 0                              |
        | xcopy    | Copy files and directories        | xcopy /?                | xcopy C:\data D:\backup /E /H /C /I           |
        | robocopy | Advanced file copy                | robocopy /?             | robocopy C:\data D:\backup /MIR /MT:8         |
        | attrib   | Change file attributes            | attrib /?               | attrib +h secret.txt                          |
        +----------+-----------------------------------+-------------------------+-----------------------------------------------+        
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
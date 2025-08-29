import asyncio
import logging
import platform
from typing import Tuple

from .session import Session

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CommandExecutor:
    """
    Executes system commands asynchronously and manages the process.
    """

    async def execute_command(self, command: str, session: Session) -> Tuple[int, str]:
        """
        Execute a shell command asynchronously.

        Args:
            command (str): The command to execute.
            session (Session): The session in which the command will run.

        Returns:
            Tuple[int, str]: A tuple containing the exit code and the full output.
        """
        process = None
        command_id = ""
        try:
            # Create the subprocess with Windows compatibility
            if platform.system() == "Windows":
                logger.debug("Creating subprocess for Windows: cmd /c %s", command)
                # On Windows, use create_subprocess_exec with cmd.exe
                process = await asyncio.create_subprocess_exec(
                    "cmd", "/c", command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=session.current_working_directory,
                    env=session.environment_variables,
                )
            else:
                logger.debug("Creating subprocess for Unix-like system: %s", command)
                # On Unix-like systems, use create_subprocess_shell
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=session.current_working_directory,
                    env=session.environment_variables,
                )

            # Add the process to the session so it can be cancelled
            command_id = f"cmd_{id(process)}"
            session.active_processes[command_id] = process
            logger.info("Command '%s' started with PID: %d in session %s", command, process.pid, session.session_id)

            # Asynchronously read stdout and stderr in parallel
            stdout_task = asyncio.create_task(self._read_stream(process.stdout))
            stderr_task = asyncio.create_task(self._read_stream(process.stderr))

            # Wait for both streams to be fully read
            stdout_bytes, stderr_bytes = await asyncio.gather(
                stdout_task,
                stderr_task
            )

            # Wait for the process to terminate
            await process.wait()
            exit_code = process.returncode
            logger.info("Command '%s' finished with exit code: %d", command, exit_code)

            output = stdout_bytes.decode(errors='replace')
            stderr_output = stderr_bytes.decode(errors='replace')
            if stderr_output:
                output += f"\n[STDERR]\n{stderr_output}"

            return exit_code, output

        except asyncio.CancelledError:
            logger.warning("Command '%s' was cancelled.", command)
            if process and process.returncode is None:
                process.terminate()
                await process.wait()
            return -1, "Command execution was cancelled."

        except Exception as e:
            logger.error("Error executing command '%s': %s", command, e, exc_info=True)
            return -1, f"An unexpected error occurred: {e}"

        finally:
            if command_id and command_id in session.active_processes:
                del session.active_processes[command_id]

    async def _read_stream(self, stream: asyncio.StreamReader) -> bytes:
        """Reads all data from a stream until EOF."""
        if not stream:
            return b""
        return await stream.read()

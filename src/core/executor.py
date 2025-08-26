import asyncio
import logging
import traceback
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
        command_id = None
        full_output_chunks = []
        try:
            # Nested callback to capture output and forward it for real-time streaming
            async def stream_and_capture_callback(session_id: str, chunk: str):
                full_output_chunks.append(chunk)

            # Create the subprocess with Windows compatibility
            if platform.system() == "Windows":
                logger.info("Creating subprocess for Windows")
                # On Windows, use create_subprocess_exec with cmd.exe
                process = await asyncio.create_subprocess_exec(
                    "cmd", "/c", command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=session.current_working_directory,
                    env=session.environment_variables
                )
            else:
                logger.info("Creating subprocess for Unix-like system")
                # On Unix-like systems, use create_subprocess_shell
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=session.current_working_directory,
                    env=session.environment_variables
                )

            # Add the process to the session so it can be cancelled
            command_id = f"cmd_{id(process)}"
            session.active_processes[command_id] = process
            print(f"Command '{command}' started with PID: {process.pid}")

            # Asynchronously read stdout and stderr
            await asyncio.gather(
                self._stream_output(process.stdout, session.session_id, stream_and_capture_callback),
                self._stream_output(process.stderr, session.session_id, stream_and_capture_callback)
            )

            await process.wait()
            exit_code = process.returncode
            logger.info(f"Command '{command}' finished with exit code: {exit_code}")

        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            tb = traceback.format_exc()
            error_message = f"Error: {tb}\n"
            full_output_chunks.append(error_message)
            await self.output_callback(session.session_id, error_message)
            exit_code = -1
        finally:
            if command_id and command_id in session.active_processes:
                del session.active_processes[command_id]

        return exit_code, "".join(full_output_chunks)
    


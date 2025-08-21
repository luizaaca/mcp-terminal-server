import asyncio
import logging
from typing import Callable, Any, Coroutine, Tuple

from .session import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommandExecutor:
    """
    Executes system commands asynchronously and manages the process.
    """
    def __init__(self, output_callback: Callable[[str], Coroutine[Any, Any, None]]):
        """
        Initialize the CommandExecutor.

        Args:
            output_callback: An async callback function to send command output.
        """
        self.output_callback = output_callback


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
                # Call original callback to stream in real time (e.g., websocket)
                await self.output_callback(session_id, chunk)

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
            error_message = f"Error: {e}\n"
            full_output_chunks.append(error_message)
            await self.output_callback(session.session_id, error_message)
            exit_code = -1
        finally:
            if command_id and command_id in session.active_processes:
                del session.active_processes[command_id]

        return exit_code, "".join(full_output_chunks)

    async def _stream_output(self, stream: asyncio.StreamReader, session_id: str, callback: Callable[[str, str], Coroutine[Any, Any, None]]):
        """
        Read output from a stream and forward it to the callback.
        """
        while True:
            try:
                line = await stream.readline()
                if not line:
                    break
                await callback(session_id, line.decode('utf-8', errors='replace'))
            except Exception as e:
                logger.error(f"Error reading output stream: {e}")
                break

    async def cancel_command(self, command_id: str, session: Session):
        """
        Cancel a running command.

        Args:
            command_id (str): The ID of the command to cancel.
            session (Session): The session where the command is running.
        """
        if command_id in session.active_processes:
            process = session.active_processes[command_id]
            try:
                process.terminate()
                await process.wait()
                logger.info(f"Command {command_id} cancelled.")
                del session.active_processes[command_id]
            except ProcessLookupError:
                logger.warning(f"Process for command {command_id} no longer existed.")
            except Exception as e:
                logger.error(f"Error cancelling command {command_id}: {e}")
        else:
            logger.warning(f"Attempted to cancel unknown command: {command_id}")

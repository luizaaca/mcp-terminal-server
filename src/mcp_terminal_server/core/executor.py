import asyncio
import logging
from typing import Callable, Any, Coroutine, Tuple

from .session import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommandExecutor:
    """
    Executa comandos do sistema de forma assíncrona e gerencia o processo.
    """
    def __init__(self, output_callback: Callable[[str], Coroutine[Any, Any, None]]):
        """
        Inicializa o CommandExecutor.

        Args:
            output_callback: Uma função de callback assíncrona para enviar o output do comando.
        """
        self.output_callback = output_callback


    async def execute_command(self, command: str, session: Session) -> Tuple[int, str]:
        """
        Executa um comando no terminal de forma assíncrona.

        Args:
            command (str): O comando a ser executado.
            session (Session): A sessão na qual o comando será executado.

        Returns:
            Tuple[int, str]: Uma tupla contendo o código de saída e o output completo.
        """
        command_id = None
        full_output_chunks = []
        try:
            # Define um callback aninhado para capturar o output e fazer o streaming
            async def stream_and_capture_callback(session_id: str, chunk: str):
                full_output_chunks.append(chunk)
                # Chama o callback original para streaming em tempo real (e.g., websocket)
                await self.output_callback(session_id, chunk)

            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=session.current_working_directory,
                env=session.environment_variables
            )

            # Adiciona o processo à sessão para que possa ser cancelado
            command_id = f"cmd_{id(process)}"
            session.active_processes[command_id] = process

            # Leitura assíncrona do stdout e stderr
            await asyncio.gather(
                self._stream_output(process.stdout, session.session_id, stream_and_capture_callback),
                self._stream_output(process.stderr, session.session_id, stream_and_capture_callback)
            )

            await process.wait()
            exit_code = process.returncode
            logger.info(f"Comando '{command}' finalizado com código de saída: {exit_code}")

        except Exception as e:
            logger.error(f"Erro ao executar o comando '{command}': {e}")
            error_message = f"Erro: {e}\n"
            full_output_chunks.append(error_message)
            await self.output_callback(session.session_id, error_message)
            exit_code = -1
        finally:
            if command_id and command_id in session.active_processes:
                del session.active_processes[command_id]

        return exit_code, "".join(full_output_chunks)

    async def _stream_output(self, stream: asyncio.StreamReader, session_id: str, callback: Callable[[str, str], Coroutine[Any, Any, None]]):
        """
        Lê o output de um stream e o envia para o callback.
        """
        while True:
            try:
                line = await stream.readline()
                if not line:
                    break
                await callback(session_id, line.decode('utf-8', errors='replace'))
            except Exception as e:
                logger.error(f"Erro ao ler o stream de output: {e}")
                break

    async def cancel_command(self, command_id: str, session: Session):
        """
        Cancela um comando em execução.

        Args:
            command_id (str): O ID do comando a ser cancelado.
            session (Session): A sessão onde o comando está rodando.
        """
        if command_id in session.active_processes:
            process = session.active_processes[command_id]
            try:
                process.terminate()
                await process.wait()
                logger.info(f"Comando {command_id} cancelado.")
                del session.active_processes[command_id]
            except ProcessLookupError:
                logger.warning(f"Processo para o comando {command_id} já não existia.")
            except Exception as e:
                logger.error(f"Erro ao cancelar o comando {command_id}: {e}")
        else:
            logger.warning(f"Tentativa de cancelar um comando não encontrado: {command_id}")

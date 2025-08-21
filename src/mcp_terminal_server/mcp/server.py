import asyncio
import logging
from typing import Any, Dict

from ..core.database import DatabaseManager
from ..core.executor import CommandExecutor
from ..core.security import SecurityManager
from ..core.session import SessionManager
from .handlers import COMMAND_HANDLERS

logger = logging.getLogger(__name__)

class MCPServer:
    """
    Servidor MCP que gerencia a lógica de negócio e o ciclo de vida das requisições.
    """
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.security_manager = SecurityManager()
        self.session_manager = SessionManager()
        
        # O executor agora passa o session_id para o callback de stream
        self.executor = CommandExecutor(output_callback=self.stream_output)
        
        self._is_running = False

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa uma única requisição MCP.
        """
        command_name = request.get("command")
        params = request.get("params", {})
        session_id = params.get("session_id")

        # Garante que uma sessão exista
        if not self.session_manager.get_session(session_id):
            self.session_manager.create_session(session_id)
            logger.info(f"Nova sessão criada: {session_id}")
        
        params["session_id"] = session_id # Garante que o session_id está nos params

        handler = COMMAND_HANDLERS.get(command_name)
        if handler:
            try:
                return await handler(self, params)
            except Exception as e:
                logger.error(f"Erro ao processar o comando '{command_name}': {e}")
                return {"error": str(e)}
        else:
            return {"error": f"Comando desconhecido: {command_name}"}

    async def stream_output(self, session_id: str, output: str):
        """
        Callback para o streaming de output do executor.
        Envia dados para o cliente via WebSocket, se houver uma conexão ativa.
        """
        session = self.session_manager.get_session(session_id)
        if session and hasattr(session, 'websocket') and session.websocket:
            try:
                await session.websocket.send_json({"type": "stream", "output": output})
            except Exception as e:
                logger.warning(f"Não foi possível enviar stream para a sessão {session_id}: {e}")
        else:
            # Fallback para o console se não houver websocket
            print(output, end='')

    async def start(self, host: str = "127.0.0.1", port: int = 8000):
        """
        Inicia o servidor para escutar por conexões (simulado).
        """
        self._is_running = True
        logger.info(f"Servidor MCP iniciado em {host}:{port}. Aguardando requisições...")
        # Em um servidor real, aqui teríamos um loop de eventos (ex: com aiohttp, FastAPI).
        # Para este exemplo, vamos manter o servidor "rodando" em um loop simples.
        while self._is_running:
            await asyncio.sleep(1)

    async def shutdown(self):
        """
        Finaliza o servidor e seus componentes.
        """
        self._is_running = False
        self.db_manager.close()
        logger.info("Servidor MCP finalizado.")

# Exemplo de como o servidor poderia ser usado (para fins de teste)
async def main():
    server = MCPServer()
    # Simula a criação de uma sessão
    session = server.session_manager.create_session("user123")

    # Simula uma requisição para listar arquivos
    request = {
        "command": "execute_command",
        "params": {
            "command": "ls -l" if os.name != 'nt' else 'dir',
            "session_id": session.session_id
        }
    }
    response = await server.handle_request(request)
    print("\n--- Resposta do Servidor ---")
    print(response)
    
    # Simula uma requisição para mudar de diretório
    request_cd = {
        "command": "change_directory",
        "params": {"path": "..", "session_id": session.session_id}
    }
    response_cd = await server.handle_request(request_cd)
    print("\n--- Resposta do Servidor (cd) ---")
    print(response_cd)

if __name__ == "__main__":
    import os
    asyncio.run(main())

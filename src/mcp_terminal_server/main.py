"""
Ponto de entrada do MCP Terminal Server
"""

import argparse
import asyncio
import logging
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any

from mcp_terminal_server.mcp.server import MCPServer

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Modelo Pydantic para validar as requisições
class MCPRequest(BaseModel):
    command: str
    params: Dict[str, Any] = {}

# Cria a aplicação FastAPI
app = FastAPI()
server = MCPServer()

@app.on_event("startup")
async def startup_event():
    # A lógica de inicialização do servidor pode vir aqui, se necessário
    logger.info("Servidor FastAPI iniciado e pronto para receber requisições.")

@app.on_event("shutdown")
async def shutdown_event():
    await server.shutdown()
    logger.info("Servidor FastAPI finalizado.")

@app.post("/command")
async def handle_command_request(request: MCPRequest):
    """
    Endpoint HTTP para receber comandos.
    """
    response = await server.handle_request(request.model_dump())
    return JSONResponse(content=response)

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    Endpoint WebSocket para comunicação em tempo real.
    """
    await websocket.accept()
    
    # Garante que a sessão exista
    if not server.session_manager.get_session(session_id):
        server.session_manager.create_session(session_id)
        logger.info(f"Nova sessão WebSocket criada: {session_id}")

    # Associa o websocket à sessão para streaming de output
    server.session_manager.get_session(session_id).websocket = websocket

    try:
        while True:
            data = await websocket.receive_json()
            request = MCPRequest(**data)
            
            # Define o session_id a partir da URL
            request.params["session_id"] = session_id
            
            response = await server.handle_request(request.model_dump())
            await websocket.send_json(response)
    except WebSocketDisconnect:
        logger.info(f"Sessão WebSocket {session_id} desconectada.")
        # Limpa a referência ao websocket
        if server.session_manager.get_session(session_id):
            server.session_manager.get_session(session_id).websocket = None
    except Exception as e:
        logger.error(f"Erro na sessão WebSocket {session_id}: {e}")
        await websocket.send_json({"error": str(e)})

def main():
    """
    Ponto de entrada principal para iniciar o servidor.
    """
    parser = argparse.ArgumentParser(description="MCP Terminal Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host para o servidor escutar.")
    parser.add_argument("--port", type=int, default=8000, help="Porta para o servidor escutar.")
    args = parser.parse_args()

    try:
        logger.info(f"Iniciando servidor em {args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Recebido sinal de interrupção, finalizando o servidor...")

if __name__ == "__main__":
    main()

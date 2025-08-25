"""
Entry point for the MCP Terminal Server
"""

import argparse
import logging
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
from contextlib import asynccontextmanager
import asyncio

from mcp_terminal_server.mcp.server import MCPServer

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pydantic model to validate requests
class MCPRequest(BaseModel):
    command: str
    params: Dict[str, Any] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("FastAPI server started and ready to accept requests.")
    yield
    # Shutdown logic
    logger.info("FastAPI server shut down.")

# Create the FastAPI application with lifespan handler
app = FastAPI(lifespan=lifespan)

server = MCPServer()

@app.post("/command")
async def handle_command_request(request: MCPRequest):
    """
    HTTP endpoint to receive commands.
    """
    response = await server.handle_request(request.model_dump())
    return JSONResponse(content=response)

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time communication.
    """
    await websocket.accept()
    
    # Ensure the session exists
    if not server.session_manager.get_session(session_id):
        server.session_manager.create_session(session_id)
        logger.info(f"New WebSocket session created: {session_id}")

    # Attach the websocket to the session for output streaming
    server.session_manager.get_session(session_id).websocket = websocket

    try:
        while True:
            data = await websocket.receive_json()
            request = MCPRequest(**data)
            
            # Set the session_id from the URL
            request.params["session_id"] = session_id
            
            response = await server.handle_request(request.model_dump())
            await websocket.send_json(response)
    except WebSocketDisconnect:
        logger.info(f"WebSocket session {session_id} disconnected.")
        # Clear the websocket reference
        if server.session_manager.get_session(session_id):
            server.session_manager.get_session(session_id).websocket = None
    except Exception as e:
        logger.error(f"Error in WebSocket session {session_id}: {e}")
        await websocket.send_json({"error": str(e)})

def main():
    """
    Main entry point to start the server.
    """
    parser = argparse.ArgumentParser(description="MCP Terminal Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host for the server to bind to.")
    parser.add_argument("--port", type=int, default=8000, help="Port for the server to listen on.")
    args = parser.parse_args()

    try:
        logger.info(f"Starting server on {args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Interrupt received, shutting down the server...")

if __name__ == "__main__":
    main()

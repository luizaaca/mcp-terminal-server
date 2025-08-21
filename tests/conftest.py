import sys
import os

# Adiciona o diretório 'src' ao sys.path para facilitar os imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest
import asyncio
from pathlib import Path
import tempfile

from mcp_terminal_server.core.database import DatabaseManager
from mcp_terminal_server.core.session import Session, SessionManager
from mcp_terminal_server.core.security import SecurityManager
from mcp_terminal_server.core.executor import CommandExecutor
from mcp_terminal_server.mcp.server import MCPServer
from mcp_terminal_server.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="function")
def temp_db():
    """Cria um banco de dados SQLite temporário para um teste."""
    # Cria um arquivo temporário que é automaticamente removido na saída
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    db_manager = DatabaseManager(database_url=f"sqlite:///{db_path}")
    db_manager.init_db()
    
    yield db_manager
    
    # Limpeza: remove o arquivo do banco de dados após o teste
    os.unlink(db_path)

@pytest.fixture
def test_client():
    """Fixture para o TestClient do FastAPI."""
    with TestClient(app) as client:
        yield client

# Permite que todos os testes sejam executados como assíncronos
@pytest.fixture(scope="session")
def event_loop():
    """Cria uma instância do event loop para a sessão de testes."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
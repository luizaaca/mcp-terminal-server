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
    """Creates a temporary SQLite database with schema for testing."""
    # Create a temporary directory that will contain both the DB and schema files
    temp_dir = tempfile.mkdtemp()
    
    # Create the database file
    db_path = Path(temp_dir) / "test_db.db"
    
    # Create a temporary schema file in the same directory
    schema_path = Path(temp_dir) / "commands.sql"
    
    # Write the schema to the file (same as in the real schema file)
    with open(schema_path, 'w') as f:
        f.write("""
        CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            command TEXT NOT NULL,
            output TEXT,
            exit_code INTEGER,
            success BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
    
    # Pass the db_path to DatabaseManager
    db_manager = DatabaseManager(db_path=db_path)
    
    yield db_manager
    
    # Cleanup: close connection and remove temporary files
    try:
        if hasattr(db_manager, 'connection') and db_manager.connection:
            db_manager.connection.close()
        # Remove the temporary directory and all files in it
        import shutil
        shutil.rmtree(temp_dir)
    except (PermissionError, FileNotFoundError) as e:
        # If we can't delete, it's not critical for the test
        print(f"Warning: Could not clean up temp test files: {e}")

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
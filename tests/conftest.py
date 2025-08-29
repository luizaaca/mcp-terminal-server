import sys
import os

# Adiciona o diretório 'src' ao sys.path para facilitar os imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


import pytest
import asyncio
from fastapi.testclient import TestClient

import importlib

@pytest.fixture
def test_client(monkeypatch):
    """Fixture para o TestClient do FastAPI, com patch para FastMCP if needed."""
    # Patch FastMCP to avoid ValueError during tests
    from mcp.server import fastmcp
    class DummyFastMCP(fastmcp.FastMCP):
        def __init__(self, *args, **kwargs):
            # Do not raise ValueError
            super().__init__(*args, **kwargs)
            self._tools = {}
        def tool(self):
            def decorator(func):
                self._tools[func.__name__] = func
                return func
            return decorator
        def run(self, *args, **kwargs):
            pass
    monkeypatch.setattr(fastmcp, "FastMCP", DummyFastMCP)
    # Import app after patching
    app_module = importlib.import_module("mcp_terminal_server.main")
    with TestClient(app_module.app) as client:
        yield client


# Permite que todos os testes sejam executados como assíncronos
@pytest.fixture(scope="session")
def event_loop():
    """Cria uma instância do event loop para a sessão de testes."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
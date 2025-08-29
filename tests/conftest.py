import sys
import os

# Add the 'src' directory to sys.path to ease imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


import pytest
import asyncio
from fastapi.testclient import TestClient

import importlib

@pytest.fixture
def test_client(monkeypatch):
    """Fixture for FastAPI TestClient, with patch for FastMCP if needed."""
    # Patch FastMCP to avoid ValueError during tests
    from mcp.server import fastmcp
    from fastapi import FastAPI
    
    class DummyFastMCP:
        def __init__(self, name, description):
            self.name = name
            self.description = description
            self._tools = {}
            self.app = FastAPI()  # Create a FastAPI app
        
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
    with TestClient(app_module.app.app) as client:  # Access the FastAPI app
        yield client


# Allows all tests to be run as asynchronous
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop instance for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
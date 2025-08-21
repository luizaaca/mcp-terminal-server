# MCP Terminal Server

A MCP (Model Context Protocol) server for secure execution of terminal commands via LLMs, with full operating system control.

## 🚀 Features

- **Universal Execution**: Full support for Windows / Linux / macOS
- **Full Control**: Administrative commands with controlled privilege elevation
- **Security**: Mandatory confirmation before execution
- **Streaming**: Real-time command output
- **Persistence**: Maintains context (working directory, environment variables)
- **Concurrency**: Concurrent execution with process management
- **Cancellation**: Detection and interruption of long-running commands
- **History**: Database of executed commands

## 📦 Installation

```bash
pip install mcp-terminal-server
```

### Development

```bash
git clone https://github.com/usuario/mcp-terminal-server
cd mcp-terminal-server
pip install -e ".[dev]"
```

## 🔧 Usage

### As an MCP Server

```bash
mcp-terminal-server --port 8000 --host localhost
```

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "terminal": {
      "command": "mcp-terminal-server",
      "args": ["--port", "8000"]
    }
  }
}
```

### Programmatic

```python
from mcp_terminal_server import MCPTerminalServer

server = MCPTerminalServer()
await server.start()
```

## 🏗️ Project Structure

```
mcp-terminal-server/
├── README.md
├── LICENSE
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── .gitignore
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── release.yml
├── src/
│   └── mcp_terminal_server/
│       ├── __init__.py
│       ├── main.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── executor.py          # CommandExecutor
│       │   ├── session.py           # SessionManager
│       │   ├── security.py          # SecurityManager
│       │   └── database.py          # DatabaseManager
│       ├── mcp/
│       │   ├── __init__.py
│       │   ├── server.py            # MCPServer
│       │   └── handlers.py          # Request handlers
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── platform.py          # OS detection
│       │   ├── process.py           # Process utilities
│       │   └── validation.py        # Input validation
│       └── data/
│           ├── commands.sql         # Initial schema
│           └── known_commands.json  # Known commands
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_executor.py
│   ├── test_session.py
│   ├── test_security.py
│   ├── test_database.py
│   ├── test_server.py
│   └── integration/
│       ├── __init__.py
│       ├── test_full_workflow.py
│       └── test_platforms.py
├── docs/
│   ├── api.md
│   ├── security.md
│   ├── examples.md
│   └── troubleshooting.md
└── scripts/
    ├── setup.py
    └── build.sh
```

## 🔒 Security

- **Mandatory confirmation** for sensitive commands
- **Automatic detection** of administrative commands
- **Controlled privilege escalation**
- **Input validation** and sanitization
- **Comprehensive logging**

## 🧪 Tests

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/

# Coverage
pytest --cov=mcp_terminal_server tests/
```

## 📋 Available Commands

### Basic
- `execute_command`: Execute a command in the terminal
- `get_current_directory`: Return the current working directory
- `change_directory`: Change the working directory
- `list_processes`: List active processes
- `cancel_command`: Cancel a running command

### Advanced
- `get_system_info`: System information
- `get_command_history`: Command history
- `set_environment_var`: Set an environment variable
- `get_environment_vars`: List environment variables

## 🤝 Contributing

1. Fork the repository
2. Create a branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## ⚠️ Warning

This server allows unrestricted execution of system commands. Run only in trusted environments and always review commands before execution.
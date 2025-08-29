# MCP Terminal Server

A MCP (Model Context Protocol) server for executing terminal commands.

## 🚀 Features

- **Windows CMD Execution**: Execute commands in a persistent Windows `cmd.exe` session.
- **Session Persistence**: Maintains context (working directory, environment variables) across commands for a given session ID.
- **Security**: Includes a confirmation mechanism for potentially destructive commands.

## 📦 Installation

First, clone the repository and navigate into the directory:
```bash
git clone https://github.com/usuario/mcp-terminal-server
cd mcp-terminal-server
```

### Development

```bash
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

## 🏗️ Project Structure

```
mcp-terminal-server/
├── README.md
├── LICENSE
├── pyproject.toml
├── .gitignore
├── .github/
│   └── workflows/
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
│   └── integration/
│       ├── __init__.py
│       ├── test_full_workflow.py
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

- `execute_command`: Execute a command in the terminal

## 🗺️ Roadmap

- **Multi-OS Support**: Automatically detect the operating system and provide shell-specific commands.
- **Command Layer**: Implement a command abstraction layer before the executor for better control and extensibility.
- **Enhanced Security**: Improve the security and confirmation logic for sensitive operations.

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

# MCP Terminal Server

A MCP (Model Context Protocol) server for executing terminal commands.

## 🚀 Features

- **Windows CMD Execution**: Execute commands in a persistent Windows `cmd.exe` session.
- **Session Persistence**: Maintains context (working directory, environment variables) across commands for a given session ID.
- **Security**: Includes a confirmation mechanism for potentially destructive commands.


## 🛠️ Set up your environment
First, let’s install uv and set up our Python project and environment:

### macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
### Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"


## 📦 Installation

First, clone the repository and navigate into the directory:
```bash
git clone https://github.com/luizaaca/mcp-terminal-server
cd mcp-terminal-server
```

## 🔧 Usage

### Run as MCP Server

```bash
python cli.py
##or
uv run src/mcp_terminal_server/main.py
```

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "terminal": {
      "command": "PATH\\TO\\UV\\uv.exe",
      "args": [
        "--directory",
        "PATH\\TO\\PROJECT\\SRC\\mcp_terminal_server\\",
        "main.py"
      ]
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
│       │   └── security.py          # SecurityManager
│       └── data/
│           └── known_commands.json  # Known commands
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_main.py
│   ├── test_executor.py
│   ├── test_session.py
│   └── test_security.py

```

## 🔒 Security

- **Mandatory confirmation** for sensitive commands
- **Automatic detection** of administrative commands
- **Controlled privilege escalation**

## 🧪 Tests

```bash
# Unit tests
pytest tests/

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

This server allows unrestricted execution of system commands, making it possible to edit files and have total control over the operating system. Run only in trusted environments and always review commands before execution.

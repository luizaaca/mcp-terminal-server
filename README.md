# MCP Terminal Server

A MCP (Model Context Protocol) server for secure execution of terminal commands via LLMs, with full operating system control.

## 🚀 Features

- **Windows Execution**: Currently support for Windows, Linux based in future versions.
- **Full Control**: Administrative commands with controlled privilege elevation
- **Security**: Mandatory confirmation before execution
- **Persistence**: Maintains context (working directory, environment variables)
- **Concurrency**: Concurrent execution with process management

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


## 📋 Available Commands

- `execute_command`: Execute a command in the terminal

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

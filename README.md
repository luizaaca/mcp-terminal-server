# MCP Terminal Server

Um servidor MCP (Model Context Protocol) para execução segura de comandos de terminal via LLM, com controle total do sistema operacional.

## 🚀 Funcionalidades

- **Execução Universal**: Suporte completo Windows/Linux/macOS
- **Controle Total**: Comandos administrativos com elevação automática de privilégios
- **Segurança**: Confirmação obrigatória antes da execução
- **Streaming**: Output em tempo real dos comandos
- **Persistência**: Mantém contexto (diretório, variáveis de ambiente)
- **Concorrência**: Execução simultânea com controle de processos
- **Cancelamento**: Detecção e interrupção de comandos longos
- **Histórico**: Base de dados com comandos executados

## 📦 Instalação

```bash
pip install mcp-terminal-server
```

### Desenvolvimento

```bash
git clone https://github.com/usuario/mcp-terminal-server
cd mcp-terminal-server
pip install -e ".[dev]"
```

## 🔧 Uso

### Como Servidor MCP

```bash
mcp-terminal-server --port 8000 --host localhost
```

### Configuração em Claude Desktop

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

### Programático

```python
from mcp_terminal_server import MCPTerminalServer

server = MCPTerminalServer()
await server.start()
```

## 🏗️ Estrutura do Projeto

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
│       │   ├── process.py           # Process utils
│       │   └── validation.py        # Input validation
│       └── data/
│           ├── commands.sql         # Schema inicial
│           └── known_commands.json  # Comandos conhecidos
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

## 🔒 Segurança

- **Confirmação obrigatória** para todos os comandos
- **Detecção automática** de comandos administrativos
- **Elevação controlada** de privilégios
- **Validação** de entrada e sanitização
- **Logging** completo de ações

## 🧪 Testes

```bash
# Testes unitários
pytest tests/

# Testes de integração
pytest tests/integration/

# Coverage
pytest --cov=mcp_terminal_server tests/
```

## 📋 Comandos Disponíveis

### Básicos
- `execute_command`: Executa comando no terminal
- `get_current_directory`: Retorna diretório atual
- `change_directory`: Altera diretório de trabalho
- `list_processes`: Lista processos ativos
- `cancel_command`: Cancela comando em execução

### Avançados
- `get_system_info`: Informações do sistema
- `get_command_history`: Histórico de comandos
- `set_environment_var`: Define variável de ambiente
- `get_environment_vars`: Lista variáveis de ambiente

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## ⚠️ Aviso

Este servidor permite execução irrestrita de comandos do sistema. Use apenas em ambientes confiáveis e sempre revise comandos antes da execução.
import pytest
import asyncio
import platform
from pathlib import Path
from unittest.mock import patch, AsyncMock

from src.mcp_terminal_server.core.executor import CommandExecutor
from src.mcp_terminal_server.core.session import Session


@pytest.fixture
def executor():
    """Fixture para criar uma instância do CommandExecutor."""
    return CommandExecutor()


@pytest.fixture
def test_session(tmp_path):
    """Fixture para criar uma sessão de teste."""
    session = Session("test-session", str(tmp_path))
    return session


@pytest.mark.asyncio
async def test_execute_simple_command(executor, test_session):
    """Testa execução de um comando simples."""
    exit_code, output = await executor.execute_command("echo 'Hello World'", test_session)

    assert exit_code == 0
    assert "Hello World" in output


@pytest.mark.asyncio
async def test_execute_command_with_error(executor, test_session):
    """Testa execução de um comando que retorna erro."""
    # Comando que falha (exit code != 0)
    exit_code, output = await executor.execute_command("exit 1", test_session)

    assert exit_code == 1


@pytest.mark.asyncio
async def test_execute_command_with_stderr(executor, test_session):
    """Testa captura de saída de erro padrão."""
    if platform.system() == "Windows":
        command = 'echo "Error message" 1>&2'
    else:
        command = 'echo "Error message" >&2'

    exit_code, output = await executor.execute_command(command, test_session)

    assert exit_code == 0
    assert "Error message" in output
    assert "[STDERR]" in output


@pytest.mark.asyncio
async def test_execute_command_in_different_directory(executor, test_session, tmp_path):
    """Testa execução de comando em diretório específico."""
    # Criar um subdiretório
    subdir = tmp_path / "test_subdir"
    subdir.mkdir()

    # Mudar para o subdiretório
    test_session.change_directory(str(subdir))

    # Executar comando que mostra o diretório atual
    if platform.system() == "Windows":
        command = "cd"
    else:
        command = "pwd"

    exit_code, output = await executor.execute_command(command, test_session)

    assert exit_code == 0
    assert str(subdir) in output


@pytest.mark.asyncio
async def test_command_cancellation(executor, test_session):
    """Testa cancelamento de comando em execução."""
    # Comando que demora (no Windows usamos timeout, no Unix sleep)
    if platform.system() == "Windows":
        command = "timeout /t 5"
    else:
        command = "sleep 5"

    # Criar tarefa e cancelar após um tempo
    task = asyncio.create_task(executor.execute_command(command, test_session))

    # Aguardar um pouco e cancelar
    await asyncio.sleep(0.1)
    task.cancel()

    try:
        exit_code, output = await task
        # Se não foi cancelado, verificar se pelo menos iniciou
        assert exit_code in [0, -1]  # 0 para sucesso, -1 para erro/cancelamento
    except asyncio.CancelledError:
        pytest.fail("Command was cancelled but should have handled gracefully")


@pytest.mark.asyncio
async def test_invalid_command(executor, test_session):
    """Testa execução de comando inválido."""
    exit_code, output = await executor.execute_command("invalid_command_xyz", test_session)

    # Comando inválido deve retornar código de erro
    assert exit_code != 0
    assert "invalid_command_xyz" in output or "not found" in output or "not recognized" in output


@pytest.mark.asyncio
async def test_environment_variables(executor, test_session):
    """Testa se variáveis de ambiente são passadas corretamente."""
    # Adicionar variável de ambiente à sessão
    test_session.environment_variables["TEST_VAR"] = "test_value"

    # Comando que imprime a variável
    if platform.system() == "Windows":
        command = "echo %TEST_VAR%"
    else:
        command = "echo $TEST_VAR"

    exit_code, output = await executor.execute_command(command, test_session)

    assert exit_code == 0
    assert "test_value" in output


@pytest.mark.asyncio
async def test_process_registration_and_cleanup(executor, test_session):
    """Testa se processos são registrados e removidos corretamente da sessão."""
    # Verificar que não há processos ativos inicialmente
    assert len(test_session.active_processes) == 0

    # Executar comando
    await executor.execute_command("echo 'test'", test_session)

    # Após execução, não deve haver processos ativos
    assert len(test_session.active_processes) == 0


@pytest.mark.asyncio
async def test_read_stream_with_none():
    """Testa o método _read_stream com stream None."""
    executor = CommandExecutor()

    result = await executor._read_stream(None)
    assert result == b""


@pytest.mark.asyncio
async def test_read_stream_with_data():
    """Testa o método _read_stream com dados."""
    executor = CommandExecutor()

    # Criar um StreamReader mock
    mock_stream = AsyncMock()
    mock_stream.read.return_value = b"test data"

    result = await executor._read_stream(mock_stream)

    assert result == b"test data"
    mock_stream.read.assert_called_once()

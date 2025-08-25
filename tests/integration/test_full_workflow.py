import pytest
import uuid

@pytest.mark.asyncio
async def test_full_workflow(test_client):
    """
    Testa um fluxo completo: conectar, executar comando, verificar output e desconectar.
    """
    session_id = str(uuid.uuid4())
    
    with test_client.websocket_connect(f"/ws/{session_id}") as websocket:
        # 1. Executar um comando simples
        websocket.send_json({
            "command": "execute_command",
            "params": {"command": "echo 'Integration Test'"}
        })
        
        # Receber o stream de output
        stream_data = websocket.receive_json()
        assert stream_data["type"] == "stream"
        assert "Integration Test" in stream_data["output"]
        
        # Receber a resposta final
        final_response = websocket.receive_json()
        assert final_response["success"] is True
        assert final_response["exit_code"] == 0
        assert "Integration Test" in final_response["output"]

        # 2. Mudar de diretório
        websocket.send_json({
            "command": "change_directory",
            "params": {"path": "src"}
        })
        cd_response = websocket.receive_json()
        assert "src" in cd_response["current_directory"]

        # 3. Obter histórico de comandos
        websocket.send_json({
            "command": "get_command_history",
            "params": {"limit": 5}
        })
        history_response = websocket.receive_json()
        
        # Verificar a estrutura da resposta do histórico
        assert "history" in history_response
        assert isinstance(history_response["history"], list)
        assert len(history_response["history"]) >= 1
        
        # Verificar o primeiro comando no histórico
        first_command = history_response["history"][0]
        assert isinstance(first_command, dict)
        assert "command" in first_command
        assert "echo 'Integration Test'" in first_command["command"]
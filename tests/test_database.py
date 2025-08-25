import pytest

@pytest.mark.asyncio
async def test_log_and_get_history(temp_db):
    """
    Testa se o log de um comando é salvo e pode ser recuperado.
    """
    # Arrange
    session_id = "test-session"
    
    # Act
    temp_db.log_command(
        session_id=session_id,
        command="echo 'Hello DB'",
        output="Hello DB\n",
        exit_code=0,
        success=True
    )
    
    history = temp_db.get_history(session_id=session_id, limit=10)
    
    # Assert
    assert len(history) == 1, f"Expected 1 entry, got {len(history)}. All entries: {all_history}"
    log_entry = history[0]
    assert log_entry["session_id"] == session_id
    assert log_entry["command"] == "echo 'Hello DB'"
    assert log_entry["success"] is True
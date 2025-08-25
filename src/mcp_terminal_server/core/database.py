import sqlite3
from pathlib import Path
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages the database for command history.
    """
    def __init__(self, db_path: Path = None):
        """
        Initialize the DatabaseManager.

        Args:
            db_path (Path, optional): Path to the database file. If None, uses the default in 'src/mcp_terminal_server/data/terminal_history.db'.
        """
        if db_path is None:
            self.db_path = Path(__file__).parent.parent / "data" / "terminal_history.db"
        else:
            self.db_path = db_path
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = None
        self._initialize_db()

    def _get_connection(self):
        """Return a new connection to the database."""
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def _initialize_db(self):
        """
        Ensure the database and history table exist.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Read the SQL script to create the table
                sql_script_path = self.db_path.parent / "commands.sql"
                if not sql_script_path.exists():
                    logger.error(f"SQL schema file not found at: {sql_script_path}")
                    return

                with open(sql_script_path, 'r') as f:
                    schema = f.read()
                
                cursor.executescript(schema)
                conn.commit()
                logger.info("Database initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error initializing the database: {e}")
        except IOError as e:
            logger.error(f"Error reading the SQL schema file: {e}")

    def log_command(self, session_id: str, command: str, output: str, exit_code: int, success: bool):
        """
        Record an executed command in the database.

        Args:
            session_id (str): The session ID where the command was executed.
            command (str): The executed command.
            output (str): The command output.
            exit_code (int): The command exit code.
            success (bool): Whether the command executed successfully.
        """
        sql = """
        INSERT INTO command_history (session_id, command, output, exit_code, success)
        VALUES (?, ?, ?, ?, ?)
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (session_id, command, output, exit_code, success))
                conn.commit()
                logger.info(f"Command logged for session {session_id}: {command}")
        except sqlite3.Error as e:
            logger.error(f"Error logging command to the database: {e}")

    def get_history(self, session_id: str = None, limit: int = 100):
        """
        Retrieve the command history.

        Args:
            session_id (str, optional): Filter history by session ID. If None, returns across all sessions.
            limit (int, optional): Limit the number of records returned.

        Returns:
            list: A list of dictionaries containing history records.
        """
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row  # Enable dictionary-like access
                cursor = conn.cursor()
                if session_id:
                    sql = "SELECT * FROM command_history WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?"
                    cursor.execute(sql, (session_id, limit))
                else:
                    sql = "SELECT * FROM command_history ORDER BY timestamp DESC LIMIT ?"
                    cursor.execute(sql, (limit,))
                
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    row_dict = dict(row)
                    if 'success' in row_dict:
                        row_dict['success'] = bool(row_dict['success'])
                    result.append(row_dict)
                    
                return result
        except sqlite3.Error as e:
            logger.error(f"Error fetching command history: {e}")
            return []

    def close(self):
        """Close the database connection if open."""
        # Connections are managed by `with` blocks, so this method may not be strictly necessary
        # unless a persistent connection is used in the future.
        logger.info("Database manager shut down.")

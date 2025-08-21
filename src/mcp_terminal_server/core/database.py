import sqlite3
from pathlib import Path
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gerencia o banco de dados para o histórico de comandos.
    """
    def __init__(self, db_path: Path = None):
        """
        Inicializa o DatabaseManager.

        Args:
            db_path (Path, optional): Caminho para o arquivo do banco de dados. 
                                      Se None, usa o padrão em 'src/mcp_terminal_server/data/terminal_history.db'.
        """
        if db_path is None:
            self.db_path = Path(__file__).parent.parent / "data" / "terminal_history.db"
        else:
            self.db_path = db_path
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = None
        self._initialize_db()

    def _get_connection(self):
        """Retorna uma nova conexão com o banco de dados."""
        try:
            return sqlite3.connect(self.db_path)
        except sqlite3.Error as e:
            logger.error(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def _initialize_db(self):
        """
        Garante que o banco de dados e a tabela de histórico existam.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Lê o script SQL para criar a tabela
                sql_script_path = self.db_path.parent / "commands.sql"
                if not sql_script_path.exists():
                    logger.error(f"Arquivo de schema SQL não encontrado em: {sql_script_path}")
                    return

                with open(sql_script_path, 'r') as f:
                    schema = f.read()
                
                cursor.executescript(schema)
                conn.commit()
                logger.info("Banco de dados inicializado com sucesso.")
        except sqlite3.Error as e:
            logger.error(f"Erro ao inicializar o banco de dados: {e}")
        except IOError as e:
            logger.error(f"Erro ao ler o arquivo de schema SQL: {e}")

    def log_command(self, session_id: str, command: str, output: str, exit_code: int, success: bool):
        """
        Registra um comando executado no banco de dados.

        Args:
            session_id (str): O ID da sessão onde o comando foi executado.
            command (str): O comando que foi executado.
            output (str): A saída do comando.
            exit_code (int): O código de saída do comando.
            success (bool): Se o comando foi executado com sucesso.
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
                logger.info(f"Comando registrado para a sessão {session_id}: {command}")
        except sqlite3.Error as e:
            logger.error(f"Erro ao registrar comando no banco de dados: {e}")

    def get_history(self, session_id: str = None, limit: int = 100):
        """
        Recupera o histórico de comandos.

        Args:
            session_id (str, optional): Filtra o histórico por ID de sessão. Se None, retorna de todas as sessões.
            limit (int, optional): Limita o número de registros retornados.

        Returns:
            list: Uma lista de tuplas com os registros do histórico.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if session_id:
                    sql = "SELECT * FROM command_history WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?"
                    cursor.execute(sql, (session_id, limit))
                else:
                    sql = "SELECT * FROM command_history ORDER BY timestamp DESC LIMIT ?"
                    cursor.execute(sql, (limit,))
                
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Erro ao buscar histórico de comandos: {e}")
            return []

    def close(self):
        """Fecha a conexão com o banco de dados, se estiver aberta."""
        # As conexões são gerenciadas pelo `with`, então este método pode não ser estritamente necessário
        # a menos que uma conexão persistente seja usada no futuro.
        logger.info("Gerenciador de banco de dados finalizado.")

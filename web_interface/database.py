# Integração com SQLite
import sqlite3

class Database:
    def __init__(self, db_name="data.db"):
        self.connection = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def insert_log(self, prompt, response):
        with self.connection:
            self.connection.execute(
                "INSERT INTO logs (prompt, response) VALUES (?, ?)",
                (prompt, response)
            )

    def fetch_logs(self):
        with self.connection:
            return self.connection.execute("SELECT * FROM logs").fetchall()

# Exemplo de uso
if __name__ == "__main__":
    db = Database()
    db.insert_log("Qual é a capital da França?", "Paris")
    logs = db.fetch_logs()
    print(logs)
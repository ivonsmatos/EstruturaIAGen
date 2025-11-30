# Integração com PostgreSQL na nuvem
import psycopg2

class Database:
    def __init__(self):
        self.connection = psycopg2.connect(
            dbname="cloud_db",
            user="admin",
            password="password",
            host="cloud-db-instance.amazonaws.com",
            port="5432"
        )
        self.create_tables()

    def create_tables(self):
        with self.connection:
            self.connection.cursor().execute(
                """
                CREATE TABLE IF NOT EXISTS logs (
                    id SERIAL PRIMARY KEY,
                    prompt TEXT,
                    response TEXT,
                    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def insert_log(self, prompt, response):
        with self.connection:
            self.connection.cursor().execute(
                "INSERT INTO logs (prompt, response) VALUES (%s, %s)",
                (prompt, response)
            )

    def fetch_logs(self):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM logs")
            return cursor.fetchall()

# Exemplo de uso
if __name__ == "__main__":
    db = Database()
    db.insert_log("Qual é a capital da França?", "Paris")
    logs = db.fetch_logs()
    print(logs)
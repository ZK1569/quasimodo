import psycopg2
from contextlib import contextmanager

from src.utils.env import EnvVariable

class PostgresDatabase:
    def __init__(self):
        self.conn = self.create_connection()

    def create_connection(self):
        try:
            return psycopg2.connect(
                dbname=EnvVariable().db_name,
                user=EnvVariable().db_user,
                password=EnvVariable().db_password,
                host=EnvVariable().db_host,
                port=EnvVariable().db_port
            )
        except Exception as e:
            print("Erreur de connexion à la base de données :", e)
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def test_connection(self):
        with self.cursor_context() as cursor:
            cursor.execute("SELECT 1;")


    @contextmanager
    def cursor_context(self):
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
        

postgresql_database = PostgresDatabase()

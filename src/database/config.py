from dotenv import load_dotenv
from contextlib import contextmanager
import os
import psycopg2

# Charge les variables de .env
load_dotenv()

@contextmanager
def db_cursor():
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT")
    )
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    finally:
        cursor.close()
        conn.close()

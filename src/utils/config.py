from contextlib import contextmanager
import psycopg2

from src.utils.env import EnvVariable

@contextmanager
def db_cursor():
    conn = psycopg2.connect(
        dbname=EnvVariable().db_name,
        user=EnvVariable().db_user,
        password=EnvVariable().db_password,
        host=EnvVariable().db_host,
        port=EnvVariable().db_port
    )
    cursor = conn.cursor()
    # Connection test
    try:
        cursor.execute("SELECT 1")
        print("Database connection successful!")
    except Exception as e:
        print("Database connection failed :", e)

    # If the connection succeeds, yield the cursor
    try:
        yield cursor
        conn.commit()
    finally:
        cursor.close()
        conn.close()

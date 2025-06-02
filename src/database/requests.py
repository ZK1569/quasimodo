from src.database.config import db_cursor

def select_faces():
    with db_cursor() as cursor:
        cursor.execute("SELECT id, firstname, face_embeddings FROM face")
        return cursor.fetchall()
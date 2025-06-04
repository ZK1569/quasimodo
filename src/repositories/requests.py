from src.utils.config import db_cursor

def select_faces():
    with db_cursor() as cursor:
        cursor.execute("SELECT id, firstname, lastname, face_embeddings FROM face")
        return cursor.fetchall()
    
def insert_face(firstname, lastname, face_embedding):
    try:
        with db_cursor() as cursor:
            cursor.execute(
                "INSERT INTO face (firstname, lastname, face_embeddings) VALUES (%s, %s, %s)",
                (firstname, lastname, face_embedding)
            )
        return True
    except Exception as e:
        print(f"Insertion failed: {e}")
        return False
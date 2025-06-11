from typing import Generator

from src.utils.config import postgresql_database
from src.repositories.repository import FaceRepositoryAbs


class FaceRepository(FaceRepositoryAbs):
    def __init__(self):
        pass

    def select_faces(self):
        with postgresql_database.cursor_context() as cursor:
            cursor.execute(
                "SELECT id, firstname, lastname, face_embeddings FROM face")
            return cursor.fetchall()

    def insert_face(self, firstname, lastname, face_embedding):
        print(f"Inserting face: {firstname} {lastname}")
        try:
            with postgresql_database.cursor_context() as cursor:
                cursor.execute(
                    "INSERT INTO face (firstname, lastname, face_embeddings) VALUES (%s, %s, %s)",
                    (firstname, lastname, face_embedding)
                )
                return True
        except Exception as e:
            print(f"Insertion failed: {e}")
            return False


def get_face_repository() -> Generator[FaceRepositoryAbs, None, None]:
    yield FaceRepository()

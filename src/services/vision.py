from typing import Any, Generator
import numpy as np
import insightface
from fastapi import Depends

from src.services.service import VisionServiceAbs
from src.repositories.repository import FaceRepositoryAbs
from src.repositories.face import FaceRepository, get_face_repository
from src.models.face import Face


class VisionService(VisionServiceAbs):
    def __init__(self, face_repository: FaceRepositoryAbs):
        # Load face detector and MobileFaceNet model
        self.face_repository = face_repository
        self.detector = insightface.app.FaceAnalysis(
            name='buffalo_s', providers=['CPUExecutionProvider'])
        self.detector.prepare(ctx_id=0, det_size=(640, 640))

    def get_image_embedding(self, frame: Any) -> list:
        faces = self.detector.get(frame)
        if len(faces) == 0:
            print("No faces detected in the image.")
            return None
        embeddings = [list(face.embedding) for face in faces]
        print(f"Extracted {len(embeddings)} embeddings.")
        return embeddings

    def process_image(self, frame: Any) -> Face | None:
        # print("Processing image with shape:", frame.shape)
        embeddings = self.get_image_embedding(frame)
        if not embeddings:
            return
        for embedding in embeddings:
            return self.find_matching_face(embedding)

    def cosine_similarity(self, vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def find_matching_face(self, target_embedding, threshold=0.6):
        all_results = self.face_repository.select_faces()
        if not all_results:
            return None

        target_embedding = np.array(target_embedding, dtype=np.float32)

        for face_id, firstname, lastname, binary_embedding in all_results:
            stored_embedding = np.frombuffer(
                binary_embedding, dtype=np.float32)
            similarity = self.cosine_similarity(
                target_embedding, stored_embedding)
            if similarity > threshold:
                face = Face()
                face.name = lastname
                face.firstname = firstname
                face.face_id = face_id
                face.similarity = similarity
                return face

        return None


def get_vision_service(
    face_repository: FaceRepositoryAbs = Depends(get_face_repository)
) -> Generator[VisionServiceAbs, None, None]:
    yield VisionService(face_repository)


from typing import Any, Generator
import numpy as np
import insightface

from src.services.service import VisionServiceAbs
from src.repositories.requests import select_faces

class VisionService(VisionServiceAbs):
    def __init__(self):
        # Load face detector and MobileFaceNet model
        self.detector = insightface.app.FaceAnalysis(name='buffalo_s', providers=['CPUExecutionProvider'])
        self.detector.prepare(ctx_id=0, det_size=(640, 640))

    def get_image_embedding(self, frame: Any) -> list:
        faces = self.detector.get(frame)
        if len(faces) == 0:
            print("No faces detected in the image.")
            return None
        embeddings = [list(face.embedding) for face in faces]
        print(f"Extracted {len(embeddings)} embeddings.")
        return embeddings

    def process_image(self, frame: Any) -> None:
        print("Processing image with shape:", frame.shape)
        embeddings = self.get_image_embedding(frame)
        if not embeddings:
            return
        for embedding in embeddings:
            results = find_matching_face(embedding)
            print(results)
            if results:
                print(f"Face match: {results[2]}, {results[1]} (id={results[0]}, similarity={results[3]:.2f})")
            else:
                print("Unknown face detected")




def get_vision_service() -> Generator[VisionServiceAbs, None, None]:
    yield VisionService()

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def find_matching_face(target_embedding, threshold=0.6):

    all_results = select_faces()
    if not all_results:
        return None
    
    target_embedding = np.array(target_embedding, dtype=np.float32)
    
    for face_id, firstname, lastname, binary_embedding in all_results:
        stored_embedding = np.frombuffer(binary_embedding, dtype=np.float32)
        similarity = cosine_similarity(target_embedding, stored_embedding)
        if similarity > threshold:
            return (face_id, firstname, lastname, similarity)
        
    return None 
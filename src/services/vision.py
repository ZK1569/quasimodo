from typing import Any, Generator
import numpy as np
import insightface

from src.services.service import VisionServiceAbs


class VisionService(VisionServiceAbs):
    def __init__(self):
        # Load face detector and MobileFaceNet model
        self.detector = insightface.app.FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        self.detector.prepare(ctx_id=0, det_size=(640, 640))

    def process_image(self, frame: Any) -> None:
        # frame is a numpy array (BGR, as from OpenCV)
        print("Processing image with shape:", frame.shape)
        faces = self.detector.get(frame)
        print(f"Detected {len(faces)} faces.")
        for face in faces:
            # face.embedding is the MobileFaceNet feature vector
            print("Detected face embedding:", face.embedding)
            # You can now compare embeddings for recognition



def get_vision_service() -> Generator[VisionServiceAbs, None, None]:
    yield VisionService()

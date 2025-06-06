from abc import ABC, abstractmethod
from typing import Any

class FaceRepositoryAbs(ABC):

    @abstractmethod
    def insert_face(self, frame: Any) -> None:
        pass

    @abstractmethod
    def select_faces(self) -> list:
        pass



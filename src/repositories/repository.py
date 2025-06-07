from abc import ABC, abstractmethod
from typing import Any


class FaceRepositoryAbs(ABC):

    @abstractmethod
    def insert_face(self, frame: Any) -> None:
        pass

    @abstractmethod
    def select_faces(self) -> list:
        pass


class NotificationRepositoryAbs(ABC):

    @abstractmethod
    def send_message(self, message: str, image: Any | None = None) -> None:
        pass

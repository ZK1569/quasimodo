from abc import ABC, abstractmethod
from typing import Any

from src.models.face import Face


class VisionServiceAbs(ABC):

    @abstractmethod
    def process_image(self, frame: Any) -> Face | None:
        pass


class AudioServiceAbs(ABC):

    @abstractmethod
    def process_audio(self, data: bytes) -> None:
        pass


class NotificationServiceAbs(ABC):
    @abstractmethod
    def send_message(self, message: str, image: Any | None = None) -> None:
        pass

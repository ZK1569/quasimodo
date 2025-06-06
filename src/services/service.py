from abc import ABC, abstractmethod
from typing import Any


class VisionServiceAbs(ABC):

    @abstractmethod
    def process_image(self, frame: Any) -> None:
        pass


class AudioServiceAbs(ABC):

    @abstractmethod
    def process_audio(self, data: bytes) -> None:
        pass


class NotificationServiceAbs(ABC):
    @abstractmethod
    def send_message(self, message: str) -> None:
        pass

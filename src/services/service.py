from abc import ABC, abstractmethod
from typing import Any

from src.models.face import Face
from src.models.history import History


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


class HistoryServiceAbs(ABC):

    @abstractmethod
    def get_all_history(self) -> list[History]:
        pass

    @abstractmethod
    def add(self, face: Face) -> bool:
        pass


class LlmServiceAbs(ABC):

    @abstractmethod
    def get_llm_response(self, input_text: str) -> str:
        pass

    @abstractmethod
    def get_doorbell_notification(self, transcribed_message: str) -> str:
        pass


class SpeechServiceAbs(ABC):

    @abstractmethod
    def text_to_speech(self, input_text: str, type: str = None, output_filename: str = None) -> str:
        pass


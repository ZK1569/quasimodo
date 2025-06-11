from datetime import date
from abc import ABC, abstractmethod
from typing import Any, Dict

from src.models.face import Face
from src.models.history import History


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


class HistoryRepositoryAbs(ABC):

    @abstractmethod
    def add(self, face: Face) -> bool:
        pass

    @abstractmethod
    def get_all_history(self) -> list[History]:
        pass

    @abstractmethod
    def count_by_day(self, start: date, end: date) -> Dict[date, int]:
        pass

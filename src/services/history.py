from typing import Generator
from fastapi import Depends

from src.services.service import HistoryServiceAbs
from src.repositories.repository import HistoryRepositoryAbs
from src.repositories.history import get_history_repository
from src.models.face import Face
from src.models.history import History


class HistoryService(HistoryServiceAbs):
    def __init__(self, history_repository: HistoryRepositoryAbs):
        self.history_repository = history_repository

    def add(self, face: Face) -> bool:
        return self.history_repository.add(face)

    def get_all_history(self) -> list[History]:
        return self.history_repository.get_all_history()


def get_history_service(
    history_repository: HistoryRepositoryAbs = Depends(get_history_repository)
) -> Generator[HistoryServiceAbs, None, None]:
    yield HistoryService(history_repository)

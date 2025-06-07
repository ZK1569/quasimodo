from typing import Generator, Any

from fastapi import Depends

from src.services.service import NotificationServiceAbs
from src.repositories.notification import NotificationRepository, get_notification_repository
from src.repositories.repository import NotificationRepositoryAbs


class NotificationService(NotificationServiceAbs):
    def __init__(self, notification_repository: NotificationRepositoryAbs):
        self.notification_repository: NotificationRepository = notification_repository

    def send_message(self, message, image: Any | None = None) -> None:
        self.notification_repository.send_message(message, image)


def get_notification_service(
    repo: NotificationRepositoryAbs = Depends(get_notification_repository),
) -> Generator[NotificationServiceAbs, None, None]:
    yield NotificationService(repo)

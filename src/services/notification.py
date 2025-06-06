from typing import Generator

from fastapi import Depends

from src.services.service import NotificationServiceAbs
from src.repositories.notification import NotificationRepository, get_notification_repository


class NotificationService(NotificationServiceAbs):
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository: NotificationRepository = notification_repository

    def send_message(self, message) -> None:
        self.notification_repository.send_message(message)


def get_notification_service(
    repo: NotificationRepository = Depends(get_notification_repository),
) -> Generator[NotificationServiceAbs, None, None]:
    yield NotificationService(repo)

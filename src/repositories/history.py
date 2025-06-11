from typing import Generator, List, Dict
from datetime import date, timedelta

from src.repositories.repository import HistoryRepositoryAbs
from src.models.face import Face
from src.models.history import History
from src.utils.config import postgresql_database


class HistoryRepository(HistoryRepositoryAbs):
    def __init__(self):
        pass

    def add(self, face: Face) -> bool:
        fullname = face.firstname + " " + face.name
        try:
            with postgresql_database.cursor_context() as cursor:
                cursor.execute(
                    "INSERT INTO histories(fullname) VALUES (%s)",
                    (fullname,)
                )
                return True
        except Exception as e:
            print(f"Insertion history failed: {e}")
            return False

    def get_all_history(self) -> list[History]:
        with postgresql_database.cursor_context() as cursor:
            cursor.execute(
                "SELECT id, fullname, created_at FROM histories ORDER BY created_at DESC LIMIT 15")
            rows = cursor.fetchall()
            return [History(*row) for row in rows]

    def count_by_day(self, start: date, end: date) -> Dict[date, int]:
        with postgresql_database.cursor_context() as cursor:
            cursor.execute(
                """
                SELECT date_trunc('day', created_at)::date AS d,
                       COUNT(*)                        AS c
                FROM   histories
                WHERE  created_at >= %s AND created_at < %s
                GROUP  BY d
                """,
                (start, end),
            )
            return {row[0]: row[1] for row in cursor.fetchall()}


def get_history_repository() -> Generator[HistoryRepositoryAbs, None, None]:
    yield HistoryRepository()

from datetime import datetime


class History:
    def __init__(
        self,
        id: int,
        fullname: str,
        created_at: datetime
    ):
        self.id = id
        self.fullname = fullname
        self.created_at = created_at

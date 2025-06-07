class Face:
    def __init__(
        self,
        name: str = "",
        firstname: str = "",
        face_id: int = 0,
        similarity: float = 0
    ):
        self.name: str = name
        self.firstname: str = firstname
        self.face_id: int = face_id
        self.similarity: float = similarity

from typing import Generator

from src.services.service import AudioServiceAbs


class AudioService(AudioServiceAbs):
    def __init__(self):
        pass

    def process_audio(self, data: bytes) -> None:
        return

def get_audio_service() -> Generator[AudioServiceAbs, None, None]:
    yield AudioService()

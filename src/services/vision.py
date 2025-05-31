from typing import Any, Generator

from src.services.service import VisionServiceAbs


class VisionService(VisionServiceAbs):
    def __init__(self):
        pass

    def process_image(self, frame: Any) -> None:
        return



def get_vision_service() -> Generator[VisionServiceAbs, None, None]:
    yield VisionService()

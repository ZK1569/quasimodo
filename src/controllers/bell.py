import base64

import cv2
import numpy as np
from fastapi import APIRouter, Depends, WebSocket

from src.services.audio import AudioServiceAbs, get_audio_service
from src.services.service import AudioServiceAbs, VisionServiceAbs
from src.services.vision import VisionService, get_vision_service

router = APIRouter(prefix="/bell", tags=["bell"])

class ConnectionManager:
    def __init__(self):
        self.active_connection: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connection.append(websocket)

    async def disconnect(self, websocket: WebSocket): 
        await websocket.close()
        self.active_connection.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connection:
            await connection.send_text(message)


manager = ConnectionManager()

@router.websocket("/ws/video")
async def websocket_endpoint(
        websocket: WebSocket,
        vision_service: VisionServiceAbs = Depends(get_vision_service),
):

    await manager.connect(websocket)
    print("🎥 Video WebSocket connected")

    try:
        while True:
            data = await websocket.receive_text()
            img_data = base64.b64decode(data)
            np_arr = np.frombuffer(img_data, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            vision_service.process_image(frame)

    except Exception as e:
        print("❌ Video error:", e)
        await manager.disconnect(websocket)
    finally:
        await manager.disconnect(websocket)

@router.websocket("/ws/audio")
async def audio_stream_ws(
        websocket: WebSocket,
        audio_service: AudioServiceAbs = Depends(get_audio_service),
):
    await manager.connect(websocket)
    print("🔊 Audio WebSocket connected")

    try:
        while True:
            b64_audio = await websocket.receive_text()
            audio_bytes = base64.b64decode(b64_audio)

            audio_service.process_audio(audio_bytes)



    except Exception as e:
        print("❌ Audio error:", e)
        await manager.disconnect(websocket)
    finally:
        await manager.disconnect(websocket)

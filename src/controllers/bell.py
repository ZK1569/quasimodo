import base64

import cv2
import numpy as np
from fastapi import APIRouter, Depends, WebSocket
from starlette.websockets import WebSocketState

from src.services.audio import get_audio_service
from src.services.service import AudioServiceAbs, VisionServiceAbs, NotificationServiceAbs
from src.services.vision import get_vision_service

from src.services.notification import get_notification_service

router = APIRouter(prefix="/bell", tags=["bell"])


class ConnectionManager:
    def __init__(self):
        self.active_connection: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connection.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        if websocket.application_state != WebSocketState.DISCONNECTED:
            try:
                await websocket.close()
            except RuntimeError:
                pass  # déjà fermé

        if websocket in self.active_connection:
            self.active_connection.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connection:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/video")
async def websocket_endpoint(
        websocket: WebSocket,
        vision_service: VisionServiceAbs = Depends(get_vision_service),
        notification_service: NotificationServiceAbs = Depends(
            get_notification_service)
):

    await manager.connect(websocket)
    print("🎥 Video WebSocket connected")

    notification_service.send_message("Il y a un flux video qui est arrivé")

    try:
        while True:
            data = await websocket.receive_text()
            img_data = base64.b64decode(data)
            np_arr = np.frombuffer(img_data, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is not None:
                cv2.imwrite("last_frame.jpg", frame)

                vision_service.process_image(frame)

    except Exception as e:
        print("❌ Video error:", e)
    finally:
        await manager.disconnect(websocket)
        cv2.destroyAllWindows()


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
    finally:
        await manager.disconnect(websocket)

import base64

import cv2
import numpy as np
import json
from fastapi import APIRouter, Depends, WebSocket
from starlette.websockets import WebSocketState

from src.services.audio import get_audio_service
from src.services.service import AudioServiceAbs, VisionServiceAbs, NotificationServiceAbs, LlmServiceAbs, SpeechServiceAbs
from src.services.vision import get_vision_service
from src.services.notification import get_notification_service
from src.services.llm import get_llm_service
from src.services.speech import get_speech_service

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
                pass

        if websocket in self.active_connection:
            self.active_connection.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connection:
            await connection.send_text(message)


video_manager = ConnectionManager()
audio_manager = ConnectionManager()


@router.websocket("/ws/video")
async def websocket_endpoint(
        websocket: WebSocket,
        vision_service: VisionServiceAbs = Depends(get_vision_service),
        notification_service: NotificationServiceAbs = Depends(
            get_notification_service),
        speech_service: SpeechServiceAbs = Depends(get_speech_service),

):

    await video_manager.connect(websocket)
    print("🎥 Video WebSocket connected")

    try:
        while True:
            data = await websocket.receive_text()
            img_data = base64.b64decode(data)
            np_arr = np.frombuffer(img_data, dtype=np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                print("👤 Frame is None, continue")
                continue

            face = vision_service.process_image(frame)
            if face is None:
                print("👤 No face detected, continue")
                continue

            notification_service.send_message(
                f"{face.firstname} {face.name} est à la porte",
                frame
            )
            name, firstname = ("", "") if face.name == "unknow" else (
                face.name, face.firstname)
            message = f"Bonjour {name} {firstname}! Michel n'est pas là pour le moment, veuillez laisser un message ou revenir plus tard."
            print(f"🎤 Message to be sent: {message}")

            try:
                audio_stream = speech_service.text_to_speech(message)
                # audio_stream = None
                print(f"🎤 Audio stream generated")

                if audio_stream:
                    audio_stream.seek(0)
                    audio_bytes = audio_stream.read()
                    audio_base64 = base64.b64encode(
                        audio_bytes).decode('utf-8')

                    response_data = {
                        "type": "audio_response",
                        "audio": audio_base64
                    }

                    await websocket.send_text(json.dumps(response_data))
                    print(
                        f"🔊 Audio sent back to Raspberry Pi ({len(audio_bytes)} bytes)")

            except Exception as e:
                print(f"❌ Error generating audio: {e}")
                fallback_data = {
                    "type": "beep_notification",
                    "pattern": [440, 200, 554, 200]
                }
                await websocket.send_text(json.dumps(fallback_data))
                print("🔊 Sent beep notification as fallback")

            break

    except Exception as e:
        print("❌ Video error:", e)
    finally:
        await video_manager.disconnect(websocket)
        print("❌🎥 fin Video")


@router.websocket("/ws/audio")
async def audio_stream_ws(
        websocket: WebSocket,
        audio_service: AudioServiceAbs = Depends(get_audio_service),
        notification_service: NotificationServiceAbs = Depends(
            get_notification_service),
        llm_service: LlmServiceAbs = Depends(get_llm_service),
):
    await audio_manager.connect(websocket)
    print("🔊 Audio WebSocket connected")

    try:
        while True:
            b64_audio = await websocket.receive_text()
            audio_bytes = base64.b64decode(b64_audio)

            audio_service.process_audio(audio_bytes)

    except Exception as e:
        print("❌ Audio error:", e)
    finally:
        await audio_manager.disconnect(websocket)
        transcription = audio_service.transcribe()
        if transcription:
            cleaned_transcription = llm_service.get_llm_response(transcription)

            notification_message = llm_service.get_doorbell_notification(
                cleaned_transcription)

            notification_service.send_message(notification_message)

        else:
            cleaned_transcription = "No transcription available"
        print("🔊 Audio transcription:", cleaned_transcription)
        print("❌🔊 fin Audio")

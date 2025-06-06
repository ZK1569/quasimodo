from typing import Generator
import whisper
import numpy as np
import soundfile as sf
import base64
import io

from src.services.service import AudioServiceAbs


class AudioService(AudioServiceAbs):
    def __init__(self, sample_rate: int = 16000, language: str = 'fr', model_size: str = 'base'):
        self.model = whisper.load_model(model_size)  
        if sample_rate != 16000:
            raise ValueError("Whisper model requires audio with a sample rate of 16000 Hz.")
        self.sample_rate = sample_rate    # Whisper model needs 16000 Hz audio
        self.buffer = bytearray()
        self.language = language

    def process_audio(self, data: bytes) -> None:
        self.buffer.extend(data)

    def transcribe(self) -> str:
        if not self.buffer:
            print("[Warning] No audio to transcribe.")
            return

        audio_np = np.frombuffer(self.buffer, dtype=np.int16).astype(np.float32) / 32768.0
        print(f"[Info] Transcription of {len(audio_np)} audio chunks...")

        result = self.model.transcribe(audio_np, language=self.language)
        print("[Transcription]:", result["text"])

        return result["text"].strip()

    def reset_buffer(self) -> None:
        # Reset buffer after transcription
        self.buffer.clear()

def get_audio_service() -> Generator[AudioServiceAbs, None, None]:
    yield AudioService()

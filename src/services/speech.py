from src.services.service import SpeechServiceAbs
from src.utils.env import EnvVariable
from elevenlabs import ElevenLabs
import io
import struct
from typing import Generator


class SpeechService(SpeechServiceAbs):
    def __init__(self, default_voice="JBFqnCBsd6RMkjVDRZzb", default_model="eleven_multilingual_v1"):
        env = EnvVariable()
        self.eleven_labs_api_key = env.eleven_labs_api_key
        if not self.eleven_labs_api_key:
            raise ValueError(
                "ELEVEN_LABS_API_KEY is not set in the environment variables.")
        self.client = ElevenLabs(api_key=self.eleven_labs_api_key)

        self.voice = default_voice
        self.model = default_model

    def generate_audio(self, input_text: str) -> io.BytesIO:
        try:
            audio_stream = self.client.text_to_speech.stream(
                text=input_text,
                voice_id=self.voice,
                model_id=self.model,
                output_format="pcm_16000"
            )

            audio_bytes = io.BytesIO()

            pcm_data = b""
            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    pcm_data += chunk

            channels = 1
            sample_rate = 16000
            bits_per_sample = 16

            data_size = len(pcm_data)
            byte_rate = sample_rate * channels * bits_per_sample // 8
            block_align = channels * bits_per_sample // 8

            audio_bytes.write(b'RIFF')
            audio_bytes.write(struct.pack(
                '<I', 36 + data_size))
            audio_bytes.write(b'WAVE')

            audio_bytes.write(b'fmt ')
            audio_bytes.write(struct.pack('<I', 16))
            audio_bytes.write(struct.pack('<H', 1))
            audio_bytes.write(struct.pack('<H', channels))
            audio_bytes.write(struct.pack('<I', sample_rate))
            audio_bytes.write(struct.pack('<I', byte_rate))
            audio_bytes.write(struct.pack('<H', block_align))
            audio_bytes.write(struct.pack('<H', bits_per_sample))

            audio_bytes.write(b'data')
            audio_bytes.write(struct.pack('<I', data_size))
            audio_bytes.write(pcm_data)

            audio_bytes.seek(0)
            return audio_bytes

        except Exception as e:
            print(f"Erreur lors de la génération de la parole : {e}")
            return None

    def text_to_speech(self, input_text: str, type: str = "stream", output_filename: str = None) -> io.BytesIO | str:
        audio_stream = self.generate_audio(input_text)
        if not audio_stream:
            print("Aucun audio généré.")
            return None

        if type == "stream":
            return audio_stream

        elif type == "save":
            if not output_filename:
                output_filename = "/tmp/output.wav"

            with open(output_filename, "wb") as f:
                f.write(audio_stream.read())

            print(f"Audio généré avec succès : {output_filename}")
            return output_filename

        else:
            print("Invalid type")
            return None


def get_speech_service(
    default_voice: str = "JBFqnCBsd6RMkjVDRZzb",
    default_model: str = "eleven_multilingual_v1"
) -> Generator[SpeechServiceAbs, None, None]:
    yield SpeechService(default_voice, default_model)


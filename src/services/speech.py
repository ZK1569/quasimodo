from src.services.service import SpeechServiceAbs
from src.utils.env import EnvVariable
from elevenlabs import ElevenLabs
import io
from typing import Generator

class SpeechService(SpeechServiceAbs):
    def __init__(self, default_voice="JBFqnCBsd6RMkjVDRZzb", default_model="eleven_multilingual_v1"):
        env = EnvVariable()
        self.eleven_labs_api_key = env.eleven_labs_api_key
        if not self.eleven_labs_api_key:
            raise ValueError("ELEVEN_LABS_API_KEY is not set in the environment variables.")
        self.client = ElevenLabs(api_key=self.eleven_labs_api_key)

        self.voice = default_voice
        self.model = default_model


    def generate_audio(self, input_text: str) -> str:
        try:
            audio_stream = self.client.text_to_speech.stream(
                text=input_text,
                voice_id=self.voice,
                model_id=self.model
            )
            
            return audio_stream
            
        except Exception as e:
            print(f"Erreur lors de la génération de la parole : {e}")
            return ""

    def text_to_speech(self, input_text: str, type: str = "stream", output_filename : str = None) -> str:
        audio_stream = self.generate_audio(input_text)
        if not audio_stream:
            print("Aucun audio généré.")
            return ""
        
        if type == "stream":
            audio_bytes = io.BytesIO()
            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    audio_bytes.write(chunk)

            return audio_bytes
            
        elif type == "save":
            if not output_filename:
                output_filename ="/mnt/c/Users/Elise/Desktop/output.wav"
            with open(output_filename, "wb") as f:
                for chunk in audio_stream:
                    if isinstance(chunk, bytes):
                        f.write(chunk)
            
            print(f"Audio généré avec succès : {output_filename}")
            return output_filename
    
        else :
            print("Invalid type")
            return
        

def get_speech_service(
    default_voice: str = "JBFqnCBsd6RMkjVDRZzb",
    default_model: str = "eleven_multilingual_v1"
) -> Generator[SpeechServiceAbs, None, None]:
    yield SpeechService(default_voice, default_model)
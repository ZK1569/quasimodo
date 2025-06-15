from openai import OpenAI
from typing import Generator

from src.utils.env import EnvVariable
from src.services.service import LlmServiceAbs

class LlmService(LlmServiceAbs):
    def __init__(self, model_name="gpt-4o-mini"):
        self.model = model_name

        env = EnvVariable()
        self.chat_gpt_api_key = env.chat_gpt_api_key
        self.chat_gpt_client = OpenAI(api_key=self.chat_gpt_api_key)

    def get_llm_response(self, input_text):
        try:
            # Messages pour le contexte
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Tu es un assistant de correction pour des transcriptions automatiques d'audio en texte. "
                        "L'audio provient d'une caméra embarquée sur une sonnette d'entrée d'une maison. Le texte reçu provient donc d'un humain qui laisse un message après être venu,"
                        " et le propriétaire de la maison est absent"
                        "Ton rôle est de corriger les erreurs fréquentes de transcription vocale en français, comme les confusions phonétiques, les mots proches ou mal reconnus. "
                        "Ta mission est de reformuler le texte pour qu'il corresponde à ce que l'utilisateur a probablement voulu dire à l'oral, "
                        "en gardant un ton naturel et en respectant la syntaxe du français courant. "
                        "Ne modifie pas ce qui semble correct. Ne reformule pas tout : uniquement ce qui semble incohérent ou dû à une mauvaise interprétation vocale. "
                        "Si une phrase contient des mots mal transcrits, propose la version corrigée, sans explication ni commentaire."
                    )
                },
                {"role": "user", "content": input_text},
            ]

            chat_completion = self.chat_gpt_client.chat.completions.create(
                model=self.model, messages=messages
            )
            return chat_completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"Erreur OpenAI : {e}")

def get_llm_service(
    model_name: str = "gpt-4o"
) -> Generator[LlmServiceAbs, None, None]:
    yield LlmService(model_name)
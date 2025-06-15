import os

from dotenv import load_dotenv

class EnvVariableMeta(type):

    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class EnvVariable(metaclass=EnvVariableMeta):
    def __init__(self):
        load_dotenv()

        self.environnement = self._get_env("ENV", "development")
        self.version = self._get_env("VERSION", "0.0.0")
        self.address = self._get_env("ADDR", "localhost")
        self.port = self._get_env("PORT", "8080")

        self.db_name = self._get_env("DB_NAME", "postgres")
        self.db_user = self._get_env("DB_USER", "postgres")
        self.db_password = self._get_env("DB_PASSWORD", "postgres")
        self.db_host = self._get_env("DB_HOST", "localhost")
        self.db_port = self._get_env("DB_PORT", "5432")

        self.discord_bot_token = self._get_env("DISCORD_BOT_TOKEN")
        self.discord_channel = self._get_env("DISCORD_CHANNEL")

        self.chat_gpt_api_key = self._get_env("CHAT_GPT_API_KEY")

    @staticmethod
    def _get_env(env_path: str, default: str = "") -> str:
        val = os.getenv(env_path)
        return val if val else default

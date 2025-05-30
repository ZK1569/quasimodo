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

    @staticmethod
    def _get_env(env_path: str, default: str = "") -> str:
        val = os.getenv(env_path)
        return val if val else default

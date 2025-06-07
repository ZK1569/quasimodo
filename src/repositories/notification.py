from abc import ABCMeta
from typing import Dict, Optional, Generator, Any
import asyncio
import threading
import io
from pathlib import Path
import cv2
import numpy as np

from fastapi import Depends

import discord
from discord.ext import commands

from src.utils.env import EnvVariable
from src.repositories.repository import NotificationRepositoryAbs


class SingletonMeta(ABCMeta):
    _instances: Dict[type, "NotificationRepository"] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class NotificationRepository(NotificationRepositoryAbs, metaclass=SingletonMeta):

    def __init__(self) -> None:
        env = EnvVariable()
        self.channel_id: int = int(env.discord_channel)
        token: str = env.discord_bot_token

        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self._ready = threading.Event()

        @self.bot.event
        async def on_ready():
            print(f"[Discord] Connected as {self.bot.user}")
            self._ready.set()

        threading.Thread(target=self.bot.run, args=(
            token,), daemon=True).start()

    def send_message(self, message: str, image: Any | None = None) -> Optional[discord.Message]:
        if not self._ready.is_set():
            self._ready.wait(timeout=10)

        async def _send():
            channel = self.bot.get_channel(self.channel_id)
            if channel is None:
                channel = await self.bot.fetch_channel(self.channel_id)

            if image is None:
                return await channel.send(content=message)

            if isinstance(image, np.ndarray):
                ok, buf = cv2.imencode(".jpg", image)
                if not ok:
                    raise ValueError("Échec d'encodage de l'image")
                img_bytes = buf.tobytes()
                file = discord.File(io.BytesIO(img_bytes),
                                    filename="image.jpg")

            elif isinstance(image, (bytes, bytearray)):
                file = discord.File(io.BytesIO(image), filename="image.jpg")

            elif isinstance(image, (str, Path)):
                file = discord.File(str(image))

            else:
                raise TypeError(
                    "`image` doit être np.ndarray, bytes, str ou Path"
                )

            return await channel.send(content=message, file=file)

        fut = asyncio.run_coroutine_threadsafe(_send(), self.bot.loop)
        return fut.result()


def get_notification_repository() -> Generator[NotificationRepositoryAbs, None, None]:
    yield NotificationRepository()

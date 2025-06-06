from abc import ABCMeta
from typing import Dict, Optional
import asyncio
import threading

import discord
from discord.ext import commands

from src.utils.env import EnvVariable


class SingletonMeta(ABCMeta):
    _instances: Dict[type, "NotificationRepository"] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class NotificationRepository(metaclass=SingletonMeta):

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

    def send_message(self, message: str) -> Optional[discord.Message]:
        if not self._ready.is_set():
            self._ready.wait(timeout=10)

        async def _send():
            channel = self.bot.get_channel(self.channel_id)
            if channel is None:
                channel = await self.bot.fetch_channel(self.channel_id)
            return await channel.send(message)

        fut = asyncio.run_coroutine_threadsafe(_send(), self.bot.loop)
        return fut.result()


def get_notification_repository() -> NotificationRepository:
    return NotificationRepository()

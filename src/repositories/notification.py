from abc import ABCMeta
import typing
from typing import Dict, Optional, Generator, Any
import asyncio
import threading
import io
from pathlib import Path
from datetime import date
import calendar
import cv2
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib
from dateutil.relativedelta import relativedelta

from fastapi import Depends

import discord
from discord.ext import commands

from src.utils.env import EnvVariable
from src.repositories.repository import NotificationRepositoryAbs, HistoryRepositoryAbs
from src.repositories.history import get_history_repository

matplotlib.use("Agg")


class SingletonMeta(ABCMeta):
    _instances: Dict[type, "NotificationRepository"] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class NotificationRepository(NotificationRepositoryAbs, metaclass=SingletonMeta):

    def __init__(self, history_repo: HistoryRepositoryAbs) -> None:
        self.history_repository = history_repo

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

        @self.bot.command()
        async def history(ctx):
            histories = self.history_repository.get_all_history()
            lines = [
                f"- {h.fullname} est passé le {h.created_at:%d/%m/%Y à %H:%M}"
                for h in histories
            ]

            text = "Alors il y a :\n" + "\n".join(lines)

            await ctx.send(text)

        @self.bot.command(name="calendrier")
        async def calendrier(ctx, year: int | None = None, month: int | None = None):
            today = date.today()
            year = year or today.year
            month = month or today.month

            first = date(year, month, 1)
            last = first + relativedelta(months=1)

            counts = self.history_repository.count_by_day(first, last)

            def make_png() -> io.BytesIO:

                weeks = calendar.Calendar().monthdatescalendar(year, month)
                rows, cols = len(weeks), 7
                matrix = [
                    [counts.get(d, 0) if d.month == month else None for d in w]
                    for w in weeks
                ]

                cmap = colors.ListedColormap(
                    ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
                )
                norm = colors.BoundaryNorm([0, 1, 2, 5, 10, 999], cmap.N)

                fig, ax = plt.subplots(figsize=(cols, rows))
                ax.imshow(
                    [[0 if v is None else v for v in r] for r in matrix],
                    cmap=cmap, norm=norm
                )

                ax.set_xticks(range(cols))
                ax.set_xticklabels(["Lu", "Ma", "Me", "Je", "Ve", "Sa", "Di"])
                ax.set_yticks([])
                ax.tick_params(length=0)
                for spine in ax.spines.values():
                    spine.set_visible(False)

                buf = io.BytesIO()
                fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
                plt.close(fig)
                buf.seek(0)
                return buf

            # génération hors event-loop
            buf = await asyncio.to_thread(make_png)

            await ctx.send(
                content=f"Calendrier des passages – {calendar.month_name[month]} {year}",
                file=discord.File(buf, filename="heatmap.png")
            )

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


def get_notification_repository(
    history_repo: HistoryRepositoryAbs = Depends(get_history_repository)
) -> Generator[NotificationRepositoryAbs, None, None]:
    yield NotificationRepository(history_repo)

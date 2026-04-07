"""Discord bot instance and extension loader."""

from __future__ import annotations

import asyncio
import logging
from typing import Sequence

import discord
from discord.ext import commands

from usagibot.settings import Settings

logger = logging.getLogger(__name__)

COGS: Sequence[str] = (
    "usagibot.cogs.general",
    "usagibot.cogs.ff14",
    "usagibot.cogs.generative",
    "usagibot.cogs.music",
)


class UsagiBot(commands.Bot):
    settings: Settings

    def __init__(self, settings: Settings) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True

        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=intents)
        self.settings = settings

    async def setup_hook(self) -> None:
        for ext in COGS:
            await self.load_extension(ext)
            logger.info("Extension loaded: %s", ext)

        if self.settings.sync_guild_id is not None:
            guild = discord.Object(id=self.settings.sync_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info("Slash command sync (guild): %s", self.settings.sync_guild_id)
        else:
            await self.tree.sync()
            logger.info("Slash command sync (global)")

    async def on_ready(self) -> None:
        assert self.user is not None
        logger.info("Logged in as: %s (%s)", self.user, self.user.id)


def run_bot(settings: Settings) -> None:
    async def runner() -> None:
        bot = UsagiBot(settings)
        await bot.start(settings.discord_token)

    asyncio.run(runner())

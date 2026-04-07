"""Generative responses via OpenAI-compatible API (enabled by env vars)."""

from __future__ import annotations

import logging
from typing import cast

from discord import app_commands
from discord.ext import commands
from openai import OpenAI

from usagibot.bot import UsagiBot

logger = logging.getLogger(__name__)


class GenerativeCog(commands.Cog):
    """Short AI question and answer command."""

    def __init__(self, bot: UsagiBot) -> None:
        self.bot = bot

    @app_commands.command(name="ai", description="Ask a short question to the AI.")
    @app_commands.describe(prompt="Your question or request")
    async def ai_ask(self, interaction, prompt: str) -> None:
        key = self.bot.settings.openai_api_key
        if not key:
            await interaction.response.send_message(
                "Generative AI is disabled. Set `OPENAI_API_KEY` in your `.env` file.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(thinking=True)
        try:
            client = OpenAI(api_key=key)
            model = self.bot.settings.openai_model
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a concise assistant helping FFXIV players. "
                        "If information is uncertain, explicitly say so and keep replies short.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=800,
            )
            text = completion.choices[0].message.content or "(empty response)"
            if len(text) > 3900:
                text = text[:3890] + "..."
            await interaction.followup.send(text)
        except Exception:
            logger.exception("OpenAI request failed")
            await interaction.followup.send(
                "AI request failed. Please check API key, model name, and quota.",
                ephemeral=True,
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GenerativeCog(cast(UsagiBot, bot)))

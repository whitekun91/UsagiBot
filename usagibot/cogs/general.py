"""Basic diagnostics and info commands."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from usagibot import __version__


class GeneralCog(commands.Cog):
    """Ping and bot information commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency.")
    async def ping(self, interaction: discord.Interaction) -> None:
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"pong - **{latency_ms}** ms")

    @app_commands.command(name="about", description="Show bot summary and version.")
    async def about(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="Usagi Bot",
            description="A Discord bot focused on FFXIV info, everyday community features, generative AI, and music playback.",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Version", value=__version__, inline=True)
        embed.set_footer(text="Usagi means rabbit in Japanese.")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GeneralCog(bot))

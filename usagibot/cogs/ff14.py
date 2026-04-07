"""FFXIV reference links (expandable to Lodestone/API integrations)."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

FFXIV_LINKS = {
    "Official": "https://www.finalfantasyxiv.com/",
    "Lodestone": "https://na.finalfantasyxiv.com/lodestone/",
    "Patch Notes (Global)": "https://na.finalfantasyxiv.com/lodestone/topics/",
    "Teamcraft": "https://ffxivteamcraft.com/",
}


class FF14Cog(commands.Cog):
    """FFXIV helper commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ff14", description="Show useful FFXIV quick links.")
    async def ff14_links(self, interaction: discord.Interaction) -> None:
        lines = [f"- **{name}**: {url}" for name, url in FFXIV_LINKS.items()]
        embed = discord.Embed(
            title="FFXIV Quick Links",
            description="\n".join(lines),
            color=discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(FF14Cog(bot))

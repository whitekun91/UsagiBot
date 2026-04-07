"""FFXIV 관련 안내·링크 (추후 Lodestone/API 연동 확장)."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

# 자주 쓰는 공개 리소스 (필요 시 명령으로 분리·로컬 DB 연동 가능)
FFXIV_LINKS = {
    "공식": "https://www.finalfantasyxiv.com/",
    "Lodestone": "https://na.finalfantasyxiv.com/lodestone/",
    "갱신 노트(글로벌)": "https://na.finalfantasyxiv.com/lodestone/topics/",
    "팀크래프트(Teamcraft)": "https://ffxivteamcraft.com/",
}


class FF14Cog(commands.Cog):
    """FF14 안내."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ff14", description="FFXIV 관련 바로가기 링크를 보여줍니다.")
    async def ff14_links(self, interaction: discord.Interaction) -> None:
        lines = [f"• **{name}**: {url}" for name, url in FFXIV_LINKS.items()]
        embed = discord.Embed(
            title="FFXIV 바로가기",
            description="\n".join(lines),
            color=discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(FF14Cog(bot))

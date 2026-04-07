"""기본 진단·정보 명령."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from usagibot import __version__


class GeneralCog(commands.Cog):
    """핑, 봇 정보."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="봇 지연 시간을 확인합니다.")
    async def ping(self, interaction: discord.Interaction) -> None:
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"pong — **{latency_ms}** ms")

    @app_commands.command(name="about", description="봇 소개와 버전을 표시합니다.")
    async def about(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="Usagi Bot",
            description="FFXIV 정보·일상 대화·생성형 AI·음악 재생을 지향하는 Discord 봇입니다.",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="버전", value=__version__, inline=True)
        embed.set_footer(text="Usagi = 일본어로 토끼")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GeneralCog(bot))

"""OpenAI 호환 API를 통한 생성형 응답 (환경 변수로 활성화)."""

from __future__ import annotations

import logging
from typing import cast

from discord import app_commands
from discord.ext import commands
from openai import OpenAI

from usagibot.bot import UsagiBot

logger = logging.getLogger(__name__)


class GenerativeCog(commands.Cog):
    """짧은 질의응답."""

    def __init__(self, bot: UsagiBot) -> None:
        self.bot = bot

    @app_commands.command(name="ai", description="생성형 AI에게 짧게 질문합니다.")
    @app_commands.describe(prompt="질문 또는 요청 내용")
    async def ai_ask(self, interaction: discord.Interaction, prompt: str) -> None:
        key = self.bot.settings.openai_api_key
        if not key:
            await interaction.response.send_message(
                "생성형 AI가 비활성화되어 있습니다. `.env`에 `OPENAI_API_KEY`를 설정하세요.",
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
                        "content": "당신은 FFXIV 플레이어를 돕는 간결한 조수입니다. "
                        "확실하지 않은 정보는 추측임을 밝히고, 짧게 답합니다.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=800,
            )
            text = completion.choices[0].message.content or "(빈 응답)"
            if len(text) > 3900:
                text = text[:3890] + "…"
            await interaction.followup.send(text)
        except Exception:
            logger.exception("OpenAI 요청 실패")
            await interaction.followup.send(
                "AI 요청 중 오류가 발생했습니다. 키·모델명·할당량을 확인하세요.",
                ephemeral=True,
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GenerativeCog(cast(UsagiBot, bot)))

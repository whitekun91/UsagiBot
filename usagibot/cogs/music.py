"""음성 채널 음악 재생 (yt-dlp + FFmpeg). 호스트에 FFmpeg 설치 필요."""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Optional, Tuple

import discord
import yt_dlp
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)

_YTDL_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch",
}


def _extract_audio(query: str) -> Tuple[str, str]:
    q = query.strip()
    if not q.startswith("http"):
        q = f"ytsearch1:{q}"
    with yt_dlp.YoutubeDL(_YTDL_OPTS) as ydl:
        info = ydl.extract_info(q, download=False)
    if info is None:
        raise ValueError("재생 정보를 가져오지 못했습니다.")
    if "entries" in info:
        entries = info["entries"]
        if not entries:
            raise ValueError("검색 결과가 없습니다.")
        info = entries[0]
    url = info.get("url")
    if not url:
        raise ValueError("스트림 URL이 없습니다.")
    title = str(info.get("title") or "Unknown")
    return str(url), title


class MusicCog(commands.Cog):
    """대기열 기반 음악 재생."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.queues: Dict[int, List[str]] = {}
        self.now_playing: Dict[int, str] = {}

    async def _ensure_voice(self, interaction: discord.Interaction) -> Optional[discord.VoiceClient]:
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return None
        if not interaction.user.voice or not interaction.user.voice.channel:
            return None
        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client
        if vc is None:
            return await channel.connect()
        if vc.channel and vc.channel.id != channel.id:
            await vc.move_to(channel)
        return vc

    def _after_track(self, guild_id: int, error: Optional[BaseException]) -> None:
        if error:
            logger.error("음성 재생 오류: %s", error)
        fut = asyncio.run_coroutine_threadsafe(self._play_next(guild_id), self.bot.loop)
        try:
            fut.result(timeout=120)
        except Exception:
            logger.exception("대기열 다음 곡 재생 실패")

    async def _play_next(self, guild_id: int) -> None:
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return
        vc = guild.voice_client
        if vc is None:
            self.queues.pop(guild_id, None)
            self.now_playing.pop(guild_id, None)
            return

        q = self.queues.setdefault(guild_id, [])
        if not q:
            self.now_playing.pop(guild_id, None)
            return

        query = q.pop(0)
        try:
            stream_url, title = await self.bot.loop.run_in_executor(None, _extract_audio, query)
        except Exception as e:
            logger.warning("추출 실패(건너뜀): %s — %s", query, e)
            await self._play_next(guild_id)
            return

        self.now_playing[guild_id] = title
        source = discord.FFmpegPCMAudio(
            stream_url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn",
        )
        wrapped = discord.PCMVolumeTransformer(source, volume=0.45)

        def _after(err: Optional[BaseException]) -> None:
            self._after_track(guild_id, err)

        vc.play(wrapped, after=_after)

    @app_commands.command(name="play", description="YouTube URL 또는 검색어로 음악을 재생·대기열에 추가합니다.")
    @app_commands.describe(query="URL 또는 검색어")
    async def play(self, interaction: discord.Interaction, query: str) -> None:
        if not interaction.guild:
            await interaction.response.send_message("서버(길드)에서만 사용할 수 있습니다.", ephemeral=True)
            return

        await interaction.response.defer(thinking=True)
        vc = await self._ensure_voice(interaction)
        if vc is None:
            await interaction.followup.send("음성 채널에 먼저 들어간 뒤 다시 시도해 주세요.")
            return

        gid = interaction.guild.id
        self.queues.setdefault(gid, []).append(query)

        if vc.is_playing() or vc.is_paused():
            await interaction.followup.send(f"대기열 추가: **{query}**")
            return

        await self._play_next(gid)
        title = self.now_playing.get(gid, query)
        await interaction.followup.send(f"재생 중: **{title}**")

    @app_commands.command(name="skip", description="현재 곡을 건너뜁니다.")
    async def skip(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        vc = interaction.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await interaction.response.send_message("건너뛰었습니다.")
        else:
            await interaction.response.send_message("재생 중인 곡이 없습니다.", ephemeral=True)

    @app_commands.command(name="queue", description="대기열을 보여줍니다.")
    async def queue_cmd(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        gid = interaction.guild.id
        q = self.queues.get(gid, [])
        cur = self.now_playing.get(gid)
        lines: List[str] = []
        if cur:
            lines.append(f"**지금:** {cur}")
        if q:
            preview = "\n".join(f"{i+1}. {item[:80]}" for i, item in enumerate(q[:15]))
            lines.append("**대기열:**\n" + preview)
            if len(q) > 15:
                lines.append(f"… 외 {len(q) - 15}곡")
        if not lines:
            await interaction.response.send_message("대기열이 비어 있습니다.")
            return
        await interaction.response.send_message("\n\n".join(lines)[:1900])

    @app_commands.command(name="pause", description="재생을 일시정지합니다.")
    async def pause(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("일시정지했습니다.")
        else:
            await interaction.response.send_message("재생 중이 아닙니다.", ephemeral=True)

    @app_commands.command(name="resume", description="일시정지를 해제합니다.")
    async def resume(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("재개했습니다.")
        else:
            await interaction.response.send_message("일시정지 상태가 아닙니다.", ephemeral=True)

    @app_commands.command(name="leave", description="음성 채널에서 나가고 대기열을 비웁니다.")
    async def leave_cmd(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message("서버에서만 사용할 수 있습니다.", ephemeral=True)
            return
        gid = interaction.guild.id
        vc = interaction.guild.voice_client
        self.queues.pop(gid, None)
        self.now_playing.pop(gid, None)
        if vc:
            await vc.disconnect()
        await interaction.response.send_message("연결을 종료했습니다.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MusicCog(bot))

"""Voice music playback via yt-dlp + FFmpeg (FFmpeg required on host)."""

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
        raise ValueError("Could not fetch playback metadata.")
    if "entries" in info:
        entries = info["entries"]
        if not entries:
            raise ValueError("No search results found.")
        info = entries[0]
    url = info.get("url")
    if not url:
        raise ValueError("Missing stream URL.")
    title = str(info.get("title") or "Unknown")
    return str(url), title


class MusicCog(commands.Cog):
    """Queue-based music playback."""

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
            logger.error("Voice playback error: %s", error)
        fut = asyncio.run_coroutine_threadsafe(self._play_next(guild_id), self.bot.loop)
        try:
            fut.result(timeout=120)
        except Exception:
            logger.exception("Failed to play next queue item")

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
            logger.warning("Extraction failed (skipped): %s - %s", query, e)
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

    @app_commands.command(name="play", description="Play or queue a YouTube URL/search term.")
    @app_commands.describe(query="URL or search term")
    async def play(self, interaction: discord.Interaction, query: str) -> None:
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        await interaction.response.defer(thinking=True)
        vc = await self._ensure_voice(interaction)
        if vc is None:
            await interaction.followup.send("Join a voice channel first, then try again.")
            return

        gid = interaction.guild.id
        self.queues.setdefault(gid, []).append(query)

        if vc.is_playing() or vc.is_paused():
            await interaction.followup.send(f"Added to queue: **{query}**")
            return

        await self._play_next(gid)
        title = self.now_playing.get(gid, query)
        await interaction.followup.send(f"Now playing: **{title}**")

    @app_commands.command(name="skip", description="Skip the current track.")
    async def skip(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        vc = interaction.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await interaction.response.send_message("Skipped.")
        else:
            await interaction.response.send_message("No track is currently playing.", ephemeral=True)

    @app_commands.command(name="queue", description="Show the current queue.")
    async def queue_cmd(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        gid = interaction.guild.id
        q = self.queues.get(gid, [])
        cur = self.now_playing.get(gid)
        lines: List[str] = []
        if cur:
            lines.append(f"**Now:** {cur}")
        if q:
            preview = "\n".join(f"{i+1}. {item[:80]}" for i, item in enumerate(q[:15]))
            lines.append("**Queue:**\n" + preview)
            if len(q) > 15:
                lines.append(f"... and {len(q) - 15} more")
        if not lines:
            await interaction.response.send_message("The queue is empty.")
            return
        await interaction.response.send_message("\n\n".join(lines)[:1900])

    @app_commands.command(name="pause", description="Pause playback.")
    async def pause(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("Paused.")
        else:
            await interaction.response.send_message("Nothing is currently playing.", ephemeral=True)

    @app_commands.command(name="resume", description="Resume playback.")
    async def resume(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("Resumed.")
        else:
            await interaction.response.send_message("Playback is not paused.", ephemeral=True)

    @app_commands.command(name="leave", description="Leave voice and clear the queue.")
    async def leave_cmd(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        gid = interaction.guild.id
        vc = interaction.guild.voice_client
        self.queues.pop(gid, None)
        self.now_playing.pop(gid, None)
        if vc:
            await vc.disconnect()
        await interaction.response.send_message("Disconnected and cleared queue.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MusicCog(bot))

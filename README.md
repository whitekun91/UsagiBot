# Usagi Bot

<p align="center">
  <img src="./docs/main-image.png" alt="Usagi Main Image" width="560" />
</p>

A Discord bot focused on FFXIV info, daily community features, generative AI, and music playback.  
(Usagi means rabbit in Japanese.)

![Python](https://img.shields.io/badge/python-3.10+-blue)

## Requirements

- Python 3.10+
- A bot token from the [Discord Developer Portal](https://discord.com/developers/applications)
- For music playback: **FFmpeg** must be available in your system PATH ([ffmpeg.org](https://ffmpeg.org/download.html))
- For slash commands and message reading: enable `MESSAGE CONTENT INTENT` in Privileged Gateway Intents

## Installation

```bash
cd UsagiBot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root using `.env.example` as reference.
   - `DISCORD_TOKEN` (required)
   - `OPENAI_API_KEY` (required for `/ai`)
   - `SYNC_GUILD_ID` (optional, for faster guild-only command sync during development)

You can also put only `"token"` into `config/config.json`. (`DISCORD_TOKEN` in `.env` has priority.)

## Run

```bash
python -m usagibot
```

Logs are written to `logs/usagibot.log`.

## Slash Commands

| Command | Description |
| --- | --- |
| `/ping` | Check bot latency |
| `/about` | Show bot info |
| `/ff14` | Show FFXIV quick links |
| `/ai` | Ask generative AI (API key required) |
| `/play` | Play/add from YouTube URL or search term |
| `/skip` | Skip current track |
| `/queue` | Show queue |
| `/pause` / `/resume` | Pause / resume playback |
| `/leave` | Leave voice channel and clear queue |

## Project Structure

```text
UsagiBot/
  usagibot/           # Package root
    __main__.py       # Entry point
    bot.py            # Bot class and extension loader
    settings.py       # Env/JSON settings loader
    cogs/             # Feature cogs
      general.py
      ff14.py
      generative.py
      music.py
    utils/
      logging.py
  config/             # Optional JSON config samples
  logs/               # Created at runtime
```

## Version

- **v2.1.0** — English localization for docs/code messages and version bump
- v2.0.0 — `discord.ext.commands` + slash commands + cog architecture + AI/music modules
- v1.0.1 — Initial file structure (2024-03-20)
- v1.0.0 — First release (2024-03-19)

## Notes

- Please follow YouTube terms and copyright rules when using music commands.
- For always-on hosting, use platforms that support long-running processes (Railway, Render, VPS, etc.).

"""Load bot settings from environment variables and optional JSON config."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
_ENV_PATH = _ROOT / ".env"

load_dotenv(_ENV_PATH)


def _token_from_json() -> str | None:
    path = _ROOT / "config" / "config.json"
    if not path.is_file():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    token = data.get("token")
    return token if isinstance(token, str) and token.strip() else None


@dataclass(frozen=True)
class Settings:
    discord_token: str
    openai_api_key: str | None
    openai_model: str
    sync_guild_id: int | None


def load_settings() -> Settings:
    token = os.getenv("DISCORD_TOKEN") or _token_from_json()
    if not token:
        raise RuntimeError(
            "DISCORD_TOKEN is missing. Set DISCORD_TOKEN in .env or token in config/config.json."
        )

    openai_key = os.getenv("OPENAI_API_KEY") or None
    if openai_key == "":
        openai_key = None

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    sync_raw = os.getenv("SYNC_GUILD_ID", "").strip()
    sync_guild_id: int | None
    if sync_raw:
        try:
            sync_guild_id = int(sync_raw)
        except ValueError as e:
            raise ValueError("SYNC_GUILD_ID must be an integer.") from e
    else:
        sync_guild_id = None

    return Settings(
        discord_token=token.strip(),
        openai_api_key=openai_key,
        openai_model=model,
        sync_guild_id=sync_guild_id,
    )

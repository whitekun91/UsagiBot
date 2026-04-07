from __future__ import annotations

from pathlib import Path

from usagibot.bot import run_bot
from usagibot.settings import load_settings
from usagibot.utils.logging import setup_logging


def main() -> None:
    setup_logging(Path(__file__).resolve().parent.parent / "logs" / "usagibot.log")
    settings = load_settings()
    run_bot(settings)


if __name__ == "__main__":
    main()

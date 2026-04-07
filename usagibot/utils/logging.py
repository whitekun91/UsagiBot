"""Logging setup."""

from __future__ import annotations

import logging
from pathlib import Path


def setup_logging(log_path: Path | None = None) -> None:
    root = logging.getLogger()
    if root.handlers:
        return

    root.setLevel(logging.INFO)

    if log_path is None:
        log_path = Path(__file__).resolve().parent.parent.parent / "logs" / "usagibot.log"

    log_path.parent.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    root.addHandler(fh)
    root.addHandler(ch)

    logging.getLogger("discord").setLevel(logging.INFO)
    logging.getLogger("discord.http").setLevel(logging.WARNING)

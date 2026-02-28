"""
Centralized logging configuration for Euphoria Trance Drum Designer.

Usage:
    from logger import get_logger
    log = get_logger(__name__)
    log.info("kick generated")
    log.warning("clipping detected")
    log.error("file write failed", exc_info=True)

Log file: ~/.euphoria_drum_designer.log  (rotates at 2 MB, keeps 3 backups)
Console:  WARNING and above only (avoids spam during normal use)
"""
import logging
import logging.handlers
from pathlib import Path

_LOG_FILE = Path.home() / ".euphoria_drum_designer.log"
_initialized = False


def _setup() -> None:
    global _initialized
    if _initialized:
        return

    root_logger = logging.getLogger("euphoria")
    root_logger.setLevel(logging.DEBUG)

    # Rotating file handler — full DEBUG-level detail
    file_handler = logging.handlers.RotatingFileHandler(
        _LOG_FILE,
        maxBytes=2 * 1024 * 1024,  # 2 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))

    # Console handler — warnings and above only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter(
        "%(levelname)s: %(message)s"
    ))

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the 'euphoria' namespace."""
    _setup()
    # Strip package prefix so names stay compact in log lines
    short_name = name.split(".")[-1] if "." in name else name
    return logging.getLogger(f"euphoria.{short_name}")

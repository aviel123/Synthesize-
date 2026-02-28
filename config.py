"""
Session configuration manager — persists user settings between app restarts.
Settings are stored in ~/.euphoria_drum_designer.json
"""
import json
import os
from pathlib import Path

_CONFIG_FILE = Path.home() / ".euphoria_drum_designer.json"

_DEFAULTS: dict = {
    "output_filename": "output.wav",
    "last_preset": "Buzzism Euphoria",
    "last_tab": 0,
    "window_geometry": "860x680",
    "theme": "clam",
}


def load() -> dict:
    """Load persisted settings, falling back to defaults for missing keys."""
    config = dict(_DEFAULTS)
    if _CONFIG_FILE.exists():
        try:
            with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            config.update(saved)
        except Exception:
            pass  # corrupt file — silently use defaults
    return config


def save(settings: dict) -> None:
    """Persist settings to disk. Unknown keys are preserved."""
    current = load()
    current.update(settings)
    try:
        with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(current, f, indent=2)
    except Exception:
        pass  # non-critical; silently ignore write errors


def get(key: str, default=None):
    """Convenience: read a single key from persisted settings."""
    return load().get(key, default)


def set(key: str, value) -> None:
    """Convenience: update a single key in persisted settings."""
    save({key: value})

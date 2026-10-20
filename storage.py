"""Save/load helpers (Week 9 Advanced: File Input/Output)."""

import json
import os
from pathlib import Path
from game import Game

SAVE_FILE = Path("sydney_save.json")


class SaveError(Exception):
    """Raised when a save cannot be read or written safely."""


def save_game(game, filename=SAVE_FILE):
    """Write JSON to a temporary file, then replace the original safely."""
    target = Path(filename)
    temporary = target.with_name(target.name + ".tmp")
    try:
        with open(temporary, "w", encoding="utf-8") as handle:
            json.dump(game.to_dict(), handle, indent=2)
        os.replace(temporary, target)
    except (OSError, TypeError, ValueError) as error:
        raise SaveError(f"Could not save the game: {error}") from error


def load_game(filename=SAVE_FILE):
    """Read JSON and validate it before creating a Game object."""
    try:
        with open(filename, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return Game.from_dict(data)
    except (OSError, json.JSONDecodeError, UnicodeError, ValueError) as error:
        raise SaveError(f"Could not load the game: {error}") from error

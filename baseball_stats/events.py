from dataclasses import dataclass
from pathlib import Path


@dataclass
class Play:
    ...


@dataclass
class Game:
    plays: list[Play]


def load_events_file(path: Path) -> list[Game]:
    games: list[Game] = []
    current_game: None | Game = None
    for line in path.read_text().splitlines():
        print(line)
    return games

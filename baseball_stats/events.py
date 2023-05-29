from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class Player:
    id: str
    name: str


@dataclass
class Play:
    ...


@dataclass
class Team:
    id: str
    plays: list[Play]
    lineup: list[Player]


@dataclass
class Game:
    id: str
    home_team: Team
    visiting_team: Team

    @classmethod
    def from_game_lines(cls, lines: list[str]) -> "Game":
        game_id: None | str = None
        home_id: None | str = None
        visiting_id: None | str = None
        home_plays: list[Play] = []
        visiting_plays: list[Play] = []
        home_lineup: list[Player] = []
        visiting_lineup: list[Player] = []
        for line in lines:
            split_line = line.split(",")
            if split_line[0] == "id":
                game_id = split_line[1]

            elif split_line[0] == "start":
                player = Player(
                    id=split_line[1],
                    name=split_line[2],
                )

                team = split_line[3]
                if team == "0":
                    visiting_lineup.append(player)
                elif team == "1":
                    home_lineup.append(player)
                else:
                    print(line)
                    raise Exception(f"Unexpected home vs. visiting team value: {team}")

            # TODO:
            # - team ids
            # - play parsing

        return cls(
            id=game_id,  # type: ignore
            home_team=Team(
                id=home_id,  # type: ignore
                plays=home_plays,
                lineup=home_lineup,
            ),
            visiting_team=Team(
                id=visiting_id,  # type: ignore
                plays=visiting_plays,
                lineup=visiting_lineup,
            ),
        )


def load_events_file(path: Path) -> list[Game]:
    return [Game.from_game_lines(lines) for lines in _yield_game_lines(path)]


def _yield_game_lines(path: Path) -> Iterator[list[str]]:
    """Yield the lines corresponding to each game in the events file."""
    current_game_lines: list[str] = []
    for line in path.read_text().splitlines():
        if line.split(",")[0] == "id":
            if current_game_lines:
                yield current_game_lines
                current_game_lines.clear()

        current_game_lines.append(line)

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from baseball_obp_and_cobp.play import Play
from baseball_obp_and_cobp.player import Player
from baseball_obp_and_cobp.team import Team, TeamType


@dataclass
class GameLine:
    """Represents a line from Retrosheet game (event) data."""

    id: str
    values: list[str]


@dataclass
class Game:
    """Parsed Retrosheet game (event) data."""

    id: str
    players: list[Player]

    @classmethod
    def from_game_lines(cls, game_lines: list[GameLine], team: Team) -> "Game":
        game_id = _get_game_id(game_lines)
        home_team = _get_home_team(game_lines)
        visiting_team = _get_visiting_team(game_lines)
        players = list(_get_teams_players(game_lines, team, visiting_team, home_team))
        player_id_to_player = {player.id: player for player in players}
        for play in _get_plays(game_lines):
            if batter := player_id_to_player.get(play.batter_id):
                batter.plays.append(play)

        return cls(id=game_id, players=players)

    def get_player(self, player_id: str) -> Player:
        for player in self.players:
            if player.id == player_id:
                return player
        raise Exception(f"Unable to find player id of {player_id} within the game")


def load_events_file(path: Path) -> list[Game]:
    team = _get_files_team(path)
    return [Game.from_game_lines(lines, team) for lines in _yield_game_lines(path)]


def _get_files_team(path: Path) -> Team:
    id_line = path.read_text().splitlines()[0]
    file_id = id_line.split(",")[1]
    team_id = "".join(c for c in file_id if c.isalpha())
    return Team(team_id)


def _yield_game_lines(path: Path) -> Iterator[list[GameLine]]:
    """Yield the lines corresponding to each game in the Retrosheet events file."""
    current_game_lines: list[GameLine] = []
    for line in path.read_text().splitlines():
        split_line = line.split(",")
        game_line = GameLine(id=split_line[0], values=split_line[1:])
        if game_line.id == "id":
            if current_game_lines:
                yield current_game_lines
                current_game_lines.clear()

        current_game_lines.append(game_line)


def _get_game_id(game_lines: list[GameLine]) -> str:
    for line in game_lines:
        if line.id == "id":
            return line.values[0]

    raise Exception("Unable to locate the game's id")


def _get_home_team(game_lines: list[GameLine]) -> Team:
    for line in game_lines:
        if line.id == "info" and line.values[0] == "hometeam":
            return Team(line.values[1])

    raise Exception("Unable to locate home team")


def _get_visiting_team(game_lines: list[GameLine]) -> Team:
    for line in game_lines:
        if line.id == "info" and line.values[0] == "visteam":
            return Team(line.values[1])

    raise Exception("Unable to locate visiting team")


def _get_teams_players(
    game_lines: list[GameLine], team: Team, visiting_team: Team, home_team: Team
) -> Iterator[Player]:
    for line in game_lines:
        if line.id == "start":
            player = Player.from_start_line(line.values)
            # only include the team we're interested in players
            players_team_type = TeamType(int(line.values[2]))
            team_is_visiting_team = visiting_team == team and players_team_type == TeamType.VISITING
            team_is_home_team = home_team == team and players_team_type == TeamType.HOME
            if team_is_visiting_team or team_is_home_team:
                yield player


def _get_plays(game_lines: list[GameLine]) -> Iterator[Play]:
    for line in game_lines:
        if line.id == "play":
            yield Play.from_play_line(line.values)

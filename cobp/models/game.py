"""Loads and parses Retrosheet game data."""
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import date
from logging import getLogger
from pathlib import Path
from typing import Iterator, Mapping

from cobp.models.base import BaseToPlayerId
from cobp.models.play import Play
from cobp.models.player import Player
from cobp.models.team import TEAM_RETROSHEET_ID_TO_TEAM, Team, TeamLocation

logger = getLogger(__name__)


@dataclass
class GameLine:
    """Represents a line from Retrosheet game (event) data."""

    id: str
    values: list[str]

    @classmethod
    def from_line(cls, line: str) -> "GameLine":
        split_line = line.split(",")
        return cls(split_line[0], split_line[1:])


@dataclass
class Game:
    """Parsed Retrosheet game (event) data for a given team."""

    id: str
    team: Team
    home_team: Team
    visiting_team: Team
    players: list[Player]
    inning_to_plays: Mapping[int, list[Play]]

    @property
    def player_id_to_player(self) -> dict[str, Player]:
        return {player.id: player for player in self.players}

    @classmethod
    def from_game_lines(cls, game_lines: list[GameLine], team: Team) -> "Game":
        game_id = _get_game_id(game_lines)
        home_team = _get_home_team(game_lines)
        visiting_team = _get_visiting_team(game_lines)
        players = list(_get_teams_players(game_lines, team, visiting_team, home_team))
        plays = list(_get_teams_plays(game_lines, players))
        inning_to_plays = _get_inning_to_plays(plays)
        _add_plays_to_players(plays, players)
        return cls(
            id=game_id,
            team=team,
            home_team=home_team,
            visiting_team=visiting_team,
            inning_to_plays=inning_to_plays,
            players=players,
        )

    @property
    def pretty_id(self) -> str:
        return f"{self.date.strftime('%Y/%m/%d')} {self.visiting_team.pretty_name} @ {self.home_team.pretty_name}"

    @property
    def date(self) -> date:
        date_ = "".join([c for c in self.id if c.isnumeric()])
        return date(year=int(date_[0:4]), month=int(date_[4:6]), day=int(date_[6:8]))

    def get_player(self, player_id: str) -> Player | None:
        return self.player_id_to_player.get(player_id)

    def get_plays_resulting_on_base_in_inning(self, inning: int) -> list[Play]:
        return [inning_play for inning_play in self.inning_to_plays[inning] if inning_play.results_in_on_base]

    def inning_has_an_on_base(self, inning: int) -> bool:
        return len(self.get_plays_resulting_on_base_in_inning(inning)) > 0

    def play_has_on_base_before_it_in_inning(self, inning: int, play: Play) -> bool:
        for inning_play in self.inning_to_plays[inning]:
            if inning_play == play:
                return False
            if inning_play.results_in_on_base:
                return True

        raise ValueError(f"Unable to find play within inning. {inning=} | play={play.pretty_description}")

    def play_is_first_of_inning(self, inning: int, play: Play) -> bool:
        return self.inning_to_plays[inning][0] == play


def load_teams_games(season_event_files: list[Path], team: Team) -> Iterator[Game]:
    for event_file in season_event_files:
        yield from [Game.from_game_lines(lines, team) for lines in _yield_game_lines(event_file, team)]


def get_players_in_games(games: list[Game]) -> list[Player]:
    seen_player_ids = set()
    players = []
    for game in games:
        for player in game.players:
            if player.id not in seen_player_ids:
                players.append(player)
                seen_player_ids.add(player.id)
    return players


def _yield_game_lines(events_file_path: Path, team: Team) -> Iterator[list[GameLine]]:
    """Yield the lines corresponding to each game in the Retrosheet events file."""
    current_game_lines: list[GameLine] = []
    lines = events_file_path.read_text().splitlines()
    team_is_in_game = False
    for i, line in enumerate(lines):
        game_line = GameLine.from_line(line)
        if game_line.id == "id":
            if current_game_lines:
                yield deepcopy(current_game_lines)
                current_game_lines.clear()

            visiting_team = lines[i + 2].split(",")[-1]
            home_team = lines[i + 3].split(",")[-1]
            team_is_in_game = team.retrosheet_id in [visiting_team, home_team]

        if team_is_in_game:
            current_game_lines.append(game_line)

    if current_game_lines:
        yield deepcopy(current_game_lines)


def _get_game_id(game_lines: list[GameLine]) -> str:
    for line in game_lines:
        if line.id == "id":
            return line.values[0]

    raise Exception("Unable to locate the game's id")


def _get_home_team(game_lines: list[GameLine]) -> Team:
    for line in game_lines:
        if line.id == "info" and line.values[0] == "hometeam":
            return TEAM_RETROSHEET_ID_TO_TEAM[line.values[1]]

    raise Exception("Unable to locate home team")


def _get_visiting_team(game_lines: list[GameLine]) -> Team:
    for line in game_lines:
        if line.id == "info" and line.values[0] == "visteam":
            return TEAM_RETROSHEET_ID_TO_TEAM[line.values[1]]

    raise Exception("Unable to locate visiting team")


def _get_teams_players(game_lines: list[GameLine], team: Team, visiting_team: Team, home_team: Team) -> list[Player]:
    seen_players = set()
    players = []
    for line in game_lines:
        if line.id in ["start", "sub"]:
            player = Player.from_start_line(line.values)
            # only include the team we're interested in players
            players_team_location = TeamLocation(int(line.values[2]))
            team_is_visiting_team = visiting_team == team and players_team_location == TeamLocation.VISITING
            team_is_home_team = home_team == team and players_team_location == TeamLocation.HOME
            if (team_is_visiting_team or team_is_home_team) and player.id not in seen_players:
                players.append(player)
                seen_players.add(player.id)

    return players


def _get_teams_plays(game_lines: list[GameLine], team_players: list[Player]) -> list[Play]:
    team_player_ids = {player.id for player in team_players}
    current_inning = 1
    current_base_state: BaseToPlayerId = {}
    current_team = None
    teams_plays = []
    for line in game_lines:
        if line.id == "play":
            inning = int(line.values[0])
            team = line.values[1]
            if inning != current_inning or current_team != team:
                current_inning = inning
                current_base_state = {}
                current_team = team

            play = Play.from_play_line(line.values, current_base_state)
            current_base_state = play.resulting_base_state
            if play.batter_id in team_player_ids:
                teams_plays.append(play)

    return teams_plays


def _get_inning_to_plays(plays: list[Play]) -> Mapping[int, list[Play]]:
    inning_to_plays: Mapping[int, list[Play]] = defaultdict(list)
    for play in plays:
        inning_to_plays[play.inning].append(play)
    return inning_to_plays


def _add_plays_to_players(plays: list[Play], players: list[Player]) -> None:
    player_id_to_player = {player.id: player for player in players}
    for play in plays:
        if player := player_id_to_player.get(play.batter_id):
            player.plays.append(play)

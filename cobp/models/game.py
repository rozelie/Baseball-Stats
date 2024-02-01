# """Loads and parses Retrosheet game data."""
# from collections import defaultdict
# from copy import deepcopy
# from dataclasses import dataclass
# from datetime import date
# from logging import getLogger
# from pathlib import Path
# from typing import Iterator, Mapping

# from cobp.models.base import BaseToPlayerId
# from cobp.models.play import Play
# from cobp.models.player import TEAM_PLAYER_ID, Player
# from cobp.models.substitution import Substitution
# from cobp.models.team import Team, TeamLocation, get_team_for_year

# logger = getLogger(__name__)


# @dataclass
# class GameLine:
#     """Represents a line from Retrosheet game (event) data."""

#     id: str
#     values: list[str]

#     @classmethod
#     def from_line(cls, line: str) -> "GameLine":
#         split_line = line.split(",")
#         return cls(split_line[0], split_line[1:])


# @dataclass
# class Game:
#     """Parsed Retrosheet game (event) data for a given team."""

#     id: str
#     team: Team
#     home_team: Team
#     visiting_team: Team
#     players: list[Player]
#     inning_to_plays: Mapping[int, list[Play]]

#     @property
#     def player_id_to_player(self) -> dict[str, Player]:
#         return {player.id: player for player in self.players}

#     @classmethod
#     def from_game_lines_basic_info_only(cls, game_lines: list[GameLine], team: Team, year: int) -> "Game":
#         game_id = _get_game_id(game_lines)
#         home_team = _get_home_team(game_lines, year)
#         visiting_team = _get_visiting_team(game_lines, year)
#         return cls(
#             id=game_id,
#             team=team,
#             home_team=home_team,
#             visiting_team=visiting_team,
#             players=[],
#             inning_to_plays={},
#         )

#     @classmethod
#     def from_game_lines(cls, game_lines: list[GameLine], team: Team, year: int) -> "Game":
#         game_id = _get_game_id(game_lines)
#         logger.debug(f"Loading game: {game_id=} | {team=}")
#         home_team = _get_home_team(game_lines, year)
#         visiting_team = _get_visiting_team(game_lines, year)
#         team_number = 0 if team == visiting_team else 1
#         players = list(_get_teams_players(game_lines, team, visiting_team, home_team))
#         plays = list(_get_teams_plays(game_lines, players, team_number))
#         inning_to_plays = _get_inning_to_plays(plays)
#         _add_plays_to_players(plays, players)
#         return cls(
#             id=game_id,
#             team=team,
#             home_team=home_team,
#             visiting_team=visiting_team,
#             players=players,
#             inning_to_plays=inning_to_plays,
#         )

#     @property
#     def pretty_id(self) -> str:
#         return f"{self.date.strftime('%Y/%m/%d')} {self.visiting_team.pretty_name} @ {self.home_team.pretty_name}"

#     @property
#     def date(self) -> date:
#         date_ = "".join([c for c in self.id if c.isnumeric()])
#         return date(year=int(date_[0:4]), month=int(date_[4:6]), day=int(date_[6:8]))

#     def get_player(self, player_id: str) -> Player | None:
#         return self.player_id_to_player.get(player_id)

#     def get_plays_resulting_on_base_in_inning(self, inning: int) -> list[Play]:
#         return [inning_play for inning_play in self.inning_to_plays[inning] if inning_play.results_in_on_base]

#     def inning_has_an_on_base(self, inning: int) -> bool:
#         return len(self.get_plays_resulting_on_base_in_inning(inning)) > 0

#     def play_has_on_base_before_it_in_inning(self, inning: int, play: Play) -> bool:
#         for inning_play in self.inning_to_plays[inning]:
#             if inning_play == play:
#                 return False
#             if inning_play.results_in_on_base:
#                 return True

#         raise ValueError(f"Unable to find play within inning. {inning=} | play={play.pretty_description}")

#     def play_is_first_of_inning(self, inning: int, play: Play) -> bool:
#         return self.inning_to_plays[inning][0] == play


# def load_teams_games(
#     season_event_files: list[Path], team: Team, game_ids: list[str] | None, year: int
# ) -> Iterator[Game]:
#     logger.info(f"Loading {len(game_ids) if game_ids else 'all season'} games for {team.pretty_name}...")
#     for event_file in season_event_files:
#         for game_lines in _yield_game_lines(event_file, team):
#             game_id = _get_game_id(game_lines)
#             if (not game_ids) or (game_id in game_ids):
#                 yield Game.from_game_lines(game_lines, team, year)


# def load_teams_games_basic_info(season_event_files: list[Path], team: Team, year: int) -> Iterator[Game]:
#     logger.info(f"Loading {team.pretty_name}'s game basic info...")
#     for event_file in season_event_files:
#         yield from [
#             Game.from_game_lines_basic_info_only(lines, team, year) for lines in _yield_game_lines(event_file, team)
#         ]


# def get_players_in_games(games: list[Game]) -> list[Player]:
#     seen_player_ids = set()
#     players = []
#     for game in games:
#         for player in game.players:
#             if player.id not in seen_player_ids:
#                 players.append(player)
#                 seen_player_ids.add(player.id)
#     return players


# def _yield_game_lines(events_file_path: Path, team: Team) -> Iterator[list[GameLine]]:
#     """Yield the lines corresponding to each game in the Retrosheet events file."""
#     current_game_lines: list[GameLine] = []
#     lines = events_file_path.read_text().splitlines()
#     team_is_in_game = False
#     for i, line in enumerate(lines):
#         game_line = GameLine.from_line(line)
#         if game_line.id == "id":
#             if current_game_lines:
#                 yield deepcopy(current_game_lines)
#                 current_game_lines.clear()

#             visiting_team = lines[i + 2].split(",")[-1]
#             home_team = lines[i + 3].split(",")[-1]
#             team_is_in_game = team.retrosheet_id in [visiting_team, home_team]

#         if team_is_in_game:
#             current_game_lines.append(game_line)

#     if current_game_lines:
#         yield deepcopy(current_game_lines)


# def _get_game_id(game_lines: list[GameLine]) -> str:
#     for line in game_lines:
#         if line.id == "id":
#             return line.values[0]

#     raise Exception("Unable to locate the game's id")


# def _get_home_team(game_lines: list[GameLine], year: int) -> Team:
#     for line in game_lines:
#         if line.id == "info" and line.values[0] == "hometeam":
#             return get_team_for_year(line.values[1], year)

#     raise Exception("Unable to locate home team")


# def _get_visiting_team(game_lines: list[GameLine], year: int) -> Team:
#     for line in game_lines:
#         if line.id == "info" and line.values[0] == "visteam":
#             return get_team_for_year(line.values[1], year)

#     raise Exception("Unable to locate visiting team")


# def _get_teams_players(game_lines: list[GameLine], team: Team, visiting_team: Team, home_team: Team) -> list[Player]:
#     seen_players = set()
#     seen_lineup_positions = set()
#     players = []
#     for line in game_lines:
#         if line.id in ["start", "sub"]:
#             player = Player.from_start_line(line.values)
#             # there is a coding error in Retrosheet data where Zoilo Almonte
#             # is mixed up with Drew Stubbs for 2013 Yankees data
#             # 2013NYA.EVA: sub,almoz001,"Drew Stubbs",1,9,11
#             if player.id == "almoz001" and player.name == "Drew Stubbs":
#                 player.name = "Zoilo Almonte"

#             players_team_location = TeamLocation(int(line.values[2]))
#             team_is_visiting_team = visiting_team == team and players_team_location == TeamLocation.VISITING
#             team_is_home_team = home_team == team and players_team_location == TeamLocation.HOME
#             if (team_is_visiting_team or team_is_home_team) and player.id not in seen_players:
#                 # Since lineup positions are ordered when iterating and substitions are encoded
#                 # with the lineup position they are replacing, we set the subs' lineup position to be 0
#                 # as we do not want to overwrite the original lineup to be able to determine substitutions later
#                 if player.lineup_position not in seen_lineup_positions:
#                     seen_lineup_positions.add(player.lineup_position)
#                 else:
#                     player.lineup_position = 0

#                 players.append(player)
#                 seen_players.add(player.id)

#     return players


# def _get_teams_plays(game_lines: list[GameLine], team_players: list[Player], team_number: int) -> list[Play]:
#     team_player_ids = {player.id for player in team_players}
#     current_inning = 1
#     current_base_state: BaseToPlayerId = {}
#     teams_plays = []
#     radj_set = False
#     for line in game_lines:
#         # handle substitutions
#         if line.id == "sub":
#             substitution = Substitution.from_sub_descriptor(line.values)
#             if substitution.player_id not in team_player_ids:
#                 continue

#             substitution_player = _get_player_by_id(substitution.player_id, team_players)
#             substituted_player = _get_player_from_batting_position(
#                 substitution.replacing_player_of_batting_order,
#                 team_players,
#             )
#             if substitution_player.id == substituted_player.id:
#                 # player is just switching field positions which can ignore
#                 continue

#             logger.debug(
#                 f"Handling substitution: {line.values=} | sub={substitution_player.id} |
# .                  subbed={substituted_player.id}"
#             )
#             if substitution.replacing_player_of_batting_order != 0:
#                 logger.debug("Sub replaces player in batting order - switching lineup positions")
#                 substitution_player.lineup_position = substituted_player.lineup_position
#                 substituted_player.lineup_position = 0

#             if substitution.is_pinch_runner:
#                 logger.debug("Sub is pinch runner - swapping player in base state")
#                 base_to_replace_player = _get_players_base_position(substituted_player.id, current_base_state)
#                 current_base_state[base_to_replace_player] = substitution.player_id

#         # handle runner adjustments
#         if line.id == "radj":
#             runner_id, base = line.values
#             if runner_id not in team_player_ids:
#                 continue

#             logger.debug(f"Handling runner adjustments: {line.values} | {base=} | {runner_id=}")
#             current_base_state[base] = runner_id
#             radj_set = True

#         elif line.id == "play":
#             inning = int(line.values[0])
#             team = int(line.values[1])
#             if team != team_number:
#                 continue

#             if inning != current_inning:
#                 current_inning = inning
#                 # setting a runner on second base in extra-innings is defined prior or after
#                 # the inning's plays (thanks Retrosheet) so we need to account for this
#                 if not radj_set:
#                     current_base_state = {}

#             radj_set = False
#             play = Play.from_play_line(line.values, current_base_state)
#             current_base_state = play.delta.resulting_base_state
#             if play.batter_id in team_player_ids:
#                 teams_plays.append(play)

#     return teams_plays


# def get_all_players_id_to_player(games: list[Game], include_team: bool = True) -> dict[str, Player]:
#     all_players = get_players_in_games(games)
#     player_id_to_player = {p.id: p for p in all_players}
#     if include_team:
#         player_id_to_player[TEAM_PLAYER_ID] = Player.as_team()
#     return player_id_to_player


# def _get_inning_to_plays(plays: list[Play]) -> Mapping[int, list[Play]]:
#     inning_to_plays: Mapping[int, list[Play]] = defaultdict(list)
#     for play in plays:
#         inning_to_plays[play.inning].append(play)
#     return inning_to_plays


# def _add_plays_to_players(plays: list[Play], players: list[Player]) -> None:
#     player_id_to_player = {player.id: player for player in players}
#     for play in plays:
#         if player := player_id_to_player.get(play.batter_id):
#             player.plays.append(play)


# def _get_player_from_batting_position(batting_position: int, team_players: list[Player]) -> Player:
#     for player in team_players:
#         if player.lineup_position == batting_position:
#             return player

#     raise ValueError(f"Unable to find player in batting position: {batting_position=}")


# def _get_players_base_position(player_id: str, base_state: BaseToPlayerId) -> str:
#     for base, base_player_id in base_state.items():
#         if player_id == base_player_id:
#             return base

#     raise ValueError(f"Unable to find players base position: {player_id=} | {base_state=}")


# def _get_player_by_id(player_id: str, team_players: list[Player]) -> Player:
#     for player in team_players:
#         if player.id == player_id:
#             return player

#     raise ValueError(f"Unable to find player on team: {player_id=}")

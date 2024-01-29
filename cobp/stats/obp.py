"""Calculate OBP and COBP stats from game data."""
from dataclasses import dataclass, field

from pyretrosheet.models.game import Game
from pyretrosheet.models.play import Play
from pyretrosheet.models.player import Player

from cobp.stats.stat import Stat
from cobp.utils import (
    TEAM_PLAYER_ID,
    does_inning_have_an_on_base,
    does_play_have_on_base_before_it_in_inning,
    get_players_plays_used_in_stats,
    is_play_at_bat,
    is_play_first_of_inning,
    is_play_hit,
    is_play_hit_by_pitch,
    is_play_sacrifice_fly,
    is_play_walk,
)


@dataclass
class OBP(Stat):
    hits: int = 0
    walks: int = 0
    hit_by_pitches: int = 0
    at_bats: int = 0
    sacrifice_flys: int = 0
    game_to_stat: dict[str, "OBP"] = field(default_factory=dict)

    def add_arithmetic(self) -> None:
        numerator = f"*H={self.hits} + W={self.walks} + HBP={self.hit_by_pitches} == {self.numerator}*"
        denominator = f"*AB={self.at_bats} + W={self.walks} + HBP={self.hit_by_pitches} + SF={self.sacrifice_flys} == {self.denominator}*"  # noqa: E501
        self.explanation.extend([numerator, denominator])

    @property
    def numerator(self) -> int:
        return self.hits + self.walks + self.hit_by_pitches

    @property
    def denominator(self) -> int:
        return self.at_bats + self.walks + self.hit_by_pitches + self.sacrifice_flys

    @property
    def value(self) -> float:
        try:
            return self.numerator / self.denominator
        except ZeroDivisionError:
            return 0.0


PlayerToOBP = dict[str, OBP]


def get_player_to_obp(games: list[Game], players: list[Player]) -> PlayerToOBP:
    player_to_obp = {player.id: _get_obp(games, player) for player in players}
    player_to_obp[TEAM_PLAYER_ID] = _get_teams_obp(player_to_obp)
    return player_to_obp


def get_player_to_cobp(games: list[Game], players: list[Player]) -> PlayerToOBP:
    player_to_cobp = {player.id: _get_cobp(games, player) for player in players}
    player_to_cobp[TEAM_PLAYER_ID] = _get_teams_obp(player_to_cobp)
    return player_to_cobp


def get_player_to_sobp(games: list[Game], players: list[Player]) -> PlayerToOBP:
    player_to_sobp = {player.id: _get_sobp(games, player) for player in players}
    player_to_sobp[TEAM_PLAYER_ID] = _get_teams_obp(player_to_sobp)
    return player_to_sobp


def get_player_to_loop(games: list[Game], players: list[Player]) -> PlayerToOBP:
    player_to_loop = {player.id: _get_loop(games, player) for player in players}
    player_to_loop[TEAM_PLAYER_ID] = _get_teams_obp(player_to_loop)
    return player_to_loop


def _get_obp(games: list[Game], player: Player) -> OBP:
    obp = OBP()
    for game, plays in get_players_plays_used_in_stats(games, player):
        for play in plays:
            obp.add_play(play)
            _increment_obp_counters(game, play, obp)

    obp.add_arithmetic()
    return obp


def _get_cobp(games: list[Game], player: Player) -> OBP:
    obp = OBP()
    for game, plays in get_players_plays_used_in_stats(games, player):
        for play in plays:
            if not does_inning_have_an_on_base(game, play.inning, play.team_location):
                obp.add_play(play, resultant="N/A (no other on-base in inning)", color="red")
                continue

            obp.add_play(play)
            _increment_obp_counters(game, play, obp)

    obp.add_arithmetic()
    return obp


def _get_sobp(games: list[Game], player: Player) -> OBP:
    obp = OBP()
    for game, plays in get_players_plays_used_in_stats(games, player):
        for play in plays:
            if not does_play_have_on_base_before_it_in_inning(game, play):
                obp.add_play(play, resultant="N/A (no other on-base prior to play)", color="red")
                continue
            if play.inning != 1 and not does_inning_have_an_on_base(game, play.inning - 1, play.team_location):
                obp.add_play(play, resultant="N/A (no other on-base in prior inning)", color="red")
                continue
            if is_play_first_of_inning(game, play):
                obp.add_play(play, resultant="N/A (player is first batter in inning)", color="red")
                continue

            obp.add_play(play)
            _increment_obp_counters(game, play, obp)

    obp.add_arithmetic()
    return obp


def _get_loop(games: list[Game], player: Player) -> OBP:
    obp = OBP()
    for game, plays in get_players_plays_used_in_stats(games, player):
        for play in plays:
            if not is_play_first_of_inning(game, play):
                obp.add_play(play, resultant="N/A (player is not first batter in inning)", color="red")
                continue

            obp.add_play(play)
            _increment_obp_counters(game, play, obp)

    obp.add_arithmetic()
    return obp


def _get_teams_obp(player_to_obp: PlayerToOBP) -> OBP:
    team_obp = OBP()
    for obp in player_to_obp.values():
        team_obp.at_bats += obp.at_bats
        team_obp.hit_by_pitches += obp.hit_by_pitches
        team_obp.walks += obp.walks
        team_obp.hits += obp.hits
        team_obp.sacrifice_flys += obp.sacrifice_flys
        for game_id, game_obp in obp.game_to_stat.items():
            if game_id not in team_obp.game_to_stat:
                team_obp.game_to_stat[game_id] = OBP()

            team_game_obp = team_obp.game_to_stat[game_id]
            team_game_obp.at_bats += game_obp.at_bats
            team_game_obp.hit_by_pitches += game_obp.hit_by_pitches
            team_game_obp.walks += game_obp.walks
            team_game_obp.hits += game_obp.hits
            team_game_obp.sacrifice_flys += game_obp.sacrifice_flys

    return team_obp


def _increment_obp_counters(game: Game, play: Play, obp: OBP) -> None:
    if game.id.raw not in obp.game_to_stat:
        obp.game_to_stat[game.id.raw] = OBP()

    game_obp = obp.game_to_stat[game.id.raw]
    if is_play_at_bat(play):
        obp.at_bats += 1
        game_obp.at_bats += 1

    if is_play_hit(play):
        obp.hits += 1
        game_obp.hits += 1
    elif is_play_walk(play):
        obp.walks += 1
        game_obp.walks += 1
    elif is_play_hit_by_pitch(play):
        obp.hit_by_pitches += 1
        game_obp.hit_by_pitches += 1
    elif is_play_sacrifice_fly(play):
        obp.sacrifice_flys += 1
        game_obp.sacrifice_flys += 1

"""Calculate OBP and COBP stats from game data."""
from dataclasses import dataclass, field

from pyretrosheet.models.game import Game
from pyretrosheet.models.play import Play
from pyretrosheet.models.player import Player

from cobp.stats.conditions import ConditionFunction, is_conditional_play, is_leadoff_play, is_sequential_play
from cobp.stats.stat import Stat
from cobp.utils import TEAM_PLAYER_ID, get_players_plays


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
    return _get_player_to_obp(games, players, condition=None)


def get_player_to_cobp(games: list[Game], players: list[Player]) -> PlayerToOBP:
    return _get_player_to_obp(games, players, condition=is_conditional_play)


def get_player_to_sobp(games: list[Game], players: list[Player]) -> PlayerToOBP:
    return _get_player_to_obp(games, players, condition=is_sequential_play)


def get_player_to_loop(games: list[Game], players: list[Player]) -> PlayerToOBP:
    return _get_player_to_obp(games, players, condition=is_leadoff_play)


def _get_player_to_obp(games: list[Game], players: list[Player], condition: ConditionFunction | None) -> PlayerToOBP:
    player_to_obp = {player.id: _get_obp(games, player, condition=condition) for player in players}
    player_to_obp[TEAM_PLAYER_ID] = _get_teams_obp(player_to_obp)
    return player_to_obp


def _get_obp(games: list[Game], player: Player, condition: ConditionFunction | None) -> OBP:
    obp = OBP()
    for game, plays in get_players_plays(games, player):
        for play in plays:
            if condition:
                is_condition = condition(game, play)
                if not is_condition.is_met:
                    obp.add_play(play, resultant=is_condition.reason, color="red")
                    continue

            obp.add_play(play)
            _increment_obp_counters(game, play, obp)

    obp.add_arithmetic()
    return obp


def _increment_obp_counters(game: Game, play: Play, obp: OBP) -> None:
    if game.id.raw not in obp.game_to_stat:
        obp.game_to_stat[game.id.raw] = OBP()

    game_obp = obp.game_to_stat[game.id.raw]
    if play.is_an_at_bat():
        obp.at_bats += 1
        game_obp.at_bats += 1

    if play.is_hit():
        obp.hits += 1
        game_obp.hits += 1
    elif play.is_walk():
        obp.walks += 1
        game_obp.walks += 1
    elif play.is_hit_by_pitch():
        obp.hit_by_pitches += 1
        game_obp.hit_by_pitches += 1
    elif play.is_sacrifice_fly():
        obp.sacrifice_flys += 1
        game_obp.sacrifice_flys += 1


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

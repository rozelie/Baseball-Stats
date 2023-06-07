"""Calculate OBP and COBP stats from game data."""
from dataclasses import dataclass

from baseball_obp_and_cobp.game import Game, get_players_in_games
from baseball_obp_and_cobp.play import Play
from baseball_obp_and_cobp.player import TEAM_PLAYER_ID, Player
from baseball_obp_and_cobp.stats.stat import Stat


@dataclass
class OBP(Stat):
    hits: int = 0
    walks: int = 0
    hit_by_pitches: int = 0
    at_bats: int = 0
    sacrifice_flys: int = 0

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
    def obp(self) -> float:
        try:
            return self.numerator / self.denominator
        except ZeroDivisionError:
            return 0.0


PlayerToOBP = dict[str, OBP]


def get_player_to_obp(games: list[Game]) -> PlayerToOBP:
    players = get_players_in_games(games)
    player_to_obp = {player.id: _get_obp(games, player) for player in players}
    player_to_obp[TEAM_PLAYER_ID] = _get_teams_obp(player_to_obp)
    return player_to_obp


def get_player_to_cobp(games: list[Game]) -> PlayerToOBP:
    players = get_players_in_games(games)
    player_to_cobp = {player.id: _get_cobp(games, player) for player in players}
    player_to_cobp[TEAM_PLAYER_ID] = _get_teams_obp(player_to_cobp)
    return player_to_cobp


def get_player_to_sobp(games: list[Game]) -> PlayerToOBP:
    players = get_players_in_games(games)
    player_to_sobp = {player.id: _get_sobp(games, player) for player in players}
    player_to_sobp[TEAM_PLAYER_ID] = _get_teams_obp(player_to_sobp)
    return player_to_sobp


def _get_obp(games: list[Game], player: Player) -> OBP:
    obp = OBP()
    for game in games:
        if not (game_player := game.get_player(player.id)):
            continue

        for play in game_player.plays:
            if play.is_unused_in_obp_calculations:
                continue

            obp.add_play(play)
            _increment_obp_counters(play, obp)

    obp.add_arithmetic()
    return obp


def _get_cobp(games: list[Game], player: Player) -> OBP:
    obp = OBP()
    for game in games:
        if not (game_player := game.get_player(player.id)):
            continue

        for play in game_player.plays:
            if play.is_unused_in_obp_calculations:
                continue
            if not game.inning_has_an_on_base(play.inning):
                obp.add_play(play, resultant="N/A (no other on-base in inning)", color="red")
                continue

            obp.add_play(play)
            _increment_obp_counters(play, obp)

    obp.add_arithmetic()
    return obp


def _get_sobp(games: list[Game], player: Player) -> OBP:
    obp = OBP()
    for game in games:
        if not (game_player := game.get_player(player.id)):
            continue

        for play in game_player.plays:
            if play.is_unused_in_obp_calculations:
                continue
            if not game.play_has_on_base_before_it_in_inning(play.inning, play):
                obp.add_play(play, resultant="N/A (no other on-base prior to play)", color="red")
                continue

            obp.add_play(play)
            _increment_obp_counters(play, obp)

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

    return team_obp


def _increment_obp_counters(play: Play, obp: OBP) -> None:
    if play.is_at_bat:
        obp.at_bats += 1

    if play.is_hit:
        obp.hits += 1
    elif play.is_walk:
        obp.walks += 1
    elif play.is_hit_by_pitch:
        obp.hit_by_pitches += 1
    elif play.is_sacrifice_fly:
        obp.sacrifice_flys += 1

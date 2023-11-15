"""Calculate OBP and COBP stats from game data."""
from dataclasses import dataclass, field

from cobp.models.game import Game, get_players_in_games
from cobp.models.play import Play
from cobp.models.player import TEAM_PLAYER_ID, Player
from cobp.stats.stat import Stat


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


def get_player_to_loop(games: list[Game]) -> PlayerToOBP:
    players = get_players_in_games(games)
    player_to_loop = {player.id: _get_loop(games, player) for player in players}
    player_to_loop[TEAM_PLAYER_ID] = _get_teams_obp(player_to_loop)
    return player_to_loop


def _get_obp(games: list[Game], player: Player) -> OBP:
    obp = OBP()
    for game in games:
        if not (game_player := game.get_player(player.id)):
            continue

        for play in game_player.plays:
            if play.is_unused_in_stats:
                continue

            obp.add_play(play)
            _increment_obp_counters(game, play, obp)

    obp.add_arithmetic()
    return obp


def _get_cobp(games: list[Game], player: Player) -> OBP:
    obp = OBP()
    for game in games:
        if not (game_player := game.get_player(player.id)):
            continue

        for play in game_player.plays:
            if play.is_unused_in_stats:
                continue
            if not game.inning_has_an_on_base(play.inning):
                obp.add_play(play, resultant="N/A (no other on-base in inning)", color="red")
                continue

            obp.add_play(play)
            _increment_obp_counters(game, play, obp)

    obp.add_arithmetic()
    return obp


def _get_sobp(games: list[Game], player: Player) -> OBP:
    obp = OBP()
    for game in games:
        if not (game_player := game.get_player(player.id)):
            continue

        for play in game_player.plays:
            if play.is_unused_in_stats:
                continue
            if not game.play_has_on_base_before_it_in_inning(play.inning, play):
                obp.add_play(play, resultant="N/A (no other on-base prior to play)", color="red")
                continue
            if play.inning != 1 and not game.inning_has_an_on_base(play.inning - 1):
                obp.add_play(play, resultant="N/A (no other on-base in prior inning)", color="red")
                continue
            if game.play_is_first_of_inning(play.inning, play):
                obp.add_play(play, resultant="N/A (player is first batter in inning)", color="red")
                continue

            obp.add_play(play)
            _increment_obp_counters(game, play, obp)

    obp.add_arithmetic()
    return obp


def _get_loop(games: list[Game], player: Player) -> OBP:
    obp = OBP()
    for game in games:
        if not (game_player := game.get_player(player.id)):
            continue

        for play in game_player.plays:
            if play.is_unused_in_stats:
                continue

            if not game.play_is_first_of_inning(play.inning, play):
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
    if game.id not in obp.game_to_stat:
        obp.game_to_stat[game.id] = OBP()

    game_obp = obp.game_to_stat[game.id]
    if play.is_at_bat:
        obp.at_bats += 1
        game_obp.at_bats += 1

    if play.is_hit:
        obp.hits += 1
        game_obp.hits += 1
    elif play.is_walk:
        obp.walks += 1
        game_obp.walks += 1
    elif play.is_hit_by_pitch:
        obp.hit_by_pitches += 1
        game_obp.hit_by_pitches += 1
    elif play.is_sacrifice_fly:
        obp.sacrifice_flys += 1
        game_obp.sacrifice_flys += 1

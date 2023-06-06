"""Calculate SP stats from game data."""
from dataclasses import dataclass, field

from baseball_obp_and_cobp.game import Game, get_players_in_games
from baseball_obp_and_cobp.player import TEAM_PLAYER_ID, Player
from baseball_obp_and_cobp.stats.stat import Stat


@dataclass
class SP(Stat):
    singles: int = 0
    doubles: int = 0
    triples: int = 0
    home_runs: int = 0
    at_bats: int = 0
    explanation: list[str] = field(default_factory=list)

    @property
    def numerator(self) -> int:
        return sum([self.singles, 2 * self.doubles, 3 * self.triples, 4 * self.home_runs])

    @property
    def denominator(self) -> int:
        return self.at_bats

    def add_arithmetic(self) -> None:
        numerator = f"*1 * 1B={self.singles} + 2 * 2B={self.doubles} + 3 * 3B={self.triples} + 4 * HR={self.home_runs} = {self.numerator}*"  # noqa
        denominator = f"*AB={self.at_bats}*"
        self.explanation.extend([numerator, denominator])

    @property
    def sp(self) -> float:
        try:
            return self.numerator / self.denominator
        except ZeroDivisionError:
            return 0.0


PlayerToSP = dict[str, SP]


def get_player_to_sp(games: list[Game]) -> PlayerToSP:
    players = get_players_in_games(games)
    player_to_ba = {player.id: _get_sp(games, player) for player in players}
    player_to_ba[TEAM_PLAYER_ID] = _get_teams_sp(player_to_ba)
    return player_to_ba


def _get_sp(games: list[Game], player: Player) -> SP:
    sp = SP()
    for game in games:
        try:
            game_player = [p for p in game.players if p.id == player.id][0]
        except IndexError:
            continue

        for play in game_player.plays:
            if play.is_at_bat:
                sp.at_bats += 1

            if play.is_single:
                sp.singles += 1
            elif play.is_double:
                sp.doubles += 1
            elif play.is_triple:
                sp.triples += 1
            elif play.is_home_run:
                sp.home_runs += 1

            sp.add_play(play)

    sp.add_arithmetic()
    return sp


def _get_teams_sp(player_to_sp: PlayerToSP) -> SP:
    team_sp = SP()
    for sp in player_to_sp.values():
        team_sp.singles += sp.singles
        team_sp.doubles += sp.doubles
        team_sp.triples += sp.triples
        team_sp.home_runs += sp.home_runs
        team_sp.at_bats += sp.at_bats

    return team_sp

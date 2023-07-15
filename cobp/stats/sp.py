"""Calculate SP (Slugging Percentage) stats from game data."""
from dataclasses import dataclass, field

from cobp.game import Game, get_players_in_games
from cobp.player import TEAM_PLAYER_ID, Player
from cobp.stats.stat import Stat


@dataclass
class SP(Stat):
    singles: int = 0
    doubles: int = 0
    triples: int = 0
    home_runs: int = 0
    at_bats: int = 0
    explanation: list[str] = field(default_factory=list)
    game_to_stat: dict[str, "SP"] = field(default_factory=dict)

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
    def value(self) -> float:
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
        if not (game_player := game.get_player(player.id)):
            continue

        game_sp = SP()
        for play in game_player.plays:
            if play.is_at_bat:
                sp.at_bats += 1
                game_sp.at_bats += 1

            if play.is_single:
                sp.singles += 1
                game_sp.singles += 1
            elif play.is_double:
                sp.doubles += 1
                game_sp.doubles += 1
            elif play.is_triple:
                sp.triples += 1
                game_sp.triples += 1
            elif play.is_home_run:
                sp.home_runs += 1
                game_sp.home_runs += 1

            sp.add_play(play)

        sp.game_to_stat[game.id] = game_sp

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
        for game_id, game_sp in sp.game_to_stat.items():
            if game_id not in team_sp.game_to_stat:
                team_sp.game_to_stat[game_id] = SP()

            team_game_sp = team_sp.game_to_stat[game_id]
            team_game_sp.singles += game_sp.singles
            team_game_sp.doubles += game_sp.doubles
            team_game_sp.triples += game_sp.triples
            team_game_sp.home_runs += game_sp.home_runs
            team_game_sp.at_bats += game_sp.at_bats

    return team_sp

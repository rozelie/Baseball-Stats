"""Calculate BA stats from game data."""
from dataclasses import dataclass

from pyretrosheet.models.game import Game
from pyretrosheet.models.player import Player

from cobp.stats.stat import Stat
from cobp.utils import TEAM_PLAYER_ID, get_players_plays_used_in_stats, is_play_at_bat, is_play_hit


@dataclass
class BA(Stat):
    hits: int = 0
    at_bats: int = 0

    def add_arithmetic(self) -> None:
        self.explanation.append(f"*H={self.hits} / AB={self.at_bats} == {round(self.value, 3)}*")

    @property
    def value(self) -> float:
        try:
            return self.hits / self.at_bats
        except ZeroDivisionError:
            return 0.0


PlayerToBA = dict[str, BA]


def get_player_to_ba(games: list[Game], players: list[Player]) -> PlayerToBA:
    player_to_ba = {player.id: _get_ba(games, player) for player in players}
    player_to_ba[TEAM_PLAYER_ID] = _get_teams_ba(player_to_ba)
    return player_to_ba


def _get_ba(games: list[Game], player: Player) -> BA:
    ba = BA()
    for _, plays in get_players_plays_used_in_stats(games, player):
        for play in plays:
            if not is_play_hit(play) and not is_play_at_bat(play):
                ba.add_play(play, resultant="N/A", color="red")
                continue

            if is_play_hit(play):
                ba.hits += 1
            if is_play_at_bat(play):
                ba.at_bats += 1
            ba.add_play(play)

    ba.add_arithmetic()
    return ba


def _get_teams_ba(player_to_ba: PlayerToBA) -> BA:
    team_ba = BA()
    for ba in player_to_ba.values():
        team_ba.hits += ba.hits
        team_ba.at_bats += ba.at_bats
    return team_ba

"""Calculate BA stats from game data."""
from dataclasses import dataclass

from baseball_obp_and_cobp.game import Game, get_players_in_games
from baseball_obp_and_cobp.player import TEAM_PLAYER_ID, Player
from baseball_obp_and_cobp.stats.stat import Stat


@dataclass
class BA(Stat):
    hits: int = 0
    at_bats: int = 0

    def add_arithmetic(self) -> None:
        self.explanation.append(f"*H={self.hits} / AB={self.at_bats} == {round(self.ba, 3)}*")

    @property
    def ba(self) -> float:
        try:
            return self.hits / self.at_bats
        except ZeroDivisionError:
            return 0.0


PlayerToBA = dict[str, BA]


def get_player_to_ba(games: list[Game]) -> PlayerToBA:
    players = get_players_in_games(games)
    player_to_ba = {player.id: _get_ba(games, player) for player in players}
    player_to_ba[TEAM_PLAYER_ID] = _get_teams_ba(player_to_ba)
    return player_to_ba


def _get_ba(games: list[Game], player: Player) -> BA:
    ba = BA()
    for game in games:
        if not (game_player := game.get_player(player.id)):
            continue

        for play in game_player.plays:
            if play.is_unused_in_ba_calculations:
                continue

            if not play.is_hit and not play.is_at_bat:
                ba.add_play(play, resultant="N/A", color="red")
                continue

            if play.is_hit:
                ba.hits += 1
            if play.is_at_bat:
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

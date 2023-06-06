from dataclasses import dataclass

from baseball_obp_and_cobp.game import Game, get_players_in_games
from baseball_obp_and_cobp.player import TEAM_PLAYER_ID
from baseball_obp_and_cobp.stats.obp import PlayerToOBP
from baseball_obp_and_cobp.stats.sp import PlayerToSP
from baseball_obp_and_cobp.stats.stat import Stat


@dataclass
class COPS(Stat):
    cobp: float = 0.0
    sp: float = 0.0

    def __post_init__(self) -> None:
        self.explanation.append(f"COBP={round(self.cobp, 3)} + SP={round(self.sp, 3)}")

    @property
    def cops(self):
        return self.cobp + self.sp


PlayerToCOPS = dict[str, COPS]


def get_player_to_cops(games: list[Game], player_to_cobp: PlayerToOBP, player_to_sp: PlayerToSP) -> PlayerToCOPS:
    player_to_cops = {}
    for player in get_players_in_games(games):
        cobp = 0.0
        if cobp_ := player_to_cobp.get(player.id):
            cobp = cobp_.obp

        sp = 0.0
        if sp_ := player_to_sp.get(player.id):
            sp = sp_.sp

        player_to_cops[player.id] = COPS(cobp=cobp, sp=sp)

    player_to_cops[TEAM_PLAYER_ID] = COPS(cobp=player_to_cobp[TEAM_PLAYER_ID].obp, sp=player_to_sp[TEAM_PLAYER_ID].sp)
    return player_to_cops

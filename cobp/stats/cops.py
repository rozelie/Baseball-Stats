from dataclasses import dataclass

from pyretrosheet.models.player import Player

from cobp.stats.obp import PlayerToOBP
from cobp.stats.sp import PlayerToSP
from cobp.stats.stat import Stat
from cobp.utils import TEAM_PLAYER_ID


@dataclass
class COPS(Stat):
    cobp: float = 0.0
    sp: float = 0.0

    def __post_init__(self) -> None:
        self.explanation.append(f"*COBP={round(self.cobp, 3)} + SP={round(self.sp, 3)}*")

    @property
    def value(self):
        return self.cobp + self.sp


PlayerToCOPS = dict[str, COPS]


def get_player_to_cops(players: list[Player], player_to_cobp: PlayerToOBP, player_to_sp: PlayerToSP) -> PlayerToCOPS:
    player_to_cops = {}
    for player in players:
        cobp = 0.0
        if cobp_ := player_to_cobp.get(player.id):
            cobp = cobp_.value

        sp = 0.0
        if sp_ := player_to_sp.get(player.id):
            sp = sp_.value

        player_to_cops[player.id] = COPS(cobp=cobp, sp=sp)

    player_to_cops[TEAM_PLAYER_ID] = COPS(
        cobp=player_to_cobp[TEAM_PLAYER_ID].value, sp=player_to_sp[TEAM_PLAYER_ID].value
    )
    return player_to_cops

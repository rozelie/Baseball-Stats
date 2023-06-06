from dataclasses import dataclass

from baseball_obp_and_cobp.game import Game, get_players_in_games
from baseball_obp_and_cobp.player import TEAM_PLAYER_ID
from baseball_obp_and_cobp.stats.obp import PlayerToOBP
from baseball_obp_and_cobp.stats.sp import PlayerToSP
from baseball_obp_and_cobp.stats.stat import Stat


@dataclass
class OPS(Stat):
    obp: float = 0.0
    sp: float = 0.0

    def __post_init__(self) -> None:
        self.explanation.append(f"*OBP={round(self.obp, 3)} + SP={round(self.sp, 3)}*")

    @property
    def ops(self):
        return self.obp + self.sp


PlayerToOPS = dict[str, OPS]


def get_player_to_ops(games: list[Game], player_to_obp: PlayerToOBP, player_to_sp: PlayerToSP) -> PlayerToOPS:
    player_to_cops = {}
    for player in get_players_in_games(games):
        obp = 0.0
        if obp_ := player_to_obp.get(player.id):
            obp = obp_.obp

        sp = 0.0
        if sp_ := player_to_sp.get(player.id):
            sp = sp_.sp

        player_to_cops[player.id] = OPS(obp=obp, sp=sp)

    player_to_cops[TEAM_PLAYER_ID] = OPS(obp=player_to_obp[TEAM_PLAYER_ID].obp, sp=player_to_sp[TEAM_PLAYER_ID].sp)
    return player_to_cops

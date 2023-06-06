from dataclasses import dataclass

from baseball_obp_and_cobp.game import Game, get_players_in_games
from baseball_obp_and_cobp.player import Player
from baseball_obp_and_cobp.stats.ba import BA, get_player_to_ba
from baseball_obp_and_cobp.stats.cops import COPS, get_player_to_cops
from baseball_obp_and_cobp.stats.obp import OBP, get_player_to_cobp, get_player_to_obp, get_player_to_sobp
from baseball_obp_and_cobp.stats.ops import OPS, get_player_to_ops
from baseball_obp_and_cobp.stats.sp import SP, get_player_to_sp


@dataclass
class PlayerStats:
    obp: OBP
    cobp: OBP
    sobp: OBP
    ba: BA
    sp: SP
    ops: OPS
    cops: COPS


PlayerToStats = dict[str, PlayerStats]


def get_player_to_stats(games: list[Game]) -> PlayerToStats:
    player_to_obp = get_player_to_obp(games)
    player_to_cobp = get_player_to_cobp(games)
    player_to_sobp = get_player_to_sobp(games)
    player_to_ba = get_player_to_ba(games)
    player_to_sp = get_player_to_sp(games)
    player_to_ops = get_player_to_ops(games, player_to_obp, player_to_sp)
    player_to_cops = get_player_to_cops(games, player_to_cobp, player_to_sp)
    all_players = [Player.as_team(), *get_players_in_games(games)]
    return {
        player.id: PlayerStats(
            obp=player_to_obp.get(player.id) or OBP(),
            cobp=player_to_cobp.get(player.id) or OBP(),
            sobp=player_to_sobp.get(player.id) or OBP(),
            ba=player_to_ba.get(player.id) or BA(),
            sp=player_to_sp.get(player.id) or SP(),
            ops=player_to_ops.get(player.id) or OPS(),
            cops=player_to_cops.get(player.id) or COPS(),
        )
        for player in all_players
    }

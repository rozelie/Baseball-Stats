from collections import defaultdict
from dataclasses import dataclass, field
from typing import Mapping

import pandas as pd

from baseball_obp_and_cobp.game import Game, get_players_in_games
from baseball_obp_and_cobp.player import TEAM_PLAYER_ID, Player
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

    at_bats: int = field(init=False)
    hits: int = field(init=False)
    walks: int = field(init=False)
    hit_by_pitches: int = field(init=False)
    sacrifice_flys: int = field(init=False)
    singles: int = field(init=False)
    doubles: int = field(init=False)
    triples: int = field(init=False)
    home_runs: int = field(init=False)

    def __post_init__(self):
        self.at_bats = self.obp.at_bats
        self.hits = self.obp.hits
        self.walks = self.obp.walks
        self.hit_by_pitches = self.obp.hit_by_pitches
        self.sacrifice_flys = self.obp.sacrifice_flys
        self.singles = self.sp.singles
        self.doubles = self.sp.doubles
        self.triples = self.sp.triples
        self.home_runs = self.sp.home_runs


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


def get_player_to_stats_df(games: list[Game], player_to_stats: PlayerToStats) -> pd.DataFrame:
    all_players = get_players_in_games(games)
    player_id_to_player = {p.id: p for p in all_players}
    player_id_to_player[TEAM_PLAYER_ID] = Player.as_team()
    data: Mapping[str, list[str | float]] = defaultdict(list)
    for player_id, stats in player_to_stats.items():
        player = player_id_to_player[player_id]
        data["Player"].append(player.name)
        data["AB"].append(stats.at_bats)
        data["H"].append(stats.hits)
        data["W"].append(stats.walks)
        data["HBP"].append(stats.hit_by_pitches)
        data["SF"].append(stats.sacrifice_flys)
        data["S"].append(stats.singles)
        data["D"].append(stats.doubles)
        data["T"].append(stats.triples)
        data["HR"].append(stats.home_runs)
        data["OBP"].append(stats.obp.obp)
        data["COBP"].append(stats.cobp.obp)
        data["SOBP"].append(stats.sobp.obp)
        data["BA"].append(stats.ba.ba)
        data["SP"].append(stats.sp.sp)
        data["OPS"].append(stats.ops.ops)
        data["COPS"].append(stats.cops.cops)

    return pd.DataFrame(data=data)

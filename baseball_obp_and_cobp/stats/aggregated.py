from collections import defaultdict
from dataclasses import dataclass
from typing import Mapping

import pandas as pd

from baseball_obp_and_cobp.game import Game, get_players_in_games
from baseball_obp_and_cobp.player import TEAM_PLAYER_ID, Player
from baseball_obp_and_cobp.stats.ba import BA, get_player_to_ba
from baseball_obp_and_cobp.stats.basic import BasicStats, get_player_to_basic_stats
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
    basic: BasicStats


PlayerToStats = dict[str, PlayerStats]


def get_player_to_stats(games: list[Game]) -> PlayerToStats:
    player_to_obp = get_player_to_obp(games)
    player_to_cobp = get_player_to_cobp(games)
    player_to_sobp = get_player_to_sobp(games)
    player_to_ba = get_player_to_ba(games)
    player_to_sp = get_player_to_sp(games)
    player_to_ops = get_player_to_ops(games, player_to_obp, player_to_sp)
    player_to_cops = get_player_to_cops(games, player_to_cobp, player_to_sp)
    player_to_basic_stats = get_player_to_basic_stats(games)
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
            basic=player_to_basic_stats.get(player.id) or BasicStats(),
        )
        for player in all_players
    }


def get_player_to_stats_df(games: list[Game], player_to_stats: PlayerToStats) -> pd.DataFrame:
    player_id_to_player = _get_all_players_id_to_player(games)
    data: Mapping[str, list[str | float]] = defaultdict(list)
    for player_id, stats in player_to_stats.items():
        player = player_id_to_player[player_id]
        data["Player"].append(player.name)
        data["G"].append(stats.basic.games)
        data["AB"].append(stats.basic.at_bats)
        data["H"].append(stats.basic.hits)
        data["W"].append(stats.basic.walks)
        data["HBP"].append(stats.basic.hit_by_pitches)
        data["SF"].append(stats.basic.sacrifice_flys)
        data["S"].append(stats.basic.singles)
        data["D"].append(stats.basic.doubles)
        data["T"].append(stats.basic.triples)
        data["HR"].append(stats.basic.home_runs)
        data["OBP"].append(stats.obp.obp)
        data["COBP"].append(stats.cobp.obp)
        data["SOBP"].append(stats.sobp.obp)
        data["BA"].append(stats.ba.ba)
        data["SP"].append(stats.sp.sp)
        data["OPS"].append(stats.ops.ops)
        data["COPS"].append(stats.cops.cops)

    return pd.DataFrame(data=data)


def get_player_to_game_cobp_df(games: list[Game], player_to_stats: PlayerToStats) -> pd.DataFrame:
    player_id_to_player = _get_all_players_id_to_player(games)
    data: Mapping[str, list[str | float]] = defaultdict(list)
    for game_id, player_game_cobp in _get_game_to_player_cobp(games, player_to_stats).items():
        data["Game"].append(game_id)
        for player_id, game_cobp in player_game_cobp.items():
            player = player_id_to_player[player_id]
            data[player.name].append(game_cobp)

    return pd.DataFrame(data=data)


def _get_game_to_player_cobp(games: list[Game], player_to_stats: PlayerToStats) -> Mapping[str, Mapping[str, float]]:
    game_to_player_cobp: Mapping[str, Mapping[str, float]] = defaultdict(dict)
    player_id_to_player = _get_all_players_id_to_player(games, include_team=False)
    for player_id, player in player_id_to_player.items():
        if player_to_stats[player_id].basic.at_bats == 0:
            continue

        for game in games:
            player_game_cobp = player_to_stats[player_id].cobp.game_to_obp.get(game.id)
            player_game_cobp_ = player_game_cobp.obp if player_game_cobp else None
            game_to_player_cobp[game.id][player_id] = player_game_cobp_  # type: ignore

    return game_to_player_cobp


def _get_all_players_id_to_player(games: list[Game], include_team: bool = True) -> dict[str, Player]:
    all_players = get_players_in_games(games)
    player_id_to_player = {p.id: p for p in all_players}
    if include_team:
        player_id_to_player[TEAM_PLAYER_ID] = Player.as_team()
    return player_id_to_player

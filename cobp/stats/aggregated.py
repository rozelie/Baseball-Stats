import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Mapping

import pandas as pd
from pyretrosheet.models.game import Game
from pyretrosheet.models.player import Player
from pyretrosheet.views import get_team_players

from cobp.data import baseball_reference
from cobp.models.team import Team
from cobp.stats.ba import BA, get_player_to_ba
from cobp.stats.basic import BasicStats, get_player_to_basic_stats
from cobp.stats.cops import COPS, get_player_to_cops
from cobp.stats.obp import OBP, get_player_to_cobp, get_player_to_loop, get_player_to_obp, get_player_to_sobp
from cobp.stats.ops import OPS, get_player_to_ops
from cobp.stats.sp import SP, get_player_to_sp
from cobp.utils import TEAM_PLAYER_ID, build_team_player

logger = logging.getLogger(__name__)


@dataclass
class PlayerStats:
    obp: OBP
    cobp: OBP
    sobp: OBP
    loop: OBP
    ba: BA
    sp: SP
    ops: OPS
    cops: COPS
    basic: BasicStats

    @property
    def loops(self) -> float:
        return self.loop.value + self.ops.value

    @property
    def sops(self) -> float:
        return self.sobp.value + self.ops.value


PlayerToStats = dict[str, PlayerStats]


def get_player_to_stats(games: list[Game], team: Team) -> PlayerToStats:
    players = get_team_players(games, team.retrosheet_id)
    player_to_obp = get_player_to_obp(games, players)
    player_to_cobp = get_player_to_cobp(games, players)
    player_to_sobp = get_player_to_sobp(games, players)
    player_to_loop = get_player_to_loop(games, players)
    player_to_ba = get_player_to_ba(games, players)
    player_to_sp = get_player_to_sp(games, players)
    player_to_ops = get_player_to_ops(players, player_to_obp, player_to_sp)
    player_to_cops = get_player_to_cops(players, player_to_cobp, player_to_sp)
    player_to_basic_stats = get_player_to_basic_stats(games, players)
    all_players = [build_team_player(), *players]
    return {
        player.id: PlayerStats(
            obp=player_to_obp.get(player.id) or OBP(),
            cobp=player_to_cobp.get(player.id) or OBP(),
            sobp=player_to_sobp.get(player.id) or OBP(),
            loop=player_to_loop.get(player.id) or OBP(),
            ba=player_to_ba.get(player.id) or BA(),
            sp=player_to_sp.get(player.id) or SP(),
            ops=player_to_ops.get(player.id) or OPS(),
            cops=player_to_cops.get(player.id) or COPS(),
            basic=player_to_basic_stats.get(player.id) or BasicStats(),
        )
        for player in all_players
    }


def get_player_to_stats_df(
    games: list[Game],
    player_to_stats: PlayerToStats,
    team: Team,
    year: int,
) -> pd.DataFrame:
    players = [build_team_player(), *get_team_players(games, team.retrosheet_id)]
    player_id_to_player = {p.id: p for p in players}
    data: Mapping[str, list[str | float | int]] = defaultdict(list)
    for player_id, stats in player_to_stats.items():
        player = player_id_to_player[player_id]
        runs, rbis = _get_runs_and_rbis(year, team, player, stats)
        data["Team"].append(team.name)
        data["Year"].append(year)
        data["Player"].append(player.name)
        data["ID"].append(player.name)
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
        data["R"].append(runs)
        data["RBI"].append(rbis)
        data["OBP"].append(stats.obp.value)
        data["COBP"].append(stats.cobp.value)
        data["LOOP"].append(stats.loop.value)
        data["SOBP"].append(stats.sobp.value)
        data["BA"].append(stats.ba.value)
        data["SP"].append(stats.sp.value)
        data["OPS"].append(stats.ops.value)
        data["COPS"].append(stats.cops.value)
        data["LOOPS"].append(stats.loops)
        data["SOPS"].append(stats.sops)

    return pd.DataFrame(data=data)


def get_player_to_game_stat_df(
    games: list[Game], team: Team, player_to_stats: PlayerToStats, stat_name: str
) -> pd.DataFrame:
    players = [build_team_player(), get_team_players(games, team.retrosheet_id)]
    player_id_to_player = {p.id: p for p in players}
    data: Mapping[str, list[str | float]] = defaultdict(list)
    for game_id, player_game_stat in _get_game_to_player_stat(games, team, player_to_stats, stat_name).items():
        data["Game"].append(game_id)
        for player_id, game_stat in player_game_stat.items():
            player = player_id_to_player[player_id]
            data[player.name].append(game_stat)

    return pd.DataFrame(data=data)


def _get_game_to_player_stat(
    games: list[Game], team: Team, player_to_stats: PlayerToStats, stat_name: str
) -> Mapping[str, Mapping[str, float]]:
    players = get_team_players(games, team.retrosheet_id)
    player_id_to_player = {p.id for p in players}
    game_to_player_stat: Mapping[str, Mapping[str, float]] = defaultdict(dict)
    for player_id, _ in player_id_to_player.items():
        if player_to_stats[player_id].basic.at_bats == 0:
            continue

        player_stats = player_to_stats[player_id]
        player_stat = getattr(player_stats, stat_name)
        for game in games:
            player_game_stat = player_stat.game_to_stat.get(game.id)
            player_game_stat_value = player_game_stat.value if player_game_stat else None
            game_to_player_stat[game.id][player_id] = player_game_stat_value  # type: ignore

    return game_to_player_stat


def _get_runs_and_rbis(year: int, team: Team, player: Player, stats: PlayerStats) -> tuple[int, int]:
    if player.id == TEAM_PLAYER_ID:
        return stats.basic.runs, stats.basic.runs_batted_in

    # players without any bats will not appear in the Baseball Reference data
    if stats.basic.at_bats == 0:
        return 0, 0

    # rare case where the player will appear in the baseball reference data due to having more than one
    # at bat for the season, but they had all of their hits for a single team and no hits for another team
    # so they are not reported to have any hitting stats for that team
    no_team_at_bats = [
        ("Mat Latos", "ANA", 2015),
        ("Jay Buente", "TBA", 2011),
        ("Cha Seung Baek", "SEA", 2008),
        ("Todd Wellemeyer", "KCA", 2007),
        ("Cory Lidle", "NYA", 2006),
        ("Felix Heredia", "NYA", 2003),
        ("Jason Bere", "CLE", 2000),
        ("Steve Woodard", "CLE", 2000),
    ]
    if (player.name, team.retrosheet_id, year) in no_team_at_bats:
        return 0, 0

    bb_ref_stats = baseball_reference.get_seasonal_players_stats(year)
    bb_ref_player = baseball_reference.lookup_player(bb_ref_stats, player, team, year)
    return bb_ref_player["runs"].values[0], bb_ref_player["rbis"].values[0]  # type: ignore

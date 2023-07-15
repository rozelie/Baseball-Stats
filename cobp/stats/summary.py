import statistics
from collections import defaultdict
from dataclasses import dataclass
from typing import Mapping

import pandas as pd

from cobp.game import Game
from cobp.player import TEAM_PLAYER_ID
from cobp.stats import supports
from cobp.stats.aggregated import PlayerToStats


@dataclass
class SummaryStats:
    mean: float
    median: float
    min: float
    max: float
    standard_deviation: float


def get_team_seasonal_summary_stats_df(games: list[Game], player_to_stats: PlayerToStats) -> pd.DataFrame:
    data: Mapping[str, list[str | float]] = defaultdict(list)
    for stat in supports.SUMMARY_STATS:
        summary_stats = _get_team_seasonal_summary_stats_for_stat(games, player_to_stats, stat)
        data["Stat"].append(stat.upper())
        data["Mean"].append(summary_stats.mean)
        data["Median"].append(summary_stats.median)
        data["Std. Dev"].append(summary_stats.standard_deviation)
        data["Min"].append(summary_stats.min)
        data["Max"].append(summary_stats.max)

    return pd.DataFrame(data=data)


def _get_team_seasonal_summary_stats_for_stat(
    games: list[Game], player_to_stats: PlayerToStats, stat: str
) -> SummaryStats:
    team_stats = player_to_stats[TEAM_PLAYER_ID]
    stat_values: list[float] = []
    team_stat = getattr(team_stats, stat)
    for game in games:
        team_game_stat = team_stat.game_to_stat.get(game.id)
        if team_game_stat:
            stat_values.append(team_game_stat.value)

    return SummaryStats(
        mean=statistics.mean(stat_values),
        median=statistics.median(stat_values),
        min=min(stat_values),
        max=max(stat_values),
        standard_deviation=statistics.stdev(stat_values),
    )

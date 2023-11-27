from dataclasses import dataclass
from functools import lru_cache

import pybaseball
from pybaseball import cache as pybaseball_cache

pybaseball_cache.enable()


@dataclass
class BattingStats:
    rbis: int


PlayerId = tuple[str, str]  # (name, team_id)
PlayerIdToBattingStats = dict[PlayerId, BattingStats]


@lru_cache(maxsize=None)
def get_player_to_yearly_batting_stats(year: int) -> PlayerIdToBattingStats:
    """Retrieve player batting stats from Fangraph.

    NOTE: this only includes top 130 batters
    """
    batting_stats_df = pybaseball.batting_stats(year, year)
    return {(row.Name, row.Team): BattingStats(rbis=row.RBI) for row in batting_stats_df.itertuples()}

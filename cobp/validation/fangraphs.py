import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

import pandas as pd

from cobp import paths
from cobp.data.fangraphs import get_player_to_yearly_batting_stats
from cobp.models.team import Team

logger = logging.getLogger(__name__)


@dataclass
class RBIDiscrepancy:
    player_name: str
    team: Team
    year: int
    retrosheet_rbis: int
    fangraph_rbis: int


def validate_players_rbis(player_name: str, team: Team, year: int, retrosheet_rbis: int) -> RBIDiscrepancy | None:
    player_to_yearly_batting_stats = get_player_to_yearly_batting_stats(year)
    player_id = (player_name, team.retrosheet_id)
    try:
        fangraph_rbis = player_to_yearly_batting_stats[player_id].rbis
        if retrosheet_rbis != fangraph_rbis:
            return RBIDiscrepancy(
                player_name=player_name,
                team=team,
                year=year,
                retrosheet_rbis=retrosheet_rbis,
                fangraph_rbis=fangraph_rbis,
            )
    except KeyError:
        # fangraph player data only seems to return top batters
        logger.debug(f"Unable to lookup fangraph player: {player_id=}")

    return None


def write_rbi_discrepancies(discrepancies: list[RBIDiscrepancy]) -> None:
    data: Mapping[str, list[str | int]] = defaultdict(list)
    for discrepancy in discrepancies:
        data["year"].append(discrepancy.year)
        data["team"].append(discrepancy.team.pretty_name)
        data["player"].append(discrepancy.player_name)
        data["retrosheet_rbis"].append(discrepancy.retrosheet_rbis)
        data["fangraph_rbis"].append(discrepancy.fangraph_rbis)

    df = pd.DataFrame(data=data)

    paths.DISCREPANCY_DIR.mkdir(exist_ok=True, parents=True)
    discrepancy_file = paths.DISCREPANCY_DIR / f'{datetime.now().strftime("%Y_%m_%d_%H_%M")}.csv'
    logger.info(f"Writing rbi discrepancies to {discrepancy_file.as_posix()}")
    df.to_csv(path_or_buf=discrepancy_file, index=False)

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from cobp import paths
from cobp.data import baseball_reference
from cobp.models.player import TEAM_PLAYER_ID
from cobp.models.team import Team

logger = logging.getLogger(__name__)


@dataclass
class RBICrossReference:
    year: int
    player_name: str
    player_id: str
    team_id: str
    retrosheet_rbis: int
    bb_ref_rbis: int

    @property
    def is_equal(self) -> bool:
        return self.retrosheet_rbis == self.bb_ref_rbis


def cross_reference_retrosheet_seasonal_rbis_with_baseball_reference(
    year: int, player_name: str, player_id: str, team: Team, retrosheet_rbis: int
) -> RBICrossReference | None:
    team_id = team.baseball_reference_id or team.retrosheet_id
    all_bb_ref_stats = baseball_reference.get_seasonal_players_stats(year)
    bb_ref_player = baseball_reference.lookup_player(all_bb_ref_stats, player_name, team_id)
    try:
        bb_ref_rbis = bb_ref_player["rbis"].values[0]  # type: ignore
    except IndexError:
        logger.debug(
            "Unable to find Baseball Reference player rbis: " f"{year=} | {player_name=} | {player_id=} | {team_id=}"
        )
        return None

    return RBICrossReference(
        year=year,
        player_name=player_name,
        player_id=player_id,
        team_id=team_id,
        retrosheet_rbis=retrosheet_rbis,
        bb_ref_rbis=bb_ref_rbis,
    )


def get_bb_ref_and_retrosheet_rbi_discrepancies(
    year: int, team: Team, retrosheet_df: pd.DataFrame
) -> list[RBICrossReference]:
    unequal_references = []
    found_players = 0
    team_id = team.baseball_reference_id or team.retrosheet_id
    for row in retrosheet_df.itertuples():
        player_name = row.Player
        if player_name == TEAM_PLAYER_ID:
            continue

        reference_result = cross_reference_retrosheet_seasonal_rbis_with_baseball_reference(
            year=year,
            player_name=player_name,
            player_id=row.ID,
            team=team,
            retrosheet_rbis=row.RBI,
        )
        if not reference_result:
            continue
        else:
            found_players += 1

        if not reference_result.is_equal:
            unequal_references.append(reference_result)

    if found_players == 0:
        raise ValueError(
            f"Found {found_players} players for {year} {team_id} "
            f"- it is likely that Retrosheet and Baseball Reference team ids do not "
            f"match and a lookup needs to be added."
        )

    logger.info(f"Found {found_players} players for {year} {team_id} in Baseball Reference cross reference")
    return unequal_references


def write_bb_ref_and_retrosheet_rbi_discrepancies(file_name: str, discrepancies: list[RBICrossReference]) -> None:
    file_path = get_bb_ref_and_retrosheet_rbi_discrepancies_file_path(file_name)
    file_path.unlink(missing_ok=True)

    lines = ["year,player,team,retrosheet_rbis,baseball_reference_rbis"]
    lines.extend(
        [
            ",".join([str(d.year), d.player_name, d.team_id, str(d.retrosheet_rbis), str(d.bb_ref_rbis)])
            for d in discrepancies
        ]
    )

    file_path.write_text("\n".join(lines))
    logger.info(f"Wrote Baseball Reference and Retrosheet discrepancies to {file_path.as_posix()}")


def get_bb_ref_and_retrosheet_rbi_discrepancies_file_path(file_name: str) -> Path:
    return paths.DISCREPANCY_DIR / file_name

"""Project entrypoint.

Runs the streamlit application and handles high-level control flow.
"""
import logging

import streamlit as st

from cobp import results, session
from cobp.env import ENV
from cobp.models.team import TEAM_RETROSHEET_ID_TO_TEAM, Team, get_team_for_year
from cobp.ui import selectors
from cobp.ui.core import display_header, set_streamlit_config

logger = logging.getLogger(__name__)


def main(
    team: Team | str | None = ENV.TEAM,
    year: int | str | None = ENV.YEAR,
    game_id: str | None = ENV.GAME_ID,
) -> None:
    """Run the streamlit application."""
    set_streamlit_config()
    display_header()

    if team and team == ENV.TEAM:
        team = get_team_for_year(team, year)  # type: ignore

    if game_id:
        team, year = _get_team_and_year_from_game_id(game_id, team)  # type: ignore

    if team or year:
        logger.info(f"Executing: {team=} | {year=}...")

    year = year or selectors.get_year_selection()
    if year and not team:
        team = selectors.get_team_selection(year)

    if not team or not year:
        return

    if session.get_state(session.StateKey.REFRESH_NEEDED) is True:
        st.text("Please refresh to continue")
        return

    results.display(team, year, game_id)
    logger.info(f"Execution finished for: {team=} | {year=}")


def _get_team_and_year_from_game_id(game_id: str, team: Team | None) -> tuple[Team, int]:
    team_id = "".join([c for c in game_id if c.isalpha()])
    date_ = "".join([c for c in game_id if c.isnumeric()])
    year = int(date_[0:4])
    return team or get_team_for_year(team_id, year), year


if __name__ == "__main__":
    main()

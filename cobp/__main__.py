"""Project entrypoint.

Runs the streamlit application and handles high-level control flow.
"""
import logging

import streamlit as st

from cobp import results, session
from cobp.models.team import Team
from cobp.ui import selectors
from cobp.ui.core import display_header, set_streamlit_config

logger = logging.getLogger(__name__)


def main(team: Team | str | None = None, year: int | str | None = None) -> None:
    """Run the streamlit application."""
    set_streamlit_config()
    display_header()

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

    results.display(team, year)
    logger.info(f"Execution finished for: {team=} | {year=}")


if __name__ == "__main__":
    main()

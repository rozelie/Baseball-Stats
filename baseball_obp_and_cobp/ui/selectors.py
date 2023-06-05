from typing import Any

import streamlit as st

from baseball_obp_and_cobp.game import Game
from baseball_obp_and_cobp.team import Team

EMPTY_CHOICE = ""
ENTIRE_SEASON = "Entire Season"


def get_team_and_year_selection() -> tuple[Team | None, int | None]:
    team_column, year_column = st.columns(2)
    with team_column:
        team = _get_team_selection()
    with year_column:
        year = _get_year_selection()
    return team, year


def get_game_selection(games: list[Game]) -> Game | str | None:
    game_id_to_game = {g.id: g for g in games}
    game_pretty_ids = [g.pretty_id for g in games]
    game_pretty_id_to_game_id = {g.pretty_id: g.id for g in games}
    options = [EMPTY_CHOICE, ENTIRE_SEASON, *sorted(game_pretty_ids)]
    selection = _get_selection("Select Game:", options=options)
    if not selection:
        return None
    if selection == ENTIRE_SEASON:
        return ENTIRE_SEASON

    game_id_selected = game_pretty_id_to_game_id[selection]
    return game_id_to_game[game_id_selected]


def _get_team_selection() -> Team | None:
    team_pretty_name_to_team = {t.pretty_name: t for t in Team}
    options = [EMPTY_CHOICE, *sorted(team_pretty_name_to_team.keys())]
    selected_team_pretty_name = _get_selection("Select Team:", options=options)
    return team_pretty_name_to_team.get(selected_team_pretty_name)


def _get_year_selection() -> int | None:
    options = [EMPTY_CHOICE, *reversed(range(2000, 2023))]
    year = _get_selection("Select Year:", options=options)
    return year if year else None


def _get_selection(prompt: str, options: list[Any]) -> Any:
    return st.selectbox(prompt, options=options)

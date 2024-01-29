from typing import Any

import streamlit as st
from pyretrosheet.models.game import Game
from pyretrosheet.models.player import Player

from cobp.models.team import TEAMS, Team, get_teams_for_year
from cobp.utils import get_game_pretty_id

EMPTY_CHOICE = ""
ENTIRE_SEASON = "Entire Season"
FULL_PERIOD = "Full Period"
ALL_TEAMS = "All Teams"
FIRST_AVAILABLE_YEAR = 2000
LAST_AVAILABLE_YEAR = 2022


def get_year_selection() -> int | str | None:
    options = [EMPTY_CHOICE, FULL_PERIOD, *reversed(range(FIRST_AVAILABLE_YEAR, LAST_AVAILABLE_YEAR + 1))]
    year = _get_selection("Select Year:", options=options)
    return year if year else None


def get_team_selection(year: int | str) -> Team | str | None:
    years_teams = TEAMS if year == FULL_PERIOD else get_teams_for_year(year)  # type: ignore
    team_pretty_name_to_team = {t.pretty_name: t for t in years_teams}
    options = [EMPTY_CHOICE, ALL_TEAMS, *sorted(team_pretty_name_to_team.keys())]
    selected_team = _get_selection("Select Team:", options=options)
    if selected_team == ALL_TEAMS:
        return ALL_TEAMS
    return team_pretty_name_to_team.get(selected_team)


def get_game_selection(games: list[Game]) -> Game | str | None:
    game_id_to_game = {g.id.raw: g for g in games}
    game_pretty_ids = [get_game_pretty_id(g) for g in games]
    game_pretty_id_to_game_id = {get_game_pretty_id(g): g.id.raw for g in games}
    options = [EMPTY_CHOICE, ENTIRE_SEASON, *sorted(game_pretty_ids)]
    selection = _get_selection("Select Game:", options=options)
    if not selection:
        return None
    if selection == ENTIRE_SEASON:
        return ENTIRE_SEASON

    game_id_selected = game_pretty_id_to_game_id[selection]
    return game_id_to_game[game_id_selected]


def get_player_selection(players: list[Player]) -> Player | None:
    player_id_to_player = {p.id: p for p in players}
    player_name_to_id = {p.name: p.id for p in players}
    options = [EMPTY_CHOICE, *player_name_to_id.keys()]
    player_name = _get_selection("Select Player:", options=options)
    return player_id_to_player[player_name_to_id[player_name]] if player_name else None


def get_correlation_method() -> str:
    return _get_selection("Correlation Method:", options=["pearson", "kendall", "spearman"])  # type: ignore


def get_stat_to_correlate() -> str | None:
    selection = _get_selection("Stat To Correlate:", options=[EMPTY_CHOICE, "OBP", "COBP", "SOBP", "SP"])
    return selection if selection != EMPTY_CHOICE else None


def _get_selection(prompt: str, options: list[Any]) -> Any:
    return st.selectbox(prompt, options=options)

"""Generates and displays results based on user input."""
from traceback import format_exc

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from cobp import session
from cobp.data import retrosheet
from cobp.models import game
from cobp.models.game import Game
from cobp.models.team import Team, get_teams_for_year
from cobp.stats.aggregated import get_player_to_stats, get_player_to_stats_df
from cobp.ui import download, selectors
from cobp.ui.core import display_error
from cobp.ui.selectors import ALL_TEAMS, ENTIRE_SEASON, FIRST_AVAILABLE_YEAR, FULL_PERIOD, LAST_AVAILABLE_YEAR
from cobp.ui.stats import display_game


def display(team: Team | str, year: int | str) -> None:
    if team == ALL_TEAMS and not year == FULL_PERIOD:
        _display_download_for_all_teams_for_year(year)  # type: ignore
    elif not team == ALL_TEAMS and year == FULL_PERIOD:
        _display_download_for_team_for_all_years(team)  # type: ignore
    elif team == ALL_TEAMS and year == FULL_PERIOD:
        _display_download_for_all_teams_for_all_years()
    else:
        _display_stats_for_team_in_year(year, team)  # type: ignore


def _load_season_games(year: int, team: Team) -> list[Game]:
    seasons_event_files = retrosheet.get_seasons_event_files(year)
    try:
        return list(game.load_teams_games(seasons_event_files, team))
    except ValueError:
        display_error(f"Error in loading {year} {team.pretty_name}'s data: {format_exc()}")
        return []


def _display_download_for_all_teams_for_year(year: int) -> None:
    df = pd.DataFrame()
    progress = st.progress(0)
    teams_for_year = get_teams_for_year(year)
    for i, team_ in enumerate(teams_for_year):
        df = _add_teams_yearly_stats_to_df(
            progress=progress,
            current_iteration=i,
            total_iterations=len(teams_for_year),
            team=team_,
            year=year,
            df=df,
        )

    progress.empty()
    download.download_df_button(df, f"{year}_all_teams.csv")
    session.set_state(session.StateKey.REFRESH_NEEDED, True)


def _display_download_for_team_for_all_years(team: Team) -> None:
    df = pd.DataFrame()
    progress = st.progress(0)
    for i, year_ in enumerate(reversed(range(FIRST_AVAILABLE_YEAR, LAST_AVAILABLE_YEAR + 1))):
        df = _add_teams_yearly_stats_to_df(
            progress=progress,
            current_iteration=i,
            total_iterations=LAST_AVAILABLE_YEAR - FIRST_AVAILABLE_YEAR,
            team=team,
            year=year_,
            df=df,
        )

    progress.empty()
    download.download_df_button(df, f"{FIRST_AVAILABLE_YEAR}_to_{LAST_AVAILABLE_YEAR}_{team.pretty_name}.csv")
    session.set_state(session.StateKey.REFRESH_NEEDED, True)


def _display_download_for_all_teams_for_all_years() -> None:
    df = pd.DataFrame()
    progress = st.progress(0)
    current_iteration = 0
    for year_ in reversed(range(FIRST_AVAILABLE_YEAR, LAST_AVAILABLE_YEAR + 1)):
        teams_for_year = get_teams_for_year(year_)
        for team_ in teams_for_year:
            df = _add_teams_yearly_stats_to_df(
                progress=progress,
                current_iteration=current_iteration,
                total_iterations=LAST_AVAILABLE_YEAR - FIRST_AVAILABLE_YEAR,
                team=team_,
                year=year_,
                df=df,
            )
        current_iteration += 1

    progress.empty()
    download.download_df_button(df, f"{FIRST_AVAILABLE_YEAR}_to_{LAST_AVAILABLE_YEAR}_all_teams.csv")
    session.set_state(session.StateKey.REFRESH_NEEDED, True)


def _display_stats_for_team_in_year(year: int, team: Team) -> None:
    all_games = _load_season_games(year, team)
    if not all_games:
        return

    games = _get_games_selection(all_games)
    if not games:
        return

    player_to_stats = get_player_to_stats(games)
    display_game(
        games=games,
        player_to_stats=player_to_stats,
        player_to_stats_df=get_player_to_stats_df(games, player_to_stats),
    )


def _get_games_selection(all_games: list[Game]) -> list[Game] | None:
    game_ = selectors.get_game_selection(all_games)
    if not game_:
        return None

    return all_games if game_ == ENTIRE_SEASON else [game_]  # type: ignore


def _add_teams_yearly_stats_to_df(
    progress: DeltaGenerator,
    current_iteration: int,
    total_iterations: int,
    team: Team,
    year: int,
    df: pd.DataFrame,
) -> pd.DataFrame:
    progress.progress(current_iteration / total_iterations, text=f"Loading {year} {team.pretty_name} data...")
    team_games: list[Game] = _load_season_games(year, team)
    team_player_to_stats = get_player_to_stats(team_games)
    team_player_to_stats_df = get_player_to_stats_df(
        team_games,
        team_player_to_stats,
        team=team,
        year=year,
    )
    return pd.concat([df, team_player_to_stats_df])
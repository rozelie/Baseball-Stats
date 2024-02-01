"""Generates and displays results based on user input."""
import logging
from traceback import format_exc

import pandas as pd
import streamlit as st
from pyretrosheet.load import load_games
from pyretrosheet.models.game import Game
from streamlit.delta_generator import DeltaGenerator

from cobp import session
from cobp.data import cross_reference
from cobp.env import ENV
from cobp.models.team import Team, get_teams_for_year
from cobp.stats.aggregated import get_player_to_stats, get_player_to_stats_df
from cobp.ui import download, selectors
from cobp.ui.core import display_error
from cobp.ui.selectors import ALL_TEAMS, ENTIRE_SEASON, FIRST_AVAILABLE_YEAR, FULL_PERIOD, LAST_AVAILABLE_YEAR
from cobp.ui.stats import display_game

logger = logging.getLogger(__name__)


def load_season_games(
    year: int,
    team: Team,
    basic_info_only: bool = False,
    game_ids: list[str] | None = None,
) -> list[Game]:
    try:
        # @TODO: Cache results for yearly results
        games_for_year = list(load_games(year=year, basic_info_only=basic_info_only))
        logger.info(f"Loaded {len(games_for_year)} games for {year} ({basic_info_only=})")
        if game_ids:
            teams_games_for_year = [g for g in games_for_year if g.id.raw in game_ids]
            logger.info(f"Loaded {len(teams_games_for_year)} games for {year}, matching {len(game_ids)} game ids")
        else:
            teams_games_for_year = [
                g for g in games_for_year if team.retrosheet_id in (g.home_team_id, g.visiting_team_id)
            ]
            logger.info(f"Loaded {len(teams_games_for_year)} games for {year} {team.pretty_name}")

        return teams_games_for_year
    except ValueError:
        display_error(f"Error in loading {year} {team.pretty_name}'s data:\n\n{format_exc()}")
        raise


def display(team: Team | str, year: int | str, game_id: str | None) -> None:
    logger.info(f"Building results for team={team} | {year=} | {game_id=}")
    if team == ALL_TEAMS and not year == FULL_PERIOD:
        _display_download_for_all_teams_for_year(year)  # type: ignore
    elif not team == ALL_TEAMS and year == FULL_PERIOD:
        _display_download_for_team_for_all_years(team)  # type: ignore
    elif team == ALL_TEAMS and year == FULL_PERIOD:
        _display_download_for_all_teams_for_all_years()
    else:
        _display_stats_for_team_in_year(year, team, game_id)  # type: ignore


def _display_download_for_all_teams_for_year(year: int) -> None:
    df = pd.DataFrame()
    progress = st.progress(0)
    teams_for_year = get_teams_for_year(year)
    for i, team_ in enumerate(teams_for_year):
        team_player_to_stats_df = _get_team_player_to_stats_df(
            progress=progress,
            current_iteration=i,
            total_iterations=len(teams_for_year),
            team=team_,
            year=year,
        )
        df = pd.concat([df, team_player_to_stats_df])

    progress.empty()
    download.download_df_button(df, f"{year}_all_teams.csv")
    session.set_state(session.StateKey.REFRESH_NEEDED, True)


def _display_download_for_team_for_all_years(team: Team) -> None:
    df = pd.DataFrame()
    progress = st.progress(0)
    for i, year_ in enumerate(reversed(range(FIRST_AVAILABLE_YEAR, LAST_AVAILABLE_YEAR + 1))):
        team_player_to_stats_df = _get_team_player_to_stats_df(
            progress=progress,
            current_iteration=i,
            total_iterations=LAST_AVAILABLE_YEAR - FIRST_AVAILABLE_YEAR,
            team=team,
            year=year_,
        )
        df = pd.concat([df, team_player_to_stats_df])

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
            team_player_to_stats_df = _get_team_player_to_stats_df(
                progress=progress,
                current_iteration=current_iteration,
                total_iterations=LAST_AVAILABLE_YEAR - FIRST_AVAILABLE_YEAR,
                team=team_,
                year=year_,
            )
            df = pd.concat([df, team_player_to_stats_df])

        current_iteration += 1

    progress.empty()
    download.download_df_button(df, f"{FIRST_AVAILABLE_YEAR}_to_{LAST_AVAILABLE_YEAR}_all_teams.csv")
    session.set_state(session.StateKey.REFRESH_NEEDED, True)


def _display_stats_for_team_in_year(year: int, team: Team, game_id: str | None) -> None:
    games = load_season_games(year, team, basic_info_only=True)
    if not games:
        return

    if game_id:
        game_ids = [game_id]
    elif ENV.YEAR:
        game_ids = [game.id.raw for game in games]
    else:
        game_selection = _get_games_selection(games)
        if not game_selection:
            return
        game_ids = [game.id.raw for game in game_selection]

    loaded_games = load_season_games(year, team, basic_info_only=False, game_ids=game_ids)
    player_to_stats = get_player_to_stats(loaded_games, team)
    display_game(
        team=team,
        games=loaded_games,
        player_to_stats=player_to_stats,
        player_to_stats_df=get_player_to_stats_df(loaded_games, player_to_stats, team=team, year=year),
    )


def _get_games_selection(all_games: list[Game]) -> list[Game] | None:
    game_ = selectors.get_game_selection(all_games)
    if not game_:
        return None

    return all_games if game_ == ENTIRE_SEASON else [game_]


def _get_team_player_to_stats_df(
    progress: DeltaGenerator,
    current_iteration: int,
    total_iterations: int,
    team: Team,
    year: int,
) -> pd.DataFrame:
    progress.progress(current_iteration / total_iterations, text=f"Loading {year} {team.pretty_name} data...")
    team_games: list[Game] = load_season_games(year, team)
    team_player_to_stats = get_player_to_stats(team_games, team)
    df = get_player_to_stats_df(
        team_games,
        team_player_to_stats,
        team=team,
        year=year,
    )
    # remove players without ABs as they are not currently useful
    df = df[df["AB"] > 0]

    if not ENV.USE_BASEBALL_REFERENCE_R_AND_RBI_STATS:
        discrepancies = cross_reference.get_bb_ref_and_retrosheet_rbi_discrepancies(
            year=year,
            team=team,
            retrosheet_df=df,
        )
        if discrepancies:
            cross_reference.write_bb_ref_and_retrosheet_rbi_discrepancies(
                f"{year}_{team.retrosheet_id}.csv", discrepancies
            )

    return df

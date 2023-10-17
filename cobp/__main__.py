import logging
import sys
from dataclasses import dataclass

import pandas as pd
import streamlit as st

from cobp import game
from cobp.data import retrosheet
from cobp.game import Game
from cobp.stats.aggregated import PlayerToStats, get_player_to_stats, get_player_to_stats_df
from cobp.team import Team
from cobp.ui import download, selectors
from cobp.ui.core import display_error, set_streamlit_config
from cobp.ui.selectors import ALL_TEAMS, ENTIRE_SEASON, FULL_PERIOD
from cobp.ui.stats import display_game

REFRESH_NEEDED = "refresh_needed"
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.DEBUG, stream=sys.stdout)


@dataclass
class AggregateSelection:
    team: Team
    year: int
    player_to_stats: PlayerToStats


def main(team: Team | str | None = None, year: int | str | None = None, all_games: bool | None = None) -> None:
    """Project entrypoint."""
    set_streamlit_config()
    if not team or not year:
        team, year = selectors.get_team_and_year_selection()

    if not team or not year:
        return

    if st.session_state.get(REFRESH_NEEDED) is True:
        st.text("Please refresh to continue")
        return

    if team == ALL_TEAMS and not year == FULL_PERIOD:
        df = pd.DataFrame()
        progress = st.progress(0)
        num_teams = len(Team)
        for i, team_ in enumerate(Team):
            progress.progress(i / num_teams, text=f"Loading {team_.pretty_name} {year} data...")
            team_games: list[Game] = _load_season_games(year, team_)  # type: ignore
            team_player_to_stats = get_player_to_stats(team_games)
            team_player_to_stats_df = get_player_to_stats_df(
                team_games,
                team_player_to_stats,
                team=team_,
            )
            df = pd.concat([df, team_player_to_stats_df])

        progress.empty()
        download.download_df_button(df, f"{year}_all_teams.csv")
        st.session_state[REFRESH_NEEDED] = True

    elif not team == ALL_TEAMS and year == FULL_PERIOD:
        st.text("Work in progress - coming soon")
        # year_to_all_games = {}
        # for year_ in range(FIRST_AVAILABLE_YEAR, LAST_AVAILABLE_YEAR + 1):
        #     year_to_all_games[year] = _load_season_games(year_, team)

    elif team == ALL_TEAMS and year == FULL_PERIOD:
        st.text("Work in progress - coming soon")
        # team_year_to_all_games = {}
        # for team_ in Team:
        #     for year_ in range(FIRST_AVAILABLE_YEAR, LAST_AVAILABLE_YEAR + 1):
        #         team_year_to_all_games[(team_, year_)] = _load_season_games(year_, team_)

    else:
        all_games_ = _load_season_games(year, team)  # type: ignore
        if not all_games_:
            return

        games = all_games_ if all_games else _get_games_selection(all_games_)
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


def _load_season_games(year: int, team: Team) -> list[Game]:
    seasons_event_files = retrosheet.get_seasons_event_files(year)
    try:
        return list(game.load_teams_games(seasons_event_files, team))
    except ValueError as error:
        display_error(str(error))
        return []


if __name__ == "__main__":
    main(
        # team=Team.CHICAGO_CUBS,
        # year=2022,
        # all_games=True,
    )

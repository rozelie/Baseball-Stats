from baseball_obp_and_cobp import game, retrosheet
from baseball_obp_and_cobp.game import Game
from baseball_obp_and_cobp.stats.aggregated import (
    get_player_to_game_cobp_df,
    get_player_to_stats,
    get_player_to_stats_df,
)
from baseball_obp_and_cobp.team import Team
from baseball_obp_and_cobp.ui import selectors
from baseball_obp_and_cobp.ui.core import display_error, set_streamlit_config
from baseball_obp_and_cobp.ui.selectors import ENTIRE_SEASON
from baseball_obp_and_cobp.ui.stats import display_game


def main() -> None:
    """Project entrypoint."""
    set_streamlit_config()
    team, year = selectors.get_team_and_year_selection()
    if not team or not year:
        return

    games = _get_games_selection(year, team)
    if not games:
        return

    player_to_stats = get_player_to_stats(games)
    display_game(
        games=games,
        player_to_stats=player_to_stats,
        player_to_stats_df=get_player_to_stats_df(games, player_to_stats),
        player_to_game_cobp_df=get_player_to_game_cobp_df(games, player_to_stats),
    )


def _get_games_selection(year: int, team: Team) -> list[Game] | None:
    all_games = _load_season_games(year, team)
    if not all_games:
        return None

    game_ = selectors.get_game_selection(all_games)
    if not game_:
        return None

    return all_games if game_ == ENTIRE_SEASON else [game_]  # type: ignore


def _load_season_games(year: int, team: Team) -> list[Game] | None:
    seasons_event_files = retrosheet.get_seasons_event_files(year)
    try:
        return list(game.load_games_for_team(seasons_event_files, team))
    except ValueError as error:
        display_error(str(error))
        return None


if __name__ == "__main__":
    main()

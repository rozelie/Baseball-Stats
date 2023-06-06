from baseball_obp_and_cobp import game, retrosheet
from baseball_obp_and_cobp.game import Game
from baseball_obp_and_cobp.stats.aggregated import get_player_to_stats
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

    all_games = _load_games(year, team.value)
    if not all_games:
        return

    game_ = selectors.get_game_selection(all_games)
    if not game_:
        return

    if game_ == ENTIRE_SEASON:
        games = all_games
    else:
        games = [game_]  # type: ignore

    display_game(games, get_player_to_stats(games))


def _load_games(year: int, team_id: str) -> list[Game] | None:
    game_events_file = retrosheet.get_teams_years_event_file(year, team_id)
    try:
        return game.load_events_file(game_events_file)
    except ValueError as error:
        display_error(str(error))
        return None


if __name__ == "__main__":
    main()

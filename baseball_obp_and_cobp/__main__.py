from baseball_obp_and_cobp import game, obp, retrosheet, selectors, ui
from baseball_obp_and_cobp.game import Game
from baseball_obp_and_cobp.selectors import ENTIRE_SEASON

EMPTY_CHOICE = ""


def main() -> None:
    """Project entrypoint."""
    ui.set_streamlit_config()
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

    player_to_game_obps = obp.get_player_to_obps(games)
    ui.display_game(games, player_to_game_obps)


def _load_games(year: int, team_id: str) -> list[Game] | None:
    game_events_file = retrosheet.get_teams_years_event_file(year, team_id)
    try:
        return game.load_events_file(game_events_file)
    except ValueError as error:
        ui.display_error(str(error))
        return None


if __name__ == "__main__":
    main()

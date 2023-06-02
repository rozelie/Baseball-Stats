from baseball_obp_and_cobp import game, obp, retrosheet, selectors, ui
from baseball_obp_and_cobp.game import Game

EMPTY_CHOICE = ""


def main() -> None:
    """Project entrypoint."""
    ui.set_streamlit_config()
    team = selectors.get_team_selection()
    year = selectors.get_year_selection()
    if not team or not year:
        return

    games = _load_games(year, team.value)
    if not games:
        return

    game_ = selectors.get_game_selection(games)
    if not game_:
        return

    player_to_game_obps = obp.get_player_to_game_obps(game_)
    ui.display_game(game_, player_to_game_obps)


def _load_games(year: int, team_id: str) -> list[Game] | None:
    game_events_file = retrosheet.get_teams_years_event_file(year, team_id)
    try:
        return game.load_events_file(game_events_file)
    except ValueError as error:
        ui.display_error(str(error))
        return None


if __name__ == "__main__":
    main()

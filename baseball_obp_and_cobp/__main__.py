from baseball_obp_and_cobp import game, obp, retrosheet, ui
from baseball_obp_and_cobp.game import Game
from baseball_obp_and_cobp.team import Team

EMPTY_CHOICE = ""


def main() -> None:
    """Project entrypoint."""
    ui.set_streamlit_config()
    team = _get_team_choice()
    year = _get_year_choice()
    if not team or not year:
        return

    game_events_file = retrosheet.get_teams_years_event_file(year, team.value)
    try:
        games = game.load_events_file(game_events_file)
    except ValueError as error:
        ui.display_error(str(error))
        return

    game_ = _get_game_choice(games)
    if not game_:
        return

    player_to_game_obps = obp.get_player_to_game_obps(game_)
    ui.display_game(game_, player_to_game_obps)


def _get_team_choice() -> Team | str:
    team_pretty_name_to_team = {t.pretty_name: t for t in Team}
    options = [EMPTY_CHOICE, *sorted(team_pretty_name_to_team.keys())]
    selected_team_pretty_name = ui.get_selection("Select Team:", options=options)
    return team_pretty_name_to_team.get(selected_team_pretty_name)


def _get_year_choice() -> int | str:
    options = [EMPTY_CHOICE, *reversed(range(2000, 2023))]
    return ui.get_selection("Select Year:", options=options)


def _load_games(year: int, team_id: str) -> list[Game]:
    game_events_file = retrosheet.get_teams_years_event_file(year, team_id)
    return game.load_events_file(game_events_file)


def _get_game_choice(games) -> Game | str:
    game_id_to_game = {g.id: g for g in games}
    game_pretty_ids = [g.pretty_id for g in games]
    game_pretty_id_to_game_id = {g.pretty_id: g.id for g in games}
    options = [EMPTY_CHOICE, *sorted(game_pretty_ids)]
    game_pretty_id_selected = ui.get_selection("Select Game:", options=options)
    if not game_pretty_id_selected:
        return EMPTY_CHOICE

    game_id_selected = game_pretty_id_to_game_id[game_pretty_id_selected]
    return game_id_to_game[game_id_selected]


if __name__ == "__main__":
    main()

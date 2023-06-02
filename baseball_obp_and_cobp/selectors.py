from baseball_obp_and_cobp import ui
from baseball_obp_and_cobp.game import Game
from baseball_obp_and_cobp.team import Team

EMPTY_CHOICE = ""


def get_team_selection() -> Team | None:
    team_pretty_name_to_team = {t.pretty_name: t for t in Team}
    options = [EMPTY_CHOICE, *sorted(team_pretty_name_to_team.keys())]
    selected_team_pretty_name = ui.get_selection("Select Team:", options=options)
    return team_pretty_name_to_team.get(selected_team_pretty_name)


def get_year_selection() -> int | None:
    options = [EMPTY_CHOICE, *reversed(range(2000, 2023))]
    year = ui.get_selection("Select Year:", options=options)
    return year if year else None


def get_game_selection(games: list[Game]) -> Game | None:
    game_id_to_game = {g.id: g for g in games}
    game_pretty_ids = [g.pretty_id for g in games]
    game_pretty_id_to_game_id = {g.pretty_id: g.id for g in games}
    options = [EMPTY_CHOICE, *sorted(game_pretty_ids)]
    game_pretty_id_selected = ui.get_selection("Select Game:", options=options)
    if not game_pretty_id_selected:
        return None

    game_id_selected = game_pretty_id_to_game_id[game_pretty_id_selected]
    return game_id_to_game[game_id_selected]

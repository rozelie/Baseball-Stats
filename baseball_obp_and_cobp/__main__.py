from baseball_obp_and_cobp import game, obp, paths, ui


def main() -> None:
    """Project entrypoint."""
    ui.set_streamlit_config()
    game_selected = _get_game_choice()
    player_to_game_obps = obp.get_player_to_game_obps(game_selected)
    ui.display_game(game_selected, player_to_game_obps)


def _get_game_choice() -> game.Game:
    cubs_2022_events = paths.DATA_DIR / "2022CHN.EVN"
    cubs_2022_games = game.load_events_file(cubs_2022_events)
    game_id_to_game = {g.id: g for g in cubs_2022_games}
    game_pretty_ids = [g.pretty_id for g in cubs_2022_games]
    game_pretty_id_to_game_id = {g.pretty_id: g.id for g in cubs_2022_games}
    game_pretty_id_selected = ui.get_selection("Select Game:", options=sorted(game_pretty_ids))
    game_id_selected = game_pretty_id_to_game_id[game_pretty_id_selected]
    return game_id_to_game[game_id_selected]


if __name__ == "__main__":
    main()

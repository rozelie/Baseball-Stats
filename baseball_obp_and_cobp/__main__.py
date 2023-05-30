from baseball_obp_and_cobp import game, obp, paths


def main() -> None:
    """Project entrypoint."""
    cubs_2022_events = paths.DATA_DIR / "2022CHN.EVN"
    cubs_2022_games = game.load_events_file(cubs_2022_events)
    game_example = cubs_2022_games[0]
    obp.get_player_to_game_on_base_percentage(game_example, explain=True, is_conditional=True)


if __name__ == "__main__":
    main()

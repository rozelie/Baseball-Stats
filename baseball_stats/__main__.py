from baseball_stats import games, paths, stats


def main() -> None:
    """Project entrypoint."""
    cubs_2022_events = paths.DATA_DIR / "2022CHN.EVN"
    cubs_2022_games = games.load_events_file(cubs_2022_events)
    game_example = cubs_2022_games[1]
    stats.get_player_to_game_on_base_percentage(game_example, explain=True)


if __name__ == "__main__":
    main()

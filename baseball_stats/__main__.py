from baseball_stats import events, paths


def main() -> None:
    """Project entrypoint."""
    cubs_2022_events = paths.DATA_DIR / "2022CHN.EVN"
    cubs_2022_games = events.load_events_file(cubs_2022_events)


if __name__ == "__main__":
    main()

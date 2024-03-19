from typing import Iterator

from pyretrosheet.models.game import Game
from pyretrosheet.models.play import Play
from pyretrosheet.models.player import Player
from pyretrosheet.models.team import TeamLocation
from pyretrosheet.views import get_inning_plays, get_plays

TEAM_PLAYER_ID = "Team"


def build_team_player() -> Player:
    return Player(
        id=TEAM_PLAYER_ID,
        name=TEAM_PLAYER_ID,
        team_location=TeamLocation.HOME,
        batting_order_position=0,
        fielding_position=0,
        is_sub=False,
        raw="",
    )


def get_players_plays(games: list[Game], player: Player) -> Iterator[tuple[Game, list[Play]]]:
    for game in games:
        plays = [p for p in get_plays(game) if p.batter_id == player.id]
        yield game, plays


def does_inning_have_an_on_base(game: Game, inning: int, team_location: TeamLocation) -> bool:
    inning_plays = get_inning_plays(
        game,
        include_visiting_team=team_location == TeamLocation.VISITING,
        include_home_team=team_location == TeamLocation.HOME,
    )
    for play in inning_plays[inning]:
        if play.batter_gets_on_base():
            return True
    return False


def does_inning_have_another_play_get_on_base(game: Game, play: Play, team_location: TeamLocation) -> bool:
    inning_plays = get_inning_plays(
        game,
        include_visiting_team=team_location == TeamLocation.VISITING,
        include_home_team=team_location == TeamLocation.HOME,
    )
    for inning_play in inning_plays[play.inning]:
        if inning_play == play:
            continue

        if inning_play.batter_gets_on_base():
            return True

    return False


def does_play_have_on_base_before_it_in_inning(game: Game, play: Play) -> bool:
    inning_plays = get_inning_plays(
        game,
        include_visiting_team=play.team_location == TeamLocation.VISITING,
        include_home_team=play.team_location == TeamLocation.HOME,
    )
    for inning_play in inning_plays[play.inning]:
        if inning_play == play:
            return False
        if inning_play.batter_gets_on_base():
            return True

    raise ValueError(f"Unable to find play within inning | play={play.raw}")


def is_play_first_of_inning(game: Game, play: Play) -> bool:
    inning_plays = get_inning_plays(
        game,
        include_visiting_team=play.team_location == TeamLocation.VISITING,
        include_home_team=play.team_location == TeamLocation.HOME,
    )
    return inning_plays[play.inning][0] == play  # type: ignore


def prettify_play(play: Play) -> str:
    event = play.event
    desc = event.description
    parts = []
    if desc.batter_event:
        parts.append(desc.batter_event.name)
    if desc.runner_event:
        parts.append(desc.runner_event.name)
    for modifier in event.modifiers:
        parts.append(modifier.type.name)

    parts.append(play.raw)
    return " | ".join(parts)


def dump_team_plays_to_test_fixtures(games: list[Game], team_location: TeamLocation) -> None:
    """
    Usage:
    ```python
        from pyretrosheet.models.team import TeamLocation
        from cobp.utils import dump_team_plays_to_test_fixtures

        dump_team_plays_to_test_fixtures(games, TeamLocation.VISITING)
    ```
    """
    players = []
    plays = []
    for game in games:
        for event in game.chronological_events:
            if isinstance(event, Player):
                player = event
                if player.team_location != team_location:
                    continue

                players.append(
                    f'{player.id} = mock_player_builder(id="{player.id}", name="{player.name}", team_location={player.team_location})' # noqa
                )

            if isinstance(event, Play):
                play = event
                if play.team_location != team_location:
                    continue

                description = play.event.description
                modifiers = ", ".join([f"mock_modifier_builder({m.type})" for m in play.event.modifiers])
                plays.append(
                    f"mock_play_builder(mock_event_builder(batter_event={description.batter_event}, runner_event={description.runner_event}, modifiers=[{modifiers}]), batter_id={play.batter_id}.id, inning={play.inning})," # noqa
                )

    print("\n".join(players))
    print()
    print("mock_game.chronological_events = [")
    print("    \n".join(plays))
    print("]")

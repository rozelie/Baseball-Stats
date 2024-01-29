from typing import Iterator

from pyretrosheet.models.game import Game
from pyretrosheet.models.play import Play
from pyretrosheet.models.play.description import BatterEvent, RunnerEvent
from pyretrosheet.models.play.modifier import ModifierType
from pyretrosheet.models.player import Player
from pyretrosheet.models.team import TeamLocation
from pyretrosheet.views import get_inning_plays, get_players, get_plays

from cobp.models.team import Team

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


def get_game_pretty_id(game: Game) -> str:
    return f"{game.id.date.strftime('%Y/%m/%d')} {game.visiting_team_id} @ {game.home_team_id}"


def get_team_players(games: list[Game], team: Team) -> list[Player]:
    players = []
    seen_player_ids = set()
    for game in games:
        if game.home_team_id == team.retrosheet_id:
            include_home_team = True
            include_visiting_team = False
        elif game.visiting_team_id == team.retrosheet_id:
            include_home_team = False
            include_visiting_team = True
        else:
            raise ValueError(f"Could not find {team.retrosheet_id} in game={game.id.raw}")

        for player in get_players(
            game, include_home_team=include_home_team, include_visiting_team=include_visiting_team
        ):
            if player.id not in seen_player_ids:
                players.append(player)
                seen_player_ids.add(player.id)

    return players


def is_play_unused_in_stats(play: Play) -> bool:
    is_batter_event_unused = play.event.description.batter_event in [
        BatterEvent.NO_PLAY,
        BatterEvent.CATCHER_INTERFERENCE,
        BatterEvent.ERROR_ON_FOUL_FLY_BALL,
    ]
    is_runner_event_unused = play.event.description.runner_event in [
        RunnerEvent.WILD_PITCH,
        RunnerEvent.CAUGHT_STEALING,
        RunnerEvent.STOLEN_BASE,
        RunnerEvent.OTHER_ADVANCE,
        RunnerEvent.PASSED_BALL,
        RunnerEvent.BALK,
        RunnerEvent.PICKED_OFF,
    ]
    return is_batter_event_unused or is_runner_event_unused


def is_play_walk(play: Play) -> bool:
    return play.event.description.batter_event in [
        BatterEvent.WALK,
        BatterEvent.INTENTIONAL_WALK,
    ]


def is_play_hit_by_pitch(play: Play) -> bool:
    return play.event.description.batter_event == BatterEvent.HIT_BY_PITCH


def is_play_sacrifice_fly(play: Play) -> bool:
    return any(modifier == ModifierType.SACRIFICE_FLY for modifier in play.event.modifiers)


def is_play_at_bat(play: Play) -> bool:
    return all(
        [
            not is_play_unused_in_stats(play),
            not is_play_walk(play),
            not is_play_hit_by_pitch(play),
            not is_play_sacrifice_fly(play),
        ]
    )


def is_play_single(play: Play) -> bool:
    return play.event.description.batter_event == BatterEvent.SINGLE


def is_play_double(play: Play) -> bool:
    return play.event.description.batter_event in [BatterEvent.DOUBLE, BatterEvent.GROUND_RULE_DOUBLE]


def is_play_triple(play: Play) -> bool:
    return play.event.description.batter_event == BatterEvent.TRIPLE


def is_play_home_run(play: Play) -> bool:
    return play.event.description.batter_event in [BatterEvent.HOME_RUN_INSIDE_PARK, BatterEvent.HOME_RUN_LEAVING_PARK]


def is_play_hit(play: Play) -> bool:
    return any(
        [
            is_play_single(play),
            is_play_double(play),
            is_play_triple(play),
            is_play_home_run(play),
        ]
    )


def get_players_plays_used_in_stats(games: list[Game], player: Player) -> Iterator[tuple[Game, list[Play]]]:
    for game in games:
        plays = [p for p in get_plays(game) if not is_play_unused_in_stats(p) and p.batter_id == player.id]
        yield game, plays


def is_play_hit_by_pitch(play: Play) -> bool:
    return play.event.description.batter_event == BatterEvent.HIT_BY_PITCH


def does_play_result_in_on_base(play: Play) -> bool:
    return any([is_play_hit(play), is_play_walk(play), is_play_hit_by_pitch(play)])


def does_inning_have_an_on_base(game: Game, inning: int, team_location: TeamLocation) -> bool:
    inning_plays = get_inning_plays(
        game,
        include_visiting_team=team_location == TeamLocation.VISITING,
        include_home_team=team_location == TeamLocation.HOME,
    )
    for play in inning_plays[inning]:
        if does_play_result_in_on_base(play):
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
        if does_play_result_in_on_base(inning_play):
            return True

    raise ValueError(f"Unable to find play within inning | play={play.raw}")


def is_play_first_of_inning(game: Game, play: Play) -> bool:
    inning_plays = get_inning_plays(
        game,
        include_visiting_team=play.team_location == TeamLocation.VISITING,
        include_home_team=play.team_location == TeamLocation.HOME,
    )
    return inning_plays[play.inning][0] == play


#     @property
#     def id(self) -> str:
#         """ID to be used in play-by-play explanations."""
#         if self.is_hit:
#             return "HIT, AB"
#         elif self.is_walk:
#             return "WALK"
#         elif self.is_hit_by_pitch:
#             return "HBP"
#         elif self.is_sacrifice_fly:
#             return "SF"
#         elif self.is_at_bat:
#             return "AB"
#         else:
#             return "N/A"

#     @property
#     def color(self) -> str:
#         """Color to be used in"""
#         if self.is_unused_in_stats:
#             return "red"
#         elif self.results_in_on_base:
#             return "green"
#         else:
#             return "orange"

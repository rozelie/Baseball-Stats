from dataclasses import dataclass
from typing import Callable

from pyretrosheet.models.game import Game
from pyretrosheet.models.play import Play

from cobp.utils import does_inning_have_an_on_base, does_play_have_on_base_before_it_in_inning, is_play_first_of_inning


@dataclass
class Condition:
    is_met: bool
    reason: str | None = None


ConditionFunction = Callable[[Game, Play], Condition]


def is_conditional_play(game: Game, play: Play) -> Condition:
    if not does_inning_have_an_on_base(game, play.inning, play.team_location):
        return Condition(False, "no other on-base in inning")

    return Condition(True)


def is_sequential_play(game: Game, play: Play) -> Condition:
    if not does_play_have_on_base_before_it_in_inning(game, play):
        return Condition(False, "no other on-base prior to play")

    if is_play_first_of_inning(game, play):
        return Condition(False, "player is first batter in inning")

    return Condition(True)


def is_leadoff_play(game: Game, play: Play) -> Condition:
    if not does_inning_have_an_on_base(game, play.inning, play.team_location):
        return Condition(False, "no on-base in inning")

    if not is_play_first_of_inning(game, play):
        return Condition(False, "player is not first batter in inning")

    return Condition(True)

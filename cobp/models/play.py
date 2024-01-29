# from copy import deepcopy
# from dataclasses import dataclass
# from logging import getLogger

# from cobp.models.advance import get_advances_from_play
# from cobp.models.base import BaseToPlayerId
# from cobp.models.delta import PlayDelta, deduce_play_delta
# from cobp.models.out import get_outs_from_play
# from cobp.models.play_modifier import PlayModifier, get_modifiers_from_play
# from cobp.models.play_result import PlayResult

# logger = getLogger(__name__)


# @dataclass
# class Play:
#     """Internal representation of a play."""

#     inning: int
#     batter_id: str
#     play_descriptor: str
#     result: PlayResult
#     base_running_play_result: PlayResult | None
#     modifiers: list[PlayModifier]
#     previous_base_state: BaseToPlayerId
#     delta: PlayDelta

#     @classmethod
#     def from_play_line(cls, line_values: list[str], base_state: dict[str, str | None]) -> "Play":
#         """Load a play from a "play" line, as defined in Retrosheet spec.

#         https://www.retrosheet.org/eventfile.htm ("The event field of the play record" section)
#         """
#         previous_base_state = deepcopy(base_state)
#         inning, _, batter_id, _, _, play_descriptor = line_values
#         result = PlayResult.from_play_descriptor(play_descriptor)
#         base_running_play_result = None
#         if "+" in play_descriptor:
#             base_running_play_result = PlayResult.from_play_descriptor(play_descriptor.split("+")[1])

#         logger.debug(f"Processing play: {line_values} | {result=} | {base_running_play_result=} | {base_state=}")

#         modifiers = get_modifiers_from_play(play_descriptor)
#         outs = get_outs_from_play(play_descriptor, result)
#         advances = get_advances_from_play(play_descriptor, result, modifiers, base_running_play_result, outs)
#         delta = deduce_play_delta(previous_base_state, batter_id, advances, outs)
#         return cls(
#             inning=int(inning),
#             batter_id=batter_id,
#             play_descriptor=play_descriptor,
#             result=result,
#             base_running_play_result=base_running_play_result,
#             modifiers=modifiers,
#             previous_base_state=previous_base_state,
#             delta=delta,
#         )

#     @property
#     def pretty_description(self) -> str:
#         pretty_description = self.result.name
#         if self.modifiers:
#             modifiers = "/".join(modifier.name for modifier in self.modifiers)
#             pretty_description = f"{pretty_description}/{modifiers}"

#         return f"{self.inning}: {pretty_description} ({self.play_descriptor})"

#     @property
#     def is_sacrifice_fly(self) -> bool:
#         return any(modifier == PlayModifier.SACRIFICE_FLY for modifier in self.modifiers)

#     @property
#     def is_hit(self) -> bool:
#         return any(
#             [
#                 self.is_single,
#                 self.is_double,
#                 self.is_triple,
#                 self.is_home_run,
#                 self.result == PlayResult.GROUND_RULE_DOUBLE,
#             ]
#         )

#     @property
#     def is_single(self) -> bool:
#         return self.result == PlayResult.SINGLE

#     @property
#     def is_double(self) -> bool:
#         return self.result in [PlayResult.DOUBLE, PlayResult.GROUND_RULE_DOUBLE]

#     @property
#     def is_triple(self) -> bool:
#         return self.result == PlayResult.TRIPLE

#     @property
#     def is_home_run(self) -> bool:
#         return self.result in [PlayResult.HOME_RUN, PlayResult.HOME_RUN_2]

#     @property
#     def is_walk(self) -> bool:
#         return self.result in [
#             PlayResult.WALK,
#             PlayResult.INTENTIONAL_WALK,
#             PlayResult.INTENTIONAL_WALK_2,
#         ]

#     @property
#     def is_hit_by_pitch(self) -> bool:
#         return self.result is PlayResult.HIT_BY_PITCH

#     @property
#     def is_at_bat(self) -> bool:
#         return all(
#             [
#                 not self.is_unused_in_stats,
#                 not self.is_walk,
#                 not self.is_hit_by_pitch,
#                 not self.is_sacrifice_fly,
#             ]
#         )

#     @property
#     def results_in_on_base(self) -> bool:
#         return any([self.is_hit, self.is_walk, self.is_hit_by_pitch])

#     @property
#     def is_unused_in_stats(self) -> bool:
#         return self.result in [
#             PlayResult.NO_PLAY,
#             PlayResult.WILD_PITCH,
#             PlayResult.CAUGHT_STEALING,
#             PlayResult.CATCHER_INTERFERENCE,
#             PlayResult.STOLEN_BASE,
#             PlayResult.OTHER_ADVANCE,
#             PlayResult.PASSED_BALL,
#             PlayResult.ERROR_ON_FOUL_FLY_BALL,
#             PlayResult.BALK,
#             PlayResult.PICKED_OFF,
#         ]

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

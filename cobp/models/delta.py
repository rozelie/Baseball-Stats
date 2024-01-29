# import logging
# from copy import deepcopy
# from dataclasses import dataclass
# from pprint import pformat
# from typing import Iterator

# from cobp.models.advance import Advance
# from cobp.models.base import Base, BaseToPlayerId
# from cobp.models.out import Out

# logger = logging.getLogger(__name__)


# @dataclass
# class PlayDelta:
#     resulting_base_state: BaseToPlayerId
#     player_ids_scoring_a_run: list[str]
#     batter_rbis: int


# def deduce_play_delta(
#     previous_base_state: BaseToPlayerId, batter_id: str, advances: list[Advance], outs: list[Out]
# ) -> PlayDelta:
#     resulting_base_state = deepcopy(previous_base_state)
#     player_ids_scoring_a_run = []
#     batter_rbis = 0
#     advances = list(_dedupe_advances(advances))
#     ordered_deltas = _order_deltas(advances, outs)
#     logger.debug(f"Deducing play delta: deltas=\n{pformat(ordered_deltas)}...")
#     for delta in ordered_deltas:
#         if isinstance(delta, Out):
#             out = delta
#             # if the runner started at home and becomes out, there is nothing to change in the base state
#             if out.starting_base == Base.BATTER_AT_HOME:
#                 continue
#             del resulting_base_state[out.starting_base.value]

#         elif isinstance(delta, Advance):
#             advance = delta
#             # there are a few instances where an advancement to the same base occurs
#             if advance.starting_base == advance.ending_base:
#                 continue

#             if advance.starting_base == Base.BATTER_AT_HOME:
#                 player_id = batter_id
#             else:
#                 player_id = previous_base_state[advance.starting_base.value]  # type: ignore

#             # home run results in no changes to the base state for the batter
#             if advance.starting_base == Base.BATTER_AT_HOME and advance.ending_base == Base.HOME:
#                 player_ids_scoring_a_run.append(player_id)
#                 # RBIs include the batter himself
#                 if advance.is_rbi_credited:
#                     batter_rbis += 1
#                 continue

#             # determine batters advance
#             if advance.starting_base == Base.BATTER_AT_HOME:
#                 resulting_base_state[advance.ending_base.value] = player_id
#                 continue

#             # non-batter advances to home
#             if advance.ending_base == Base.HOME:
#                 player_ids_scoring_a_run.append(player_id)
#                 if advance.is_rbi_credited:
#                     batter_rbis += 1

#                 del resulting_base_state[advance.starting_base.value]
#                 continue

#             # non-batter advances to somewhere other than home
#             resulting_base_state[advance.ending_base.value] = player_id
#             del resulting_base_state[advance.starting_base.value]

#     play_delta = PlayDelta(
#         resulting_base_state=resulting_base_state,
#         player_ids_scoring_a_run=player_ids_scoring_a_run,
#         batter_rbis=batter_rbis,
#     )
#     logger.debug(f"Deduced play delta: {play_delta=}")
#     return play_delta


# def _order_deltas(advances: list[Advance], outs: list[Out]) -> list[Advance | Out]:
#     # order deltas, but ensuring rare backward advances occur last
#     # there is only one case that I know of:
#     # - MIL201304190: CS2(15).2-1 in the bottom of the 8th
#     # - https://www.businessinsider.com/video-brewers-jean-segura-stole-second-and-then-stole-first-2013-4
#     ordered_deltas: list[Out | Advance] = []
#     for delta in list(reversed(sorted([*advances, *outs], key=lambda x: x.starting_base))):  # type: ignore
#         if isinstance(delta, Advance) and delta.player_advances_backwards:
#             continue
#         ordered_deltas.append(delta)  # type: ignore

#     backward_advances = [a for a in advances if a.player_advances_backwards]
#     if backward_advances:
#         ordered_deltas = [*ordered_deltas, *backward_advances]

#     return ordered_deltas


# def _dedupe_advances(advances: list[Advance]) -> Iterator[Advance]:
#     # There are some cases were advances are duplicated
#     # e.g. K+CS3(24E5).2-3 => caught stealing advance due to error and the explicit advance of 2-3
#     seen_deltas = set()
#     for advance in advances:
#         delta = (advance.starting_base, advance.ending_base)
#         if delta not in seen_deltas:
#             yield advance
#             seen_deltas.add(delta)

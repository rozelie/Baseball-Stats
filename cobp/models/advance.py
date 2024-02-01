# from dataclasses import dataclass

# from cobp.models.base import Base
# from cobp.models.out import Out, is_errored_out_but_advance_still_happens
# from cobp.models.play_modifier import PlayModifier
# from cobp.models.play_result import PlayResult


# @dataclass
# class Advance:
#     """Captures a player advancing bases."""

#     starting_base: Base
#     ending_base: Base
#     is_rbi_credited: bool = True
#     player_advances_backwards: bool = False

#     @property
#     def scores(self) -> bool:
#         return self.ending_base == Base.HOME

#     @classmethod
#     def from_advance(
#         cls,
#         advance_descriptor: str,
#         play_result: PlayResult,
#         modifiers: list[PlayModifier],
#     ) -> "Advance":
#         """
#         Parameters are used to indicate if a run is
#         unearned (UR) and if RBI is to be credited (RBI) or not (NR),
#         (NORBI). When these parameters are not present, normal rules are
#         followed.

#         play,9,0,davie001,30,BBBB,W+PB.3-H(NR);1-3
#             The run scored on the passed ball is not credited as an RBI to the
#             batter.

#         play,8,1,sax-s001,22,BCFBFX,S4/G34.2-H(E4/TH)(UR)(NR);1-3;B-2
#             Three parameters are given on the 2-H advance. The first indicates a
#             second baseman throwing error, the second indicates it is an unearned
#             run and the third indicates no RBI.

#         play,2,1,willk001,11,BFX,E6/G6.3-H(RBI);2-3;B-1
#             In this play an RBI is given to the batter.
#         """
#         should_attribute_rbi_despite_error = True

#         starting_base, ending_base = advance_descriptor.split("-")
#         # parenthesis are used to encode extra info we are not interested in - ignore this data
#         if "(" in ending_base:
#             # the advance may be unearned or have an error
#             # if either, assume no RBI
#             # e.g. 2-H(UR)(E6/TH)
#             if "(UR)" in advance_descriptor and "(E" in advance_descriptor:
#                 should_attribute_rbi_despite_error = False

#             ending_base = ending_base.split("(")[0]

#         # '#' is used to encode extra info we are not interested in - ignore this data
#         if "#" in ending_base:
#             ending_base = ending_base.replace("#", "")

#         no_rbi = "NR" in advance_descriptor

#         is_error = play_result == PlayResult.ERROR
#         if is_error:
#             unearned = "UR" in advance_descriptor
#             is_rbi = "RBI" in advance_descriptor
#             if is_rbi:
#                 should_attribute_rbi_despite_error = True
#             elif unearned:
#                 should_attribute_rbi_despite_error = False

#         return cls(
#             Base(starting_base),
#             Base(ending_base),
#             is_rbi_credited=all(
#                 [
#                     not no_rbi,
#                     PlayModifier.GROUND_BALL_DOUBLE_PLAY not in modifiers,
#                     # e.g. E4/TH/G34+.3-H;2-H(NR);B-2 => RBI for 3-H, not 2-H(NR)
#                     # e.g. E4/G89S.3-H;1-3;B-2        => RBI for 3-H
#                     # e.g. E3/G.2-H(UR);1-2           => no RBI for 2-H(UR)
#                     should_attribute_rbi_despite_error,
#                 ]
#             ),
#             player_advances_backwards=ending_base < starting_base,
#         )

#     @classmethod
#     def from_stolen_base(cls, stolen_base: str) -> "Advance":
#         # ignore unused metadata following certain characters
#         for char in [".", "/", "("]:
#             if char in stolen_base:
#                 stolen_base = stolen_base.split(char)[0]

#         base_stolen = Base(stolen_base.replace("SB", ""))
#         # it seems Retrosheet does not explicitly show what base a runner came from during a steal
#         # so we assume they were on the base prior
#         if base_stolen == Base.HOME:
#             return cls(Base.THIRD_BASE, Base.HOME, is_rbi_credited=False)
#         elif base_stolen == Base.THIRD_BASE:
#             return cls(Base.SECOND_BASE, Base.THIRD_BASE, is_rbi_credited=False)
#         elif base_stolen == Base.SECOND_BASE:
#             return cls(Base.FIRST_BASE, Base.SECOND_BASE, is_rbi_credited=False)
#         else:
#             raise ValueError(f"Unable to load stolen base advance: {stolen_base=}")

#     @classmethod
#     def from_caught_stealing_error(cls, caught_stealing_descriptor: str) -> "Advance":
#         # examples: CS2(1E6), POCS2(13E4/TH)
#         if caught_stealing_descriptor.startswith("CS"):
#             stolen_base = Base(caught_stealing_descriptor[2])
#         elif caught_stealing_descriptor.startswith("POCS"):
#             stolen_base = Base(caught_stealing_descriptor[4])
#         else:
#             raise ValueError(f"Unable to parse caught stealing error as advance: {caught_stealing_descriptor=}")

#         if stolen_base == Base.HOME:
#             return cls(Base.THIRD_BASE, Base.HOME, is_rbi_credited=False)
#         elif stolen_base == Base.THIRD_BASE:
#             return cls(Base.SECOND_BASE, Base.THIRD_BASE, is_rbi_credited=False)
#         elif stolen_base == Base.SECOND_BASE:
#             return cls(Base.FIRST_BASE, Base.SECOND_BASE, is_rbi_credited=False)
#         else:
#             raise ValueError(f"Unable to parse caught stealing error as advance: {caught_stealing_descriptor=}")


# def get_advances_from_play(
#     play_descriptor: str,
#     result: PlayResult,
#     modifiers: list[PlayModifier],
#     base_running_play_result: PlayResult | None,
#     outs: list[Out],
# ) -> list[Advance]:
#     advances: list[Advance] = []
#     _add_non_batter_advances(play_descriptor, result, modifiers, base_running_play_result, advances, outs)
#     _add_batter_advances(result, advances, outs)
#     return advances


# def _add_non_batter_advances(
#     play_descriptor: str,
#     result: PlayResult,
#     modifiers: list[PlayModifier],
#     base_running_play_result: PlayResult | None,
#     advances: list[Advance],
#     outs: list[Out],
# ) -> None:
#     # data after '.' is for advances that are NOT from the batter
#     if "." in play_descriptor:
#         # S9/L9S.2-H;1-3 => runner on 2nd advanced to home, runner on 1st advanced to 3rd
#         advance_or_out_descriptors = play_descriptor.split(".")
#         if len(advance_or_out_descriptors) == 2:
#             advance_or_out_descriptors = advance_or_out_descriptors[1].split(";")
#         elif len(advance_or_out_descriptors) > 2:
#             # handle rare cases like 'FC3/DP/G3S.3XH(32);1X2(8).B-1' where batter advance is explicit
#             advance_or_out_descriptors_nested = [x.split(";") for x in advance_or_out_descriptors[1:]]
#             advance_or_out_descriptors = [y for x in advance_or_out_descriptors_nested for y in x]  # flatten list
#         else:
#             raise ValueError(f"Unable to parse non-batter advances from play descriptor: {play_descriptor=}")

#         advance_descriptors = [descriptor for descriptor in advance_or_out_descriptors if "X" not in descriptor]
#         advances.extend([Advance.from_advance(advance, result, modifiers) for advance in advance_descriptors])
#         _add_advances_from_errored_out(advance_or_out_descriptors, advances)

#     _add_stealing_advances(play_descriptor, result, base_running_play_result, advances, outs)


# def _add_advances_from_errored_out(advance_or_out_descriptors: list[str], advances: list[Advance]) -> None:
#     out_descriptors = [descriptor for descriptor in advance_or_out_descriptors if "X" in descriptor]
#     for out_descriptor in out_descriptors:
#         if is_errored_out_but_advance_still_happens(out_descriptor):
#             out = Out.from_out(out_descriptor)
#             advances.append(
#                 Advance(Base(out.starting_base), Base(out.out_on_base), is_rbi_credited="NR" not in out_descriptor)
#             )


# def _add_stealing_advances(
#     play_descriptor: str,
#     result: PlayResult,
#     base_running_play_result: PlayResult | None,
#     advances: list[Advance],
#     outs: list[Out],
# ) -> None:
#     if base_running_play_result == PlayResult.STOLEN_BASE:
#         base_running_play_descriptor = play_descriptor.split("+")[1]
#         for stolen_base in base_running_play_descriptor.split(";"):
#             _add_stolen_base_advance_if_applicable(stolen_base, advances, outs)
#     elif base_running_play_result == PlayResult.CAUGHT_STEALING:
#         base_running_play_descriptor = play_descriptor.split("+")[1]
#         for caught_stealing in base_running_play_descriptor.split(";"):
#             if "." in caught_stealing:
#                 caught_stealing = caught_stealing.split(".")[0]

#             # Handle cases where the advance is explicit but caught stealing is also encoded
#             # e.g. CS2(2E4).3-H(UR);1-2
#             if not caught_stealing.startswith("CS"):
#                 continue

#             advance = Advance.from_caught_stealing_error(caught_stealing)
#             # handle cases like: K+CS2(2E6).1-1
#             # where we don't want to advance the runner from caught stealing since it's explicit in 1-1
# .           advance already
#             if is_errored_out_but_advance_still_happens(
#                 caught_stealing
#             ) and not _is_advance_already_accounted_for_after_stolen_base(advances, advance):
#                 advances.append(advance)

#     if result == PlayResult.STOLEN_BASE:
#         for stolen_base in play_descriptor.split(";"):
#             _add_stolen_base_advance_if_applicable(stolen_base, advances, outs)

#     # advance a runner caught stealing but advanced due to an error
#     if result in [PlayResult.CAUGHT_STEALING, PlayResult.PICKED_OFF_CAUGHT_STEALING] and "E" in play_descriptor:
#         advance = Advance.from_caught_stealing_error(play_descriptor)
#         if not _is_advance_already_accounted_for_after_stolen_base(advances, advance):
#             advances.append(advance)


# def _add_stolen_base_advance_if_applicable(stolen_base: str, advances: list[Advance], outs: list[Out]) -> None:
#     # handle cases like 'SB2.3-H(PB)(NR)(UR);1-3'
#     if not stolen_base.startswith("SB"):
#         return

#     stolen_base_advance = Advance.from_stolen_base(stolen_base)
#     if not _is_advance_already_accounted_for_after_stolen_base(
#         advances, stolen_base_advance
#     ) and not _is_out_already_accounted_for_after_stolen_base(outs, stolen_base_advance):
#         advances.append(stolen_base_advance)


# def _is_advance_already_accounted_for_after_stolen_base(advances: list[Advance], stolen_base_advance: Advance)
# -> bool:
#     """For a stolen base, there is the possible case of an error happening after the base has been stolen that causes
#     the stealer to advance further.

#      e.g. SB2.1-3(E2/TH) => stole second, ended up advancing from first to third
#      e.g. POCS2(2E3).2-H(NR)(UR);1-3 => stole second, ended up advancing from first to third
#     """
#     return any([advance.starting_base == stolen_base_advance.starting_base for advance in advances])


# def _is_out_already_accounted_for_after_stolen_base(outs: list[Out], stolen_base_advance: Advance) -> bool:
#     """For a stolen base, there is the possible case of a runner trying to steal twice, or something?

#     An example is 'SB2.1X3(25)', which means they stole second base, but were out going from first to second?

#     What?
#     """
#     return any([out.starting_base == stolen_base_advance.starting_base for out in outs])


# def _add_batter_advances(result: PlayResult, advances: list[Advance], outs: list[Out]) -> None:
#     # there are certain cases where the batter's advancement is encoded in non-batter advances
#     # examples:
#     # - batter hits a single, but a wild pitch allows him to advance to second base (S7/G6+.B-2)
#     if any([advance.starting_base == Base.BATTER_AT_HOME for advance in advances]):
#         return

#     # advances from the batter are (typically) not explicitly coded so we deduce them here
#     is_batter_not_fielded_out = PlayResult.FIELDED_OUT and any([out.is_explicit_out for out in outs])
#     if (
#         result
#         in [
#             PlayResult.SINGLE,
#             PlayResult.WALK,
#             PlayResult.INTENTIONAL_WALK,
#             PlayResult.INTENTIONAL_WALK_2,
#             PlayResult.HIT_BY_PITCH,
#             PlayResult.ERROR,
#             PlayResult.ERROR_ASSUME_BATTER_ADVANCES_TO_FIRST,
#             PlayResult.CATCHER_INTERFERENCE,
#             PlayResult.FIELDERS_CHOICE,
#         ]
#         or is_batter_not_fielded_out
#     ):
#         advances.append(Advance(Base.BATTER_AT_HOME, Base.FIRST_BASE))
#     elif result in [PlayResult.DOUBLE, PlayResult.GROUND_RULE_DOUBLE]:
#         advances.append(Advance(Base.BATTER_AT_HOME, Base.SECOND_BASE))
#     elif result == PlayResult.TRIPLE:
#         advances.append(Advance(Base.BATTER_AT_HOME, Base.THIRD_BASE))
#     elif result in [PlayResult.HOME_RUN, PlayResult.HOME_RUN_2]:
#         advances.append(Advance(Base.BATTER_AT_HOME, Base.HOME))

from dataclasses import dataclass

from cobp.models.base import Base
from cobp.models.out import Out, is_errored_out_but_advance_still_happens
from cobp.models.play_result import PlayResult


@dataclass
class Advance:
    """Captures a player advancing bases."""

    starting_base: Base
    ending_base: Base
    is_unearned: bool = False
    is_rbi_credited: bool = True

    @property
    def scores(self) -> bool:
        return self.ending_base == Base.HOME

    @classmethod
    def from_advance(cls, advance_descriptor: str) -> "Advance":
        starting_base, ending_base = advance_descriptor.split("-")
        # parenthesis are used to encode extra info we are not interested in - ignore this data
        if "(" in ending_base:
            ending_base = ending_base.split("(")[0]

        # TODO: figure out what the # represents and if it is needed
        if "#" in ending_base:
            ending_base = ending_base.replace("#", "")

        return cls(
            Base(starting_base),
            Base(ending_base),
            # not including this for the time-being as this seems to discount
            # a lot of actual earned runs and RBIs
            # is_unearned="UR" in advance_descriptor,
            # is_rbi_credited="NR" not in advance_descriptor,
        )

    @classmethod
    def from_stolen_base(cls, stolen_base: str) -> "Advance":
        # ignore unused metadata following a '.'
        if "." in stolen_base:
            stolen_base = stolen_base.split(".")[0]

        base_stolen = Base(stolen_base.replace("SB", ""))
        # it seems Retrosheet does not explicitly show what base a runner came from during a steal
        # so we assume they were on the base prior
        if base_stolen == Base.HOME:
            return cls(Base.THIRD_BASE, Base.HOME)
        elif base_stolen == Base.THIRD_BASE:
            return cls(Base.SECOND_BASE, Base.THIRD_BASE)
        elif base_stolen == Base.SECOND_BASE:
            return cls(Base.FIRST_BASE, Base.SECOND_BASE)
        else:
            raise ValueError(f"Unable to load stolen base advance: {stolen_base=}")

    @classmethod
    def from_caught_stealing_error(cls, caught_stealing_descriptor: str) -> "Advance":
        # examples: CS2(1E6), POCS2(13E4/TH)
        if caught_stealing_descriptor.startswith("CS"):
            stolen_base = Base(caught_stealing_descriptor[2])
        elif caught_stealing_descriptor.startswith("POCS"):
            stolen_base = Base(caught_stealing_descriptor[4])
        else:
            raise ValueError(f"Unable to parse caught stealing error as advance: {caught_stealing_descriptor=}")

        if stolen_base == Base.HOME:
            return cls(Base.THIRD_BASE, Base.HOME, is_unearned=True, is_rbi_credited=False)
        elif stolen_base == Base.THIRD_BASE:
            return cls(Base.SECOND_BASE, Base.THIRD_BASE, is_unearned=True, is_rbi_credited=False)
        elif stolen_base == Base.SECOND_BASE:
            return cls(Base.FIRST_BASE, Base.SECOND_BASE, is_unearned=True, is_rbi_credited=False)
        else:
            raise ValueError(f"Unable to parse caught stealing error as advance: {caught_stealing_descriptor=}")


def get_advances_from_play(
    play_descriptor: str, result: PlayResult, base_running_play_result: PlayResult | None, outs: list[Out]
) -> list[Advance]:
    advances: list[Advance] = []
    _add_non_batter_advances(play_descriptor, result, base_running_play_result, advances, outs)
    _add_batter_advances(result, advances)
    return advances


def _add_non_batter_advances(
    play_descriptor: str,
    result: PlayResult,
    base_running_play_result: PlayResult | None,
    advances: list[Advance],
    outs: list[Out],
) -> None:
    # data after '.' is for advances that are NOT from the batter
    if "." in play_descriptor:
        # S9/L9S.2-H;1-3 => runner on 2nd advanced to home, runner on 1st advanced to 3rd
        advance_or_out_descriptors = play_descriptor.split(".")[1].split(";")
        advance_descriptors = [descriptor for descriptor in advance_or_out_descriptors if "X" not in descriptor]
        advances.extend([Advance.from_advance(advance) for advance in advance_descriptors])
        _add_advances_from_errored_out(advance_or_out_descriptors, advances)

    _add_stealing_advances(play_descriptor, result, base_running_play_result, advances, outs)


def _add_advances_from_errored_out(advance_or_out_descriptors: list[str], advances: list[Advance]) -> None:
    out_descriptors = [descriptor for descriptor in advance_or_out_descriptors if "X" in descriptor]
    for out_descriptor in out_descriptors:
        if is_errored_out_but_advance_still_happens(out_descriptor):
            out = Out.from_out(out_descriptor)
            advances.append(Advance(Base(out.starting_base), Base(out.out_on_base)))


def _add_stealing_advances(
    play_descriptor: str,
    result: PlayResult,
    base_running_play_result: PlayResult | None,
    advances: list[Advance],
    outs: list[Out],
) -> None:
    if base_running_play_result == PlayResult.STOLEN_BASE:
        base_running_play_descriptor = play_descriptor.split("+")[1]
        for stolen_base in base_running_play_descriptor.split(";"):
            _add_stolen_base_advance_if_applicable(stolen_base, advances, outs)

    if result == PlayResult.STOLEN_BASE:
        for stolen_base in play_descriptor.split(";"):
            _add_stolen_base_advance_if_applicable(stolen_base, advances, outs)

    # advance a runner caught stealing but advanced due to an error
    if result in [PlayResult.CAUGHT_STEALING, PlayResult.PICKED_OFF_CAUGHT_STEALING] and "E" in play_descriptor:
        advance = Advance.from_caught_stealing_error(play_descriptor)
        if not _is_advance_already_accounted_for_after_stolen_base(advances, advance):
            advances.append(advance)


def _add_stolen_base_advance_if_applicable(stolen_base: str, advances: list[Advance], outs: list[Out]) -> None:
    # handle cases like 'SB2.3-H(PB)(NR)(UR);1-3'
    if not stolen_base.startswith("SB"):
        return

    stolen_base_advance = Advance.from_stolen_base(stolen_base)
    if not _is_advance_already_accounted_for_after_stolen_base(
        advances, stolen_base_advance
    ) and not _is_out_already_accounted_for_after_stolen_base(outs, stolen_base_advance):
        advances.append(stolen_base_advance)


def _is_advance_already_accounted_for_after_stolen_base(advances: list[Advance], stolen_base_advance: Advance) -> bool:
    """For a stolen base, there is the possible case of an error happening after the base has been stolen that causes
    the stealer to advance further.

     e.g. SB2.1-3(E2/TH) => stole second, ended up advancing from first to third
     e.g. POCS2(2E3).2-H(NR)(UR);1-3 => stole second, ended up advancing from first to third
    """
    return any([advance.starting_base == stolen_base_advance.starting_base for advance in advances])


def _is_out_already_accounted_for_after_stolen_base(outs: list[Out], stolen_base_advance: Advance) -> bool:
    """For a stolen base, there is the possible case of a runner trying to steal twice, or something?

    An example is 'SB2.1X3(25)', which means they stole second base, but were out going from first to second?

    What?
    """
    return any([out.starting_base == stolen_base_advance.starting_base for out in outs])


def _add_batter_advances(result: PlayResult, advances: list[Advance]) -> None:
    # there are certain cases where the batter's advancement is encoded in non-batter advances
    # examples:
    # - batter hits a single, but a wild pitch allows him to advance to second base (S7/G6+.B-2)
    if any([advance.starting_base == Base.BATTER_AT_HOME for advance in advances]):
        return

    # advances from the batter are (typically) not explicitly coded so we deduce them here
    if result in [
        PlayResult.SINGLE,
        PlayResult.WALK,
        PlayResult.INTENTIONAL_WALK,
        PlayResult.INTENTIONAL_WALK_2,
        PlayResult.HIT_BY_PITCH,
        PlayResult.ERROR,
        PlayResult.ERROR_ASSUME_BATTER_ADVANCES_TO_FIRST,
    ]:
        advances.append(Advance(Base.BATTER_AT_HOME, Base.FIRST_BASE))
    elif result in [PlayResult.DOUBLE, PlayResult.GROUND_RULE_DOUBLE]:
        advances.append(Advance(Base.BATTER_AT_HOME, Base.SECOND_BASE))
    elif result == PlayResult.TRIPLE:
        advances.append(Advance(Base.BATTER_AT_HOME, Base.THIRD_BASE))
    elif result in [PlayResult.HOME_RUN, PlayResult.HOME_RUN_2]:
        advances.append(Advance(Base.BATTER_AT_HOME, Base.HOME))

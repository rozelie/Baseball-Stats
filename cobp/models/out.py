from dataclasses import dataclass

from cobp.models.base import Base
from cobp.models.play_result import PlayResult


@dataclass
class Out:
    """Captures a player becoming out for the inning."""

    starting_base: Base
    out_on_base: Base

    @classmethod
    def from_out(cls, out_descriptor: str) -> "Out":
        # 2X3 implies player from second base was put out going to third base
        start_base, out_on_base = out_descriptor.split("X")

        # parenthesis are used to encode extra info we are not interested in - ignore this data
        if "(" in out_on_base:
            out_on_base = out_on_base.split("(")[0]

        return cls(Base(start_base), Base(out_on_base))

    @classmethod
    def from_caught_stealing(cls, caught_stealing_descriptor: str) -> "Out":
        # examples: CS2, POCS3
        if caught_stealing_descriptor.startswith("CS"):
            caught_stealing_base = Base(caught_stealing_descriptor[2])
        elif caught_stealing_descriptor.startswith("POCS"):
            caught_stealing_base = Base(caught_stealing_descriptor[4])
        else:
            raise ValueError(f"Unable to parse caught stealing as out: {caught_stealing_descriptor=}")

        if caught_stealing_base == Base.HOME:
            return Out(Base.THIRD_BASE, Base.HOME)
        elif caught_stealing_base == Base.THIRD_BASE:
            return Out(Base.SECOND_BASE, Base.THIRD_BASE)
        elif caught_stealing_base == Base.SECOND_BASE:
            return Out(Base.FIRST_BASE, Base.SECOND_BASE)
        else:
            raise ValueError(f"Unable to parse caught stealing as out: {caught_stealing_descriptor=}")


def get_outs_from_play(play_descriptor: str, result: PlayResult) -> list[Out]:
    # data after '.' is for outs that are NOT from the batter
    outs = []
    if "." in play_descriptor:
        advance_or_out_descriptors = play_descriptor.split(".")[1].split(";")
        out_descriptors = [descriptor for descriptor in advance_or_out_descriptors if "X" in descriptor]
        for out in out_descriptors:
            if is_errored_out_but_advance_still_happens(out):
                continue
            outs.append(Out.from_out(out))

    if result in [PlayResult.CAUGHT_STEALING, PlayResult.PICKED_OFF_CAUGHT_STEALING]:
        if "E" not in play_descriptor:
            outs.append(Out.from_caught_stealing(play_descriptor))

    return outs


def is_errored_out_but_advance_still_happens(out_descriptor: str) -> bool:
    # Retrosheet has this ridiculous case where rarely it will encode an out that didn't actually
    # happen due to an error
    return "(" in out_descriptor and "E" in out_descriptor

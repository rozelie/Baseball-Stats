from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from logging import getLogger

logger = getLogger(__name__)

BaseToPlayerId = dict[str, str | None]


class Base(Enum):
    BATTER_AT_HOME = "B"
    FIRST_BASE = "1"
    SECOND_BASE = "2"
    THIRD_BASE = "3"
    HOME = "H"


@dataclass
class Advance:
    """Captures a player advancing bases."""

    starting_base: Base
    ending_base: Base

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

        return cls(Base(starting_base), Base(ending_base))


def get_resulting_base_state(
    previous_base_state: BaseToPlayerId, batter_id: str, advances: list[Advance], outs: list[str]
) -> BaseToPlayerId:
    resulting_base_state = deepcopy(previous_base_state)
    logger.debug(f"Calculating resulting base state: {advances=} | {outs=} | {previous_base_state=}")
    for advance in advances:
        if advance.starting_base == Base.BATTER_AT_HOME:
            resulting_base_state[advance.ending_base.value] = batter_id
            continue

        resulting_base_state[advance.ending_base.value] = previous_base_state[advance.starting_base.value]
        if advance.starting_base.value in resulting_base_state:
            del resulting_base_state[advance.starting_base.value]

    for out in outs:
        del resulting_base_state[out]

    logger.debug(f"Resulting base state: {resulting_base_state}")
    return resulting_base_state

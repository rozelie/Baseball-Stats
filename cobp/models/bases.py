from enum import Enum

BaseToPlayerId = dict[str, str | None]


class Base(Enum):
    BATTER_AT_HOME = "B"
    FIRST_BASE = "1"
    SECOND_BASE = "2"
    THIRD_BASE = "3"
    HOME = "H"

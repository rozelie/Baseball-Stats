from enum import Enum


class PlayResult(Enum):
    """Play results, as defined in Retrosheet spec.

    https://www.retrosheet.org/eventfile.htm ("The event field of the play record" section)
    """

    SINGLE = "S"
    DOUBLE = "D"
    TRIPLE = "T"
    HOME_RUN = "H"
    HOME_RUN_2 = "HR"
    WALK = "W"
    INTENTIONAL_WALK = "I"
    INTENTIONAL_WALK_2 = "IW"
    CATCHER_INTERFERENCE = "C"
    GROUND_RULE_DOUBLE = "DGR"
    HIT_BY_PITCH = "HP"
    STRIKEOUT = "K"
    FIELDERS_CHOICE = "FC"
    ERROR = "E"
    ERROR_ON_FOUL_FLY_BALL = "FLE"
    NO_PLAY = "NP"
    CAUGHT_STEALING = "CS"
    STOLEN_BASE = "SB"
    WILD_PITCH = "WP"
    BALK = "BK"
    PASSED_BALL = "PB"
    PICKED_OFF = "PO"
    PICKED_OFF_CAUGHT_STEALING = "POCS"
    DEFENSIVE_INDIFFERENCE = "DI"
    OTHER_ADVANCE = "OA"
    # mapped internally, not part of Retrosheet data spec
    FIELDED_OUT = "OUT"

    @classmethod
    def from_play_descriptor(cls, play_descriptor: str) -> "PlayResult":
        play_main_descriptor = play_descriptor.split("/")[0]
        # we are not concerned with metadata following certain characters
        for char in [".", "+", "(", ";"]:
            play_main_descriptor = play_main_descriptor.split(char)[0]

        alpha_play_main_descriptor = ""
        for char in play_main_descriptor:
            if char.isalpha():
                alpha_play_main_descriptor = f"{alpha_play_main_descriptor}{char}"
            else:
                break

        # some play descriptions include 'H' (home base), which we trim for the mapping
        if alpha_play_main_descriptor.endswith("H"):
            alpha_play_main_descriptor = alpha_play_main_descriptor.replace("H", "")

        if not alpha_play_main_descriptor:
            # descriptor is a number, which specifies a fielder causing the out
            return cls.FIELDED_OUT

        for result in cls:
            if result.value == alpha_play_main_descriptor:
                return result

        raise ValueError(f"Unable to load PlayResult from: {play_main_descriptor=}")

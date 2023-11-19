from enum import Enum


class PlayModifier(Enum):
    """Play modifiers, as defined in Retrosheet spec.

    Grants additional metadata for play results. A play can have multiple modifiers.
    https://www.retrosheet.org/eventfile.htm ("The event field of the play record" section)
    """

    APPEAL_PLAY = "AP"
    POP_UP_BUNT = "BP"
    GROUND_BALL_BUNT = "BG"
    BUNT_GROUNDED_INTO_DOUBLE_PLAY = "BGDP"
    BATTER_INTERFERENCE = "BINT"
    LINE_DRIVE_BUNT = "BL"
    BATTING_OUT_OF_TURN = "BOOT"
    BUNT_POP_UP = "BP"
    BUNT_POPPED_INTO_DOUBLE_PLAY = "BPDP"
    RUNNER_HIT_BY_BATTED_BALL = "BR"
    CALLED_THIRD_STRIKE = "C"
    COURTESY_BATTER = "COUB"
    COURTESY_FIELDER = "COUF"
    COURTESY_RUNNER = "COUR"
    UNSPECIFIED_DOUBLE_PLAY = "DP"
    ERROR_ON_FIELDER = "E"
    FLY = "F"
    FLY_BALL_DOUBLE_PLAY = "FDP"
    FAN_INTERFERENCE = "FINT"
    FOUL = "FL"
    FORCE_OUT = "FO"
    GROUND_BALL = "G"
    GROUND_BALL_DOUBLE_PLAY = "GDP"
    GROUND_BALL_TRIPLE_PLAY = "GTP"
    INFIELD_FLY_RULE = "IF"
    INTERFERENCE = "INT"
    INSIDE_THE_PARK_HOME_RUN = "IPHR"
    LINE_DRIVE = "L"
    LINED_INTO_DOUBLE_PLAY = "LDP"
    LINED_INTO_TRIPLE_PLAY = "LTP"
    MANAGER_CHALLENGE_OF_CALL_ON_THE_FIELD = "MREV"
    NO_DOUBLE_PLAY_CREDITED_FOR_THIS_PLAY = "NDP"
    OBSTRUCTION = "OBS"
    POP_FLY = "P"
    A_RUNNER_PASSED_ANOTHER_RUNNER_AND_WAS_CALLED_OUT = "PASS"
    RELAY_THROW_FROM_THE_INITIAL_FIELDER_TO_FIELDER_WITH_NO_OUT_MADE = "R"
    RUNNER_INTERFERENCE = "RINT"
    SACRIFICE_FLY = "SF"
    SACRIFICE_HIT_BUNT = "SH"
    THROW = "TH"
    UNSPECIFIED_TRIPLE_PLAY = "TP"
    UMPIRE_INTERFERENCE = "UINT"
    UMPIRE_REVIEW_OF_CALL_ON_THE_FIELD = "UREV"
    FIELDER_VALUES = "FIELDER_VALUES"
    UNKNOWN = ""

    @classmethod
    def from_play_modifier(cls, play_modifier: str) -> "PlayModifier":
        alpha_play_modifier = ""
        # trim non-alphabetic characters - we are not concerned with other metadata
        for char in play_modifier:
            if char.isalpha():
                alpha_play_modifier = f"{alpha_play_modifier}{char}"
            else:
                break

        for result in cls:
            if result.value == alpha_play_modifier:
                return result

        if all(char.isnumeric() for char in play_modifier):
            return cls.FIELDER_VALUES

        return cls.UNKNOWN


def get_modifiers_from_play(play_descriptor: str) -> list[PlayModifier]:
    if "/" in play_descriptor:
        return [PlayModifier.from_play_modifier(modifier) for modifier in play_descriptor.split("/")[1:]]
    return []

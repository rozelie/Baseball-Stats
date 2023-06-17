from dataclasses import dataclass
from enum import Enum


class PlayResult(Enum):
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


class PlayResultModifier(Enum):
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
    def from_play_modifier(cls, play_modifier: str) -> "PlayResultModifier":
        alpha_play_modifier = ""
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


@dataclass
class Play:
    inning: int
    batter_id: str
    play_descriptor: str
    result: PlayResult
    modifiers: list[PlayResultModifier]

    @classmethod
    def from_play_line(cls, line_values: list[str]) -> "Play":
        inning, _, batter_id, _, _, play_descriptor = line_values
        result = PlayResult.from_play_descriptor(play_descriptor)

        modifiers = []
        if "/" in play_descriptor:
            modifiers = [PlayResultModifier.from_play_modifier(modifier) for modifier in play_descriptor.split("/")[1:]]

        return cls(
            inning=int(inning),
            batter_id=batter_id,
            play_descriptor=play_descriptor,
            result=result,
            modifiers=modifiers,
        )

    @property
    def pretty_description(self) -> str:
        pretty_description = self.result.name
        if self.modifiers:
            modifiers = "/".join(modifier.name for modifier in self.modifiers)
            pretty_description = f"{pretty_description}/{modifiers}"

        return f"{self.inning}: {pretty_description} ({self.play_descriptor})"

    @property
    def is_sacrifice_fly(self) -> bool:
        return any(modifier == PlayResultModifier.SACRIFICE_FLY for modifier in self.modifiers)

    @property
    def is_hit(self) -> bool:
        return any(
            [
                self.is_single,
                self.is_double,
                self.is_triple,
                self.is_home_run,
                self.result == PlayResult.GROUND_RULE_DOUBLE,
            ]
        )

    @property
    def is_single(self) -> bool:
        return self.result == PlayResult.SINGLE

    @property
    def is_double(self) -> bool:
        return self.result == PlayResult.DOUBLE

    @property
    def is_triple(self) -> bool:
        return self.result == PlayResult.TRIPLE

    @property
    def is_home_run(self) -> bool:
        return self.result in [PlayResult.HOME_RUN, PlayResult.HOME_RUN_2]

    @property
    def is_walk(self) -> bool:
        return self.result in [
            PlayResult.WALK,
            PlayResult.INTENTIONAL_WALK,
            PlayResult.INTENTIONAL_WALK_2,
        ]

    @property
    def is_hit_by_pitch(self) -> bool:
        return self.result is PlayResult.HIT_BY_PITCH

    @property
    def results_in_on_base(self) -> bool:
        return any([self.is_hit, self.is_walk, self.is_hit_by_pitch])

    @property
    def is_unused_in_stats(self) -> bool:
        return self.result in [
            PlayResult.NO_PLAY,
            PlayResult.WILD_PITCH,
            PlayResult.CAUGHT_STEALING,
            PlayResult.CATCHER_INTERFERENCE,
            PlayResult.STOLEN_BASE,
        ]

    @property
    def is_at_bat(self) -> bool:
        return all(
            [
                not self.is_unused_in_stats,
                not self.is_walk,
                not self.is_hit_by_pitch,
                not self.is_sacrifice_fly,
            ]
        )

    @property
    def id(self) -> str:
        if self.is_hit:
            return "HIT, AB"
        elif self.is_walk:
            return "WALK"
        elif self.is_hit_by_pitch:
            return "HBP"
        elif self.is_sacrifice_fly:
            return "SF"
        elif self.is_at_bat:
            return "AB"
        else:
            return "N/A"

    @property
    def color(self) -> str:
        if self.is_unused_in_stats:
            return "red"
        elif self.results_in_on_base:
            return "green"
        else:
            return "orange"

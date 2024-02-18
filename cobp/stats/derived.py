from dataclasses import dataclass, field

from cobp.stats.obp import OBP
from cobp.stats.sp import SP
from cobp.stats.stat import Stat


@dataclass
class OPS(Stat):
    obp: OBP = field(default_factory=OBP)
    sp: SP = field(default_factory=SP)

    def __post_init__(self):
        self.explanation = [f"OBP={round(self.obp.value, 2)} + SP={round(self.sp.value, 2)} == {round(self.value, 2)}"]

    @property
    def value(self) -> float:
        return self.obp.value + self.sp.value


@dataclass
class COPS(Stat):
    cobp: OBP = field(default_factory=OBP)
    sp: SP = field(default_factory=SP)

    def __post_init__(self):
        self.explanation = [
            f"COBP={round(self.cobp.value, 2)} + SP={round(self.sp.value, 2)} == {round(self.value, 2)}"
        ]

    @property
    def value(self) -> float:
        return self.cobp.value + self.sp.value


@dataclass
class LOOPS(Stat):
    loop: OBP = field(default_factory=OBP)
    ops: OPS = field(default_factory=OPS)

    def __post_init__(self):
        self.explanation = [
            f"LOOP={round(self.loop.value, 2)} + OPS={round(self.ops.value, 2)} == {round(self.value, 2)}"
        ]

    @property
    def value(self) -> float:
        return self.loop.value + self.ops.value


@dataclass
class SOPS(Stat):
    sobp: OBP = field(default_factory=OBP)
    ops: OPS = field(default_factory=OPS)

    def __post_init__(self):
        self.explanation = [
            f"SOBP={round(self.sobp.value, 2)} + OPS={round(self.ops.value, 2)} == {round(self.value, 2)}"
        ]

    @property
    def value(self) -> float:
        return self.sobp.value + self.ops.value

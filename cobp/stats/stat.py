from dataclasses import dataclass, field

from pyretrosheet.models.play import Play


@dataclass
class Stat:
    explanation: list[str] = field(default_factory=list)

    def add_play(
        self,
        play: Play,
        resultant: str | None = None,
        color: str | None = None,
    ) -> None:
        resultant = resultant if resultant else "???"
        color = color if color else "white"
        value = f"{play.raw} => :{color}[{resultant}]"
        self.explanation.append(value)

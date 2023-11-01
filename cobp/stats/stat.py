from dataclasses import dataclass, field

from cobp.models.play import Play


@dataclass
class Stat:
    explanation: list[str] = field(default_factory=list)

    def add_play(
        self,
        play: Play,
        resultant: str | None = None,
        color: str | None = None,
    ) -> None:
        resultant = resultant if resultant else play.id
        color = color if color else play.color
        value = f"{play.pretty_description} => :{color}[{resultant}]"
        self.explanation.append(value)

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
        if not resultant:
            if play.is_hit():
                resultant = "H"
            elif play.is_walk():
                resultant = "W"
            elif play.is_hit_by_pitch():
                resultant = "HBP"
            elif play.is_sacrifice_fly():
                resultant = "SF"
            elif play.is_an_at_bat():
                resultant = "AB"
            else:
                resultant = "N/A"

        if not color:
            if play.is_hit():
                color = "green"
            elif play.is_an_at_bat():
                color = "orange"
            elif any([play.is_hit_by_pitch(), play.is_sacrifice_fly(), play.is_walk()]):
                color = "white"
            else:
                color = "red"

        value = f"{play.raw} => :{color}[{resultant}]"
        self.explanation.append(value)

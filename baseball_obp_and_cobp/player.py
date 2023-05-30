from dataclasses import dataclass, field

from baseball_obp_and_cobp.play import Play


@dataclass
class Player:
    id: str
    name: str
    lineup_position: int
    plays: list[Play] = field(default_factory=list)

    @classmethod
    def from_start_line(cls, line_values: list[str]) -> "Player":
        return cls(
            id=line_values[0],
            name=line_values[1].replace('"', ""),
            lineup_position=int(line_values[3]),
        )

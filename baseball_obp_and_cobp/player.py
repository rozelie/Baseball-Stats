from dataclasses import dataclass, field

from baseball_obp_and_cobp.plays import Play


@dataclass
class Player:
    id: str
    name: str
    lineup_position: int
    plays: list[Play] = field(default_factory=list)

    @classmethod
    def from_start_line(cls, line: str) -> "Player":
        split_line = line.split(",")
        return cls(
            id=split_line[1],
            name=split_line[2].replace('"', ""),
            lineup_position=int(split_line[4]),
        )

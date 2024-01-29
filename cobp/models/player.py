# from dataclasses import dataclass, field

# from cobp.models.play import Play

# TEAM_PLAYER_ID = "Team"


# @dataclass
# class Player:
#     id: str
#     name: str
#     lineup_position: int
#     plays: list[Play] = field(default_factory=list)

#     @classmethod
#     def from_start_line(cls, line_values: list[str]) -> "Player":
#         """Load from 'start' line (starting lineup), as defined in Retrosheet spec.

#         https://www.retrosheet.org/eventfile.htm
#         """
#         return cls(
#             id=line_values[0],
#             name=line_values[1].replace('"', ""),
#             lineup_position=int(line_values[3]),
#         )

#     @classmethod
#     def as_team(cls):
#         return cls(
#             id=TEAM_PLAYER_ID,
#             name=TEAM_PLAYER_ID,
#             lineup_position=-1,
#         )

from dataclasses import dataclass


@dataclass
class Substitution:
    player_id: str
    team: int
    replacing_player_of_batting_order: int
    position: int

    @classmethod
    def from_sub_descriptor(cls, sub_values: list[str]) -> "Substitution":
        """
        start and sub There are 18 (for the pre-DH era) or 20 (with the DH) start records, which
        identify the starting lineups for the game. Each start or sub record has five fields.
        The sub records are used when a player is replaced during a game. The roster files that accompany
        the event files include throwing and batting handedness information.

        1. The first field is the Retrosheet player id, which is unique for each player.
        2. The second field is the player's name.
        3. The next field is either 0 (for visiting team), or 1 (for home team). In some games, typically
           due to scheduling conflicts, the home team (the team whose stadium the game is played in) bats first
           (in the top of the innings) and the visiting team bats second (in the bottom of the innings).
           In these games, contrary to "normal" games, start records for the home team ("1") precede start records for
           the visiting team ("0"). Similarly, the play codes pertaining to the home team ("1") precede the play codes
           pertaining to the visiting team ("0").
        4. The next field is the position in the batting order, 1 - 9. When a game is played using the DH rule the
           pitcher is given the batting order position 0.
        5. The last field is the fielding position. The numbers are in the standard notation, with designated hitters
           being identified as position 10. On sub records 11 indicates a pinch hitter and 12 is used for a pinch
           runner. When a player pinch hits or pinch runs for the DH, that player automatically becomes the DH, so
           no 'sub' record is included to identify the new DH.
        """
        player_id, _, team, replacing_player_of_batting_order, position = sub_values
        return cls(
            player_id=player_id,
            team=int(team),
            replacing_player_of_batting_order=int(replacing_player_of_batting_order),
            position=int(position),
        )

    @property
    def is_pinch_hitter(self) -> bool:
        return self.position == 11

    @property
    def is_pinch_runner(self) -> bool:
        return self.position == 12

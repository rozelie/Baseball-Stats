"""Calculate OBP and COBP stats from game data."""
from dataclasses import dataclass, field

from baseball_obp_and_cobp.game import Game
from baseball_obp_and_cobp.play import Play
from baseball_obp_and_cobp.player import Player


@dataclass
class OBPCounters:
    hits: int = 0
    walks: int = 0
    hit_by_pitches: int = 0
    at_bats: int = 0
    sacrifice_flys: int = 0

    @property
    def numerator(self) -> int:
        return self.hits + self.walks + self.hit_by_pitches

    @property
    def denominator(self) -> int:
        return self.at_bats + self.walks + self.hit_by_pitches + self.sacrifice_flys

    @property
    def obp(self) -> float:
        try:
            return self.numerator / self.denominator
        except ZeroDivisionError:
            return 0.0


@dataclass
class OBPs:
    obp: float
    cobp: float


@dataclass
class Explanation:
    player: Player
    obp_explanation: list[str] = field(default_factory=list)
    cobp_explanation: list[str] = field(default_factory=list)

    def add_play(
        self,
        play: Play,
        resultant: str | None = None,
        to_obp: bool = True,
        to_cobp: bool = True,
        color: str | None = None,
    ) -> None:
        resultant = resultant if resultant else play.obp_id
        color = color if color else play.color
        value = f"{play.pretty_description} => :{color}[{resultant}]"
        if to_obp:
            self.obp_explanation.append(value)
        if to_cobp:
            self.cobp_explanation.append(value)

    def add_arithmetic(self, counters: OBPCounters, to_obp: bool = False, to_cobp: bool = False) -> None:
        numerator = f"*H={counters.hits} + W={counters.walks} + HBP={counters.hit_by_pitches} == {counters.numerator}*"
        denominator = f"*AB={counters.at_bats} + W={counters.walks} + HBP={counters.hit_by_pitches} + SF={counters.sacrifice_flys} == {counters.denominator}*"  # noqa: E501
        if to_obp:
            self.obp_explanation.extend([numerator, denominator])
        if to_cobp:
            self.cobp_explanation.extend([numerator, denominator])


GameOBPs = tuple[OBPs, Explanation]
PlayerToGameOBP = dict[str, GameOBPs]


def get_player_to_game_obps(game: Game) -> PlayerToGameOBP:
    return {player.id: _get_players_on_base_percentage(game, player) for player in game.players}


def _get_players_on_base_percentage(game: Game, player: Player) -> GameOBPs:
    explanation = Explanation(player)
    obp_counters = OBPCounters()
    cobp_counters = OBPCounters()
    for play in player.plays:
        if play.is_unused_in_obp_calculations:
            explanation.add_play(play, resultant="N/A")
            continue

        valid_cobp_play = True
        if not game.inning_has_an_on_base(play.inning):
            explanation.add_play(play, resultant="N/A (no other on-base in inning)", to_obp=False, color="red")
            valid_cobp_play = False

        result = play.result
        if result.is_at_bat:
            obp_counters.at_bats += 1
            if valid_cobp_play:
                cobp_counters.at_bats += 1

        if result.is_hit:
            obp_counters.hits += 1
            if valid_cobp_play:
                cobp_counters.hits += 1
            explanation.add_play(play, to_cobp=valid_cobp_play)

        elif result.is_walk:
            obp_counters.walks += 1
            if valid_cobp_play:
                cobp_counters.walks += 1
            explanation.add_play(play, to_cobp=valid_cobp_play)
        elif result.is_hit_by_pitch:
            obp_counters.hit_by_pitches += 1
            if valid_cobp_play:
                cobp_counters.hit_by_pitches += 1
            explanation.add_play(play, to_cobp=valid_cobp_play)
        elif play.is_sacrifice_fly:
            obp_counters.sacrifice_flys += 1
            if valid_cobp_play:
                cobp_counters.sacrifice_flys += 1
            explanation.add_play(play, to_cobp=valid_cobp_play)
        elif result.is_at_bat:
            explanation.add_play(play, to_cobp=valid_cobp_play)
        else:
            explanation.add_play(play, to_cobp=False)
            explanation.add_play(play, to_obp=False, to_cobp=valid_cobp_play)

    explanation.add_arithmetic(obp_counters, to_obp=True)
    explanation.add_arithmetic(cobp_counters, to_cobp=True)
    return OBPs(obp=obp_counters.obp, cobp=cobp_counters.obp), explanation

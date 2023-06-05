"""Calculate OBP and COBP stats from game data."""
from dataclasses import dataclass, field

from baseball_obp_and_cobp.game import Game, get_players_in_games
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


def get_player_to_obps(games: list[Game]) -> PlayerToGameOBP:
    players = get_players_in_games(games)
    return {player.id: _get_players_on_base_percentage(games, player) for player in players}


def _get_players_on_base_percentage(games: list[Game], player: Player) -> GameOBPs:
    explanation = Explanation(player)
    obp_counters = OBPCounters()
    cobp_counters = OBPCounters()
    for game in games:
        try:
            game_player = [p for p in game.players if p.id == player.id][0]
        except IndexError:
            continue

        for play in game_player.plays:
            if play.is_unused_in_obp_calculations:
                continue

            valid_cobp_play = game.inning_has_an_on_base(play.inning)
            if not valid_cobp_play:
                explanation.add_play(play, resultant="N/A (no other on-base in inning)", to_obp=False, color="red")

            if any([play.is_hit, play.is_walk, play.is_hit_by_pitch, play.is_sacrifice_fly, play.is_at_bat]):
                explanation.add_play(play, to_cobp=valid_cobp_play)
            else:
                explanation.add_play(play, to_cobp=False)
                explanation.add_play(play, to_obp=False, to_cobp=valid_cobp_play)

            if play.is_at_bat:
                _increment_counters("at_bats", obp_counters, cobp_counters, valid_cobp_play)

            if play.is_hit:
                _increment_counters("hits", obp_counters, cobp_counters, valid_cobp_play)
            elif play.is_walk:
                _increment_counters("walks", obp_counters, cobp_counters, valid_cobp_play)
            elif play.is_hit_by_pitch:
                _increment_counters("hit_by_pitches", obp_counters, cobp_counters, valid_cobp_play)
            elif play.is_sacrifice_fly:
                _increment_counters("sacrifice_flys", obp_counters, cobp_counters, valid_cobp_play)

    explanation.add_arithmetic(obp_counters, to_obp=True)
    explanation.add_arithmetic(cobp_counters, to_cobp=True)
    return OBPs(obp=obp_counters.obp, cobp=cobp_counters.obp), explanation


def _increment_counters(
    counter: str, obp_counters: OBPCounters, cobp_counters: OBPCounters, valid_cobp_play: bool
) -> None:
    obp_counters.__dict__[counter] += 1
    if valid_cobp_play:
        cobp_counters.__dict__[counter] += 1

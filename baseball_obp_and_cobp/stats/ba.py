"""Calculate BA stats from game data."""
from dataclasses import dataclass, field

from baseball_obp_and_cobp.game import Game, get_players_in_games
from baseball_obp_and_cobp.play import Play
from baseball_obp_and_cobp.player import Player


@dataclass
class BACounters:
    hits: int = 0
    at_bats: int = 0

    @property
    def ba(self) -> float:
        try:
            return self.hits / self.at_bats
        except ZeroDivisionError:
            return 0.0


@dataclass
class Explanation:
    player: Player
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

    def add_arithmetic(self, counters: BACounters) -> None:
        self.explanation.append(f"*H={counters.hits} / AB={counters.at_bats} == {round(counters.ba, 3)}*")


BA = tuple[float, Explanation]
PlayerToBA = dict[str, BA]


def get_player_to_ba(games: list[Game]) -> PlayerToBA:
    players = get_players_in_games(games)
    return {player.id: _get_players_batting_average(games, player) for player in players}


def _get_players_batting_average(games: list[Game], player: Player) -> BA:
    explanation = Explanation(player)
    counters = BACounters()
    for game in games:
        try:
            game_player = [p for p in game.players if p.id == player.id][0]
        except IndexError:
            continue

        for play in game_player.plays:
            if not play.is_hit and not play.is_at_bat:
                explanation.add_play(play, resultant="N/A", color="red")
                continue

            if play.is_hit:
                counters.hits += 1
            if play.is_at_bat:
                counters.at_bats += 1
            explanation.add_play(play)

    explanation.add_arithmetic(counters)
    return counters.ba, explanation

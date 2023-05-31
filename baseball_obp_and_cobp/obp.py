"""Calculate OBP and COBP stats from game data."""
from dataclasses import dataclass, field
from typing import Iterator, Mapping

import streamlit as st

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

    def add_play(self, play_description_prefix: str, resultant: str, to_obp: bool = True, to_cobp: bool = True) -> None:
        value = f"{play_description_prefix} => {resultant}"
        if to_obp:
            self.obp_explanation.append(value)
        if to_cobp:
            self.cobp_explanation.append(value)

    def add_arithmetic(self, counters: OBPCounters, to_obp: bool = False, to_cobp: bool = False) -> None:
        numerator = f"H={counters.hits} + W={counters.walks} + HBP={counters.hit_by_pitches} == {counters.numerator}"
        denominator = f"AB={counters.at_bats} + W={counters.walks} + HBP={counters.hit_by_pitches} + SF={counters.sacrifice_flys} == {counters.denominator}"  # noqa: E501
        if to_obp:
            self.obp_explanation.extend([numerator, denominator])
        if to_cobp:
            self.cobp_explanation.extend([numerator, denominator])


GameOBPs = tuple[OBPs, Explanation]
PlayerToGameOBP = dict[str, GameOBPs]


def get_player_to_game_obps(game: Game) -> PlayerToGameOBP:
    player_to_game_obps = {
        player.id: _get_players_on_base_percentage(player, game.inning_to_plays) for player in game.players
    }
    _display_player_obps(player_to_game_obps=player_to_game_obps, game=game)
    return player_to_game_obps


def _get_players_on_base_percentage(player: Player, inning_to_plays: Mapping[int, list[Play]]) -> GameOBPs:
    explanation = Explanation(player)
    obp_counters = OBPCounters()
    cobp_counters = OBPCounters()
    for play in player.plays:
        valid_cobp_play = True
        play_description_prefix = _get_play_description_prefix(play)
        result = play.result
        other_plays_on_base_in_inning = list(_get_other_plays_on_base_in_inning(play, inning_to_plays[play.inning]))
        if not other_plays_on_base_in_inning:
            explanation.add_play(play_description_prefix, "N/A (no other on-base in inning)", to_obp=False)
            valid_cobp_play = False

        if result.is_at_bat:
            obp_counters.at_bats += 1
            if valid_cobp_play:
                cobp_counters.at_bats += 1

        if result.is_hit:
            obp_counters.hits += 1
            if valid_cobp_play:
                cobp_counters.hits += 1
            explanation.add_play(play_description_prefix, "HIT, AB", to_cobp=valid_cobp_play)

        elif result.is_walk:
            obp_counters.walks += 1
            if valid_cobp_play:
                cobp_counters.walks += 1
            explanation.add_play(play_description_prefix, "WALK", to_cobp=valid_cobp_play)
        elif result.is_hit_by_pitch:
            obp_counters.hit_by_pitches += 1
            if valid_cobp_play:
                cobp_counters.hit_by_pitches += 1
            explanation.add_play(play_description_prefix, "HBP", to_cobp=valid_cobp_play)
        elif any(modifier.is_sacrifice_fly for modifier in play.modifiers):
            obp_counters.sacrifice_flys += 1
            if valid_cobp_play:
                cobp_counters.sacrifice_flys += 1
            explanation.add_play(play_description_prefix, "SF, AB", to_cobp=valid_cobp_play)
        elif result.is_at_bat:
            explanation.add_play(play_description_prefix, "AB", to_cobp=valid_cobp_play)
        else:
            explanation.add_play(play_description_prefix, "Unused for OBP", to_cobp=False)
            explanation.add_play(play_description_prefix, "Unused for COBP", to_obp=False, to_cobp=valid_cobp_play)

    explanation.add_arithmetic(obp_counters, to_obp=True)
    explanation.add_arithmetic(cobp_counters, to_cobp=True)
    return OBPs(obp=obp_counters.obp, cobp=cobp_counters.obp), explanation


def _get_play_description_prefix(play: Play) -> str:
    """Build a descriptive play prefix."""
    play_description_prefix = f"- {play.result.name}"
    if play.modifiers:
        modifiers = "/".join(modifier.name for modifier in play.modifiers)
        play_description_prefix = f"{play_description_prefix}/{modifiers}"

    return f"{play_description_prefix} ({play.play_descriptor})"


def _get_other_plays_on_base_in_inning(play: Play, innings_plays: list[Play]) -> Iterator[Play]:
    for inning_play in innings_plays:
        result = inning_play.result
        if any([result.is_hit, result.is_walk, result.is_hit_by_pitch]) and play != inning_play:
            yield inning_play


def _display_player_obps(player_to_game_obps: PlayerToGameOBP, game: Game) -> None:
    for player_id, (obps, explanation) in player_to_game_obps.items():
        player_column, obp_column, cobp_column = st.columns(3)
        with player_column:
            player = game.get_player(player_id)
            st.text(player.name)
        with obp_column:
            st.text(f"OBP = {round(obps.obp, 3)}")
            for line in explanation.obp_explanation:
                st.text(line)
        with cobp_column:
            st.text(f"COBP = {round(obps.cobp, 3)}")
            for line in explanation.cobp_explanation:
                st.text(line)
        st.divider()

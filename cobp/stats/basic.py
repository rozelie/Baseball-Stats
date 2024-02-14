from dataclasses import dataclass

from pyretrosheet.models.game import Game
from pyretrosheet.models.player import Player

from cobp.utils import TEAM_PLAYER_ID, get_players_plays


@dataclass
class BasicStats:
    games: int = 0
    at_bats: int = 0
    hits: int = 0
    walks: int = 0
    hit_by_pitches: int = 0
    sacrifice_flys: int = 0
    singles: int = 0
    doubles: int = 0
    triples: int = 0
    home_runs: int = 0


PlayerToBasicStats = dict[str, BasicStats]


def get_player_to_basic_stats(games: list[Game], players: list[Player]) -> PlayerToBasicStats:
    player_to_basic_stats = {player.id: _get_players_basic_stats(games, player) for player in players}
    player_to_basic_stats[TEAM_PLAYER_ID] = _get_teams_basic_stats(player_to_basic_stats)
    player_to_basic_stats[TEAM_PLAYER_ID].games = len(games)
    return player_to_basic_stats


def _get_players_basic_stats(games: list[Game], player: Player) -> BasicStats:
    basic_stats = BasicStats()
    for _, plays in get_players_plays(games, player):
        if not plays:
            continue

        basic_stats.games += 1
        for play in plays:
            if play.is_an_at_bat():
                basic_stats.at_bats += 1
            if play.is_hit():
                basic_stats.hits += 1
            if play.is_walk():
                basic_stats.walks += 1
            if play.is_hit_by_pitch():
                basic_stats.hit_by_pitches += 1
            if play.is_sacrifice_fly():
                basic_stats.sacrifice_flys += 1
            if play.is_single():
                basic_stats.singles += 1
            if play.is_double():
                basic_stats.doubles += 1
            if play.is_triple():
                basic_stats.triples += 1
            if play.is_home_run():
                basic_stats.home_runs += 1

    return basic_stats


def _get_teams_basic_stats(player_to_basic_stats: PlayerToBasicStats) -> BasicStats:
    team_basic_stats = BasicStats()
    for basic_stat in player_to_basic_stats.values():
        team_basic_stats.at_bats += basic_stat.at_bats
        team_basic_stats.hits += basic_stat.hits
        team_basic_stats.walks += basic_stat.walks
        team_basic_stats.hit_by_pitches += basic_stat.hit_by_pitches
        team_basic_stats.sacrifice_flys += basic_stat.sacrifice_flys
        team_basic_stats.singles += basic_stat.singles
        team_basic_stats.doubles += basic_stat.doubles
        team_basic_stats.triples += basic_stat.triples
        team_basic_stats.home_runs += basic_stat.home_runs

    return team_basic_stats

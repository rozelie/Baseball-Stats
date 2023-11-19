from dataclasses import dataclass

from cobp.models.game import Game, get_players_in_games
from cobp.models.player import TEAM_PLAYER_ID, Player


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
    runs: int = 0
    runs_batted_in: int = 0


PlayerToBasicStats = dict[str, BasicStats]


def get_player_to_basic_stats(games: list[Game]) -> PlayerToBasicStats:
    players = get_players_in_games(games)
    player_to_basic_stats = {player.id: _get_players_basic_stats(games, player) for player in players}
    for game in games:
        _add_player_runs_from_game(game, player_to_basic_stats)

    player_to_basic_stats[TEAM_PLAYER_ID] = _get_teams_basic_stats(player_to_basic_stats)
    player_to_basic_stats[TEAM_PLAYER_ID].games = len(games)
    return player_to_basic_stats


def _get_players_basic_stats(games: list[Game], player: Player) -> BasicStats:
    basic_stats = BasicStats()
    for game in games:
        if not (game_player := game.get_player(player.id)):
            continue

        basic_stats.games += 1
        for play in game_player.plays:
            if play.is_at_bat:
                basic_stats.at_bats += 1
            if play.is_hit:
                basic_stats.hits += 1
            if play.is_walk:
                basic_stats.walks += 1
            if play.is_hit_by_pitch:
                basic_stats.hit_by_pitches += 1
            if play.is_sacrifice_fly:
                basic_stats.sacrifice_flys += 1
            if play.is_single:
                basic_stats.singles += 1
            if play.is_double:
                basic_stats.doubles += 1
            if play.is_triple:
                basic_stats.triples += 1
            if play.is_home_run:
                basic_stats.home_runs += 1

            basic_stats.runs_batted_in += play.delta.batter_rbis

    return basic_stats


def _add_player_runs_from_game(game: Game, player_to_basic_stats: PlayerToBasicStats) -> None:
    for inning_plays in game.inning_to_plays.values():
        for play in inning_plays:
            for player_id in play.delta.player_ids_scoring_a_run:
                player_to_basic_stats[player_id].runs += 1


def _get_teams_basic_stats(player_to_basic_stats: PlayerToBasicStats) -> BasicStats:
    team_basic_stats = BasicStats()
    for basic_stat in player_to_basic_stats.values():
        team_basic_stats.at_bats += basic_stat.at_bats
        team_basic_stats.hits += basic_stat.hit_by_pitches
        team_basic_stats.walks += basic_stat.walks
        team_basic_stats.hit_by_pitches += basic_stat.hit_by_pitches
        team_basic_stats.sacrifice_flys += basic_stat.sacrifice_flys
        team_basic_stats.singles += basic_stat.singles
        team_basic_stats.doubles += basic_stat.doubles
        team_basic_stats.triples += basic_stat.triples
        team_basic_stats.home_runs += basic_stat.home_runs
        team_basic_stats.runs_batted_in += basic_stat.runs_batted_in
        team_basic_stats.runs += basic_stat.runs

    return team_basic_stats

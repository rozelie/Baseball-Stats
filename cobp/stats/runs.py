from dataclasses import dataclass

from pyretrosheet.models.player import Player

from cobp.data import baseball_reference
from cobp.models.team import Team
from cobp.stats.basic import PlayerToBasicStats
from cobp.utils import TEAM_PLAYER_ID


@dataclass
class Runs:
    runs: int = 0
    rbis: int = 0


PlayerToRuns = dict[str, Runs]


def get_player_to_runs(
    year: int, team: Team, players: list[Player], player_to_basic_stats: PlayerToBasicStats
) -> PlayerToRuns:
    player_to_runs = {
        player.id: _get_player_runs(year, team, player, player_to_basic_stats[player.id].at_bats) for player in players
    }
    player_to_runs[TEAM_PLAYER_ID] = _get_team_runs_and_rbis(player_to_runs)
    return player_to_runs


def _get_player_runs(year: int, team: Team, player: Player, at_bats: int) -> Runs:
    # players without any bats will not appear in the Baseball Reference data
    if at_bats == 0:
        return Runs(runs=0, rbis=0)

    # rare case where the player will appear in the baseball reference data due to having more than one
    # at bat for the season, but they had all of their hits for a single team and no hits for another team
    # so they are not reported to have any hitting stats for that team
    no_team_at_bats = [
        ("Mat Latos", "ANA", 2015),
        ("Jay Buente", "TBA", 2011),
        ("Cha Seung Baek", "SEA", 2008),
        ("Todd Wellemeyer", "KCA", 2007),
        ("Cory Lidle", "NYA", 2006),
        ("Felix Heredia", "NYA", 2003),
        ("Jason Bere", "CLE", 2000),
        ("Steve Woodard", "CLE", 2000),
    ]
    if (player.name, team.retrosheet_id, year) in no_team_at_bats:
        return Runs(runs=0, rbis=0)

    bb_ref_stats = baseball_reference.get_seasonal_players_stats(year)
    bb_ref_player = baseball_reference.lookup_player(bb_ref_stats, player, team)
    return Runs(
        runs=bb_ref_player["runs"].values[0],  # type: ignore
        rbis=bb_ref_player["rbis"].values[0],  # type: ignore
    )


def _get_team_runs_and_rbis(player_to_runs: PlayerToRuns) -> Runs:
    runs = 0
    rbis = 0
    for player_runs in player_to_runs.values():
        runs += player_runs.runs
        rbis += player_runs.rbis

    return Runs(runs=runs, rbis=rbis)

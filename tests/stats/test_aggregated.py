import pytest
from pyretrosheet.models.play.description import BatterEvent

from cobp.stats import aggregated
from cobp.stats.ba import BA
from cobp.stats.basic import BasicStats
from cobp.stats.obp import OBP
from cobp.stats.runs import Runs
from cobp.stats.sp import SP

MODULE_PATH = "cobp.stats.aggregated"


@pytest.fixture
def get_player_to_runs(mocker):
    return mocker.patch(f"{MODULE_PATH}.get_player_to_runs")


class TestPlayerStats:
    def test_derivative_stats(self):
        player_stats = aggregated.PlayerStats(
            obp=OBP(hits=2, at_bats=2),  # 1.0
            cobp=OBP(hits=1, at_bats=2),  # 0.5
            sobp=OBP(hits=1, at_bats=2),  # 0.5
            loop=OBP(hits=0, at_bats=2),  # 0.0
            sp=SP(singles=1, at_bats=2),  # 0.5
            ba=BA(),
            basic=BasicStats(),
            runs=Runs(),
        )

        assert player_stats.ops == 1.5
        assert player_stats.cops == 1.0
        assert player_stats.loops == 1.5
        assert player_stats.sops == 2.0


def test_aggregated_stats_scenario(
    mock_game, mock_team, mock_player, mock_player_2, mock_batter_event_play_builder, get_player_to_runs
):
    """Can be used for regression testing - was initially given a specific scenario to test against (this test)
    which allowed for finding some errors in stat calculations.

    At the time of writing, this resolved two issues:
    1. LOOP was including 1-2-3 innings, which it shouldn't have (similar logic to COBP)
    2. SOBP was skipping plays where there we not other on-bases in the prior inning (which I'm unsure why it was ever added)
    """
    mock_game.chronological_events.extend(
        [
            mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player, 1),
            mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 2),
            mock_batter_event_play_builder(BatterEvent.WALK, mock_player, 3),
            mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 4),
            mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player, 5),
            mock_batter_event_play_builder(BatterEvent.HOME_RUN_INSIDE_PARK, mock_player_2, 5),
            mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 6),
            mock_batter_event_play_builder(BatterEvent.TRIPLE, mock_player_2, 7),
            mock_batter_event_play_builder(BatterEvent.DOUBLE, mock_player, 7),
            mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 8),
            mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player_2, 9),
            mock_batter_event_play_builder(BatterEvent.UNASSISTED_FIELDED_OUT, mock_player, 9),
        ]
    )
    games = [mock_game]
    team = mock_team
    year = 2022

    player_to_stats = aggregated.get_player_to_stats(games, team, year)
    player_stats = player_to_stats[mock_player.id]

    assert player_stats.ba.value == 0.5
    assert player_stats.obp.value == 0.6
    assert player_stats.cobp.value == 0.75
    assert player_stats.loop.value == 1.0
    assert player_stats.sobp.value == 0.5

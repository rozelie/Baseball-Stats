from pyretrosheet.models.play.description import BatterEvent, RunnerEvent

from cobp.stats import ba
from cobp.utils import TEAM_PLAYER_ID


class TestBA:
    def test_ba__happy_path(self):
        ba_ = ba.BA()
        ba_.hits = 1
        ba_.at_bats = 2

        # H / AB == 1 / 2
        assert ba_.value == 0.5

    def test_ba__handles_zero_denominator(self):
        ba_ = ba.BA()
        ba_.at_bats = 0

        assert ba_.value == 0.0


def test_get_player_to_ba(
    mock_game, mock_player, mock_player_2, mock_batter_event_play_builder, mock_runner_event_play_builder
):
    mock_game.chronological_events = [
        mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player, 1),
        mock_runner_event_play_builder(RunnerEvent.CAUGHT_STEALING, mock_player_2, 1),
        mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player, 2),
        mock_batter_event_play_builder(BatterEvent.WALK, mock_player_2, 2),
    ]
    games = [mock_game]
    players = [mock_player, mock_player_2]

    player_to_ba = ba.get_player_to_ba(games, players)

    assert len(player_to_ba) == 3
    assert player_to_ba[mock_player.id].value == 0.5
    assert player_to_ba[mock_player_2.id].value == 0.0
    assert player_to_ba[TEAM_PLAYER_ID].value == 0.5


def test__get_ba_handles_player_not_in_game(mock_game, mock_player):
    mock_game.players = []
    games = [mock_game]

    ba_ = ba._get_ba(games, mock_player)

    assert ba_.hits == 0
    assert ba_.at_bats == 0

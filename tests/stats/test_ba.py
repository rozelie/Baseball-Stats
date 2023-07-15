from cobp.play import PlayResult
from cobp.player import TEAM_PLAYER_ID
from cobp.stats import ba


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


def test_get_player_to_ba(mock_game, mock_player, mock_player_2, mock_play_builder):
    mock_player.plays = [
        mock_play_builder(result=PlayResult.SINGLE, batter_id=mock_player.id, inning=1),
        mock_play_builder(result=PlayResult.STRIKEOUT, batter_id=mock_player.id, inning=2),
    ]
    mock_player_2.plays = [
        mock_play_builder(result=PlayResult.CAUGHT_STEALING, batter_id=mock_player_2.id, inning=1),
        mock_play_builder(result=PlayResult.WALK, batter_id=mock_player_2.id, inning=2),
    ]
    mock_game.players = [mock_player, mock_player_2]
    games = [mock_game]

    player_to_ba = ba.get_player_to_ba(games)

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

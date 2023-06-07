from baseball_obp_and_cobp.play import Play, PlayResult
from baseball_obp_and_cobp.player import TEAM_PLAYER_ID
from baseball_obp_and_cobp.stats import ba


class TestBA:
    def test_ba__happy_path(self):
        ba_ = ba.BA()
        ba_.hits = 1
        ba_.at_bats = 2

        assert ba_.ba == 0.5

    def test_ba__handles_zero_denominator(self):
        ba_ = ba.BA()
        ba_.at_bats = 0

        assert ba_.ba == 0.0


def test_get_player_to_ba(mock_game, mock_player, mock_player_2):
    mock_player.plays = [
        Play(inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.SINGLE, modifiers=[]),
        Play(inning=2, batter_id=mock_player.id, play_descriptor="", result=PlayResult.STRIKEOUT, modifiers=[]),
    ]
    mock_player_2.plays = [
        Play(inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.CAUGHT_STEALING, modifiers=[]),
        Play(inning=2, batter_id=mock_player.id, play_descriptor="", result=PlayResult.WALK, modifiers=[]),
    ]
    mock_game.players = [mock_player, mock_player_2]
    games = [mock_game]

    player_to_ba = ba.get_player_to_ba(games)

    assert len(player_to_ba) == 3
    assert player_to_ba[mock_player.id].ba == 0.5
    assert player_to_ba[mock_player_2.id].ba == 0.0
    assert player_to_ba[TEAM_PLAYER_ID].ba == 0.5


def test__get_ba_handles_player_not_in_game(mock_game, mock_player):
    mock_game.players = []
    games = [mock_game]

    ba_ = ba._get_ba(games, mock_player)

    assert ba_.hits == 0
    assert ba_.at_bats == 0

from cobp.models.play_result import PlayResult
from cobp.models.player import TEAM_PLAYER_ID
from cobp.stats import sp


class TestSP:
    def test_sp__happy_path(self):
        sp_ = sp.SP()
        sp_.singles = 1
        sp_.doubles = 1
        sp_.triples = 1
        sp_.home_runs = 1
        sp_.at_bats = 5

        # numerator (1 * 1 + 2 * 1 + 3 * 1 + 4 * 1) == 10
        # denominator (5) == 5
        assert sp_.value == 2.0

    def test_sp__handles_zero_denominator(self):
        sp_ = sp.SP()
        sp_.at_bats = 0

        assert sp_.value == 0.0


def test_get_player_to_sp(mock_game, mock_player, mock_player_2, mock_play_builder):
    mock_player.plays = [
        mock_play_builder(result=PlayResult.SINGLE, batter_id=mock_player.id, inning=1),
        mock_play_builder(result=PlayResult.DOUBLE, batter_id=mock_player.id, inning=2),
        mock_play_builder(result=PlayResult.TRIPLE, batter_id=mock_player.id, inning=3),
        mock_play_builder(result=PlayResult.HOME_RUN, batter_id=mock_player.id, inning=4),
        mock_play_builder(result=PlayResult.STRIKEOUT, batter_id=mock_player.id, inning=5),
    ]
    mock_player_2.plays = [
        mock_play_builder(result=PlayResult.STRIKEOUT, batter_id=mock_player.id, inning=1),
    ]
    mock_game.players = [mock_player, mock_player_2]
    games = [mock_game]

    player_to_sp = sp.get_player_to_sp(games)

    assert len(player_to_sp) == 3
    assert player_to_sp[mock_player.id].value == 2.0
    assert player_to_sp[mock_player_2.id].value == 0.0
    assert round(player_to_sp[TEAM_PLAYER_ID].value, 1) == 1.7


def test__get_sp_handles_player_not_in_game(mock_game, mock_player):
    mock_game.players = []
    games = [mock_game]

    sp_ = sp._get_sp(games, mock_player)

    assert sp_.numerator == 0
    assert sp_.denominator == 0

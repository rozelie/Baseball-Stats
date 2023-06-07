from baseball_obp_and_cobp.play import Play, PlayResult
from baseball_obp_and_cobp.player import TEAM_PLAYER_ID
from baseball_obp_and_cobp.stats import sp


class TestSP:
    def test_sp__happy_path(self):
        sp_ = sp.SP()
        sp_.singles = 1
        sp_.doubles = 1
        sp_.triples = 1
        sp_.home_runs = 1
        sp_.at_bats = 5

        assert sp_.sp == 2.0

    def test_sp__handles_zero_denominator(self):
        sp_ = sp.SP()
        sp_.at_bats = 0

        assert sp_.sp == 0.0


def test_get_player_to_sp(mock_game, mock_player, mock_player_2):
    mock_player.plays = [
        Play(inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.SINGLE, modifiers=[]),
        Play(inning=2, batter_id=mock_player.id, play_descriptor="", result=PlayResult.DOUBLE, modifiers=[]),
        Play(inning=3, batter_id=mock_player.id, play_descriptor="", result=PlayResult.TRIPLE, modifiers=[]),
        Play(inning=4, batter_id=mock_player.id, play_descriptor="", result=PlayResult.HOME_RUN, modifiers=[]),
        Play(inning=5, batter_id=mock_player.id, play_descriptor="", result=PlayResult.STRIKEOUT, modifiers=[]),
    ]
    mock_player_2.plays = [
        Play(inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.STRIKEOUT, modifiers=[]),
    ]
    mock_game.players = [mock_player, mock_player_2]
    games = [mock_game]

    player_to_sp = sp.get_player_to_sp(games)

    assert len(player_to_sp) == 3
    assert player_to_sp[mock_player.id].sp == 2.0
    assert player_to_sp[mock_player_2.id].sp == 0.0
    assert round(player_to_sp[TEAM_PLAYER_ID].sp, 1) == 1.7


def test__get_sp_handles_player_not_in_game(mock_game, mock_player):
    mock_game.players = []
    games = [mock_game]

    sp_ = sp._get_sp(games, mock_player)

    assert sp_.numerator == 0
    assert sp_.denominator == 0

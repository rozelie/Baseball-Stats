from cobp.play import Play, PlayResult, PlayResultModifier
from cobp.player import TEAM_PLAYER_ID
from cobp.stats import obp


class TestOBP:
    def test_obp__happy_path(self):
        obp_ = obp.OBP()
        obp_.hits = 1
        obp_.walks = 1
        obp_.hit_by_pitches = 1
        obp_.at_bats = 1
        obp_.sacrifice_flys = 1

        # numerator (1 + 1 + 1) == 3
        # denominator (1 + 1 + 1 + 1) == 4
        assert obp_.obp == 0.75

    def test_obp__handles_zero_denominator(self):
        obp_ = obp.OBP()
        obp_.at_bats = 0
        obp_.walks = 0
        obp_.hit_by_pitches = 0
        obp_.sacrifice_flys = 0

        assert obp_.obp == 0.0


def test_get_player_to_obp(mock_game, mock_player, mock_player_2):
    mock_player.plays = [
        Play(inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.SINGLE, modifiers=[]),
        Play(inning=2, batter_id=mock_player.id, play_descriptor="", result=PlayResult.WALK, modifiers=[]),
        Play(inning=3, batter_id=mock_player.id, play_descriptor="", result=PlayResult.HIT_BY_PITCH, modifiers=[]),
        Play(
            inning=4,
            batter_id=mock_player.id,
            play_descriptor="",
            result=PlayResult.FIELDED_OUT,
            modifiers=[PlayResultModifier.SACRIFICE_FLY],
        ),
    ]
    mock_player_2.plays = [
        Play(inning=1, batter_id=mock_player_2.id, play_descriptor="", result=PlayResult.STRIKEOUT, modifiers=[]),
        Play(inning=1, batter_id=mock_player_2.id, play_descriptor="", result=PlayResult.NO_PLAY, modifiers=[]),
    ]
    mock_game.players = [mock_player, mock_player_2]
    games = [mock_game]

    player_to_obp = obp.get_player_to_obp(games)

    assert len(player_to_obp) == 3
    assert player_to_obp[mock_player.id].obp == 0.75
    assert player_to_obp[mock_player_2.id].obp == 0.0
    assert player_to_obp[TEAM_PLAYER_ID].obp == 0.6


def test_get_player_to_cobp__inning_has_on_base(mock_game, mock_player, mock_player_2):
    play_1 = Play(inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.SINGLE, modifiers=[])
    play_2 = Play(inning=1, batter_id=mock_player_2.id, play_descriptor="", result=PlayResult.STRIKEOUT, modifiers=[])
    mock_player.plays = [play_1]
    mock_player_2.plays = [play_2]
    mock_game.players = [mock_player, mock_player_2]
    mock_game.inning_to_plays[1] = [play_1, play_2]
    games = [mock_game]

    player_to_cobp = obp.get_player_to_cobp(games)

    assert len(player_to_cobp) == 3
    assert player_to_cobp[mock_player.id].obp == 1
    assert player_to_cobp[mock_player_2.id].obp == 0.0
    assert player_to_cobp[TEAM_PLAYER_ID].obp == 0.5


def test_get_player_to_cobp__inning_has_no_on_base_skips_plays(mock_game, mock_player, mock_player_2):
    play_1 = Play(inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.STRIKEOUT, modifiers=[])
    play_2 = Play(inning=1, batter_id=mock_player_2.id, play_descriptor="", result=PlayResult.STRIKEOUT, modifiers=[])
    mock_player.plays = [play_1]
    mock_player_2.plays = [play_2]
    mock_game.players = [mock_player, mock_player_2]
    mock_game.inning_to_plays[1] = [play_1, play_2]
    games = [mock_game]

    player_to_cobp = obp.get_player_to_cobp(games)

    assert player_to_cobp[mock_player.id].obp == 0.0
    assert player_to_cobp[mock_player.id].at_bats == 0
    assert player_to_cobp[mock_player_2.id].obp == 0.0
    assert player_to_cobp[mock_player_2.id].at_bats == 0
    assert player_to_cobp[TEAM_PLAYER_ID].obp == 0.0


def test_get_player_to_sobp__play_has_on_base_before_it_in_inning(mock_game, mock_player, mock_player_2):
    play_1 = Play(inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.SINGLE, modifiers=[])
    play_2 = Play(inning=1, batter_id=mock_player_2.id, play_descriptor="", result=PlayResult.SINGLE, modifiers=[])
    mock_player.plays = [play_1]
    mock_player_2.plays = [play_2]
    mock_game.players = [mock_player, mock_player_2]
    mock_game.inning_to_plays[1] = [play_1, play_2]
    games = [mock_game]

    player_to_sobp = obp.get_player_to_sobp(games)

    assert len(player_to_sobp) == 3
    assert player_to_sobp[mock_player.id].obp == 0.0
    assert player_to_sobp[mock_player.id].at_bats == 0
    assert player_to_sobp[mock_player_2.id].obp == 1.0
    assert player_to_sobp[TEAM_PLAYER_ID].obp == 1.0


def test_get_player_to_sobp__play_has_no_on_base_before_it_in_inning_skips_play(mock_game, mock_player, mock_player_2):
    play_1 = Play(inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.STRIKEOUT, modifiers=[])
    play_2 = Play(inning=1, batter_id=mock_player_2.id, play_descriptor="", result=PlayResult.SINGLE, modifiers=[])
    mock_player.plays = [play_1]
    mock_player_2.plays = [play_2]
    mock_game.players = [mock_player, mock_player_2]
    mock_game.inning_to_plays[1] = [play_1, play_2]
    games = [mock_game]

    player_to_sobp = obp.get_player_to_sobp(games)

    assert player_to_sobp[mock_player.id].obp == 0.0
    assert player_to_sobp[mock_player.id].at_bats == 0
    assert player_to_sobp[mock_player_2.id].obp == 0.0
    assert player_to_sobp[mock_player_2.id].at_bats == 0
    assert player_to_sobp[TEAM_PLAYER_ID].obp == 0.0


def test__get_obp_handles_player_not_in_game(mock_game, mock_player):
    mock_game.players = []
    games = [mock_game]

    obp_ = obp._get_obp(games, mock_player)

    assert obp_.numerator == 0
    assert obp_.denominator == 0


def test__get_cobp_handles_player_not_in_game(mock_game, mock_player):
    mock_game.players = []
    games = [mock_game]

    cobp_ = obp._get_cobp(games, mock_player)

    assert cobp_.numerator == 0
    assert cobp_.denominator == 0


def test__get_sobp_handles_player_not_in_game(mock_game, mock_player):
    mock_game.players = []
    games = [mock_game]

    sobp_ = obp._get_sobp(games, mock_player)

    assert sobp_.numerator == 0
    assert sobp_.denominator == 0

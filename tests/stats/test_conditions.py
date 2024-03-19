from pyretrosheet.models.play.description import BatterEvent

from cobp.stats import conditions


def test_is_conditional_play__is_met(mock_game, mock_player, mock_player_2, mock_batter_event_play_builder):
    play = mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player, 1)
    play_2 = mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player_2, 1)
    mock_game.chronological_events = [play, play_2]

    is_play_conditional = conditions.is_conditional_play(mock_game, play)
    is_play_2_condiitonal = conditions.is_conditional_play(mock_game, play_2)

    assert is_play_conditional.is_met is True
    assert is_play_conditional.reason is None
    assert is_play_2_condiitonal.is_met is False
    assert is_play_2_condiitonal.reason == "no other on-base in inning"


def test_is_conditional_play__is_not_met_due_to_no_other_on_bases_in_inning(
    mock_game, mock_player, mock_player_2, mock_batter_event_play_builder
):
    play = mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player, 1)
    play_2 = mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 1)
    mock_game.chronological_events = [play, play_2]

    is_conditional_play = conditions.is_conditional_play(mock_game, play)

    for play_ in [play, play_2]:
        is_conditional_play = conditions.is_conditional_play(mock_game, play_)

        assert is_conditional_play.is_met is False
        assert is_conditional_play.reason == "no other on-base in inning"


def test_is_sequential_play__is_met(mock_game, mock_player, mock_player_2, mock_batter_event_play_builder):
    play = mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player, 1)
    play_2 = mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player_2, 1)
    mock_game.chronological_events = [play, play_2]

    is_sequential_play = conditions.is_sequential_play(mock_game, play_2)

    assert is_sequential_play.is_met is True
    assert is_sequential_play.reason is None


def test_is_sequential_play__is_not_met_due_to_being_first_batter_in_inning(
    mock_game, mock_player, mock_player_2, mock_batter_event_play_builder
):
    play = mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player, 1)
    play_2 = mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player_2, 1)
    mock_game.chronological_events = [play, play_2]

    is_sequential_play = conditions.is_sequential_play(mock_game, play)

    assert is_sequential_play.is_met is False
    assert is_sequential_play.reason == "player is first batter in inning"


def test_is_sequential_play__is_not_met_due_to_no_other_on_base_prior_to_play(
    mock_game, mock_player, mock_player_2, mock_batter_event_play_builder
):
    play = mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player, 1)
    play_2 = mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player_2, 1)
    mock_game.chronological_events = [play, play_2]

    is_sequential_play = conditions.is_sequential_play(mock_game, play_2)

    assert is_sequential_play.is_met is False
    assert is_sequential_play.reason == "no other on-base prior to play"


def test_is_leadoff_play__is_met(mock_game, mock_player, mock_player_2, mock_batter_event_play_builder):
    play = mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player, 1)
    play_2 = mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 1)
    mock_game.chronological_events = [play, play_2]

    is_leadoff_play = conditions.is_leadoff_play(mock_game, play)

    assert is_leadoff_play.is_met is True
    assert is_leadoff_play.reason is None


def test_is_leadoff_play__is_not_met_due_to_not_being_first_batter_of_inning(
    mock_game, mock_player, mock_player_2, mock_batter_event_play_builder
):
    play = mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player, 1)
    play_2 = mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player_2, 1)
    mock_game.chronological_events = [play, play_2]

    is_leadoff_play = conditions.is_leadoff_play(mock_game, play_2)

    assert is_leadoff_play.is_met is False
    assert is_leadoff_play.reason == "player is not first batter in inning"


def test_is_leadoff_play__is_not_met_due_to_inning_not_having_an_on_base(
    mock_game, mock_player, mock_player_2, mock_batter_event_play_builder
):
    play = mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player, 1)
    play_2 = mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 1)
    mock_game.chronological_events = [play, play_2]

    is_leadoff_play = conditions.is_leadoff_play(mock_game, play)

    assert is_leadoff_play.is_met is False
    assert is_leadoff_play.reason == "no on-base in inning"

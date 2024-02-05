from pyretrosheet.models.play.description import BatterEvent

from cobp import utils


def test_does_inning_have_an_on_base(mock_game, mock_play_builder, mock_event_builder, mock_team_location):
    inning = 1
    single = mock_play_builder(mock_event_builder(BatterEvent.SINGLE))
    fielded_out = mock_play_builder(mock_event_builder(BatterEvent.ASSISTED_FIELDED_OUT))
    mock_game.chronological_events = [single, fielded_out]

    does_inning_have_an_on_base = utils.does_inning_have_an_on_base(mock_game, inning, mock_team_location)

    assert does_inning_have_an_on_base is True


def test_does_play_have_on_base_before_it_in_inning(mock_game, mock_play_builder, mock_event_builder):
    single = mock_play_builder(mock_event_builder(BatterEvent.SINGLE))
    fielded_out = mock_play_builder(mock_event_builder(BatterEvent.ASSISTED_FIELDED_OUT))
    mock_game.chronological_events = [single, fielded_out]

    play_has_on_base_before_it_in_inning = utils.does_play_have_on_base_before_it_in_inning(mock_game, fielded_out)

    assert play_has_on_base_before_it_in_inning is True


def test_does_play_have_on_base_before_it_in_inning__no_prior_on_base(mock_game, mock_play_builder, mock_event_builder):
    single = mock_play_builder(mock_event_builder(BatterEvent.SINGLE))
    fielded_out = mock_play_builder(mock_event_builder(BatterEvent.ASSISTED_FIELDED_OUT))
    mock_game.chronological_events = [single, fielded_out]

    play_has_on_base_before_it_in_inning = utils.does_play_have_on_base_before_it_in_inning(mock_game, single)

    assert play_has_on_base_before_it_in_inning is False
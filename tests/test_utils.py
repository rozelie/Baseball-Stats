from pyretrosheet.models.play.description import BatterEvent

from cobp import utils


def test_does_inning_have_an_on_base(mock_game, mock_batter_event_play_builder, mock_team_location):
    inning = 1
    mock_game.chronological_events = [
        mock_batter_event_play_builder(BatterEvent.SINGLE),
        mock_batter_event_play_builder(BatterEvent.ASSISTED_FIELDED_OUT),
    ]

    does_inning_have_an_on_base = utils.does_inning_have_an_on_base(mock_game, inning, mock_team_location)

    assert does_inning_have_an_on_base is True


def test_does_inning_have_an_on_base__does_not(mock_game, mock_batter_event_play_builder, mock_team_location):
    inning = 1
    mock_game.chronological_events = [
        mock_batter_event_play_builder(BatterEvent.STRIKEOUT),
        mock_batter_event_play_builder(BatterEvent.STRIKEOUT),
    ]

    does_inning_have_an_on_base = utils.does_inning_have_an_on_base(mock_game, inning, mock_team_location)

    assert does_inning_have_an_on_base is False


def test_does_inning_have_another_play_get_on_base__it_does_before(
    mock_game, mock_batter_event_play_builder, mock_team_location
):
    play = mock_batter_event_play_builder(BatterEvent.STRIKEOUT)
    mock_game.chronological_events = [
        mock_batter_event_play_builder(BatterEvent.SINGLE),
        play,
    ]

    does_inning_have_another_play_get_on_base = utils.does_inning_have_another_play_get_on_base(
        mock_game, play, mock_team_location
    )

    assert does_inning_have_another_play_get_on_base is True


def test_does_inning_have_another_play_get_on_base__it_does_after(
    mock_game, mock_batter_event_play_builder, mock_team_location
):
    play = mock_batter_event_play_builder(BatterEvent.STRIKEOUT)
    mock_game.chronological_events = [
        play,
        mock_batter_event_play_builder(BatterEvent.SINGLE),
    ]

    does_inning_have_another_play_get_on_base = utils.does_inning_have_another_play_get_on_base(
        mock_game, play, mock_team_location
    )

    assert does_inning_have_another_play_get_on_base is True


def test_does_inning_have_another_play_get_on_base__play_is_on_base_but_no_others(
    mock_game, mock_batter_event_play_builder, mock_team_location
):
    play = mock_batter_event_play_builder(BatterEvent.SINGLE)
    mock_game.chronological_events = [
        play,
        mock_batter_event_play_builder(BatterEvent.STRIKEOUT),
    ]

    does_inning_have_another_play_get_on_base = utils.does_inning_have_another_play_get_on_base(
        mock_game, play, mock_team_location
    )

    assert does_inning_have_another_play_get_on_base is False


def test_does_inning_have_another_play_get_on_base__play_is_on_base_as_well_as_another(
    mock_game, mock_batter_event_play_builder, mock_team_location
):
    play = mock_batter_event_play_builder(BatterEvent.SINGLE)
    mock_game.chronological_events = [
        play,
        mock_batter_event_play_builder(BatterEvent.SINGLE),
    ]

    does_inning_have_another_play_get_on_base = utils.does_inning_have_another_play_get_on_base(
        mock_game, play, mock_team_location
    )

    assert does_inning_have_another_play_get_on_base is False


def test_does_play_have_on_base_before_it_in_inning(mock_game, mock_batter_event_play_builder):
    single = mock_batter_event_play_builder(BatterEvent.SINGLE)
    fielded_out = mock_batter_event_play_builder(BatterEvent.ASSISTED_FIELDED_OUT)
    mock_game.chronological_events = [single, fielded_out]

    play_has_on_base_before_it_in_inning = utils.does_play_have_on_base_before_it_in_inning(mock_game, fielded_out)

    assert play_has_on_base_before_it_in_inning is True


def test_does_play_have_on_base_before_it_in_inning__no_prior_on_base(mock_game, mock_batter_event_play_builder):
    single = mock_batter_event_play_builder(BatterEvent.SINGLE)
    fielded_out = mock_batter_event_play_builder(BatterEvent.ASSISTED_FIELDED_OUT)
    mock_game.chronological_events = [single, fielded_out]

    play_has_on_base_before_it_in_inning = utils.does_play_have_on_base_before_it_in_inning(mock_game, single)

    assert play_has_on_base_before_it_in_inning is False

import pytest

from cobp import __main__
from cobp.team import TEAM_RETROSHEET_ID_TO_TEAM, Team

MODULE_PATH = "cobp.__main__"


@pytest.fixture
def set_streamlit_config(mocker):
    return mocker.patch(f"{MODULE_PATH}.set_streamlit_config")


@pytest.fixture
def get_year_selection(mocker):
    return mocker.patch(f"{MODULE_PATH}.selectors.get_year_selection")


@pytest.fixture
def get_team_selection(mocker):
    return mocker.patch(f"{MODULE_PATH}.selectors.get_team_selection")


@pytest.fixture
def _get_games_selection(mocker):
    return mocker.patch(f"{MODULE_PATH}._get_games_selection")


@pytest.fixture
def get_player_to_stats(mocker):
    return mocker.patch(f"{MODULE_PATH}.get_player_to_stats")


@pytest.fixture
def display_game(mocker):
    return mocker.patch(f"{MODULE_PATH}.display_game")


@pytest.fixture
def get_player_to_stats_df(mocker):
    return mocker.patch(f"{MODULE_PATH}.get_player_to_stats_df")


def test_main__happy_path(
    set_streamlit_config,
    get_team_selection,
    get_year_selection,
    _get_games_selection,
    get_player_to_stats,
    display_game,
    get_player_to_stats_df,
):
    get_team_selection.return_value = TEAM_RETROSHEET_ID_TO_TEAM["ARI"]
    get_year_selection.return_value = 2022

    __main__.main()

    set_streamlit_config.assert_called_once()
    get_player_to_stats.assert_called_once_with(_get_games_selection.return_value)
    display_game.assert_called_once_with(
        games=_get_games_selection.return_value,
        player_to_stats=get_player_to_stats.return_value,
        player_to_stats_df=get_player_to_stats_df.return_value,
    )


def test_main__returns_early_on_no_team_or_year_entry(
    set_streamlit_config, get_team_selection, get_year_selection, _get_games_selection
):
    get_team_selection.return_value = None
    get_year_selection.return_value = 2022

    __main__.main()

    _get_games_selection.assert_not_called()


def test_main__returns_early_on_no_games(
    set_streamlit_config, get_team_selection, get_year_selection, _get_games_selection, get_player_to_stats
):
    get_team_selection.return_value = TEAM_RETROSHEET_ID_TO_TEAM["ARI"]
    get_year_selection.return_value = 2022
    _get_games_selection.return_value = None

    __main__.main()

    get_player_to_stats.assert_not_called()

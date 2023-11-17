import pytest

from cobp import __main__
from cobp.models.team import TEAM_RETROSHEET_ID_TO_TEAM, Team

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
def results_display(mocker):
    return mocker.patch(f"{MODULE_PATH}.results.display")


@pytest.fixture
def get_player_to_stats(mocker):
    return mocker.patch(f"{MODULE_PATH}.get_player_to_stats")


def test_main__happy_path(
    set_streamlit_config,
    get_team_selection,
    get_year_selection,
    results_display,
):
    get_team_selection.return_value = TEAM_RETROSHEET_ID_TO_TEAM["ARI"]
    get_year_selection.return_value = 2022

    __main__.main()

    set_streamlit_config.assert_called_once()
    results_display.assert_called_once_with(TEAM_RETROSHEET_ID_TO_TEAM["ARI"], 2022, None)


def test_main__returns_early_on_no_team_or_year_entry(
    set_streamlit_config, get_team_selection, get_year_selection, results_display
):
    get_team_selection.return_value = None
    get_year_selection.return_value = 2022

    __main__.main()

    results_display.assert_not_called()

import pytest

from cobp.data import retrosheet

MODULE_PATH = "cobp.data.retrosheet"


@pytest.fixture
def _get_seasons_events_file(mocker):
    return mocker.patch(f"{MODULE_PATH}._get_seasons_events_file")


@pytest.fixture
def _extract_event_files_zip(mocker):
    return mocker.patch(f"{MODULE_PATH}._extract_event_files_zip")


@pytest.fixture
def _get_years_event_files_zip(mocker):
    return mocker.patch(f"{MODULE_PATH}._get_years_event_files_zip")


def test_get_seasons_event_files__no_redownload_if_exists(mocker, _get_seasons_events_file, _get_years_event_files_zip):
    year = 2022
    _get_seasons_events_file.return_value = [mocker.Mock()] * 30

    seasons_events_file = retrosheet.get_seasons_event_files(year)

    assert seasons_events_file == _get_seasons_events_file.return_value
    _get_years_event_files_zip.assert_not_called()


def test_get_seasons_event_files__redownloads_on_missing_data(
    mocker, _get_seasons_events_file, _get_years_event_files_zip, _extract_event_files_zip
):
    year = 2022
    _get_seasons_events_file.return_value = [mocker.Mock()] * 29

    seasons_events_file = retrosheet.get_seasons_event_files(year)

    assert seasons_events_file == _get_seasons_events_file.return_value
    _get_years_event_files_zip.assert_called_once_with(year)
    _extract_event_files_zip.assert_called_once()

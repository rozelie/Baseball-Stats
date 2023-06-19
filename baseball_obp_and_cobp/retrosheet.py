from io import BytesIO
from pathlib import Path
from typing import Iterator
from zipfile import ZipFile

import requests

from baseball_obp_and_cobp import paths

RETROSHEET_URL = "https://www.retrosheet.org"


def get_seasons_event_files(year: int) -> list[Path]:
    data_year_dir = paths.DATA_DIR / str(year)
    seasons_events_file = list(_get_seasons_events_file(data_year_dir, year))
    if seasons_events_file and len(seasons_events_file) == 30:
        return seasons_events_file

    seasons_event_files_zip_content = _get_years_event_files_zip_content(year)
    data_year_dir.mkdir(parents=True, exist_ok=True)
    seasons_event_files_zip_content.extractall(data_year_dir.as_posix())
    return list(_get_seasons_events_file(data_year_dir, year))


def _get_years_event_files_zip_content(year: int) -> ZipFile:
    response = requests.get(f"{RETROSHEET_URL}/events/{year}eve.zip")
    response.raise_for_status()
    return ZipFile(BytesIO(response.content))


def _get_seasons_events_file(data_year_dir: Path, year: int) -> Iterator[Path]:
    yield from data_year_dir.glob(f"{year}*.EVN")
    yield from data_year_dir.glob(f"{year}*.EVA")

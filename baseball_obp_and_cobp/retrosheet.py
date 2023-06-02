from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import requests

from baseball_obp_and_cobp import paths

RETROSHEET_URL = "https://www.retrosheet.org"


def get_teams_years_event_file(year: int, team_id: str) -> Path:
    data_year_dir = paths.DATA_DIR / str(year)
    event_file = data_year_dir / f"{year}{team_id}.EVN"
    if event_file.exists():
        return event_file

    years_event_files_zip_content = _get_years_event_files_zip_content(year)
    data_year_dir.mkdir(parents=True, exist_ok=True)
    years_event_files_zip_content.extractall(data_year_dir.as_posix())
    return event_file


def _get_years_event_files_zip_content(year: int) -> ZipFile:
    response = requests.get(f"{RETROSHEET_URL}/events/{year}eve.zip")
    response.raise_for_status()
    return ZipFile(BytesIO(response.content))

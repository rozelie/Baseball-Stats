import logging
import time
from io import BytesIO
from pathlib import Path
from typing import Iterator
from zipfile import ZipFile

import requests

from cobp import paths

RETROSHEET_URL = "https://www.retrosheet.org"
logger = logging.getLogger(__name__)


def get_seasons_event_files(year: int) -> list[Path]:
    logger.debug(f"Retrieving events files for season of {year}...")
    data_year_dir = paths.DATA_DIR / str(year)
    seasons_events_file = list(_get_seasons_events_file(data_year_dir, year))
    # if we have all 30 teams data, return it rather than re-download
    if seasons_events_file and len(seasons_events_file) == 30:
        logger.debug("Season event files already downloaded.")
        return seasons_events_file

    logger.debug("Downloading season event files...")
    seasons_event_files_zip = _get_years_event_files_zip(year)
    _extract_event_files_zip(data_year_dir, seasons_event_files_zip)
    return list(_get_seasons_events_file(data_year_dir, year))


def _get_years_event_files_zip(year: int) -> ZipFile:
    attempts = 0
    sleep_seconds_between_failure = 1.0
    while True:
        attempts += 1
        try:
            response = requests.get(f"{RETROSHEET_URL}/events/{year}eve.zip")
            response.raise_for_status()
            break
        except requests.exceptions.RequestException:
            if attempts >= 3:
                raise
            logger.exception(f"Retrosheet request failed - sleeping for {sleep_seconds_between_failure}s and retrying")
            time.sleep(sleep_seconds_between_failure)

    return ZipFile(BytesIO(response.content))


def _extract_event_files_zip(data_year_dir: Path, seasons_event_files_zip: ZipFile) -> None:
    data_year_dir.mkdir(parents=True, exist_ok=True)
    seasons_event_files_zip.extractall(data_year_dir.as_posix())


def _get_seasons_events_file(data_year_dir: Path, year: int) -> Iterator[Path]:
    yield from data_year_dir.glob(f"{year}*.EVN")
    yield from data_year_dir.glob(f"{year}*.EVA")

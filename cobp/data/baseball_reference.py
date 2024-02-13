import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pandas as pd
from fuzzywuzzy import fuzz, process
from pyretrosheet.models.player import Player
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from cobp import paths
from cobp.models.team import Team
from cobp.ui.selectors import FIRST_AVAILABLE_YEAR, LAST_AVAILABLE_YEAR

logger = logging.getLogger(__name__)


@dataclass
class PlayerSeasonalStats:
    player_name: str
    player_id: str
    baseball_reference_team_id: str
    rbis: int
    runs: int


@dataclass
class BaseballReferenceClient:
    base_url: str = "https://www.baseball-reference.com"

    def get_players_seasonal_stats(self, year: int) -> list[PlayerSeasonalStats]:
        logger.info(f"Loading players' seasonal stats from Baseball Reference for {year=}")
        driver = webdriver.Firefox()
        driver.get(f"{self.base_url}/leagues/majors/{year}-standard-batting.shtml")
        wait_seconds_until_table_loads = 10
        batting_table = WebDriverWait(driver, wait_seconds_until_table_loads).until(
            expected_conditions.presence_of_element_located((By.ID, "players_standard_batting"))
        )
        rows = batting_table.find_elements(By.TAG_NAME, "tr")
        players_stats = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if not cells:
                continue

            player_name = cells[0].text
            # remove metadata characters in the player's name if present
            for char in ["*", "#", "?"]:
                player_name = player_name.replace(char, "")

            try:
                # href example: 'https://www.baseball-reference.com/players/a/abramcj01.shtml'
                player_href = cells[0].find_element(By.TAG_NAME, "a").get_attribute("href")
                player_id = player_href.split("/")[5].replace(".shtml", "")  # type: ignore
            except NoSuchElementException:
                # skip non-player rows
                continue

            baseball_reference_team_id = cells[2].text

            # ignore TOT team (an aggregation for all teams played on for the year)
            if baseball_reference_team_id == "TOT":
                continue

            player_stats = PlayerSeasonalStats(
                player_name=player_name,
                player_id=player_id,
                baseball_reference_team_id=baseball_reference_team_id,
                rbis=int(cells[12].text),
                runs=int(cells[7].text),
            )
            logger.info(f"Loaded player seasonal stats: {player_stats}")
            players_stats.append(player_stats)

        driver.close()
        return players_stats


def dump_players_seasonal_stats(year: int) -> None:
    baseball_reference_client = BaseballReferenceClient()
    players_seasonal_stats = baseball_reference_client.get_players_seasonal_stats(year)
    lines = ["player_name,player_id,baseball_reference_team_id,rbis,runs"]
    for player_stats in players_seasonal_stats:
        lines.append(
            ",".join(
                [
                    player_stats.player_name,
                    player_stats.player_id,
                    player_stats.baseball_reference_team_id,
                    str(player_stats.rbis),
                    str(player_stats.runs),
                ]
            )
        )

    data_path = _get_players_seasonal_stats_data_path(year)
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text("\n".join(lines))
    logger.info(f"Wrote baseball reference seasonal players rbis to {data_path.as_posix()}")


@lru_cache(maxsize=None)
def get_seasonal_players_stats(year: int) -> pd.DataFrame:
    data_path = _get_players_seasonal_stats_data_path(year)
    if data_path.exists():
        return pd.read_csv(data_path)

    dump_players_seasonal_stats(year)
    return pd.read_csv(data_path)


def lookup_player(df: pd.DataFrame, player: Player, team: Team, year: int) -> pd.Series | None:
    team_id = team.baseball_reference_id or team.retrosheet_id
    team_players_df = df.loc[df["baseball_reference_team_id"] == team_id]
    team_players = team_players_df["player_name"].tolist()
    player_name = _get_real_player_name(player)
    if player_name in team_players:
        player_name_match = player_name
    else:
        player_name_match = _fuzzy_lookup_player(player_name, team_players)

    return team_players_df.loc[df["player_name"] == player_name_match]


def dump_all_seasons():
    for year in range(FIRST_AVAILABLE_YEAR, LAST_AVAILABLE_YEAR + 1):
        dump_players_seasonal_stats(year)


def _get_players_seasonal_stats_data_path(year: int) -> Path:
    return paths.DATA_DIR / str(year) / "baseball_reference.csv"


def _get_real_player_name(player: Player) -> str:
    # handle data error where either the player id or the name is incorrect (from 2013 New York Yankees retrosheet data)
    if player.id == "almoz001" and player.name == "Drew Stubbs":
        return "Zoilo Almonte"

    return player.name  # type: ignore


def _fuzzy_lookup_player(player: str, team_players: list[str]) -> str:
    """Perform a fuzzy lookup to match a player's name to the names of players on a team."""
    # set to 80 so minor differences can be matched (e.g. accent in a name since Retrosheet does not use accents)
    threshold = 80
    matched_player, score = process.extractOne(player, team_players)
    if score >= threshold:
        return matched_player  # type: ignore

    # if match does not reach the threshold, try matching on last name only
    player_last_name = player.split(" ")[-1]
    matched_player_last_name = matched_player.split(" ")[-1]
    if player_last_name == matched_player_last_name:
        return matched_player # type: ignore

    # try fuzzy matching on last name only
    player_last_name = player.split(" ")[-1]
    for team_player in team_players:
        team_player_last_name = team_player.split(" ")[-1]
        match_ratio = fuzz.ratio(player_last_name, team_player_last_name)
        print(f"{player_last_name=} | {team_player_last_name=} | {match_ratio=}")
        if match_ratio >= 80:
            return team_player

    # special cases of players playing under other names
    player_aliases = {
        "Jose Garcia": "José Barrero",  # https://www.baseball-reference.com/players/g/garcijo02.shtml
        "Felipe Rivero": "Felipe Vazquez",  # https://www.baseball-reference.com/players/r/riverfe01.shtml
        "Manuel Pina": "Manny Piña",
        "Fausto Carmona": "Roberto Hernández",  # https://www.baseball-reference.com/players/c/carmofa01.shtml
        "Leo Nunez": "Juan Carlos Oviedo",  # https://www.baseball-reference.com/players/n/nunezle01.shtml
        "Jose J. Leon": "José León",
    }
    if player in player_aliases:
        return player_aliases[player]

    raise ValueError(f"Unable to perform a fuzzy lookup of {player=} | {matched_player=} | {score=} | {team_players=}")

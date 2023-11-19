import logging

from cobp.models.game import Game

logger = logging.getLogger(__name__)


def cross_reference_baseball_reference_game_data(game: Game) -> None:
    raise NotImplementedError()
    # from cobp.stats.basic import BasicStats, PlayerToBasicStats, get_player_to_basic_stats
    # logger.info(f"Cross-referencing data with baseball reference: {game.id=}")
    # player_to_stats = get_player_to_basic_stats([game])
    # baseball_reference_player_to_stats = _get_baseball_reference_player_to_stats(game.id)


def _get_baseball_reference_player_to_stats(game_id: str) -> None:
    # import re
    # from bs4 import BeautifulSoup
    # from cobp.data.baseball_reference import BaseballReferenceClient
    # client = BaseballReferenceClient()
    # box_score_html = client.get_box_score_html(game_id)
    # soup = BeautifulSoup(box_score_html, "html.parser")
    # batting = soup.find_all(id=re.compile(r".*batting"))
    return None

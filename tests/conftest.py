import pytest

from cobp.game import Game
from cobp.player import Player
from cobp.team import Team


@pytest.fixture
def mock_player():
    return Player(id="player", name="player", lineup_position=1)


@pytest.fixture
def mock_player_2():
    return Player(id="player_2", name="player_2", lineup_position=2)


@pytest.fixture
def mock_game():
    return Game(
        id="CHN202204080",
        team=Team.CHICAGO_CUBS,
        home_team=Team.CHICAGO_CUBS,
        visiting_team=Team.CINCINNATI_REDS,
        players=[],
        inning_to_plays={},
    )

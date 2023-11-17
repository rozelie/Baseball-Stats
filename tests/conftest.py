import pytest

from cobp.models.delta import PlayDelta
from cobp.models.game import Game
from cobp.models.play import Play
from cobp.models.play_modifier import PlayModifier
from cobp.models.play_result import PlayResult
from cobp.models.player import Player
from cobp.models.team import TEAMS


@pytest.fixture
def mock_player():
    return Player(id="player", name="player", lineup_position=1)


@pytest.fixture
def mock_player_2():
    return Player(id="player_2", name="player_2", lineup_position=2)


@pytest.fixture
def mock_play_builder(mock_player):
    def play_builder(
        result: PlayResult,
        modifiers: list[PlayModifier] | None = None,
        inning: int = 1,
        batter_id: str = mock_player.id,
        play_descriptor: str = "",
        delta: PlayDelta | None = None,
    ):
        return Play(
            inning=inning,
            batter_id=batter_id,
            play_descriptor=play_descriptor,
            result=result,
            previous_base_state={},
            modifiers=modifiers or [],
            delta=delta
            or PlayDelta(
                resulting_base_state={},
                player_ids_scoring_a_run=[],
                batter_rbis=0,
            ),
        )

    return play_builder


@pytest.fixture
def mock_game():
    return Game(
        id="CHN202204080",
        team=TEAMS[0],
        home_team=TEAMS[0],
        visiting_team=TEAMS[1],
        players=[],
        inning_to_plays={},
    )

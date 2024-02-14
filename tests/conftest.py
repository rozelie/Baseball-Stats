from datetime import date

import pytest
from pyretrosheet.models.base import Base
from pyretrosheet.models.game import Game
from pyretrosheet.models.game_id import GameID
from pyretrosheet.models.play import Play
from pyretrosheet.models.play.advance import Advance
from pyretrosheet.models.play.description import BatterEvent, Description, RunnerEvent
from pyretrosheet.models.play.event import Event
from pyretrosheet.models.play.modifier import Modifier, ModifierType
from pyretrosheet.models.player import Player
from pyretrosheet.models.team import TeamLocation


@pytest.fixture
def mock_team_location() -> TeamLocation:
    return TeamLocation.HOME


@pytest.fixture
def mock_player(mock_team_location):
    return Player(
        id="player",
        name="player",
        team_location=mock_team_location,
        batting_order_position=1,
        fielding_position=1,
        is_sub=False,
        raw="",
    )


@pytest.fixture
def mock_player_2(mock_team_location):
    return Player(
        id="player_2",
        name="player_1",
        team_location=mock_team_location,
        batting_order_position=1,
        fielding_position=1,
        is_sub=False,
        raw="",
    )


@pytest.fixture
def mock_modifier_builder():
    def modifier_builder(
        type: ModifierType,
        hit_location: str | None = None,
        fielder_positions: list[int] | None = None,
        base: Base | None = None,
        raw: str = "",
    ):
        return Modifier(
            type=type,
            hit_location=hit_location,
            fielder_positions=fielder_positions,
            base=base,
            raw=raw,
        )

    return modifier_builder


@pytest.fixture
def mock_event_builder():
    def event_builder(
        batter_event: BatterEvent | None = None,
        runner_event: RunnerEvent | None = None,
        modifiers: list[Modifier] | None = None,
        advances: list[Advance] | None = None,
    ):
        return Event(
            description=Description(
                batter_event=batter_event,
                runner_event=runner_event,
                fielder_assists={},
                fielder_put_outs={},
                fielder_handlers={},
                fielder_errors={},
                put_out_at_base=None,
                stolen_base=None,
                raw="",
            ),
            modifiers=modifiers or [],
            advances=advances or [],
            raw="",
        )

    return event_builder


@pytest.fixture
def mock_play_builder(mock_player, mock_event_builder, mock_team_location):
    def play_builder(
        event: Event = mock_event_builder(),
        inning: int = 1,
        team_location: TeamLocation = mock_team_location,
        batter_id: str = mock_player.id,
        count: str = "",
        pitches: str = "",
        comments: list[str] | None = None,
        raw: str = "",
    ):
        return Play(
            inning=inning,
            team_location=team_location,
            batter_id=batter_id,
            count=count,
            pitches=pitches,
            comments=comments or [],
            event=event,
            raw=raw,
        )

    return play_builder


@pytest.fixture
def mock_game():
    return Game(
        id=GameID(
            home_team_id="",
            date=date(2024, 1, 1),
            game_number=0,
            raw="",
        ),
        info={"hometeam": "", "visteam": ""},
        chronological_events=[],
        earned_runs={},
    )

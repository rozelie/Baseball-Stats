from copy import deepcopy

import pytest
from pyretrosheet.models.play.description import BatterEvent, RunnerEvent
from pyretrosheet.models.play.modifier import ModifierType
from pyretrosheet.models.team import TeamLocation

from cobp.stats import aggregated
from cobp.stats.ba import BA
from cobp.stats.basic import BasicStats
from cobp.stats.obp import OBP
from cobp.stats.runs import Runs
from cobp.stats.sp import SP

MODULE_PATH = "cobp.stats.aggregated"


@pytest.fixture
def get_player_to_runs(mocker):
    return mocker.patch(f"{MODULE_PATH}.get_player_to_runs")


class TestPlayerStats:
    def test_derivative_stats(self):
        player_stats = aggregated.PlayerStats(
            obp=OBP(hits=2, at_bats=2),  # 1.0
            cobp=OBP(hits=1, at_bats=2),  # 0.5
            sobp=OBP(hits=1, at_bats=2),  # 0.5
            loop=OBP(hits=0, at_bats=2),  # 0.0
            sp=SP(singles=1, at_bats=2),  # 0.5
            csp=SP(singles=1, at_bats=2),  # 0.5
            lsp=SP(singles=1, at_bats=2),  # 0.5
            ssp=SP(singles=1, at_bats=2),  # 0.5
            ba=BA(),
            basic=BasicStats(),
            runs=Runs(),
        )

        assert player_stats.ops.value == 1.5  # 1.0 + 0.5
        assert player_stats.cops.value == 1.0  # 0.5 + 0.5
        assert player_stats.loops.value == 0.5  # 0.0 + 0.5
        assert player_stats.sops.value == 1.0  # 0.5 + 0.5


def test_aggregated_stats_scenario(
    mock_game, mock_team, mock_player, mock_player_2, mock_batter_event_play_builder, get_player_to_runs
):
    """Can be used for regression testing - was initially given a specific scenario to test against (this test)
    which allowed for finding some errors in stat calculations.

    At the time of writing, this resolved two issues:
    1. LOOP was including 1-2-3 innings, which it shouldn't have (similar logic to COBP)
    2. SOBP was skipping plays where there we not other on-bases in the prior inning (which I'm unsure why it was ever added)
    """
    mock_game.chronological_events.extend(
        [
            mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player, 1),
            mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 2),
            mock_batter_event_play_builder(BatterEvent.WALK, mock_player, 3),
            mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 4),
            mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player, 5),
            mock_batter_event_play_builder(BatterEvent.HOME_RUN_INSIDE_PARK, mock_player_2, 5),
            mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 6),
            mock_batter_event_play_builder(BatterEvent.TRIPLE, mock_player_2, 7),
            mock_batter_event_play_builder(BatterEvent.DOUBLE, mock_player, 7),
            mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 8),
            mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player_2, 9),
            mock_batter_event_play_builder(BatterEvent.UNASSISTED_FIELDED_OUT, mock_player, 9),
        ]
    )
    games = [mock_game]
    team = mock_team
    year = 2022

    player_to_stats = aggregated.get_player_to_stats(games, team, year)
    player_stats = player_to_stats[mock_player.id]

    assert player_stats.ba.value == 0.5
    assert player_stats.obp.value == 0.6
    assert round(player_stats.cobp.value, 3) == 0.667
    assert player_stats.loop.value == 1.0
    assert player_stats.sobp.value == 0.5

    assert player_stats.sp.value == 0.750
    assert player_stats.csp.value == 1.0
    assert player_stats.lsp.value == 1.0
    assert player_stats.ssp.value == 1.0

    assert player_stats.ops.value == 1.35
    assert round(player_stats.cops.value, 3) == 1.667
    assert player_stats.loops.value == 2.0
    assert player_stats.sops.value == 1.5


def test_aggregated_stats_across_real_games(
    mock_game,
    mock_team,
    mock_player_builder,
    mock_play_builder,
    mock_event_builder,
    mock_modifier_builder,
    get_player_to_runs,
):
    """Used to verify how stats are being calculated over a series of real games."""
    orter001 = mock_player_builder(id="orter001", name="Rafael Ortega")
    madrn001 = mock_player_builder(id="madrn001", name="Nick Madrigal")
    contw001 = mock_player_builder(id="contw001", name="Willson Contreras")
    happi001 = mock_player_builder(id="happi001", name="Ian Happ")
    schwf001 = mock_player_builder(id="schwf001", name="Frank Schwindel")
    suzus001 = mock_player_builder(id="suzus001", name="Seiya Suzuki")
    heywj001 = mock_player_builder(id="heywj001", name="Jason Heyward")
    wisdp001 = mock_player_builder(id="wisdp001", name="Patrick Wisdom")
    hoern001 = mock_player_builder(id="hoern001", name="Nico Hoerner")
    frazc001 = mock_player_builder(id="frazc001", name="Jackson Frazier")
    hermm001 = mock_player_builder(id="hermm001", name="Michael Hermosillo")
    villj001 = mock_player_builder(id="villj001", name="Jonathan Villar")
    rivaa001 = mock_player_builder(id="rivaa001", name="Alfonso Rivas")
    gomey001 = mock_player_builder(id="gomey001", name="Yan Gomes")
    players = [
        orter001,
        madrn001,
        contw001,
        happi001,
        schwf001,
        suzus001,
        heywj001,
        wisdp001,
        hoern001,
        frazc001,
        hermm001,
        villj001,
        rivaa001,
        gomey001,
    ]

    game_1 = mock_game  # 2022/04/07 MIL @ CHN
    game_1.chronological_events = players
    game_2 = deepcopy(game_1)  # 2022/04/09 MIL @ CHN
    game_3 = deepcopy(game_1)  # 2022/04/10 MIL @ CHN
    game_4 = deepcopy(game_1)  # 2022/04/12 CHN @ PIT
    game_5 = deepcopy(game_1)  # 2022/04/13 CHN @ PIT

    # fmt: off
    game_1.chronological_events.extend([
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=orter001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=madrn001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=contw001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=None, runner_event=RunnerEvent.CAUGHT_STEALING, modifiers=[]), batter_id=happi001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.GROUND_RULE_DOUBLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=happi001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=schwf001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=suzus001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FORCE_OUT), mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=heywj001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=wisdp001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=hoern001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=orter001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=madrn001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=contw001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=happi001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=schwf001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=suzus001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=heywj001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.SACRIFICE_FLY), mock_modifier_builder(ModifierType.FLY)]), batter_id=wisdp001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.HOME_RUN_LEAVING_PARK, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=hoern001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=orter001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=madrn001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.POP_FLY)]), batter_id=contw001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=happi001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=happi001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=happi001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.GROUNDED_INTO_DOUBLE_PLAY, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL_DOUBLE_PLAY), mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=schwf001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=suzus001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.POP_FLY)]), batter_id=heywj001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=hoern001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=hoern001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=orter001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.DOUBLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=frazc001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=madrn001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=contw001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.HIT_BY_PITCH, runner_event=None, modifiers=[]), batter_id=contw001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.DOUBLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=happi001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=schwf001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=suzus001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=heywj001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=8),
    ])
    game_2.chronological_events.extend([
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=orter001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.HIT_BY_PITCH, runner_event=None, modifiers=[]), batter_id=madrn001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=contw001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=happi001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FORCE_OUT), mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=schwf001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.SACRIFICE_FLY), mock_modifier_builder(ModifierType.FLY)]), batter_id=suzus001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=heywj001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=wisdp001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=hoern001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=orter001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=madrn001.id, inning=2),    

        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=contw001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.POP_FLY)]), batter_id=happi001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=schwf001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=suzus001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=heywj001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=3),    

        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=hoern001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.DOUBLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=orter001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=madrn001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.HIT_BY_PITCH, runner_event=None, modifiers=[]), batter_id=contw001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=happi001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=schwf001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=schwf001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=suzus001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=None, runner_event=RunnerEvent.WILD_PITCH, modifiers=[]), batter_id=heywj001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=heywj001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=wisdp001.id, inning=4),    

        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=hoern001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=orter001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=madrn001.id, inning=5),    

        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=contw001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=contw001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FORCE_OUT), mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=happi001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=schwf001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=suzus001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=heywj001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=wisdp001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=hoern001.id, inning=6),    

        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=orter001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=orter001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=madrn001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=contw001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.HIT_BY_PITCH, runner_event=None, modifiers=[]), batter_id=happi001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=schwf001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=schwf001.id, inning=7),    

        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=suzus001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=suzus001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=heywj001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=hermm001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=wisdp001.id, inning=8),
    ])
    game_3.chronological_events.extend([
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=orter001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=madrn001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=None, runner_event=RunnerEvent.CAUGHT_STEALING, modifiers=[]), batter_id=villj001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=villj001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=rivaa001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.HOME_RUN_LEAVING_PARK, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=suzus001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=frazc001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=heywj001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.DOUBLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=gomey001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=hoern001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=orter001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FORCE_OUT), mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=madrn001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=villj001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=rivaa001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=suzus001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=frazc001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=heywj001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=gomey001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=hoern001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=orter001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=orter001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=hermm001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.GROUNDED_INTO_DOUBLE_PLAY, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL_DOUBLE_PLAY), mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=madrn001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=villj001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=rivaa001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=schwf001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=suzus001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=frazc001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=heywj001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.FIELDERS_CHOICE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=wisdp001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=gomey001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=None, runner_event=RunnerEvent.WILD_PITCH, modifiers=[]), batter_id=gomey001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=None, runner_event=RunnerEvent.WILD_PITCH, modifiers=[]), batter_id=gomey001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=gomey001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=hoern001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=hoern001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=hoern001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=hermm001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=None, runner_event=RunnerEvent.STOLEN_BASE, modifiers=[]), batter_id=madrn001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=madrn001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=villj001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=schwf001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=schwf001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=suzus001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=frazc001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=9),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=9),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=gomey001.id, inning=9),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=hoern001.id, inning=9),
    ])
    game_4.chronological_events.extend([
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=frazc001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=contw001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=None, runner_event=RunnerEvent.PICKED_OFF_CAUGHT_STEALING, modifiers=[]), batter_id=schwf001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=schwf001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=suzus001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.GROUNDED_INTO_DOUBLE_PLAY, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL_DOUBLE_PLAY), mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=madrn001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=hermm001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=happi001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=hoern001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.GROUNDED_INTO_DOUBLE_PLAY, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL_DOUBLE_PLAY), mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=frazc001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=contw001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=schwf001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.HOME_RUN_LEAVING_PARK, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=suzus001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=madrn001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=hermm001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=happi001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=hoern001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.DOUBLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=frazc001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=contw001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=schwf001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.HOME_RUN_LEAVING_PARK, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=suzus001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=madrn001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=hermm001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=happi001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FORCE_OUT), mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=hoern001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=frazc001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=frazc001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.POP_FLY)]), batter_id=frazc001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=contw001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=None, runner_event=RunnerEvent.WILD_PITCH, modifiers=[]), batter_id=wisdp001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=schwf001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=suzus001.id, inning=9),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=suzus001.id, inning=9),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=madrn001.id, inning=9),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=hermm001.id, inning=9),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=orter001.id, inning=9),
    ])
    game_5.chronological_events.extend([
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY), mock_modifier_builder(ModifierType.FOUL)]), batter_id=orter001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=schwf001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.HOME_RUN_LEAVING_PARK, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=contw001.id, inning=1),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=happi001.id, inning=1),    

        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=suzus001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=heywj001.id, inning=2),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=2),    

        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=villj001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=hoern001.id, inning=3),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.POP_FLY)]), batter_id=orter001.id, inning=3),    

        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=schwf001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.GROUND_RULE_DOUBLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=contw001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=happi001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=suzus001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=heywj001.id, inning=4),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=wisdp001.id, inning=4),    

        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=villj001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=hoern001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=orter001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=orter001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=frazc001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=None, runner_event=RunnerEvent.WILD_PITCH, modifiers=[]), batter_id=schwf001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=schwf001.id, inning=5),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.GROUNDED_INTO_DOUBLE_PLAY, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL_DOUBLE_PLAY), mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=contw001.id, inning=5),    

        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=happi001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=suzus001.id, inning=6),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=heywj001.id, inning=6),    

        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.NO_PLAY, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=wisdp001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=villj001.id, inning=7),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.FLY)]), batter_id=hoern001.id, inning=7),    

        mock_play_builder(mock_event_builder(batter_event=BatterEvent.ASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.GROUND_BALL)]), batter_id=frazc001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.SINGLE, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=schwf001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=contw001.id, inning=8),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=happi001.id, inning=8),    

        mock_play_builder(mock_event_builder(batter_event=BatterEvent.WALK, runner_event=None, modifiers=[]), batter_id=suzus001.id, inning=9),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.UNASSISTED_FIELDED_OUT, runner_event=None, modifiers=[mock_modifier_builder(ModifierType.LINE_DRIVE)]), batter_id=heywj001.id, inning=9),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=wisdp001.id, inning=9),    
        mock_play_builder(mock_event_builder(batter_event=BatterEvent.STRIKEOUT, runner_event=None, modifiers=[]), batter_id=villj001.id, inning=9),
    ])
    # fmt: on

    games = [game_1, game_2, game_3, game_4, game_5]
    team = mock_team
    year = 2022

    player_to_stats = aggregated.get_player_to_stats(games, team, year)

    schwindel_stats = player_to_stats[schwf001.id]
    print(schwindel_stats.cobp.explanation)
    assert round(schwindel_stats.sobp.value, 3) == 0.364
    assert round(schwindel_stats.cobp.value, 3) == 0.267
    assert schwindel_stats.loop.value == 0.5

    assert round(schwindel_stats.sops.value, 3) == 0.586
    assert round(schwindel_stats.cops.value, 3) == 0.421
    assert schwindel_stats.loops.value == 1.0

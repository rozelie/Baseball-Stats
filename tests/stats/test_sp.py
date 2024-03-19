from pyretrosheet.models.play.description import BatterEvent

from cobp.stats import sp
from cobp.utils import TEAM_PLAYER_ID


class TestSP:
    def test_sp__happy_path(self):
        sp_ = sp.SP()
        sp_.singles = 1
        sp_.doubles = 1
        sp_.triples = 1
        sp_.home_runs = 1
        sp_.at_bats = 5

        # numerator (1 * 1 + 2 * 1 + 3 * 1 + 4 * 1) == 10
        # denominator (5) == 5
        assert sp_.value == 2.0

    def test_sp__handles_zero_denominator(self):
        sp_ = sp.SP()
        sp_.at_bats = 0

        assert sp_.value == 0.0


def test_get_player_to_sp(mock_game, mock_player, mock_player_2, mock_batter_event_play_builder):
    mock_game.chronological_events = [
        mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player, 1),
        mock_batter_event_play_builder(BatterEvent.DOUBLE, mock_player, 2),
        mock_batter_event_play_builder(BatterEvent.TRIPLE, mock_player, 3),
        mock_batter_event_play_builder(BatterEvent.HOME_RUN_INSIDE_PARK, mock_player, 4),
        mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player, 5),
        mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 1),
    ]
    games = [mock_game]
    players = [mock_player, mock_player_2]

    player_to_sp = sp.get_player_to_sp(games, players)

    assert len(player_to_sp) == 3
    assert player_to_sp[mock_player.id].value == 2.0
    assert player_to_sp[mock_player_2.id].value == 0.0
    assert round(player_to_sp[TEAM_PLAYER_ID].value, 1) == 1.7


def test_get_player_to_csp(mock_game, mock_player, mock_player_2, mock_batter_event_play_builder):
    mock_game.chronological_events = [
        # no on-base in inning - skip inning 1
        mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player, 1),
        mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 1),
        # on-base in inning so include inning only for mock_player
        mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player, 2),
        mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player_2, 2),
    ]
    games = [mock_game]
    players = [mock_player, mock_player_2]

    player_to_csp = sp.get_player_to_csp(games, players)
    player_1_csp = player_to_csp[mock_player.id]
    player_2_csp = player_to_csp[mock_player_2.id]

    assert player_1_csp.at_bats == 1
    assert player_2_csp.at_bats == 0
    assert player_1_csp.singles == 0
    assert player_2_csp.singles == 0
    assert player_1_csp.value == 0.0
    assert player_2_csp.value == 0.0


def test_get_player_to_ssp(mock_game, mock_player, mock_player_2, mock_batter_event_play_builder):
    mock_game.chronological_events = [
        # ignore all since there is no play on base before it in the inning
        mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player, 1),
        mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player_2, 1),
        # on-base in inning so player_2 is included, not player 1 since is first batter in inning
        mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player, 2),
        mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player_2, 2),
        # ignore player since they are the first batter, player_2 included since there is an on-base prior
        mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player, 3),
        mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 3),
    ]
    games = [mock_game]
    players = [mock_player, mock_player_2]

    player_to_ssp = sp.get_player_to_ssp(games, players)
    player_1_ssp = player_to_ssp[mock_player.id]
    player_2_ssp = player_to_ssp[mock_player_2.id]

    assert player_1_ssp.at_bats == 0
    assert player_2_ssp.at_bats == 2
    assert player_1_ssp.singles == 0
    assert player_2_ssp.singles == 1
    assert player_1_ssp.value == 0.0
    assert player_2_ssp.value == 0.5


def test_get_player_to_lsp(mock_game, mock_player, mock_player_2, mock_batter_event_play_builder):
    mock_game.chronological_events = [
        # ignore all since there is no play on base in the inning
        mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player, 1),
        mock_batter_event_play_builder(BatterEvent.STRIKEOUT, mock_player_2, 1),
        # add player since it is the first of the inning, ignore player 2 since they are not the first batter
        mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player, 2),
        mock_batter_event_play_builder(BatterEvent.SINGLE, mock_player_2, 2),
    ]
    games = [mock_game]
    players = [mock_player, mock_player_2]

    player_to_lsp = sp.get_player_to_lsp(games, players)
    player_1_lsp = player_to_lsp[mock_player.id]
    player_2_lsp = player_to_lsp[mock_player_2.id]

    assert player_1_lsp.at_bats == 1
    assert player_2_lsp.at_bats == 0
    assert player_1_lsp.singles == 1
    assert player_2_lsp.singles == 0
    assert player_1_lsp.value == 1.0
    assert player_2_lsp.value == 0.0

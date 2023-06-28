from textwrap import dedent

import pytest

from cobp import game
from cobp.game import GameLine
from cobp.play import Play, PlayResult
from cobp.team import Team

MODULE_PATH = "baseball_obp_and_cobp.game"


class TestGame:
    def test_get_plays_resulting_on_base_in_inning(self, mock_game, mock_player):
        inning = 1
        single = Play(inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.SINGLE, modifiers=[])
        fielded_out = Play(
            inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.FIELDED_OUT, modifiers=[]
        )
        mock_game.inning_to_plays = {1: [single, fielded_out]}

        plays_resulting_on_base_in_inning = mock_game.get_plays_resulting_on_base_in_inning(inning)

        assert plays_resulting_on_base_in_inning == [single]

    def test_play_has_on_base_before_it_in_inning__has_prior_on_base(self, mock_game, mock_player):
        inning = 1
        single = Play(inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.SINGLE, modifiers=[])
        fielded_out = Play(
            inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.FIELDED_OUT, modifiers=[]
        )
        mock_game.inning_to_plays = {1: [single, fielded_out]}

        play_has_on_base_before_it_in_inning = mock_game.play_has_on_base_before_it_in_inning(inning, fielded_out)

        assert play_has_on_base_before_it_in_inning is True

    def test_play_has_on_base_before_it_in_inning__no_prior_on_base(self, mock_game, mock_player):
        inning = 1
        single = Play(inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.SINGLE, modifiers=[])
        fielded_out = Play(
            inning=1, batter_id=mock_player.id, play_descriptor="", result=PlayResult.FIELDED_OUT, modifiers=[]
        )
        mock_game.inning_to_plays = {1: [fielded_out, single]}

        play_has_on_base_before_it_in_inning = mock_game.play_has_on_base_before_it_in_inning(inning, single)

        assert play_has_on_base_before_it_in_inning is False


def test__yield_game_lines(mocker):
    path = mocker.Mock()
    game_1 = """\
    id,ANA202204070
    version,2
    info,visteam,HOU
    info,hometeam,ANA
    info,site,ANA01
    """
    game_2 = """\
    id,ANA202204080
    version,2
    info,visteam,HOU
    info,hometeam,ANA
    info,site,ANA01
    """
    team_not_in_game = """\
    id,CHI202204090
    version,2
    info,visteam,HOU
    info,hometeam,CHI
    info,site,CHI01
    """
    path.read_text.return_value = dedent(game_1) + dedent(game_2) + dedent(team_not_in_game)
    team = Team.ANAHEIM_ANGELS

    game_lines = list(game._yield_game_lines(path, team))

    assert game_lines == [
        [
            GameLine(id="id", values=["ANA202204070"]),
            GameLine(id="version", values=["2"]),
            GameLine(id="info", values=["visteam", "HOU"]),
            GameLine(id="info", values=["hometeam", "ANA"]),
            GameLine(id="info", values=["site", "ANA01"]),
        ],
        [
            GameLine(id="id", values=["ANA202204080"]),
            GameLine(id="version", values=["2"]),
            GameLine(id="info", values=["visteam", "HOU"]),
            GameLine(id="info", values=["hometeam", "ANA"]),
            GameLine(id="info", values=["site", "ANA01"]),
        ],
    ]


def test__get_teams_players():
    # fourth comma-delimited value represents home vs. visiting, where visiting == 0 and home == 1
    players = dedent(
        """\
        start,altuj001,"Jose Altuve",0,1,4
        start,branm003,"Michael Brantley",1,2,10
        sub,loupa001,"Aaron Loup",0,0,1
        sub,warra003,"Austin Warren",1,0,1
        sub,branm003,"Michael Brantley",1,2,10
        """
    )
    player_game_lines = [GameLine.from_line(line) for line in players.splitlines()]
    team = Team.ANAHEIM_ANGELS
    visiting_team = Team.CHICAGO_CUBS
    home_team = team

    teams_players = game._get_teams_players(player_game_lines, team, visiting_team, home_team)

    assert set(p.name for p in teams_players) == {"Michael Brantley", "Austin Warren"}

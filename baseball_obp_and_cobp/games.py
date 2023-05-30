from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from baseball_obp_and_cobp.player import Player
from baseball_obp_and_cobp.plays import Play
from baseball_obp_and_cobp.teams import Team, TeamType


@dataclass
class Game:
    id: str
    players: list[Player]

    @classmethod
    def from_game_lines(cls, lines: list[str], team: Team) -> "Game":
        game_id: None | str = None
        players: list[Player] = []
        visiting_team: None | Team = None
        home_team: None | Team = None
        player_id_to_player: dict[str, Player] = {}
        for line in lines:
            split_line = line.split(",")
            line_id = split_line[0]
            match line_id:
                case "id":
                    game_id = split_line[1]

                case "info":
                    info_name = split_line[1]
                    info_value = split_line[2]
                    if info_name == "visteam":
                        visiting_team = Team(info_value)
                    elif info_name == "hometeam":
                        home_team = Team(info_value)

                case "start":
                    player = Player.from_start_line(line)
                    player_id_to_player[player.id] = player
                    players_team_type = TeamType(int(split_line[3]))
                    if (visiting_team == team and players_team_type == TeamType.VISITING) or (
                        home_team == team and players_team_type == TeamType.HOME
                    ):
                        players.append(player)
                case "play":
                    play = Play.from_play_line(line)
                    # ignore plays not part of the data's team
                    if batter := player_id_to_player.get(play.batter_id):
                        batter.plays.append(play)

            # TODO:
            # - player substitution handling

        return cls(
            id=game_id,  # type: ignore
            players=players,
        )

    def get_player(self, player_id: str) -> Player:
        for player in self.players:
            if player.id == player_id:
                return player
        raise Exception(f"Unable to find player id of {player_id} within the game")


def load_events_file(path: Path) -> list[Game]:
    team = _get_files_team(path)
    return [Game.from_game_lines(lines, team) for lines in _yield_game_lines(path)]


def _get_files_team(path: Path) -> Team:
    id_line = path.read_text().splitlines()[0]
    file_id = id_line.split(",")[1]
    team_id = "".join(c for c in file_id if c.isalpha())
    return Team(team_id)


def _yield_game_lines(path: Path) -> Iterator[list[str]]:
    """Yield the lines corresponding to each game in the Retrosheet events file."""
    current_game_lines: list[str] = []
    for line in path.read_text().splitlines():
        if line.split(",")[0] == "id":
            if current_game_lines:
                yield current_game_lines
                current_game_lines.clear()

        current_game_lines.append(line)

from typing import Any

import streamlit as st

from baseball_obp_and_cobp.game import Game
from baseball_obp_and_cobp.obp import PlayerToGameOBP

def set_streamlit_config() -> None:
    st.set_page_config(page_title="Baseball (C)OBP", layout="wide")


def get_selection(prompt: str, options: list[Any]) -> Any:
    return st.selectbox(prompt, options=options)


def display_player_obps(player_to_game_obps: PlayerToGameOBP, game: Game) -> None:
    st.header(f"{game.team.pretty_name} Player (C)OBP")
    for player_id, (obps, explanation) in player_to_game_obps.items():
        player_column, obp_column, cobp_column = st.columns(3)
        with player_column:
            player = game.get_player(player_id)
            st.text(player.name)
        with obp_column:
            st.text(f"OBP = {round(obps.obp, 3)}")
            for line in explanation.obp_explanation:
                st.text(line)
        with cobp_column:
            st.text(f"COBP = {round(obps.cobp, 3)}")
            for line in explanation.cobp_explanation:
                st.text(line)
        st.divider()


def display_innings(game: Game) -> None:
    st.header(f"Inning Play-by-Play For {game.team.pretty_name}")
    for inning, plays in game.inning_to_plays.items():
        has_multiple_on_bases = "Yes" if game.inning_has_multiple_on_bases(inning) else "No"
        st.text(f"Inning {inning} (Has Multiple On Bases: {has_multiple_on_bases})")
        for play in plays:
            player = game.get_player(play.batter_id)
            st.text(f"- {player.name}: {play.pretty_description} => {play.obp_id}")

        st.divider()

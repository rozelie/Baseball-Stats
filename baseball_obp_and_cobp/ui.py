from typing import Any

import streamlit as st

from baseball_obp_and_cobp.game import Game, get_players_in_games
from baseball_obp_and_cobp.stats.ba import PlayerToBA
from baseball_obp_and_cobp.stats.obp import PlayerToOBPs


def set_streamlit_config() -> None:
    st.set_page_config(page_title="Baseball (C)OBP", layout="wide")


def get_selection(prompt: str, options: list[Any]) -> Any:
    return st.selectbox(prompt, options=options)


def display_error(error: str) -> None:
    st.error(error)


def display_legend():
    with st.expander("View Legend"):
        st.markdown(":green[GREEN]: On-Base | :orange[ORANGE]: At Bat | :red[RED]: N/A")


def display_innings(game: Game) -> None:
    header = f"Inning Play-by-Play For {game.team.pretty_name}"
    with st.expander(f"View {header}"):
        st.header(header)
        for inning, plays in game.inning_to_plays.items():
            has_an_on_base = "Yes" if game.inning_has_an_on_base(inning) else "No"
            st.markdown(f"**Inning {inning}** (Has An On Base: {has_an_on_base})")
            for play in plays:
                player = game.get_player(play.batter_id)
                st.markdown(f"- {player.name}: {play.pretty_description} => :{play.color}[{play.id}]")

            st.divider()


def display_player_obps(player_to_obps: PlayerToOBPs, player_to_ba: PlayerToBA, games: list[Game]) -> None:
    player_id_to_player = {p.id: p for p in get_players_in_games(games)}
    st.header(f"{games[0].team.pretty_name} Player (C)OBP")
    explanation_toggleable = len(games) > 1
    for player_id, (obps, explanation) in player_to_obps.items():
        player = player_id_to_player[player_id]
        if not player.plays:
            continue

        player_column, obp_column, cobp_column, sobp_column, ba_column = st.columns(5)
        with player_column:
            st.markdown(f"**{player.name}**")
        with obp_column:
            _display_metric("OBP", obps.obp, explanation.obp_explanation, toggleable=explanation_toggleable)
        with cobp_column:
            _display_metric("COBP", obps.cobp, explanation.cobp_explanation, toggleable=explanation_toggleable)
        with sobp_column:
            _display_metric("SOBP", obps.sobp, explanation.sobp_explanation, toggleable=explanation_toggleable)
        with ba_column:
            ba, ba_explanation = player_to_ba[player_id]
            _display_metric("BA", ba, ba_explanation.explanation, toggleable=explanation_toggleable)
        st.divider()


def display_footer() -> None:
    retrosheet_notice = " ".join(
        """\
        The information used here was obtained free of
        charge from and is copyrighted by Retrosheet.  Interested
        parties may contact Retrosheet at 20 Sunset Rd.,
        Newark, DE 19711.
    """.split()
    )
    st.caption(retrosheet_notice)


def display_game(games: list[Game], player_to_obps: PlayerToOBPs, player_to_ba: PlayerToBA) -> None:
    display_legend()
    if len(games) == 1:
        display_innings(games[0])
    display_player_obps(player_to_obps, player_to_ba, games)
    display_footer()


def _display_metric(name: str, value: float, explanation_lines: list[str], toggleable: bool) -> None:
    if toggleable:
        with st.expander(f"**{name} = {round(value, 3)}**"):
            for line in explanation_lines:
                st.markdown(line)
    else:
        for line in explanation_lines:
            st.markdown(line)

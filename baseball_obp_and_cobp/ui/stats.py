import pandas as pd
import streamlit as st

from baseball_obp_and_cobp.game import Game, get_players_in_games
from baseball_obp_and_cobp.player import Player
from baseball_obp_and_cobp.stats.aggregated import PlayerStats, PlayerToStats
from baseball_obp_and_cobp.ui.selectors import get_player_selection


def display_game(games: list[Game], player_to_stats: PlayerToStats, player_to_stats_df: pd.DataFrame) -> None:
    _display_stats(games, player_to_stats_df)
    _display_correlations()
    if len(games) == 1:
        _display_innings_toggle(games[0])
    _display_player_stats_explanations_toggle(games, player_to_stats)
    _display_footer()


def _display_stats(games: list[Game], player_to_stats_df: pd.DataFrame) -> None:
    st.header(f"{games[0].team.pretty_name} Stats")
    # ignore players without any at bats as they will have 0 values for all stats
    filtered_df = player_to_stats_df[player_to_stats_df["AB"] > 0]
    format_rules = {stat: "{:.3f}" for stat in ["OBP", "COBP", "SOBP", "BA", "SP", "OPS", "COPS"]}
    formatted_df = filtered_df.style.format(format_rules)
    st.dataframe(formatted_df, hide_index=True, use_container_width=True)


def _display_correlations() -> None:
    # TODO
    # import matplotlib.pyplot as plt
    # import seaborn as sns
    # st.header("Correlations")
    # fig, ax = plt.subplots()
    # sns.heatmap(player_to_stats_df.corr(), ax=ax)
    # st.write(fig)
    return None


def _display_innings_toggle(game: Game) -> None:
    header = f"Inning Play-by-Play For {game.team.pretty_name}"
    with st.expander(f"View {header}"):
        st.header(header)
        for inning, plays in game.inning_to_plays.items():
            has_an_on_base = "Yes" if game.inning_has_an_on_base(inning) else "No"
            st.markdown(f"**Inning {inning}** (Has An On Base: {has_an_on_base})")
            for play in plays:
                player = game.get_player(play.batter_id)
                if player:
                    st.markdown(f"- {player.name}: {play.pretty_description} => :{play.color}[{play.id}]")

            st.divider()


def _display_player_stats_explanations_toggle(games: list[Game], player_to_stats: PlayerToStats) -> None:
    with st.expander("View Player Stat Explanations"):
        player = get_player_selection(get_players_in_games(games))
        if player:
            st.markdown(":green[GREEN]: On-Base | :orange[ORANGE]: At Bat | :red[RED]: N/A")
            _display_player_stats_explanation_row(player, player_to_stats[player.id])


def _display_footer() -> None:
    retrosheet_notice = " ".join(
        """\
        The information used here was obtained free of
        charge from and is copyrighted by Retrosheet.  Interested
        parties may contact Retrosheet at 20 Sunset Rd.,
        Newark, DE 19711.
    """.split()
    )
    st.caption(retrosheet_notice)


def _display_player_stats_explanation_row(player: Player, stats: PlayerStats) -> None:
    obp_column, cobp_column, sobp_column, ba_column, sp_column, ops_column, cops_column = st.columns(7)
    with obp_column:
        _display_stat("OBP", stats.obp.obp, stats.obp.explanation)
    with cobp_column:
        _display_stat("COBP", stats.cobp.obp, stats.cobp.explanation)
    with sobp_column:
        _display_stat("SOBP", stats.sobp.obp, stats.sobp.explanation)
    with ba_column:
        _display_stat("BA", stats.ba.ba, stats.ba.explanation)
    with sp_column:
        _display_stat("SP", stats.sp.sp, stats.sp.explanation)
    with ops_column:
        _display_stat("OPS", stats.ops.ops, stats.ops.explanation)
    with cops_column:
        _display_stat("COPS", stats.cops.cops, stats.cops.explanation)
    st.divider()


def _display_stat(name: str, value: float, explanation_lines: list[str]) -> None:
    stat_formatted = f"**{name} = {round(value, 3)}**"
    st.markdown(stat_formatted)
    if explanation_lines:
        for line in explanation_lines:
            st.markdown(line)

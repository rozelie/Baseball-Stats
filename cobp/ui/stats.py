import pandas as pd
import streamlit as st

from cobp.game import Game, get_players_in_games
from cobp.stats.aggregated import PlayerStats, PlayerToStats, get_player_to_game_stat_df
from cobp.stats.summary import get_team_seasonal_summary_stats_df
from cobp.ui import download, formatters
from cobp.ui.selectors import get_correlation_method, get_player_selection, get_stat_to_correlate


def display_game(
    games: list[Game],
    player_to_stats: PlayerToStats,
    player_to_stats_df: pd.DataFrame,
) -> None:
    _display_stats(games, player_to_stats_df)
    if len(games) > 1:
        _display_summary_stats(games, player_to_stats)
        _display_correlations(games, player_to_stats)

    if len(games) == 1:
        _display_innings_toggle(games[0])

    _display_player_stats_explanations_toggle(games, player_to_stats)
    _display_footer()


def _display_stats(games: list[Game], player_to_stats_df: pd.DataFrame) -> None:
    team_pretty_name = games[0].team.pretty_name
    st.header(f"{team_pretty_name} Stats")
    # ignore players without any at bats as they will have 0 values for all stats
    filtered_df = player_to_stats_df[player_to_stats_df["AB"] > 0]
    formatted_df = filtered_df.style.format(formatters.get_stats_floats_format())
    formatted_df = formatted_df.apply(formatters.highlight_team_row, axis=1)
    download.download_df_button(filtered_df, f"{team_pretty_name}.csv")
    st.dataframe(formatted_df, hide_index=True, use_container_width=True)


def _display_summary_stats(games: list[Game], player_to_stats: PlayerToStats) -> None:
    st.header("Summary Stats")
    team_seasonal_summary_stats_df = get_team_seasonal_summary_stats_df(games, player_to_stats)
    formatted_df = team_seasonal_summary_stats_df.style.format(formatters.format_floats)
    st.dataframe(formatted_df, hide_index=True, use_container_width=True)


def _display_correlations(games: list[Game], player_to_stats: PlayerToStats) -> None:
    st.header("Correlations")
    if stat_to_correlate := get_stat_to_correlate():
        player_to_game_stat_df = get_player_to_game_stat_df(games, player_to_stats, stat_to_correlate.lower())
        player_to_game_stat_no_game_df = player_to_game_stat_df.drop(columns=["Game"])
        _display_correlations_df(stat_to_correlate, player_to_game_stat_no_game_df)
        _display_df_toggle(f"Player {stat_to_correlate} Per Game", player_to_game_stat_df)


def _display_correlations_df(stat_name: str, player_to_game_value_df: pd.DataFrame) -> None:
    st.header(f"{stat_name} Correlations")
    st.caption(f"None/empty {stat_name} values are excluded from correlations")
    st.caption("Correlations are calculated at the game-level (rather than the inning level)")
    correlation_method = get_correlation_method()
    correlation_df = player_to_game_value_df.corr(method=correlation_method)
    formatters.replace_same_player_correlations_with_dash(correlation_df)
    formatters.remove_none_cells(correlation_df)
    formatted_df = correlation_df.style.applymap(formatters.colorize_correlations)
    formatted_df = formatted_df.format(formatters.format_floats)
    st.dataframe(formatted_df, use_container_width=True)
    return None


def _display_df_toggle(header: str, df: pd.DataFrame) -> None:
    with st.expander(f"View {header}"):
        st.header(header)
        st.dataframe(df, use_container_width=True, hide_index=True)


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
            _display_player_stats_explanation_row(player_to_stats[player.id])


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


def _display_player_stats_explanation_row(stats: PlayerStats) -> None:
    obp_column, cobp_column, sobp_column, ba_column, sp_column, ops_column, cops_column = st.columns(7)
    with obp_column:
        _display_stat("OBP", stats.obp.value, stats.obp.explanation)
    with cobp_column:
        _display_stat("COBP", stats.cobp.value, stats.cobp.explanation)
    with sobp_column:
        _display_stat("SOBP", stats.sobp.value, stats.sobp.explanation)
    with ba_column:
        _display_stat("BA", stats.ba.value, stats.ba.explanation)
    with sp_column:
        _display_stat("SP", stats.sp.value, stats.sp.explanation)
    with ops_column:
        _display_stat("OPS", stats.ops.value, stats.ops.explanation)
    with cops_column:
        _display_stat("COPS", stats.cops.value, stats.cops.explanation)
    st.divider()


def _display_stat(name: str, value: float, explanation_lines: list[str]) -> None:
    stat_formatted = f"**{name} = {round(value, 3)}**"
    st.markdown(stat_formatted)
    if explanation_lines:
        for line in explanation_lines:
            st.markdown(line)

import numpy as np
import pandas as pd

FLOAT_COLUMNS = [
    "OBP",
    "COBP",
    "LOOP",
    "SOBP",
    "BA",
    "SP",
    "OPS",
    "COPS",
    "LOOPS",
    "SOPS",
]


def highlight_team_row(row: pd.Series) -> list[str] | None:
    player = row["Player"]
    if player == "Team":
        return ["background-color: #4f4f4f"] * len(row)
    return None


def get_stats_floats_format() -> dict[str, str]:
    return {stat: "{:.3f}" for stat in FLOAT_COLUMNS}


def colorize_correlations(cell_value: float | str) -> str | None:
    if isinstance(cell_value, str):
        return None

    if cell_value >= 0.75:
        return "background-color: #00C000"
    elif cell_value >= 0.5:
        return "background-color: #008000"
    elif cell_value >= 0.25:
        return "background-color: #006400"
    elif cell_value <= -0.75:
        return "background-color: #D70000"
    elif cell_value <= -0.5:
        return "background-color: #A00000"
    elif cell_value <= -0.25:
        return "background-color: #800000"
    return None


def replace_same_player_correlations_with_dash(df: pd.DataFrame) -> None:
    for i in range(len(df)):
        df.iat[i, i] = "-"


def format_floats(cell_value: float | str) -> str | None:
    if isinstance(cell_value, float):
        if np.isnan(cell_value):
            return None
        return "{:.2f}".format(cell_value)
    return cell_value


def remove_none_cells(df: pd.DataFrame) -> None:
    for i in range(len(df)):
        for j in range(len(df)):
            cell_value = df.iat[i, j]
            if cell_value is None:
                df.iat[i, j] = "-"
            if isinstance(cell_value, float) and np.isnan(cell_value):
                df.iat[i, j] = "-"

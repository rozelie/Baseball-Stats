from typing import Any

import pandas as pd
import streamlit as st


def download_df_button(df: pd.DataFrame, file_name: str) -> None:
    csv_df = _convert_df_to_csv(df)
    st.download_button(label="Download As CSV", data=csv_df, file_name=file_name, mime="text/csv", key="download-csv")


@st.cache_data
def _convert_df_to_csv(df: pd.DataFrame) -> Any:
    return df.to_csv(index=False).encode("utf-8")

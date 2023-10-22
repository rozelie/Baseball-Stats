import streamlit as st


def set_streamlit_config() -> None:
    st.set_page_config(page_title="COBP", layout="wide")


def display_header() -> None:
    st.title("COBP: Conditional On-Base Percentage")
    st.text("Select a year and team to view or download statistics aggregated by team and players.")
    st.text("Statistics include the basics (H, R, W, etc.) and custom statistics (COBP, SOBP, OPS, etc.).")


def display_error(error: str) -> None:
    st.error(error)

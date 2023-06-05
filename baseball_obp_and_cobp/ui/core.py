import streamlit as st


def set_streamlit_config() -> None:
    st.set_page_config(page_title="Baseball (C)OBP", layout="wide")


def display_error(error: str) -> None:
    st.error(error)

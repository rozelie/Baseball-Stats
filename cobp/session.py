"""Handles a user's browsing session and its state."""
from enum import Enum
from typing import Any

import streamlit as st


class StateKey(Enum):
    REFRESH_NEEDED = "refresh_needed"


def get_state(state_key: StateKey) -> Any:
    return st.session_state.get(state_key.value)


def set_state(state_key: StateKey, value: Any) -> None:
    st.session_state[state_key.value] = value

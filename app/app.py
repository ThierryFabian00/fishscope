"""Ponto de entrada e navegação pública do FishScope."""

import streamlit as st

from src.i18n import (
    LANGUAGE_WIDGET_KEY,
    SUPPORTED_LANGUAGES,
    initialize_language,
    language_name,
    persist_selected_language,
    t,
)

st.set_page_config(
    page_title="FishScope",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_language()
st.sidebar.selectbox(
    t("language_selector"),
    SUPPORTED_LANGUAGES,
    format_func=language_name,
    key=LANGUAGE_WIDGET_KEY,
    on_change=persist_selected_language,
)

paginas = st.navigation(
    [
        st.Page("pages/home.py", title=t("home"), default=True),
        st.Page("pages/1_Explorar.py", title=t("explore")),
        st.Page("pages/compare.py", title=t("compare")),
        st.Page("pages/about.py", title=t("about")),
    ],
    position="sidebar",
)

paginas.run()

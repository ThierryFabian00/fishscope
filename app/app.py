"""Ponto de entrada e navegação pública do FishScope."""

import sys
from pathlib import Path

import streamlit as st

# O Streamlit Cloud executa este arquivo a partir de ``app/`` e não inclui
# necessariamente a raiz do repositório no caminho de importação.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.i18n import (  # noqa: E402
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

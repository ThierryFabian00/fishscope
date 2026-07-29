"""Ponto de entrada e navegação pública do FishScope."""

import streamlit as st

st.set_page_config(
    page_title="FishScope",
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded",
)

paginas = st.navigation(
    [
        st.Page("pages/home.py", title="Início", default=True),
        st.Page("pages/1_Explorar.py", title="Explorar"),
        st.Page("pages/compare.py", title="Comparar"),
        st.Page("pages/about.py", title="Sobre"),
    ],
    position="sidebar",
)

paginas.run()

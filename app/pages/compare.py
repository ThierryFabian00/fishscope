"""Entrada pública para a comparação já disponível no dashboard."""

import streamlit as st

from src.i18n import t

st.title(t("compare"))
st.write(t("compare_intro"))
st.caption(t("compare_note"))

if st.button(
    t("open_comparison"),
    type="primary",
    icon=":material/compare_arrows:",
):
    st.switch_page("pages/1_Explorar.py")

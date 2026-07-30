"""Apresentação breve do projeto até a implementação completa da página Sobre."""

import streamlit as st

from src.i18n import t

st.title(t("about"))
st.subheader(t("app_name"))
st.write(t("about_intro"))
st.caption(t("in_development"))

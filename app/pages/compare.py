"""Entrada pública para a comparação já disponível no dashboard."""

import streamlit as st

st.title("Comparar")
st.write(
    "A comparação entre países permanece disponível na aba **Comparação** "
    "da página Explorar."
)
st.caption(
    "Essa organização preserva a análise existente enquanto a experiência "
    "de comparação é preparada para funcionar como uma página independente."
)

if st.button(
    "Abrir comparação em Explorar",
    type="primary",
    icon=":material/compare_arrows:",
):
    st.switch_page("pages/1_Explorar.py")

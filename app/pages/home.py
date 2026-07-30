"""Página inicial pública do FishScope."""

from html import escape

import streamlit as st

from src.i18n import t


def aplicar_estilo() -> None:
    """Aplica somente os ajustes visuais essenciais da página inicial."""
    st.html(
        """
        <style>
        :root { --ink: #17211d; --muted: #5f6f67; --line: #d7dfdb; }
        .stApp { background: #f5f7f6; color: var(--ink); }
        .block-container {
            max-width: 1080px;
            padding-top: 5rem;
            padding-bottom: 3rem;
        }
        .home-intro { max-width: 760px; margin-bottom: 1.25rem; }
        .home-intro h1 {
            font-size: clamp(2.3rem, 7vw, 4.4rem);
            line-height: 1;
            margin-bottom: 1.2rem;
        }
        .home-intro h2 {
            font-size: clamp(1.45rem, 3vw, 2rem);
            line-height: 1.25;
            margin-bottom: .8rem;
        }
        .home-intro p { color: var(--muted); font-size: 1.08rem; line-height: 1.7; }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: #ffffff;
            border-color: var(--line);
            min-height: 150px;
        }
        [data-testid="stAppDeployButton"], [data-testid="stMainMenu"],
        [data-testid="stStatusWidget"] { display: none; }
        @media (max-width: 760px) {
            .block-container { padding: 3.5rem 1rem 2rem; }
        }
        </style>
        """
    )


aplicar_estilo()

st.html(
    f"""
    <section class="home-intro">
      <h1>{escape(t("app_name"))}</h1>
      <h2>{escape(t("hero_title"))}</h2>
      <p>{escape(t("hero_description"))}</p>
    </section>
    """
)

if st.button(
    t("start_exploring"),
    type="primary",
    icon=":material/arrow_forward:",
):
    st.switch_page("pages/1_Explorar.py")

st.markdown(f"## {t('main_features')}")

coluna_mapa, coluna_tempo, coluna_qualidade = st.columns(3)
with coluna_mapa:
    with st.container(border=True):
        st.subheader(t("occurrence_map"))
        st.write(t("occurrence_map_description"))

with coluna_tempo:
    with st.container(border=True):
        st.subheader(t("temporal_analysis"))
        st.write(t("temporal_analysis_description"))

with coluna_qualidade:
    with st.container(border=True):
        st.subheader(t("data_quality"))
        st.write(t("data_quality_description"))

st.divider()
st.caption(t("data_source"))

"""Página inicial pública do FishScope."""

import streamlit as st


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
    """
    <section class="home-intro">
      <h1>FishScope</h1>
      <h2>Explore registros de ocorrência de peixes ao redor do mundo.</h2>
      <p>
        Visualize espécies, distribuições geográficas e registros ao longo do
        tempo utilizando dados públicos do GBIF.
      </p>
    </section>
    """
)

if st.button(
    "Começar a explorar",
    type="primary",
    icon=":material/arrow_forward:",
):
    st.switch_page("pages/1_Explorar.py")

st.markdown("## Principais recursos")

coluna_mapa, coluna_tempo, coluna_qualidade = st.columns(3)
with coluna_mapa:
    with st.container(border=True):
        st.subheader("Mapa de ocorrências")
        st.write("Visualize a distribuição geográfica dos registros.")

with coluna_tempo:
    with st.container(border=True):
        st.subheader("Análise temporal")
        st.write("Explore como os registros se distribuem ao longo dos anos.")

with coluna_qualidade:
    with st.container(border=True):
        st.subheader("Qualidade dos dados")
        st.write("Entenda a cobertura e as limitações das informações analisadas.")

st.divider()
st.caption("Dados fornecidos pelo [GBIF](https://www.gbif.org/).")

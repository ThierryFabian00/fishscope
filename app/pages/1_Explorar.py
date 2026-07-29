import colorsys
import hashlib
import logging
import sys
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
import plotly.express as px
import psycopg
import pydeck as pdk
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (  # noqa: E402
    APP_CAPTION,
    APP_NAME,
    LIMITE_PONTOS_MAPA,
    LIMITE_RESULTADOS_SQL,
    PAIS_PADRAO,
    PROJECT_SLUG,
)
from src.dashboard_data import (  # noqa: E402
    ResultadoFonte,
    calcular_indicadores,
    carregar_dados_dashboard,
    catalogo_taxonomico,
    comparar_paises,
    distribuicao_origem,
    distribuicao_tipo,
    filtrar_ocorrencias,
    frequencia_alertas,
    indicadores_qualidade,
    preparar_pontos_mapa,
    ranking_especies,
    serie_anual,
    serie_temporal,
    serie_temporal_especies,
)
from src.database import ConfiguracaoBanco  # noqa: E402
from src.filter_basin import ARQUIVO_LIMITE  # noqa: E402
from src.gbif_client import ErroGBIF  # noqa: E402
from src.report import gerar_relatorio_pdf  # noqa: E402
from src.security import mensagem_erro_segura  # noqa: E402
from src.services.country_service import listar_paises, obter_pais  # noqa: E402
from src.sync_data import (  # noqa: E402
    ProgressoSincronizacao,
    sincronizar_dados_pais,
)

CONFIGURACAO_BANCO = ConfiguracaoBanco.do_ambiente()
LOGGER = logging.getLogger(__name__)

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🐟",
    layout="wide",
    initial_sidebar_state="expanded",
)

CORES_ORIGEM = {
    "NATIVE": [15, 118, 110, 190],
    "INTRODUCED": [194, 65, 59, 200],
    "CONFLICTING": [217, 119, 6, 200],
    "UNKNOWN": [100, 116, 139, 160],
}
CORES_PLOTLY = {
    "NATIVE": "#0f766e",
    "INTRODUCED": "#c2413b",
    "CONFLICTING": "#d97706",
    "UNKNOWN": "#64748b",
}
ROTULOS_ORIGEM = {
    "NATIVE": "Nativa",
    "INTRODUCED": "Introduzida",
    "CONFLICTING": "Conflitante",
    "UNKNOWN": "Desconhecida",
}
ROTULOS_ESTADO = {
    "Parana": "Paraná",
    "Sao Paulo": "São Paulo",
    "Goias": "Goiás",
    "Nao informado": "Não informado",
}


def aplicar_estilo() -> None:
    st.html(
        """
        <style>
        :root { --ink: #17211d; --muted: #5f6f67; --line: #d7dfdb; }
        * { letter-spacing: 0 !important; }
        .stApp { background: #f5f7f6; color: var(--ink); }
        .block-container { max-width: 1480px; padding-top: 3.8rem; padding-bottom: 3rem; }
        h1 { font-size: 2.15rem !important; line-height: 1.12 !important; margin-bottom: .2rem !important; }
        h2 { font-size: 1.25rem !important; }
        h3 { font-size: 1.05rem !important; }
        [data-testid="stSidebar"] { background: #edf2ef; border-right: 1px solid var(--line); }
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid var(--line);
            border-left: 4px solid #0f766e;
            border-radius: 6px;
            min-height: 106px;
            padding: 1rem 1.05rem;
        }
        [data-testid="stMetricLabel"] { color: var(--muted); }
        [data-testid="stMetricValue"] { color: var(--ink); font-size: 1.4rem; }
        .source-row { display: flex; align-items: center; gap: .55rem; color: var(--muted); margin: .2rem 0 1.1rem; }
        .source-badge {
            display: inline-flex; align-items: center; min-height: 26px;
            padding: 2px 9px; border: 1px solid #9bb8aa; border-radius: 999px;
            background: #e4f0ea; color: #245b43; font-size: .78rem; font-weight: 650;
        }
        .stTabs [data-baseweb="tab-list"] { gap: .3rem; border-bottom: 1px solid var(--line); }
        .stTabs [data-baseweb="tab"] { border-radius: 4px 4px 0 0; padding: .65rem 1rem; }
        [data-testid="stDataFrame"], [data-testid="stPlotlyChart"], [data-testid="stPydeckChart"] {
            background: #ffffff; border: 1px solid var(--line); border-radius: 6px;
        }
        .quality-note {
            border-left: 4px solid #d97706; background: #fff8eb; padding: .85rem 1rem;
            border-radius: 4px; color: #5f481b; margin-top: .75rem;
        }
        button { border-radius: 4px !important; }
        [data-testid="stAppDeployButton"], [data-testid="stMainMenu"], [data-testid="stStatusWidget"] { display: none; }
        @media (max-width: 760px) {
            .block-container { padding: 3.5rem .8rem 2rem; }
            h1 { font-size: 1.7rem !important; }
            [data-testid="stMetric"] { min-height: 92px; }
            .source-row { align-items: flex-start; flex-direction: column; }
        }
        </style>
        """
    )


@st.cache_data(ttl=300, max_entries=12, show_spinner=False)
def obter_dados(schema: str, codigo_pais: str) -> ResultadoFonte:
    return carregar_dados_dashboard(
        CONFIGURACAO_BANCO.database_url, schema, codigo_pais=codigo_pais
    )


@st.cache_data(max_entries=2, show_spinner=False)
def obter_limite_geojson() -> dict[str, Any] | None:
    if not ARQUIVO_LIMITE.exists():
        return None
    limite = gpd.read_file(ARQUIVO_LIMITE, engine="fiona").to_crs("EPSG:4326")
    limite["geometry"] = limite.geometry.simplify(0.01, preserve_topology=True)
    return limite.__geo_interface__


@st.cache_data(ttl=300, max_entries=20, show_spinner=False)
def obter_relatorio_pdf(
    dados: pd.DataFrame,
    pais_nome: str,
    pais_codigo: str,
    fonte: str,
    filtros: tuple[tuple[str, str], ...],
) -> bytes:
    return gerar_relatorio_pdf(
        dados,
        pais_nome=pais_nome,
        pais_codigo=pais_codigo,
        fonte=fonte,
        filtros=dict(filtros),
    )


def formatar_numero(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def rotulo_estado(valor: str) -> str:
    return ROTULOS_ESTADO.get(valor, valor)


def layout_grafico(figura: Any, altura: int = 390) -> Any:
    figura.update_layout(
        height=altura,
        margin=dict(l=16, r=16, t=52, b=20),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#17211d", size=12),
        title_font=dict(size=16),
        hoverlabel=dict(bgcolor="#ffffff", font_size=12),
    )
    figura.update_xaxes(showgrid=True, gridcolor="#e8eeeb", zeroline=False)
    figura.update_yaxes(showgrid=False, zeroline=False)
    return figura


def cor_especie(chave: Any) -> list[int]:
    resumo = hashlib.sha256(str(chave).encode("utf-8")).digest()
    matiz = int.from_bytes(resumo[:2], "big") / 65535
    vermelho, verde, azul = colorsys.hsv_to_rgb(matiz, 0.68, 0.78)
    return [int(vermelho * 255), int(verde * 255), int(azul * 255), 190]


def criar_mapa(
    dados: pd.DataFrame,
    exibir_limite: bool = True,
    modo: str = "Pontos por espécie",
) -> pdk.Deck | None:
    pontos, agregado = preparar_pontos_mapa(dados)
    if pontos.empty:
        return None
    modos = {"Pontos por espécie", "Mapa de calor", "Agrupamento espacial"}
    if modo not in modos:
        raise ValueError(f"Modo de mapa inválido: {modo}")
    pontos["point_color"] = (
        [[15, 118, 110, 190]] * len(pontos)
        if agregado
        else pontos["species_key"].map(cor_especie)
    )
    pontos["origin_display"] = pontos["origin_status"].map(ROTULOS_ORIGEM)
    pontos["state_display"] = pontos["state_normalized"].map(rotulo_estado)
    pontos["point_color"] = pontos["point_color"].apply(
        lambda cor: cor if isinstance(cor, list) else CORES_ORIGEM["UNKNOWN"]
    )
    pontos["point_radius"] = (
        2600 * (1 + pontos["map_occurrence_count"].pow(0.5).clip(upper=5))
        if agregado
        else 2600
    )
    camadas = []
    limite = obter_limite_geojson() if exibir_limite else None
    if limite:
        camadas.append(
            pdk.Layer(
                "GeoJsonLayer",
                limite,
                stroked=True,
                filled=True,
                get_fill_color=[15, 118, 110, 16],
                get_line_color=[39, 73, 58, 180],
                line_width_min_pixels=1,
                pickable=False,
            )
        )
    if modo == "Pontos por espécie":
        camadas.append(
            pdk.Layer(
                "ScatterplotLayer",
                pontos,
                get_position="[decimal_longitude, decimal_latitude]",
                get_fill_color="point_color",
                get_radius="point_radius",
                radius_min_pixels=3,
                radius_max_pixels=11,
                stroked=True,
                get_line_color=[255, 255, 255, 130],
                line_width_min_pixels=0.4,
                opacity=0.75,
                pickable=True,
                auto_highlight=True,
            )
        )
    elif modo == "Mapa de calor":
        camadas.append(
            pdk.Layer(
                "HeatmapLayer",
                pontos,
                get_position="[decimal_longitude, decimal_latitude]",
                get_weight="map_occurrence_count",
                radius_pixels=45,
                intensity=1,
                threshold=0.03,
            )
        )
    else:
        tipo_camada = "ColumnLayer" if agregado else "HexagonLayer"
        argumentos_camada = {
            "get_position": "[decimal_longitude, decimal_latitude]",
            "radius": 12000,
            "elevation_scale": 20,
            "extruded": True,
            "pickable": True,
            "auto_highlight": True,
            "coverage": 0.88,
        }
        if agregado:
            argumentos_camada.update(
                get_elevation="map_occurrence_count",
                get_fill_color=[15, 118, 110, 190],
            )
        else:
            argumentos_camada["elevation_range"] = [0, 1000]
        camadas.append(pdk.Layer(tipo_camada, pontos, **argumentos_camada))
    zoom = 5.0 if len(pontos) >= 50 else 6.2
    vista = pdk.ViewState(
        latitude=float(pontos["decimal_latitude"].mean()),
        longitude=float(pontos["decimal_longitude"].mean()),
        zoom=zoom,
        pitch=35 if modo == "Agrupamento espacial" else 0,
    )
    return pdk.Deck(
        layers=camadas,
        initial_view_state=vista,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip=(
            {
                "html": "<b>{canonical_name}</b><br/>{state_display}<br/>{event_year} · {basis_of_record}<br/>GBIF {gbif_id}",
                "style": {"backgroundColor": "#17211d", "color": "white"},
            }
            if modo == "Pontos por espécie" and not agregado
            else {
                "html": (
                    "<b>{map_occurrence_count} ocorrências agregadas</b><br/>"
                    "{map_species_count} espécies"
                ),
                "style": {"backgroundColor": "#17211d", "color": "white"},
            }
            if agregado
            else {
                "html": "<b>{elevationValue} ocorrências próximas</b>",
                "style": {"backgroundColor": "#17211d", "color": "white"},
            }
        ),
    )


aplicar_estilo()

paises_disponiveis = listar_paises()
nomes_por_codigo = {pais.codigo_iso: pais.nome for pais in paises_disponiveis}
codigos_paises = [pais.codigo_iso for pais in paises_disponiveis]
with st.sidebar:
    st.markdown(f"### {APP_NAME}")
    st.header("Filtros")
    codigo_pais = st.selectbox(
        "País",
        codigos_paises,
        index=codigos_paises.index(PAIS_PADRAO),
        format_func=lambda codigo: f"{nomes_por_codigo[codigo]} ({codigo})",
    )
    forcar_atualizacao = st.button(
        "Atualizar dados do GBIF",
        icon=":material/refresh:",
        width="stretch",
        disabled=CONFIGURACAO_BANCO.database_write_url is None,
        help=(
            "Defina DATABASE_WRITE_URL para habilitar atualizações."
            if CONFIGURACAO_BANCO.database_write_url is None
            else None
        ),
    )
    if CONFIGURACAO_BANCO.database_write_url is None:
        st.caption("Atualização desativada: credencial de escrita não configurada.")

pais = obter_pais(codigo_pais)
schema = CONFIGURACAO_BANCO.schema
sincronizacao = None
widget_progresso: dict[str, Any] = {"valor": None}


def atualizar_progresso(evento: ProgressoSincronizacao) -> None:
    valor = (
        min(evento.coletados / evento.total, 1.0)
        if evento.total
        else (1.0 if evento.etapa == "concluido" else 0.0)
    )
    if widget_progresso["valor"] is None:
        widget_progresso["valor"] = st.sidebar.progress(valor, text=evento.mensagem)
    else:
        widget_progresso["valor"].progress(valor, text=evento.mensagem)


database_write_url = CONFIGURACAO_BANCO.database_write_url
if forcar_atualizacao and database_write_url:
    try:
        sincronizacao = sincronizar_dados_pais(
            database_write_url,
            schema,
            pais.codigo_iso,
            forcar_atualizacao=forcar_atualizacao,
            callback=atualizar_progresso,
        )
        if sincronizacao.fonte == "GBIF":
            obter_dados.clear()
            st.sidebar.success(
                f"Atualização concluída: {sincronizacao.registros_salvos:,} registros."
            )
    except (ErroGBIF, psycopg.Error, ValueError) as erro:
        mensagem = mensagem_erro_segura(erro, "Falha inesperada na atualização.")
        LOGGER.error("Falha controlada na atualização: %s", mensagem)
        st.sidebar.error(f"Não foi possível atualizar os dados: {mensagem}")
    finally:
        if widget_progresso["valor"] is not None:
            widget_progresso["valor"].empty()
elif forcar_atualizacao:
    st.sidebar.warning(
        "Atualização indisponível: defina DATABASE_WRITE_URL com uma credencial "
        "PostgreSQL de escrita. A consulta normal usa apenas DATABASE_URL."
    )

try:
    resultado = obter_dados(schema, pais.codigo_iso)
except (FileNotFoundError, ValueError) as erro:
    mensagem = mensagem_erro_segura(erro, "A fonte de dados não está disponível.")
    LOGGER.error("Falha controlada ao carregar dados: %s", mensagem)
    st.error(f"Dados indisponíveis: {mensagem}")
    st.stop()

dados = resultado.dados

with st.sidebar:
    catalogo_especies = (
        dados[["species_key", "canonical_name"]]
        .dropna()
        .drop_duplicates("species_key")
        .sort_values(["canonical_name", "species_key"])
    )
    nomes_especies = dict(
        zip(
            catalogo_especies["species_key"],
            catalogo_especies["canonical_name"],
            strict=True,
        )
    )
    especies = st.multiselect(
        "Espécies",
        catalogo_especies["species_key"].tolist(),
        placeholder="Todas as espécies",
        format_func=lambda chave: nomes_especies.get(chave, chave),
    )
    origens_disponiveis = sorted(dados["origin_status"].dropna().unique())
    origens = st.multiselect(
        "Origem",
        origens_disponiveis,
        placeholder="Todas as classificações",
        format_func=lambda valor: ROTULOS_ORIGEM.get(valor, valor),
    )
    anos = dados["event_year"].dropna().astype(int)
    intervalo_anos = None
    if not anos.empty:
        limites_anos = (int(anos.min()), int(anos.max()))
        intervalo_anos = st.slider(
            "Período",
            min_value=limites_anos[0],
            max_value=limites_anos[1],
            value=limites_anos,
        )
    tipos_disponiveis = sorted(dados["basis_of_record"].dropna().unique())
    tipos = st.multiselect(
        "Tipo de registro",
        tipos_disponiveis,
        placeholder="Todos os tipos",
    )
    estados_disponiveis = sorted(dados["state_normalized"].dropna().unique())
    estados = st.multiselect(
        "Unidade administrativa",
        estados_disponiveis,
        placeholder="Todas as unidades",
        format_func=rotulo_estado,
    )
    st.divider()
    st.caption("GBIF · DHN250/IBGE · Catalogue of Life")

filtrados = filtrar_ocorrencias(
    dados,
    chaves_especies=especies,
    origens=origens,
    intervalo_anos=intervalo_anos,
    tipos=tipos,
    estados=estados,
)

descricao_pais = (
    "Ocorrências publicadas na porção brasileira da Região Hidrográfica do Paraná"
    if pais.codigo_iso == PAIS_PADRAO
    else f"País selecionado: {pais.nome} ({pais.codigo_iso})"
)
st.title(APP_NAME)
st.caption(APP_CAPTION)
st.html(
    f"""
    <div class="source-row">
      <span>{descricao_pais}</span>
      <span class="source-badge">Fonte ativa: {resultado.fonte}</span>
    </div>
    """
)
st.caption(f"País selecionado: {pais.nome} ({pais.codigo_iso})")
if resultado.aviso:
    st.warning(resultado.aviso)

indicadores = calcular_indicadores(filtrados)
ultima_atualizacao = (
    pd.Timestamp(resultado.resumo_importacao.atualizado_em).strftime("%d/%m/%Y")
    if resultado.resumo_importacao
    and resultado.resumo_importacao.atualizado_em is not None
    else "Não disponível"
)
colunas_metricas = st.columns(5)
metricas = [
    ("Ocorrências", formatar_numero(indicadores["occurrences"])),
    ("Espécies", formatar_numero(indicadores["species"])),
    ("Período", indicadores["period"]),
    ("Última atualização", ultima_atualizacao),
    ("Fonte", resultado.fonte),
]
for coluna, (rotulo, valor) in zip(colunas_metricas, metricas, strict=True):
    coluna.metric(rotulo, valor)

if filtrados.empty:
    st.info(
        f"Nenhuma ocorrência disponível para {pais.nome} ({pais.codigo_iso}) "
        "com os filtros selecionados."
    )
    st.stop()

(
    aba_visao,
    aba_mapa,
    aba_temporal,
    aba_especies,
    aba_comparacao,
    aba_relatorio,
    aba_qualidade,
    aba_dados,
) = st.tabs(
    [
        "Visão geral",
        "Mapa",
        "Temporal",
        "Espécies",
        "Comparação",
        "Relatório",
        "Qualidade",
        "Dados",
    ]
)

with aba_visao:
    ranking = ranking_especies(filtrados)
    origens_tabela = distribuicao_origem(filtrados)
    ranking["origin_label"] = ranking["origin_status"].map(ROTULOS_ORIGEM)
    origens_tabela["origin_label"] = origens_tabela["origin_status"].map(ROTULOS_ORIGEM)
    coluna_ranking, coluna_origem = st.columns([1.65, 1])
    with coluna_ranking:
        ranking_plot = ranking.sort_values("occurrence_count")
        figura = px.bar(
            ranking_plot,
            x="occurrence_count",
            y="canonical_name",
            color="origin_label",
            orientation="h",
            color_discrete_map={
                ROTULOS_ORIGEM[chave]: cor for chave, cor in CORES_PLOTLY.items()
            },
            labels={
                "occurrence_count": "Ocorrências",
                "canonical_name": "",
                "origin_label": "Origem",
            },
            title="Espécies mais registradas",
        )
        figura.update_layout(legend_title_text="Origem")
        st.plotly_chart(
            layout_grafico(figura, 470),
            width="stretch",
            config={"displayModeBar": False},
        )
    with coluna_origem:
        figura = px.bar(
            origens_tabela,
            x="origin_label",
            y="species_count",
            color="origin_label",
            color_discrete_map={
                ROTULOS_ORIGEM[chave]: cor for chave, cor in CORES_PLOTLY.items()
            },
            labels={"origin_label": "Origem", "species_count": "Espécies"},
            title="Espécies por origem",
        )
        figura.update_layout(showlegend=False)
        st.plotly_chart(
            layout_grafico(figura, 470),
            width="stretch",
            config={"displayModeBar": False},
        )

with aba_mapa:
    modo_mapa = st.radio(
        "Visualização do mapa",
        ["Pontos por espécie", "Mapa de calor", "Agrupamento espacial"],
        horizontal=True,
    )
    mapa = criar_mapa(
        filtrados,
        exibir_limite=pais.codigo_iso == PAIS_PADRAO,
        modo=modo_mapa,
    )
    registros_mapa = filtrados.dropna(subset=["decimal_latitude", "decimal_longitude"])
    if len(registros_mapa) > LIMITE_PONTOS_MAPA:
        st.caption(
            f"Para manter o mapa responsivo, {formatar_numero(len(registros_mapa))} "
            f"registros foram agregados em até {formatar_numero(LIMITE_PONTOS_MAPA)} "
            "células espaciais."
        )
    if mapa:
        st.pydeck_chart(mapa, width="stretch", height=610)
    else:
        st.info("O recorte atual não possui coordenadas válidas.")

    registros_detalhe = registros_mapa.head(LIMITE_RESULTADOS_SQL)
    if len(registros_mapa) > len(registros_detalhe):
        st.caption(
            "O seletor de detalhes mostra as primeiras "
            f"{formatar_numero(len(registros_detalhe))} ocorrências do recorte."
        )
    ids_mapa = registros_detalhe["gbif_id"].tolist()
    nomes_ids = registros_detalhe.set_index("gbif_id")["canonical_name"].to_dict()
    ocorrencia_selecionada = st.selectbox(
        "Detalhes de uma ocorrência",
        [None, *ids_mapa],
        key=f"ocorrencia_mapa_{pais.codigo_iso}",
        format_func=lambda chave: (
            "Selecione uma ocorrência"
            if chave is None
            else f"GBIF {chave} — {nomes_ids.get(chave, 'Espécie não informada')}"
        ),
    )
    if ocorrencia_selecionada is not None:
        detalhe = registros_detalhe.loc[
            registros_detalhe["gbif_id"].eq(ocorrencia_selecionada),
            [
                "gbif_id",
                "canonical_name",
                "family",
                "order_name",
                "event_date",
                "basis_of_record",
                "state_normalized",
                "locality",
                "decimal_latitude",
                "decimal_longitude",
            ],
        ].rename(
            columns={
                "gbif_id": "GBIF ID",
                "canonical_name": "Espécie",
                "family": "Família",
                "order_name": "Ordem",
                "event_date": "Data",
                "basis_of_record": "Tipo",
                "state_normalized": "Unidade",
                "locality": "Localidade",
                "decimal_latitude": "Latitude",
                "decimal_longitude": "Longitude",
            }
        )
        st.dataframe(detalhe, hide_index=True, width="stretch")

    tipo_tabela = distribuicao_tipo(filtrados).head(10)
    estado_tabela = (
        filtrados["state_normalized"]
        .value_counts()
        .rename_axis("state")
        .reset_index(name="occurrence_count")
        .head(10)
    )
    estado_tabela["state_display"] = estado_tabela["state"].map(rotulo_estado)
    coluna_tipo, coluna_estado = st.columns(2)
    with coluna_tipo:
        figura = px.bar(
            tipo_tabela.sort_values("occurrence_count"),
            x="occurrence_count",
            y="basis_of_record",
            orientation="h",
            labels={"occurrence_count": "Ocorrências", "basis_of_record": ""},
            title="Tipo de registro",
            color_discrete_sequence=["#7c3f58"],
        )
        st.plotly_chart(
            layout_grafico(figura),
            width="stretch",
            config={"displayModeBar": False},
        )
    with coluna_estado:
        figura = px.bar(
            estado_tabela.sort_values("occurrence_count"),
            x="occurrence_count",
            y="state_display",
            orientation="h",
            labels={"occurrence_count": "Ocorrências", "state_display": ""},
            title="Unidade administrativa informada",
            color_discrete_sequence=["#4f772d"],
        )
        st.plotly_chart(
            layout_grafico(figura),
            width="stretch",
            config={"displayModeBar": False},
        )

with aba_temporal:
    anual = serie_anual(filtrados)
    mensal = serie_temporal(filtrados)
    coluna_anual, coluna_mensal = st.columns(2)
    with coluna_anual:
        figura = px.bar(
            anual,
            x="event_year",
            y="occurrence_count",
            labels={"event_year": "Ano", "occurrence_count": "Ocorrências"},
            title="Ocorrências por ano",
            color_discrete_sequence=["#0f766e"],
        )
        st.plotly_chart(
            layout_grafico(figura, 400),
            width="stretch",
            config={"displayModeBar": False},
        )
    with coluna_mensal:
        figura = px.line(
            mensal,
            x="period",
            y="occurrence_count",
            labels={"period": "Mês", "occurrence_count": "Ocorrências"},
            title="Ocorrências por mês",
        )
        figura.update_traces(line_color="#2563eb")
        st.plotly_chart(
            layout_grafico(figura, 400),
            width="stretch",
            config={"displayModeBar": False},
        )

    comparacao = serie_temporal_especies(filtrados)
    figura = px.line(
        comparacao,
        x="event_year",
        y="occurrence_count",
        color="canonical_name",
        markers=True,
        labels={
            "event_year": "Ano",
            "occurrence_count": "Ocorrências",
            "canonical_name": "Espécie",
        },
        title="Comparação temporal entre as espécies mais registradas",
    )
    st.plotly_chart(
        layout_grafico(figura, 430),
        width="stretch",
        config={"displayModeBar": False},
    )

with aba_especies:
    st.subheader("Catálogo taxonômico")
    busca_taxonomica = st.text_input(
        "Buscar por nome científico",
        placeholder="Digite gênero ou espécie",
        key="busca_taxonomica",
    )
    taxonomia = catalogo_taxonomico(filtrados)
    if busca_taxonomica.strip():
        taxonomia = taxonomia.loc[
            taxonomia["canonical_name"]
            .fillna("")
            .str.contains(busca_taxonomica.strip(), case=False, regex=False)
        ]
    taxonomia["origin_status"] = taxonomia["origin_status"].map(ROTULOS_ORIGEM)
    st.dataframe(
        taxonomia.rename(
            columns={
                "species_key": "Chave taxonômica",
                "canonical_name": "Nome científico",
                "family": "Família",
                "order_name": "Ordem",
                "occurrence_count": "Ocorrências",
                "origin_status": "Origem",
                "iucn_category": "IUCN",
            }
        ),
        hide_index=True,
        width="stretch",
        height=520,
    )

with aba_comparacao:
    st.subheader("Comparação entre países")
    coluna_pais_a, coluna_pais_b = st.columns(2)
    with coluna_pais_a:
        codigo_comparacao_a = st.selectbox(
            "Primeiro país",
            codigos_paises,
            index=codigos_paises.index("BR"),
            format_func=lambda codigo: f"{nomes_por_codigo[codigo]} ({codigo})",
            key="pais_comparacao_a",
        )
    with coluna_pais_b:
        codigo_comparacao_b = st.selectbox(
            "Segundo país",
            codigos_paises,
            index=codigos_paises.index("CH"),
            format_func=lambda codigo: f"{nomes_por_codigo[codigo]} ({codigo})",
            key="pais_comparacao_b",
        )

    if codigo_comparacao_a == codigo_comparacao_b:
        st.warning("Selecione dois países diferentes para realizar a comparação.")
    else:
        fonte_a = obter_dados(schema, codigo_comparacao_a)
        fonte_b = obter_dados(schema, codigo_comparacao_b)
        dados_a = fonte_a.dados
        dados_b = fonte_b.dados
        if dados_a.empty or dados_b.empty:
            sem_dados = [
                nomes_por_codigo[codigo]
                for codigo, tabela in (
                    (codigo_comparacao_a, dados_a),
                    (codigo_comparacao_b, dados_b),
                )
                if tabela.empty
            ]
            st.warning(
                "Não há dados armazenados para: "
                f"{', '.join(sem_dados)}. Selecione o país no filtro principal "
                "para executar sua primeira atualização."
            )
        else:
            anos_comparacao = pd.concat(
                [dados_a["event_year"], dados_b["event_year"]]
            ).dropna()
            if not anos_comparacao.empty:
                limites_comparacao = (
                    int(anos_comparacao.min()),
                    int(anos_comparacao.max()),
                )
                intervalo_comparacao = st.slider(
                    "Período da comparação",
                    min_value=limites_comparacao[0],
                    max_value=limites_comparacao[1],
                    value=limites_comparacao,
                    key="periodo_comparacao",
                )
                dados_a = filtrar_ocorrencias(
                    dados_a, intervalo_anos=intervalo_comparacao
                )
                dados_b = filtrar_ocorrencias(
                    dados_b, intervalo_anos=intervalo_comparacao
                )

            comparacao = comparar_paises(
                dados_a,
                codigo_comparacao_a,
                nomes_por_codigo[codigo_comparacao_a],
                dados_b,
                codigo_comparacao_b,
                nomes_por_codigo[codigo_comparacao_b],
            )
            resumo_a = comparacao.resumo.iloc[0]
            resumo_b = comparacao.resumo.iloc[1]
            metricas_comparacao = st.columns(4)
            metricas_comparacao[0].metric(
                f"Espécies — {codigo_comparacao_a}",
                formatar_numero(int(resumo_a["species"])),
            )
            metricas_comparacao[1].metric(
                f"Espécies — {codigo_comparacao_b}",
                formatar_numero(int(resumo_b["species"])),
            )
            metricas_comparacao[2].metric(
                f"Ocorrências — {codigo_comparacao_a}",
                formatar_numero(int(resumo_a["occurrences"])),
            )
            metricas_comparacao[3].metric(
                f"Ocorrências — {codigo_comparacao_b}",
                formatar_numero(int(resumo_b["occurrences"])),
            )

            st.subheader("Distribuição temporal")
            coluna_bruta, coluna_normalizada = st.columns(2)
            with coluna_bruta:
                figura = px.line(
                    comparacao.temporal,
                    x="event_year",
                    y="occurrence_count",
                    color="country_name",
                    markers=True,
                    labels={
                        "event_year": "Ano",
                        "occurrence_count": "Ocorrências",
                        "country_name": "País",
                    },
                    title="Contagens anuais",
                )
                st.plotly_chart(
                    layout_grafico(figura, 410),
                    width="stretch",
                    config={"displayModeBar": False},
                )
            with coluna_normalizada:
                figura = px.line(
                    comparacao.temporal,
                    x="event_year",
                    y="sample_percentage",
                    color="country_name",
                    markers=True,
                    labels={
                        "event_year": "Ano",
                        "sample_percentage": "% da amostra do país",
                        "country_name": "País",
                    },
                    title="Distribuição anual normalizada",
                )
                st.plotly_chart(
                    layout_grafico(figura, 410),
                    width="stretch",
                    config={"displayModeBar": False},
                )

            st.subheader("Métricas normalizadas e cobertura")
            tabela_normalizada = comparacao.resumo[
                [
                    "country_name",
                    "occurrences_per_species",
                    "years_with_records",
                    "period",
                    "records_with_date_pct",
                    "records_with_coordinates_pct",
                ]
            ].rename(
                columns={
                    "country_name": "País",
                    "occurrences_per_species": "Registros por espécie",
                    "years_with_records": "Anos com registros",
                    "period": "Período",
                    "records_with_date_pct": "% com data",
                    "records_with_coordinates_pct": "% com coordenadas",
                }
            )
            st.dataframe(
                tabela_normalizada,
                hide_index=True,
                width="stretch",
                column_config={
                    "Registros por espécie": st.column_config.NumberColumn(
                        format="%.1f"
                    ),
                    "% com data": st.column_config.NumberColumn(format="%.1f%%"),
                    "% com coordenadas": st.column_config.NumberColumn(format="%.1f%%"),
                },
            )

            st.subheader("Espécies compartilhadas e exclusivas")
            colunas_sobreposicao = st.columns(4)
            colunas_sobreposicao[0].metric(
                "Compartilhadas",
                formatar_numero(len(comparacao.especies_compartilhadas)),
            )
            colunas_sobreposicao[1].metric(
                f"Exclusivas — {codigo_comparacao_a}",
                formatar_numero(len(comparacao.especies_exclusivas_a)),
            )
            colunas_sobreposicao[2].metric(
                f"Exclusivas — {codigo_comparacao_b}",
                formatar_numero(len(comparacao.especies_exclusivas_b)),
            )
            colunas_sobreposicao[3].metric(
                "Similaridade de Jaccard",
                f"{comparacao.similaridade_jaccard:.1f}%",
            )

            tabela_compartilhadas = comparacao.especies_compartilhadas.rename(
                columns={
                    "species_key": "Chave taxonômica",
                    "canonical_name": "Nome científico",
                    "occurrences_a": f"Ocorrências — {codigo_comparacao_a}",
                    "occurrences_b": f"Ocorrências — {codigo_comparacao_b}",
                }
            )
            coluna_compartilhadas, coluna_exclusivas = st.columns([1.25, 1])
            with coluna_compartilhadas:
                st.caption("Espécies presentes nos dois conjuntos")
                st.dataframe(
                    tabela_compartilhadas,
                    hide_index=True,
                    width="stretch",
                    height=360,
                )
            with coluna_exclusivas:
                st.caption("Espécies exclusivas por conjunto")
                exclusivas_a = comparacao.especies_exclusivas_a.assign(
                    country=codigo_comparacao_a
                ).rename(columns={"occurrences_a": "occurrence_count"})
                exclusivas_b = comparacao.especies_exclusivas_b.assign(
                    country=codigo_comparacao_b
                ).rename(columns={"occurrences_b": "occurrence_count"})
                exclusivas = pd.concat(
                    [exclusivas_a, exclusivas_b], ignore_index=True
                ).rename(
                    columns={
                        "species_key": "Chave taxonômica",
                        "canonical_name": "Nome científico",
                        "occurrence_count": "Ocorrências",
                        "country": "País",
                    }
                )
                st.dataframe(
                    exclusivas,
                    hide_index=True,
                    width="stretch",
                    height=360,
                )

            recebidos_a = (
                fonte_a.resumo_importacao.registros_recebidos
                if fonte_a.resumo_importacao
                else len(fonte_a.dados)
            )
            recebidos_b = (
                fonte_b.resumo_importacao.registros_recebidos
                if fonte_b.resumo_importacao
                else len(fonte_b.dados)
            )
            st.html(
                f"""
                <div class="quality-note">
                <b>Cuidado metodológico.</b> Mais ocorrências ou espécies registradas
                não significam maior abundância nem maior biodiversidade real. A
                comparação usa amostras de {formatar_numero(recebidos_a)} registros
                recebidos para {nomes_por_codigo[codigo_comparacao_a]} e
                {formatar_numero(recebidos_b)} para
                {nomes_por_codigo[codigo_comparacao_b]}. Diferenças também refletem
                área, cobertura temporal, esforço de coleta, instituições participantes
                e frequência de publicação no GBIF. A curva normalizada mostra a
                distribuição interna da amostra, não corrige integralmente esses vieses.
                </div>
                """
            )

with aba_relatorio:
    st.subheader("Relatório automático")
    st.caption(
        "O PDF reproduz o recorte atual e reúne resumo, indicadores, gráficos, "
        "mapa, metodologia, limitações, fonte e data de geração."
    )
    nomes_selecionados = [nomes_especies[chave] for chave in especies]
    periodo_relatorio = (
        f"{intervalo_anos[0]}–{intervalo_anos[1]}"
        if intervalo_anos
        else "Todos os anos disponíveis"
    )
    filtros_relatorio = {
        "País": f"{pais.nome} ({pais.codigo_iso})",
        "Espécies": ", ".join(nomes_selecionados) or "Todas as espécies",
        "Período": periodo_relatorio,
        "Origem": ", ".join(ROTULOS_ORIGEM.get(item, item) for item in origens)
        or "Todas as classificações",
        "Tipo de registro": ", ".join(tipos) or "Todos os tipos",
        "Unidade administrativa": ", ".join(rotulo_estado(item) for item in estados)
        or "Todas as unidades",
        "Atualização da fonte": ultima_atualizacao,
    }
    st.markdown(
        f"**Consulta:** {pais.nome} · {periodo_relatorio} · "
        f"{formatar_numero(indicadores['occurrences'])} ocorrências · "
        f"{formatar_numero(indicadores['species'])} espécies"
    )
    with st.spinner("Preparando relatório reproduzível..."):
        relatorio_pdf = obter_relatorio_pdf(
            filtrados,
            pais.nome,
            pais.codigo_iso,
            f"GBIF via {resultado.fonte}",
            tuple(filtros_relatorio.items()),
        )
    sufixo_periodo = periodo_relatorio.replace("–", "-").replace(" ", "_")
    st.download_button(
        "Baixar relatório PDF",
        data=relatorio_pdf,
        file_name=(
            f"{PROJECT_SLUG}_relatorio_{pais.codigo_iso.lower()}_{sufixo_periodo}.pdf"
        ),
        mime="application/pdf",
        icon=":material/picture_as_pdf:",
        type="primary",
    )
    st.caption(
        "A assinatura incluída no PDF identifica o conjunto de GBIF IDs usado. "
        "Para reproduzir o relatório, reaplique os filtros registrados usando a mesma fonte."
    )

with aba_qualidade:
    qualidade = indicadores_qualidade(filtrados)
    total = max(len(filtrados), 1)

    st.subheader("Aproveitamento da última carga")
    resumo_importacao = resultado.resumo_importacao
    if resumo_importacao:
        colunas_funil = st.columns(4)
        colunas_funil[0].metric(
            "Recebidos", formatar_numero(resumo_importacao.registros_recebidos)
        )
        colunas_funil[1].metric(
            "Aproveitados", formatar_numero(resumo_importacao.registros_salvos)
        )
        colunas_funil[2].metric(
            "Descartados", formatar_numero(resumo_importacao.registros_descartados)
        )
        colunas_funil[3].metric(
            "Aproveitamento", f"{resumo_importacao.percentual_aproveitado:.1f}%"
        )
        st.caption(
            f"Sem identificação no nível de espécie: "
            f"{formatar_numero(resumo_importacao.sem_nivel_especie)} registros."
        )
    else:
        st.caption(
            "O resumo detalhado não está disponível para esta carga. "
            "Os indicadores dos registros aproveitados permanecem abaixo."
        )

    st.subheader("Indicadores dos registros aproveitados")
    colunas_qualidade = st.columns(4)
    itens_qualidade = [
        ("Sem data", qualidade["missing_date"]),
        ("Data apenas mensal", qualidade["monthly_date"]),
        ("Coordenada ausente/inválida", qualidade["invalid_coordinates"]),
        ("Duplicidade potencial", qualidade["potential_duplicate"]),
    ]
    for coluna, (rotulo, valor) in zip(colunas_qualidade, itens_qualidade, strict=True):
        coluna.metric(rotulo, formatar_numero(valor), f"{100 * valor / total:.1f}%")

    colunas_qualidade = st.columns(4)
    itens_qualidade = [
        ("Problema indicado pelo GBIF", qualidade["gbif_issue"]),
        ("Possivelmente fora do país", qualidade["potential_outside_country"]),
        ("Sem localidade", qualidade["missing_locality"]),
        ("Unidade inesperada", qualidade["unexpected_state"]),
    ]
    for coluna, (rotulo, valor) in zip(colunas_qualidade, itens_qualidade, strict=True):
        coluna.metric(rotulo, formatar_numero(valor), f"{100 * valor / total:.1f}%")

    evidencia = distribuicao_tipo(filtrados).head(12)
    precisao = (
        filtrados["date_precision"]
        .fillna("MISSING")
        .value_counts()
        .rename_axis("date_precision")
        .reset_index(name="record_count")
    )
    rotulos_precisao = {
        "DAY": "Dia",
        "MONTH": "Mês",
        "YEAR": "Ano",
        "UNKNOWN": "Desconhecida",
        "MISSING": "Sem data",
    }
    precisao["precision_display"] = precisao["date_precision"].map(
        lambda valor: rotulos_precisao.get(valor, valor)
    )
    figura_evidencia = px.bar(
        evidencia.sort_values("occurrence_count"),
        x="occurrence_count",
        y="basis_of_record",
        orientation="h",
        labels={"occurrence_count": "Registros", "basis_of_record": ""},
        title="Distribuição por tipo de evidência",
        color_discrete_sequence=["#4f772d"],
    )
    figura_precisao = px.bar(
        precisao,
        x="precision_display",
        y="record_count",
        labels={"precision_display": "Precisão", "record_count": "Registros"},
        title="Precisão das datas",
        color_discrete_sequence=["#7c3f58"],
    )
    coluna_evidencia, coluna_precisao = st.columns(2)
    with coluna_evidencia:
        st.plotly_chart(
            layout_grafico(figura_evidencia, 420),
            width="stretch",
            config={"displayModeBar": False},
        )
    with coluna_precisao:
        st.plotly_chart(
            layout_grafico(figura_precisao, 420),
            width="stretch",
            config={"displayModeBar": False},
        )

    alertas_ocorrencia = frequencia_alertas(filtrados, "occurrence_issues").head(12)
    alertas_taxonomicos = frequencia_alertas(filtrados, "taxonomic_issues").head(12)
    coluna_ocorrencia, coluna_taxonomia = st.columns(2)
    with coluna_ocorrencia:
        figura = px.bar(
            alertas_ocorrencia.sort_values("record_count"),
            x="record_count",
            y="issue",
            orientation="h",
            labels={"record_count": "Registros", "issue": ""},
            title="Alertas de ocorrência",
            color_discrete_sequence=["#2563eb"],
        )
        st.plotly_chart(
            layout_grafico(figura, 440),
            width="stretch",
            config={"displayModeBar": False},
        )
    with coluna_taxonomia:
        figura = px.bar(
            alertas_taxonomicos.sort_values("record_count"),
            x="record_count",
            y="issue",
            orientation="h",
            labels={"record_count": "Registros", "issue": ""},
            title="Alertas taxonômicos",
            color_discrete_sequence=["#c2413b"],
        )
        st.plotly_chart(
            layout_grafico(figura, 440),
            width="stretch",
            config={"displayModeBar": False},
        )
    st.html(
        """
        <div class="quality-note">
        Alertas do GBIF registram interpretações e inconsistências potenciais. Eles não invalidam automaticamente uma ocorrência. Registros candidatos a duplicidade exigem revisão do evento de coleta antes de qualquer remoção.
        </div>
        """
    )

with aba_dados:
    busca = st.text_input(
        "Buscar nos registros",
        placeholder="Espécie, localidade ou unidade administrativa",
    )
    tabela = filtrados.copy()
    if len(busca.strip()) > 200:
        st.warning("A busca deve ter no máximo 200 caracteres.")
        tabela = tabela.iloc[0:0]
    elif busca.strip():
        termo = busca.strip()
        mascara_busca = (
            tabela["canonical_name"]
            .fillna("")
            .str.contains(termo, case=False, regex=False)
            | tabela["locality"].fillna("").str.contains(termo, case=False, regex=False)
            | tabela["state_normalized"]
            .fillna("")
            .str.contains(termo, case=False, regex=False)
        )
        tabela = tabela.loc[mascara_busca]
    tabela_exibicao = tabela[
        [
            "gbif_id",
            "country_name",
            "canonical_name",
            "origin_status",
            "event_date",
            "state_normalized",
            "locality",
            "basis_of_record",
            "decimal_latitude",
            "decimal_longitude",
        ]
    ].rename(
        columns={
            "gbif_id": "GBIF ID",
            "country_name": "País",
            "canonical_name": "Espécie",
            "origin_status": "Origem",
            "event_date": "Data",
            "state_normalized": "Unidade",
            "locality": "Localidade",
            "basis_of_record": "Tipo",
            "decimal_latitude": "Latitude",
            "decimal_longitude": "Longitude",
        }
    )
    tabela_exibicao["Origem"] = tabela_exibicao["Origem"].map(ROTULOS_ORIGEM)
    tabela_exibicao["Unidade"] = tabela_exibicao["Unidade"].map(rotulo_estado)
    tabela_navegador = tabela_exibicao.head(LIMITE_RESULTADOS_SQL)
    st.caption(f"{formatar_numero(len(tabela_exibicao))} registros")
    if len(tabela_exibicao) > len(tabela_navegador):
        st.caption(
            "A tabela mostra os primeiros "
            f"{formatar_numero(len(tabela_navegador))} registros; o CSV preserva "
            "todo o recorte filtrado."
        )
    st.dataframe(
        tabela_navegador,
        hide_index=True,
        width="stretch",
        height=540,
        column_config={
            "Data": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm"),
            "Latitude": st.column_config.NumberColumn(format="%.5f"),
            "Longitude": st.column_config.NumberColumn(format="%.5f"),
        },
    )
    st.download_button(
        "Baixar CSV",
        data=tabela_exibicao.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"{PROJECT_SLUG}_ocorrencias_filtradas.csv",
        mime="text/csv",
        icon=":material/download:",
    )

with st.expander("Metodologia e limitações"):
    st.markdown(
        """
        Os pontos representam ocorrências publicadas no GBIF e filtradas pelo limite oficial da porção brasileira da Região Hidrográfica do Paraná. As contagens refletem coleta e publicação, não abundância biológica. A fonte atual é uma amostra de 5.000 registros do pré-filtro; comparações ecológicas exigem a base integral e controle do esforço amostral.
        """
    )

st.caption(f"{APP_NAME} · Dados de ocorrências fornecidos pelo GBIF.")

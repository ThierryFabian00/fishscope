from __future__ import annotations

import hashlib
import textwrap
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Mapping, Sequence

import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

from src.dashboard_data import (
    calcular_indicadores,
    distribuicao_origem,
    indicadores_qualidade,
    ranking_especies,
    serie_anual,
)

COR_PRIMARIA = "#0f766e"
COR_SECUNDARIA = "#5f6f67"
COR_ALERTA = "#d97706"
COR_FUNDO = "#f5f7f6"
CORES_ORIGEM = {
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


@dataclass(frozen=True)
class ContextoRelatorio:
    pais_nome: str
    pais_codigo: str
    fonte: str
    filtros: Mapping[str, str]
    gerado_em: datetime


def assinatura_registros(dados: pd.DataFrame) -> str:
    """Cria uma assinatura estável do conjunto de ocorrências do relatório."""
    ids = dados["gbif_id"].astype("string").fillna("").sort_values()
    conteudo = "\n".join(ids.tolist()).encode("utf-8")
    return hashlib.sha256(conteudo).hexdigest()[:16]


def _texto_quebrado(texto: str, largura: int = 94) -> str:
    return "\n".join(textwrap.wrap(texto, width=largura, break_long_words=False))


def _configurar_pagina(
    figura: Figure, titulo: str, contexto: ContextoRelatorio
) -> None:
    figura.set_facecolor("white")
    figura.suptitle(
        titulo,
        x=0.07,
        y=0.965,
        ha="left",
        color="#17211d",
        fontsize=18,
        fontweight="bold",
    )
    figura.text(
        0.07,
        0.025,
        (
            f"Gerado em {contexto.gerado_em:%d/%m/%Y %H:%M} · "
            f"Fonte: {contexto.fonte} · {contexto.pais_nome} ({contexto.pais_codigo})"
        ),
        color=COR_SECUNDARIA,
        fontsize=8,
    )


def _pagina_resumo(dados: pd.DataFrame, contexto: ContextoRelatorio) -> Figure:
    figura = Figure(figsize=(8.27, 11.69))
    _configurar_pagina(
        figura, "Relatório automático de ocorrências de peixes", contexto
    )
    indicadores = calcular_indicadores(dados)
    qualidade = indicadores_qualidade(dados)
    assinatura = assinatura_registros(dados)

    figura.text(
        0.07,
        0.89,
        "Resumo da consulta",
        color=COR_PRIMARIA,
        fontsize=13,
        fontweight="bold",
    )
    metricas = [
        ("Ocorrências", f"{indicadores['occurrences']:,}".replace(",", ".")),
        ("Espécies", f"{indicadores['species']:,}".replace(",", ".")),
        ("Período observado", indicadores["period"]),
        ("Espécies introduzidas", str(indicadores["introduced_species"])),
    ]
    for indice, (rotulo, valor) in enumerate(metricas):
        coluna = indice % 2
        linha = indice // 2
        x = 0.07 + coluna * 0.44
        y = 0.80 - linha * 0.095
        figura.text(x, y + 0.035, rotulo, color=COR_SECUNDARIA, fontsize=9)
        figura.text(x, y, valor, color="#17211d", fontsize=18, fontweight="bold")

    figura.text(
        0.07,
        0.62,
        "Filtros aplicados",
        color=COR_PRIMARIA,
        fontsize=13,
        fontweight="bold",
    )
    y = 0.585
    for rotulo, valor in contexto.filtros.items():
        figura.text(
            0.08, y, f"{rotulo}:", color="#17211d", fontsize=9, fontweight="bold"
        )
        figura.text(
            0.27, y, _texto_quebrado(valor, 72), color=COR_SECUNDARIA, fontsize=9
        )
        y -= 0.042 * max(1, len(textwrap.wrap(valor, width=72)))

    cobertura = (
        100 * (1 - qualidade["invalid_coordinates"] / len(dados)) if len(dados) else 0
    )
    figura.text(
        0.07,
        y - 0.015,
        "Indicadores de cobertura",
        color=COR_PRIMARIA,
        fontsize=13,
        fontweight="bold",
    )
    figura.text(
        0.08,
        y - 0.065,
        (
            f"Registros com coordenadas válidas: {cobertura:.1f}%\n"
            f"Registros sem localidade: {qualidade['missing_locality']:,}\n"
            f"Registros com alertas do GBIF: {qualidade['gbif_issue']:,}\n"
            f"Assinatura dos registros: {assinatura}"
        ).replace(",", "."),
        color="#17211d",
        fontsize=9,
        linespacing=1.6,
    )

    figura.text(
        0.07, 0.235, "Metodologia", color=COR_PRIMARIA, fontsize=13, fontweight="bold"
    )
    metodologia = (
        "O relatório resume ocorrências publicadas no GBIF após a aplicação dos filtros "
        "registrados acima. Espécies são contadas por chave taxonômica aceita; a distribuição "
        "temporal usa o ano do evento e o mapa inclui somente coordenadas válidas. A assinatura "
        "é calculada sobre os GBIF IDs ordenados e permite conferir se o mesmo recorte foi usado."
    )
    figura.text(
        0.07,
        0.20,
        _texto_quebrado(metodologia),
        color="#17211d",
        fontsize=9,
        va="top",
        linespacing=1.45,
    )

    figura.text(
        0.07, 0.115, "Limitações", color=COR_ALERTA, fontsize=13, fontweight="bold"
    )
    limitacoes = (
        "As contagens refletem esforço de coleta, cobertura espacial e temporal e publicação de "
        "dados; não representam abundância nem biodiversidade real. A fonte ativa pode conter "
        "uma amostra limitada dos resultados disponíveis no GBIF. Ausências no relatório não "
        "demonstram ausência biológica, e coordenadas ou identificações podem conter incertezas."
    )
    figura.text(
        0.07,
        0.08,
        _texto_quebrado(limitacoes),
        color="#5f481b",
        fontsize=9,
        va="top",
        linespacing=1.45,
    )
    return figura


def _pagina_graficos(dados: pd.DataFrame, contexto: ContextoRelatorio) -> Figure:
    figura = Figure(figsize=(11.69, 8.27))
    _configurar_pagina(figura, "Indicadores e distribuições", contexto)
    eixos = figura.subplots(1, 3, gridspec_kw={"wspace": 0.34})

    ranking = ranking_especies(dados, limite=10).sort_values("occurrence_count")
    eixos[0].barh(
        ranking["canonical_name"], ranking["occurrence_count"], color=COR_PRIMARIA
    )
    eixos[0].set_title("Espécies mais registradas", loc="left", fontweight="bold")
    eixos[0].set_xlabel("Ocorrências")

    anual = serie_anual(dados)
    eixos[1].plot(
        anual["event_year"], anual["occurrence_count"], color=COR_PRIMARIA, marker="o"
    )
    eixos[1].set_title("Distribuição anual", loc="left", fontweight="bold")
    eixos[1].set_xlabel("Ano")
    eixos[1].set_ylabel("Ocorrências")
    eixos[1].ticklabel_format(axis="x", style="plain", useOffset=False)

    origens = distribuicao_origem(dados)
    rotulos = [ROTULOS_ORIGEM.get(valor, valor) for valor in origens["origin_status"]]
    cores = [
        CORES_ORIGEM.get(valor, CORES_ORIGEM["UNKNOWN"])
        for valor in origens["origin_status"]
    ]
    eixos[2].bar(rotulos, origens["species_count"], color=cores)
    eixos[2].set_title("Espécies por origem", loc="left", fontweight="bold")
    eixos[2].set_ylabel("Espécies")
    eixos[2].tick_params(axis="x", rotation=30)

    for eixo in eixos:
        eixo.spines[["top", "right"]].set_visible(False)
        eixo.grid(axis="y", color="#e8eeeb", linewidth=0.7)
        eixo.set_axisbelow(True)
    figura.subplots_adjust(left=0.08, right=0.96, top=0.84, bottom=0.16)
    return figura


def _pagina_mapa(dados: pd.DataFrame, contexto: ContextoRelatorio) -> Figure:
    figura = Figure(figsize=(11.69, 8.27))
    _configurar_pagina(figura, "Distribuição espacial das ocorrências", contexto)
    eixo = figura.subplots()
    pontos = dados.loc[
        dados["decimal_latitude"].between(-90, 90)
        & dados["decimal_longitude"].between(-180, 180)
    ]
    if pontos.empty:
        eixo.text(
            0.5, 0.5, "Não há coordenadas válidas no recorte.", ha="center", va="center"
        )
        eixo.set_axis_off()
    else:
        eixo.scatter(
            pontos["decimal_longitude"],
            pontos["decimal_latitude"],
            s=13,
            color=COR_PRIMARIA,
            alpha=0.42,
            edgecolors="white",
            linewidths=0.2,
        )
        eixo.set_xlabel("Longitude")
        eixo.set_ylabel("Latitude")
        eixo.grid(color="#e8eeeb", linewidth=0.7)
        eixo.spines[["top", "right"]].set_visible(False)
        eixo.set_title(
            f"{len(pontos):,} registros com coordenadas válidas".replace(",", "."),
            loc="left",
            color=COR_SECUNDARIA,
            fontsize=10,
        )
    figura.text(
        0.07,
        0.075,
        _texto_quebrado(
            "Cada ponto é uma ocorrência publicada, não um indivíduo nem uma estimativa de abundância. "
            "Sobreposição de pontos pode ocultar concentração de registros.",
            120,
        ),
        color=COR_SECUNDARIA,
        fontsize=9,
    )
    figura.subplots_adjust(left=0.09, right=0.96, top=0.84, bottom=0.16)
    return figura


def gerar_relatorio_pdf(
    dados: pd.DataFrame,
    *,
    pais_nome: str,
    pais_codigo: str,
    fonte: str,
    filtros: Mapping[str, str],
    gerado_em: datetime | None = None,
) -> bytes:
    """Gera um relatório PDF autocontido para o recorte filtrado."""
    if dados.empty:
        raise ValueError("Não é possível gerar um relatório sem ocorrências.")
    contexto = ContextoRelatorio(
        pais_nome=pais_nome,
        pais_codigo=pais_codigo,
        fonte=fonte,
        filtros=dict(filtros),
        gerado_em=gerado_em or datetime.now().astimezone(),
    )
    paginas: Sequence[Figure] = (
        _pagina_resumo(dados, contexto),
        _pagina_graficos(dados, contexto),
        _pagina_mapa(dados, contexto),
    )
    saida = BytesIO()
    with PdfPages(
        saida,
        metadata={
            "Title": f"Relatório de ocorrências de peixes — {pais_nome}",
            "Author": "Biodiversidade de Peixes",
            "Subject": f"Consulta {assinatura_registros(dados)}",
            "CreationDate": contexto.gerado_em,
        },
    ) as pdf:
        for pagina in paginas:
            pdf.savefig(pagina)
    return saida.getvalue()

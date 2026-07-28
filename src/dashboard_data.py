from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from typing import Any, Sequence

import pandas as pd
import psycopg
from psycopg.rows import dict_row

from src.analysis import ESTADOS_ESPERADOS, normalizar_estado
from src.config import (
    LIMITE_BUSCA_GBIF,
    LIMITE_PONTOS_MAPA,
    PAIS_PADRAO,
    limite_registros_dashboard,
)
from src.database import validar_schema
from src.services.country_service import normalizar_codigo_pais, obter_pais
from src.transform_fish import (
    ARQUIVO_ESPECIES,
    ARQUIVO_OCORRENCIAS,
    caminhos_processados_pais,
)

ARQUIVO_AMOSTRA_PUBLICA = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "sample"
    / "occurrences_sample.csv"
)


def caminho_amostra_publica(codigo_pais: str) -> Path:
    codigo = normalizar_codigo_pais(codigo_pais)
    if codigo == PAIS_PADRAO:
        return ARQUIVO_AMOSTRA_PUBLICA
    return ARQUIVO_AMOSTRA_PUBLICA.with_name(
        f"occurrences_{codigo.casefold()}_sample.csv"
    )


@dataclass(frozen=True)
class ResumoImportacao:
    registros_recebidos: int
    registros_salvos: int
    registros_descartados: int
    sem_nivel_especie: int
    atualizado_em: Any | None = None

    @property
    def percentual_aproveitado(self) -> float:
        if not self.registros_recebidos:
            return 0.0
        return 100 * self.registros_salvos / self.registros_recebidos


@dataclass(frozen=True)
class ResultadoFonte:
    dados: pd.DataFrame
    fonte: str
    aviso: str | None = None
    pais_codigo: str = PAIS_PADRAO
    pais_nome: str = "Brasil"
    resumo_importacao: ResumoImportacao | None = None
    total_disponivel: int | None = None
    limitado: bool = False


@dataclass(frozen=True)
class ComparacaoPaises:
    resumo: pd.DataFrame
    temporal: pd.DataFrame
    especies_compartilhadas: pd.DataFrame
    especies_exclusivas_a: pd.DataFrame
    especies_exclusivas_b: pd.DataFrame

    @property
    def similaridade_jaccard(self) -> float:
        compartilhadas = len(self.especies_compartilhadas)
        uniao = (
            compartilhadas
            + len(self.especies_exclusivas_a)
            + len(self.especies_exclusivas_b)
        )
        return 100 * compartilhadas / uniao if uniao else 0.0


COLUNAS_DASHBOARD = [
    "gbif_id",
    "species_key",
    "canonical_name",
    "family",
    "order_name",
    "origin_status",
    "iucn_category",
    "event_date",
    "date_precision",
    "event_year",
    "event_month",
    "decimal_latitude",
    "decimal_longitude",
    "state_province",
    "locality",
    "basis_of_record",
    "taxonomic_issues",
    "occurrence_issues",
]


def consulta_dashboard(schema: str) -> str:
    schema = validar_schema(schema)
    return f"""
        SELECT
            o.gbif_key AS gbif_id,
            o.taxon_key AS species_key,
            t.canonical_name,
            t.family,
            t.order_name,
            t.origin_status,
            t.iucn_category,
            o.event_date,
            o.date_precision,
            o.year AS event_year,
            o.month AS event_month,
            o.latitude AS decimal_latitude,
            o.longitude AS decimal_longitude,
            o.state_province,
            o.locality,
            o.basis_of_record,
            o.taxonomic_issues,
            o.occurrence_issues,
            COUNT(*) OVER() AS total_disponivel
        FROM {schema}.occurrences o
        JOIN {schema}.taxa t ON t.taxon_key = o.taxon_key
        WHERE o.country_code = %s
        ORDER BY o.gbif_key
        LIMIT %s
    """


def carregar_postgresql(
    database_url: str,
    schema: str,
    codigo_pais: str,
    limite: int | None = None,
) -> pd.DataFrame:
    if limite is None:
        limite = limite_registros_dashboard()
    if not 1 <= limite <= LIMITE_BUSCA_GBIF:
        raise ValueError(
            f"O limite do dashboard deve estar entre 1 e {LIMITE_BUSCA_GBIF}."
        )
    with psycopg.connect(database_url, row_factory=dict_row) as conexao:
        return _carregar_postgresql_conexao(conexao, schema, codigo_pais, limite)


def _carregar_postgresql_conexao(
    conexao: Any, schema: str, codigo_pais: str, limite: int
) -> pd.DataFrame:
    with conexao.cursor() as cursor:
        cursor.execute(consulta_dashboard(schema), (codigo_pais, limite))
        linhas = cursor.fetchall()
    total_disponivel = int(linhas[0]["total_disponivel"]) if linhas else 0
    dados = pd.DataFrame(linhas)
    dados = dados.drop(columns="total_disponivel", errors="ignore")
    dados = dados.reindex(columns=COLUNAS_DASHBOARD)
    dados.attrs["total_disponivel"] = total_disponivel
    return dados


def carregar_resumo_importacao(
    database_url: str, schema: str, codigo_pais: str
) -> ResumoImportacao | None:
    schema = validar_schema(schema)
    with psycopg.connect(database_url, row_factory=dict_row) as conexao:
        return _carregar_resumo_importacao_conexao(conexao, schema, codigo_pais)


def _carregar_resumo_importacao_conexao(
    conexao: Any, schema: str, codigo_pais: str
) -> ResumoImportacao | None:
    schema = validar_schema(schema)
    with conexao.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT records_received, records_saved, records_rejected,
                   records_rejected_taxonomy, quality_stats_complete,
                   finished_at
            FROM {schema}.data_imports
            WHERE country_code = %s AND status = 'COMPLETED'
            ORDER BY finished_at DESC NULLS LAST, id DESC
            LIMIT 1
            """,
            (codigo_pais,),
        )
        linha = cursor.fetchone()
    if not linha or not linha["quality_stats_complete"]:
        return None
    return ResumoImportacao(
        registros_recebidos=int(linha["records_received"]),
        registros_salvos=int(linha["records_saved"]),
        registros_descartados=int(linha["records_rejected"]),
        sem_nivel_especie=int(linha["records_rejected_taxonomy"]),
        atualizado_em=linha["finished_at"],
    )


def carregar_postgresql_com_resumo(
    database_url: str,
    schema: str,
    codigo_pais: str,
    limite: int | None = None,
) -> tuple[pd.DataFrame, ResumoImportacao | None]:
    if limite is None:
        limite = limite_registros_dashboard()
    if not 1 <= limite <= LIMITE_BUSCA_GBIF:
        raise ValueError(
            f"O limite do dashboard deve estar entre 1 e {LIMITE_BUSCA_GBIF}."
        )
    with psycopg.connect(database_url, row_factory=dict_row) as conexao:
        dados = _carregar_postgresql_conexao(conexao, schema, codigo_pais, limite)
        resumo = _carregar_resumo_importacao_conexao(conexao, schema, codigo_pais)
    return dados, resumo


def carregar_csv(
    caminho_ocorrencias: Path = ARQUIVO_OCORRENCIAS,
    caminho_especies: Path = ARQUIVO_ESPECIES,
) -> pd.DataFrame:
    if not caminho_ocorrencias.exists() or not caminho_especies.exists():
        raise FileNotFoundError(
            "Tabelas processadas nao encontradas para o fallback CSV."
        )
    ocorrencias = pd.read_csv(caminho_ocorrencias)
    especies = pd.read_csv(caminho_especies)
    # Occurrence rows also preserve taxonomy; the species catalog is authoritative.
    ocorrencias = ocorrencias.drop(
        columns=["family", "order", "iucnCategory"], errors="ignore"
    )

    especies = especies[
        [
            "speciesKey",
            "family",
            "order",
            "originStatus",
            "iucnCategory",
        ]
    ].drop_duplicates("speciesKey")
    dados = ocorrencias.merge(especies, on="speciesKey", how="left")
    if "datePrecision" not in dados:
        original = dados.get("eventDateOriginal", dados.get("eventDate"))
        if original is None:
            dados["datePrecision"] = pd.NA
        else:
            texto = original.astype("string").str.strip()
            dados["datePrecision"] = "UNKNOWN"
            dados.loc[texto.str.fullmatch(r"\d{4}", na=False), "datePrecision"] = "YEAR"
            dados.loc[
                texto.str.fullmatch(r"\d{4}-\d{2}", na=False), "datePrecision"
            ] = "MONTH"
            dados.loc[
                texto.str.match(r"^\d{4}-\d{2}-\d{2}", na=False), "datePrecision"
            ] = "DAY"
            dados.loc[texto.isna(), "datePrecision"] = pd.NA
    return dados.rename(
        columns={
            "gbifID": "gbif_id",
            "speciesKey": "species_key",
            "canonicalName": "canonical_name",
            "order": "order_name",
            "originStatus": "origin_status",
            "iucnCategory": "iucn_category",
            "eventDate": "event_date",
            "datePrecision": "date_precision",
            "year": "event_year",
            "month": "event_month",
            "decimalLatitude": "decimal_latitude",
            "decimalLongitude": "decimal_longitude",
            "stateProvince": "state_province",
            "basisOfRecord": "basis_of_record",
            "taxonomicIssues": "taxonomic_issues",
            "occurrenceIssues": "occurrence_issues",
        }
    )[COLUNAS_DASHBOARD]


def carregar_amostra_publica(
    caminho: Path | None = None,
    codigo_pais: str = PAIS_PADRAO,
) -> pd.DataFrame:
    """Adapta a amostra redistribuível ao contrato do dashboard."""
    caminho = caminho or caminho_amostra_publica(codigo_pais)
    if not caminho.exists():
        raise FileNotFoundError("A amostra pública do dashboard não foi encontrada.")
    amostra = pd.read_csv(caminho)
    obrigatorias = {
        "gbifID",
        "canonicalName",
        "eventDate",
        "stateProvince",
        "basisOfRecord",
        "decimalLatitude",
        "decimalLongitude",
    }
    ausentes = obrigatorias.difference(amostra.columns)
    if ausentes:
        raise ValueError(
            "Colunas ausentes na amostra pública: " + ", ".join(sorted(ausentes))
        )
    datas = pd.to_datetime(amostra["eventDate"], errors="coerce", utc=True)
    resultado = pd.DataFrame(
        {
            "gbif_id": amostra["gbifID"],
            "species_key": "sample:" + amostra["canonicalName"].astype("string"),
            "canonical_name": amostra["canonicalName"],
            "family": pd.NA,
            "order_name": pd.NA,
            "origin_status": "UNKNOWN",
            "iucn_category": pd.NA,
            "event_date": datas,
            "date_precision": "DAY",
            "event_year": datas.dt.year,
            "event_month": datas.dt.month,
            "decimal_latitude": amostra["decimalLatitude"],
            "decimal_longitude": amostra["decimalLongitude"],
            "state_province": amostra["stateProvince"],
            "locality": pd.NA,
            "basis_of_record": amostra["basisOfRecord"],
            "taxonomic_issues": "",
            "occurrence_issues": "",
        }
    )
    return resultado[COLUNAS_DASHBOARD]


def normalizar_dados(
    dados: pd.DataFrame, codigo_pais_fonte: str = PAIS_PADRAO
) -> pd.DataFrame:
    dados = dados.copy()
    if "date_precision" not in dados:
        dados["date_precision"] = pd.NA
    ausentes = set(COLUNAS_DASHBOARD).difference(dados.columns)
    if ausentes:
        raise ValueError(
            f"Colunas ausentes para o dashboard: {', '.join(sorted(ausentes))}"
        )
    pais_fonte = obter_pais(codigo_pais_fonte)
    resultado = dados
    if "country_code" not in resultado:
        resultado["country_code"] = pais_fonte.codigo_iso
    resultado["country_code"] = resultado["country_code"].map(normalizar_codigo_pais)
    resultado["country_name"] = resultado["country_code"].map(
        lambda codigo: obter_pais(codigo).nome
    )
    resultado["species_key"] = resultado["species_key"].astype("string")
    resultado["event_date"] = pd.to_datetime(
        resultado["event_date"], errors="coerce", utc=True, format="mixed"
    )
    resultado["date_precision"] = (
        resultado["date_precision"].astype("string").str.strip().str.upper()
    )
    resultado["event_year"] = pd.to_numeric(
        resultado["event_year"], errors="coerce"
    ).astype("Int64")
    resultado["event_month"] = pd.to_numeric(
        resultado["event_month"], errors="coerce"
    ).astype("Int64")
    resultado["decimal_latitude"] = pd.to_numeric(
        resultado["decimal_latitude"], errors="coerce"
    )
    resultado["decimal_longitude"] = pd.to_numeric(
        resultado["decimal_longitude"], errors="coerce"
    )
    resultado["origin_status"] = resultado["origin_status"].fillna("UNKNOWN")
    resultado["state_normalized"] = resultado["state_province"].map(normalizar_estado)
    resultado["has_taxonomic_issue"] = resultado["taxonomic_issues"].fillna("").ne("")
    resultado["has_occurrence_issue"] = resultado["occurrence_issues"].fillna("").ne("")
    resultado["has_gbif_issue"] = (
        resultado["has_taxonomic_issue"] | resultado["has_occurrence_issue"]
    )
    resultado["missing_locality"] = resultado["locality"].isna()
    resultado["missing_date"] = resultado["event_date"].isna()
    resultado["monthly_date"] = resultado["date_precision"].eq("MONTH").fillna(False)
    latitude = resultado["decimal_latitude"]
    longitude = resultado["decimal_longitude"]
    resultado["invalid_coordinates"] = (
        latitude.isna()
        | longitude.isna()
        | ~latitude.between(-90, 90)
        | ~longitude.between(-180, 180)
    )
    assinatura_duplicidade = [
        "species_key",
        "decimal_latitude",
        "decimal_longitude",
        "event_date",
    ]
    completos = resultado[assinatura_duplicidade].notna().all(axis=1)
    resultado["potential_duplicate"] = completos & resultado.duplicated(
        assinatura_duplicidade, keep=False
    )
    resultado["potential_outside_country"] = (
        resultado["occurrence_issues"]
        .fillna("")
        .str.contains(r"(?:^|\|)COUNTRY_COORDINATE_MISMATCH(?:\||$)", regex=True)
    )
    resultado["unexpected_state"] = ~resultado["state_normalized"].isin(
        ESTADOS_ESPERADOS | {"Nao informado"}
    )
    return resultado


def carregar_dados_dashboard(
    database_url: str | None,
    schema: str,
    caminho_ocorrencias: Path | None = None,
    caminho_especies: Path | None = None,
    codigo_pais: str = PAIS_PADRAO,
) -> ResultadoFonte:
    pais = obter_pais(codigo_pais)
    caminhos_automaticos = caminho_ocorrencias is None and caminho_especies is None
    if (caminho_ocorrencias is None) != (caminho_especies is None):
        raise ValueError("Informe os dois caminhos CSV ou nenhum deles.")
    if caminhos_automaticos:
        caminho_ocorrencias, caminho_especies, _ = caminhos_processados_pais(
            pais.codigo_iso
        )
    assert caminho_ocorrencias is not None
    assert caminho_especies is not None
    arquivos_do_pais_disponiveis = (
        caminhos_automaticos
        and pais.codigo_iso != PAIS_PADRAO
        and caminho_ocorrencias.exists()
        and caminho_especies.exists()
    )
    aviso_fonte = None
    resumo_importacao = None
    total_disponivel = None
    usou_amostra_publica = False
    if arquivos_do_pais_disponiveis and not database_url:
        dados = carregar_csv(caminho_ocorrencias, caminho_especies)
        fonte = "CSV"
    elif database_url:
        try:
            dados, resumo_importacao = carregar_postgresql_com_resumo(
                database_url,
                schema,
                pais.codigo_iso,
            )
            total_disponivel = int(dados.attrs.get("total_disponivel", len(dados)))
            fonte = "PostgreSQL"
        except psycopg.Error:
            aviso_fonte = "PostgreSQL indisponivel; exibindo os CSVs processados."
            if caminhos_automaticos and not (
                caminho_ocorrencias.exists() and caminho_especies.exists()
            ):
                if ARQUIVO_OCORRENCIAS.exists() and ARQUIVO_ESPECIES.exists():
                    caminho_ocorrencias = ARQUIVO_OCORRENCIAS
                    caminho_especies = ARQUIVO_ESPECIES
                else:
                    dados = carregar_amostra_publica(codigo_pais=pais.codigo_iso)
                    fonte = "Amostra pública"
                    usou_amostra_publica = True
            if not usou_amostra_publica:
                dados = carregar_csv(caminho_ocorrencias, caminho_especies)
                fonte = "CSV"
    else:
        aviso_fonte = "DATABASE_URL ausente; exibindo os CSVs processados."
        if caminhos_automaticos and not (
            caminho_ocorrencias.exists() and caminho_especies.exists()
        ):
            if ARQUIVO_OCORRENCIAS.exists() and ARQUIVO_ESPECIES.exists():
                caminho_ocorrencias = ARQUIVO_OCORRENCIAS
                caminho_especies = ARQUIVO_ESPECIES
            else:
                dados = carregar_amostra_publica(codigo_pais=pais.codigo_iso)
                fonte = "Amostra pública"
                usou_amostra_publica = True
        if not usou_amostra_publica:
            dados = carregar_csv(caminho_ocorrencias, caminho_especies)
            fonte = "CSV"

    if usou_amostra_publica:
        aviso_fonte = (
            "PostgreSQL de produção indisponível; exibindo a amostra pública "
            "redistribuível em modo somente leitura."
        )

    codigo_pais_fonte = (
        pais.codigo_iso
        if arquivos_do_pais_disponiveis or fonte == "PostgreSQL" or usou_amostra_publica
        else PAIS_PADRAO
    )
    dados = normalizar_dados(dados, codigo_pais_fonte)
    dados = dados.loc[dados["country_code"].eq(pais.codigo_iso)].copy()
    if total_disponivel is None:
        total_disponivel = len(dados)
        dados = dados.head(limite_registros_dashboard()).copy()
    limitado = total_disponivel > len(dados)
    avisos = [aviso_fonte] if aviso_fonte else []
    if limitado:
        avisos.append(
            f"Consulta limitada a {len(dados):,} de {total_disponivel:,} registros; "
            "use filtros ou uma consulta analítica para conjuntos maiores."
        )
    if pais.codigo_iso != PAIS_PADRAO and dados.empty:
        avisos.append(
            f"Ainda não há dados importados para {pais.nome} ({pais.codigo_iso})."
        )
    return ResultadoFonte(
        dados,
        fonte,
        " ".join(avisos) or None,
        pais.codigo_iso,
        pais.nome,
        resumo_importacao,
        total_disponivel,
        limitado,
    )


def filtrar_ocorrencias(
    dados: pd.DataFrame,
    especies: Sequence[str] | None = None,
    chaves_especies: Sequence[str] | None = None,
    origens: Sequence[str] | None = None,
    intervalo_anos: tuple[int, int] | None = None,
    tipos: Sequence[str] | None = None,
    estados: Sequence[str] | None = None,
) -> pd.DataFrame:
    mascara = pd.Series(True, index=dados.index)
    if especies:
        mascara &= dados["canonical_name"].isin(especies)
    if chaves_especies:
        mascara &= dados["species_key"].isin(chaves_especies)
    if origens:
        mascara &= dados["origin_status"].isin(origens)
    if intervalo_anos:
        inicio, fim = intervalo_anos
        if inicio > fim:
            raise ValueError("O início do período não pode ser posterior ao fim.")
        if inicio < 1600 or fim > 2200:
            raise ValueError("O período deve estar entre 1600 e 2200.")
        mascara &= dados["event_year"].between(inicio, fim, inclusive="both")
    if tipos:
        mascara &= dados["basis_of_record"].isin(tipos)
    if estados:
        mascara &= dados["state_normalized"].isin(estados)
    return dados.loc[mascara].copy()


def preparar_pontos_mapa(
    dados: pd.DataFrame, limite: int = LIMITE_PONTOS_MAPA
) -> tuple[pd.DataFrame, bool]:
    """Limita o volume enviado ao navegador por agregação em grade regular."""
    if limite <= 0:
        raise ValueError("O limite de pontos do mapa deve ser positivo.")
    pontos = dados.dropna(subset=["decimal_latitude", "decimal_longitude"]).copy()
    pontos = pontos.loc[
        pontos["decimal_latitude"].between(-90, 90)
        & pontos["decimal_longitude"].between(-180, 180)
    ]
    if len(pontos) <= limite:
        pontos["map_occurrence_count"] = 1
        pontos["map_species_count"] = 1
        return pontos, False

    lado = max(1, int(sqrt(limite)))

    def indice_grade(valores: pd.Series) -> pd.Series:
        minimo = float(valores.min())
        amplitude = float(valores.max() - minimo)
        if amplitude == 0:
            return pd.Series(0, index=valores.index, dtype="int64")
        normalizados = ((valores - minimo) / amplitude).clip(0, 1)
        return (normalizados * (lado - 1)).astype("int64")

    pontos["_map_lat_cell"] = indice_grade(pontos["decimal_latitude"])
    pontos["_map_lon_cell"] = indice_grade(pontos["decimal_longitude"])
    agregacoes: dict[str, Any] = {
        "decimal_latitude": "mean",
        "decimal_longitude": "mean",
        "gbif_id": "first",
    }
    for coluna in (
        "species_key",
        "canonical_name",
        "origin_status",
        "state_normalized",
        "event_year",
        "basis_of_record",
    ):
        if coluna in pontos:
            agregacoes[coluna] = "first"
    if "species_key" in pontos:
        agregacoes["map_species_count"] = ("species_key", "nunique")
    agrupados = pontos.groupby(
        ["_map_lat_cell", "_map_lon_cell"], as_index=False, observed=True
    ).agg(
        **{
            coluna: (coluna, operacao) if isinstance(operacao, str) else operacao
            for coluna, operacao in agregacoes.items()
        }
    )
    contagens = (
        pontos.groupby(
            ["_map_lat_cell", "_map_lon_cell"], as_index=False, observed=True
        )
        .size()
        .rename(columns={"size": "map_occurrence_count"})
    )
    agrupados = agrupados.merge(
        contagens, on=["_map_lat_cell", "_map_lon_cell"], how="left"
    )
    if "map_species_count" not in agrupados:
        agrupados["map_species_count"] = 0
    return agrupados.drop(columns=["_map_lat_cell", "_map_lon_cell"]), True


def calcular_indicadores(dados: pd.DataFrame) -> dict[str, Any]:
    anos = dados["event_year"].dropna()
    return {
        "occurrences": len(dados),
        "species": int(dados["species_key"].nunique()),
        "introduced_species": int(
            dados.loc[dados["origin_status"].eq("INTRODUCED"), "species_key"].nunique()
        ),
        "states": int(
            dados.loc[
                ~dados["state_normalized"].eq("Nao informado"),
                "state_normalized",
            ].nunique()
        ),
        "period": (
            f"{int(anos.min())}-{int(anos.max())}" if not anos.empty else "Sem data"
        ),
    }


def ranking_especies(dados: pd.DataFrame, limite: int = 15) -> pd.DataFrame:
    return (
        dados.groupby("canonical_name", as_index=False)
        .agg(
            occurrence_count=("gbif_id", "size"),
            origin_status=("origin_status", "first"),
        )
        .sort_values(["occurrence_count", "canonical_name"], ascending=[False, True])
        .head(limite)
    )


def serie_temporal(dados: pd.DataFrame) -> pd.DataFrame:
    validos = dados.dropna(subset=["event_year", "event_month"])
    if validos.empty:
        return pd.DataFrame(columns=["period", "occurrence_count"])
    tabela = (
        validos.groupby(["event_year", "event_month"], as_index=False)
        .size()
        .rename(columns={"size": "occurrence_count"})
    )
    tabela["period"] = pd.to_datetime(
        {
            "year": tabela["event_year"].astype(int),
            "month": tabela["event_month"].astype(int),
            "day": 1,
        }
    )
    return tabela.sort_values("period")


def serie_anual(dados: pd.DataFrame) -> pd.DataFrame:
    validos = dados.dropna(subset=["event_year"])
    if validos.empty:
        return pd.DataFrame(columns=["event_year", "occurrence_count"])
    return (
        validos.groupby("event_year", as_index=False)
        .size()
        .rename(columns={"size": "occurrence_count"})
        .sort_values("event_year")
    )


def serie_mensal(dados: pd.DataFrame) -> pd.DataFrame:
    validos = dados.dropna(subset=["event_month"])
    if validos.empty:
        return pd.DataFrame(columns=["event_month", "occurrence_count"])
    return (
        validos.groupby("event_month", as_index=False)
        .size()
        .rename(columns={"size": "occurrence_count"})
        .sort_values("event_month")
    )


def serie_temporal_especies(
    dados: pd.DataFrame, limite_especies: int = 5
) -> pd.DataFrame:
    if limite_especies <= 0:
        raise ValueError("O limite de espécies deve ser positivo.")
    validos = dados.dropna(subset=["event_year", "canonical_name"])
    if validos.empty:
        return pd.DataFrame(
            columns=["event_year", "canonical_name", "occurrence_count"]
        )
    especies = validos["canonical_name"].value_counts().head(limite_especies).index
    return (
        validos.loc[validos["canonical_name"].isin(especies)]
        .groupby(["event_year", "canonical_name"], as_index=False)
        .size()
        .rename(columns={"size": "occurrence_count"})
        .sort_values(["event_year", "canonical_name"])
    )


def catalogo_taxonomico(dados: pd.DataFrame) -> pd.DataFrame:
    return (
        dados.groupby(
            ["species_key", "canonical_name", "family", "order_name"],
            dropna=False,
            as_index=False,
        )
        .agg(
            occurrence_count=("gbif_id", "size"),
            origin_status=("origin_status", "first"),
            iucn_category=("iucn_category", "first"),
        )
        .sort_values(["canonical_name", "species_key"])
        .reset_index(drop=True)
    )


def comparar_paises(
    dados_a: pd.DataFrame,
    codigo_a: str,
    nome_a: str,
    dados_b: pd.DataFrame,
    codigo_b: str,
    nome_b: str,
) -> ComparacaoPaises:
    if codigo_a == codigo_b:
        raise ValueError("Selecione dois países diferentes para comparar.")

    def resumo_pais(dados: pd.DataFrame, codigo: str, nome: str) -> dict[str, Any]:
        anos = dados["event_year"].dropna()
        ocorrencias = len(dados)
        especies = int(dados["species_key"].nunique())
        coordenadas_validas = (~dados["invalid_coordinates"]).sum()
        return {
            "country_code": codigo,
            "country_name": nome,
            "occurrences": ocorrencias,
            "species": especies,
            "occurrences_per_species": ocorrencias / especies if especies else 0.0,
            "years_with_records": int(anos.nunique()),
            "period": (
                f"{int(anos.min())}-{int(anos.max())}" if not anos.empty else "Sem data"
            ),
            "records_with_date_pct": (
                100 * dados["event_date"].notna().sum() / ocorrencias
                if ocorrencias
                else 0.0
            ),
            "records_with_coordinates_pct": (
                100 * coordenadas_validas / ocorrencias if ocorrencias else 0.0
            ),
        }

    resumo = pd.DataFrame(
        [
            resumo_pais(dados_a, codigo_a, nome_a),
            resumo_pais(dados_b, codigo_b, nome_b),
        ]
    )

    temporais = []
    for dados, codigo, nome in (
        (dados_a, codigo_a, nome_a),
        (dados_b, codigo_b, nome_b),
    ):
        anual = serie_anual(dados)
        anual["country_code"] = codigo
        anual["country_name"] = nome
        total = int(anual["occurrence_count"].sum())
        anual["sample_percentage"] = (
            100 * anual["occurrence_count"] / total if total else 0.0
        )
        temporais.append(anual)
    temporal = pd.concat(temporais, ignore_index=True)

    def catalogo_pais(dados: pd.DataFrame, sufixo: str) -> pd.DataFrame:
        return (
            dados.dropna(subset=["species_key"])
            .groupby("species_key", as_index=False)
            .agg(
                canonical_name=("canonical_name", "first"),
                **{f"occurrences_{sufixo}": ("gbif_id", "size")},
            )
        )

    catalogo_a = catalogo_pais(dados_a, "a")
    catalogo_b = catalogo_pais(dados_b, "b")
    uniao = catalogo_a.merge(
        catalogo_b,
        on="species_key",
        how="outer",
        suffixes=("_a", "_b"),
        indicator=True,
    )
    uniao["canonical_name"] = uniao["canonical_name_a"].fillna(
        uniao["canonical_name_b"]
    )
    colunas = ["species_key", "canonical_name"]
    compartilhadas = uniao.loc[
        uniao["_merge"].eq("both"),
        [*colunas, "occurrences_a", "occurrences_b"],
    ].sort_values("canonical_name")
    exclusivas_a = uniao.loc[
        uniao["_merge"].eq("left_only"), [*colunas, "occurrences_a"]
    ].sort_values("canonical_name")
    exclusivas_b = uniao.loc[
        uniao["_merge"].eq("right_only"), [*colunas, "occurrences_b"]
    ].sort_values("canonical_name")
    return ComparacaoPaises(
        resumo=resumo,
        temporal=temporal,
        especies_compartilhadas=compartilhadas.reset_index(drop=True),
        especies_exclusivas_a=exclusivas_a.reset_index(drop=True),
        especies_exclusivas_b=exclusivas_b.reset_index(drop=True),
    )


def distribuicao_origem(dados: pd.DataFrame) -> pd.DataFrame:
    especies = dados[["species_key", "origin_status"]].drop_duplicates("species_key")
    return (
        especies.groupby("origin_status", as_index=False)
        .size()
        .rename(columns={"size": "species_count"})
        .sort_values("species_count", ascending=False)
    )


def distribuicao_tipo(dados: pd.DataFrame) -> pd.DataFrame:
    return (
        dados["basis_of_record"]
        .fillna("Nao informado")
        .value_counts()
        .rename_axis("basis_of_record")
        .reset_index(name="occurrence_count")
    )


def indicadores_qualidade(dados: pd.DataFrame) -> dict[str, int]:
    return {
        "missing_date": int(dados["missing_date"].sum()),
        "monthly_date": int(dados["monthly_date"].sum()),
        "invalid_coordinates": int(dados["invalid_coordinates"].sum()),
        "potential_duplicate": int(dados["potential_duplicate"].sum()),
        "potential_outside_country": int(dados["potential_outside_country"].sum()),
        "gbif_issue": int(dados["has_gbif_issue"].sum()),
        "missing_locality": int(dados["missing_locality"].sum()),
        "taxonomic_issue": int(dados["has_taxonomic_issue"].sum()),
        "occurrence_issue": int(dados["has_occurrence_issue"].sum()),
        "unexpected_state": int(dados["unexpected_state"].sum()),
    }


def frequencia_alertas(dados: pd.DataFrame, coluna: str) -> pd.DataFrame:
    if coluna not in {"taxonomic_issues", "occurrence_issues"}:
        raise ValueError("Coluna de alertas invalida.")
    alertas = dados[coluna].fillna("").str.split("|").explode()
    alertas = alertas[alertas.ne("")]
    return alertas.value_counts().rename_axis("issue").reset_index(name="record_count")

"""Internacionalização centralizada da interface pública do FishScope."""

from __future__ import annotations

from typing import Any

import streamlit as st

DEFAULT_LANGUAGE = "pt"
SUPPORTED_LANGUAGES = ("pt", "en")
LANGUAGE_WIDGET_KEY = "_language_selector"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "pt": {
        "language_selector": "Idioma / Language",
        "language_pt": "Português",
        "language_en": "English",
        "app_name": "FishScope",
        "home": "Início",
        "explore": "Explorar",
        "compare": "Comparar",
        "about": "Sobre",
        "app_caption": "Plataforma para exploração e análise de ocorrências de peixes.",
        "hero_title": "Explore registros de ocorrência de peixes ao redor do mundo.",
        "hero_description": "Visualize espécies, distribuições geográficas e registros ao longo do tempo utilizando dados públicos do GBIF.",
        "start_exploring": "Começar a explorar",
        "main_features": "Principais recursos",
        "occurrence_map": "Mapa de ocorrências",
        "occurrence_map_description": "Visualize a distribuição geográfica dos registros.",
        "temporal_analysis": "Análise temporal",
        "temporal_analysis_description": "Explore como os registros se distribuem ao longo dos anos.",
        "data_quality": "Qualidade dos dados",
        "data_quality_description": "Entenda a cobertura e as limitações das informações analisadas.",
        "data_source": "Dados fornecidos pelo [GBIF](https://www.gbif.org/).",
        "compare_intro": "A comparação entre países permanece disponível na aba **Comparação** da página Explorar.",
        "compare_note": "Essa organização preserva a análise existente enquanto a experiência de comparação é preparada para funcionar como uma página independente.",
        "open_comparison": "Abrir comparação em Explorar",
        "about_intro": "Plataforma para exploração e análise de registros públicos de ocorrência de peixes fornecidos pelo GBIF.",
        "in_development": "Projeto em desenvolvimento.",
        "filters": "Filtros",
        "country": "País",
        "select_country": "Selecione um país",
        "select_country_to_begin": "Selecione um país para começar.",
        "species": "Espécies",
        "origin": "Origem",
        "period": "Período",
        "record_type": "Tipo de registro",
        "administrative_unit": "Unidade administrativa",
        "all_species": "Todas as espécies",
        "all_available_period": "Todo o período disponível",
        "all_classifications": "Todas as classificações",
        "all_record_types": "Todos os tipos de registro",
        "all_units": "Todas as unidades",
        "apply_filters": "Aplicar filtros",
        "clear_filters": "Limpar filtros",
        "advanced_filters": "Filtros avançados",
        "data_administration": "Administração de dados",
        "active_filters": "Filtros ativos",
        "records_found": "{count} registros encontrados",
        "selected_species_count": "{count} espécies selecionadas",
        "selected_record_types_count": "{count} tipos de registro selecionados",
        "update_gbif": "Atualizar dados do GBIF",
        "update_help": "Defina DATABASE_WRITE_URL para habilitar atualizações.",
        "update_disabled": "Atualização desativada: credencial de escrita não configurada.",
        "update_complete": "Atualização concluída: {count} registros.",
        "update_failed": "Não foi possível atualizar os dados: {message}",
        "unexpected_update_error": "Falha inesperada na atualização.",
        "update_unavailable": "Atualização indisponível: defina DATABASE_WRITE_URL com uma credencial PostgreSQL de escrita. A consulta normal usa apenas DATABASE_URL.",
        "data_unavailable": "Dados indisponíveis: {message}",
        "source_unavailable_error": "A fonte de dados não está disponível.",
        "selected_country": "País selecionado: {name} ({code})",
        "parana_region_description": "Ocorrências publicadas na porção brasileira da Região Hidrográfica do Paraná",
        "active_source": "Fonte ativa: {source}",
        "occurrences": "Ocorrências",
        "covered_period": "Período",
        "last_update": "Última atualização",
        "source": "Fonte",
        "not_available": "Não disponível",
        "empty_filters": "Nenhuma ocorrência disponível para {name} ({code}) com os filtros selecionados.",
        "overview": "Visão geral",
        "map": "Mapa",
        "temporal": "Temporal",
        "comparison": "Comparação",
        "report": "Relatório",
        "quality": "Qualidade",
        "data": "Dados",
        "native": "Nativa",
        "introduced": "Introduzida",
        "conflicting": "Conflitante",
        "unknown": "Desconhecida",
        "not_informed": "Não informado",
        "most_recorded_species": "Espécies mais registradas",
        "species_by_origin": "Espécies por origem",
        "map_view": "Visualização do mapa",
        "map_points": "Pontos por espécie",
        "map_heat": "Mapa de calor",
        "map_clusters": "Agrupamento espacial",
        "map_aggregated": "<b>{map_occurrence_count} ocorrências agregadas</b><br/>{map_species_count} espécies",
        "map_nearby": "<b>{elevationValue} ocorrências próximas</b>",
        "map_responsive": "Para manter o mapa responsivo, {records} registros foram agregados em até {cells} células espaciais.",
        "no_coordinates": "O recorte atual não possui coordenadas válidas.",
        "details_limited": "O seletor de detalhes mostra as primeiras {count} ocorrências do recorte.",
        "occurrence_details": "Detalhes de uma ocorrência",
        "select_occurrence": "Selecione uma ocorrência",
        "species_not_informed": "Espécie não informada",
        "family": "Família",
        "order": "Ordem",
        "date": "Data",
        "type": "Tipo",
        "unit": "Unidade",
        "locality": "Localidade",
        "informed_administrative_unit": "Unidade administrativa informada",
        "year": "Ano",
        "month": "Mês",
        "occurrences_by_year": "Ocorrências por ano",
        "occurrences_by_month": "Ocorrências por mês",
        "species_temporal_comparison": "Comparação temporal entre as espécies mais registradas",
        "taxonomic_catalog": "Catálogo taxonômico",
        "search_scientific_name": "Buscar por nome científico",
        "scientific_name_placeholder": "Digite gênero ou espécie",
        "taxonomic_key": "Chave taxonômica",
        "scientific_name": "Nome científico",
        "country_comparison": "Comparação entre países",
        "first_country": "Primeiro país",
        "second_country": "Segundo país",
        "different_countries": "Selecione dois países diferentes para realizar a comparação.",
        "countries_without_data": "Não há dados armazenados para: {countries}. Selecione o país no filtro principal para executar sua primeira atualização.",
        "comparison_period": "Período da comparação",
        "species_code": "Espécies — {code}",
        "occurrences_code": "Ocorrências — {code}",
        "temporal_distribution": "Distribuição temporal",
        "annual_counts": "Contagens anuais",
        "country_sample_pct": "% da amostra do país",
        "normalized_annual_distribution": "Distribuição anual normalizada",
        "normalized_metrics": "Métricas normalizadas e cobertura",
        "records_per_species": "Registros por espécie",
        "years_with_records": "Anos com registros",
        "with_date_pct": "% com data",
        "with_coordinates_pct": "% com coordenadas",
        "shared_exclusive_species": "Espécies compartilhadas e exclusivas",
        "shared": "Compartilhadas",
        "exclusive_code": "Exclusivas — {code}",
        "jaccard_similarity": "Similaridade de Jaccard",
        "species_in_both": "Espécies presentes nos dois conjuntos",
        "exclusive_by_set": "Espécies exclusivas por conjunto",
        "methodological_caution": "<b>Cuidado metodológico.</b> Mais ocorrências ou espécies registradas não significam maior abundância nem maior biodiversidade real. A comparação usa amostras de {records_a} registros recebidos para {country_a} e {records_b} para {country_b}. Diferenças também refletem área, cobertura temporal, esforço de coleta, instituições participantes e frequência de publicação no GBIF. A curva normalizada mostra a distribuição interna da amostra, não corrige integralmente esses vieses.",
        "automatic_report": "Relatório automático",
        "report_description": "O PDF reproduz o recorte atual e reúne resumo, indicadores, gráficos, mapa, metodologia, limitações, fonte e data de geração.",
        "all_available_years": "Todos os anos disponíveis",
        "source_update": "Atualização da fonte",
        "query_summary": "**Consulta:** {country} · {period} · {occurrences} ocorrências · {species} espécies",
        "preparing_report": "Preparando relatório reproduzível...",
        "download_report": "Baixar relatório PDF",
        "report_signature": "A assinatura incluída no PDF identifica o conjunto de GBIF IDs usado. Para reproduzir o relatório, reaplique os filtros registrados usando a mesma fonte.",
        "last_load_usage": "Aproveitamento da última carga",
        "received": "Recebidos",
        "used": "Aproveitados",
        "discarded": "Descartados",
        "usage": "Aproveitamento",
        "without_species_level": "Sem identificação no nível de espécie: {count} registros.",
        "summary_unavailable": "O resumo detalhado não está disponível para esta carga. Os indicadores dos registros aproveitados permanecem abaixo.",
        "used_record_indicators": "Indicadores dos registros aproveitados",
        "missing_date": "Sem data",
        "monthly_date": "Data apenas mensal",
        "invalid_coordinates": "Coordenada ausente/inválida",
        "potential_duplicate": "Duplicidade potencial",
        "gbif_issue": "Problema indicado pelo GBIF",
        "potential_outside_country": "Possivelmente fora do país",
        "missing_locality": "Sem localidade",
        "unexpected_unit": "Unidade inesperada",
        "day": "Dia",
        "precision": "Precisão",
        "records": "Registros",
        "evidence_distribution": "Distribuição por tipo de evidência",
        "date_precision": "Precisão das datas",
        "occurrence_alerts": "Alertas de ocorrência",
        "taxonomic_alerts": "Alertas taxonômicos",
        "gbif_alert_note": "Alertas do GBIF registram interpretações e inconsistências potenciais. Eles não invalidam automaticamente uma ocorrência. Registros candidatos a duplicidade exigem revisão do evento de coleta antes de qualquer remoção.",
        "search_records": "Buscar nos registros",
        "search_records_placeholder": "Espécie, localidade ou unidade administrativa",
        "search_too_long": "A busca deve ter no máximo 200 caracteres.",
        "record_count": "{count} registros",
        "table_limited": "A tabela mostra os primeiros {shown} registros; o CSV preserva todo o recorte filtrado.",
        "download_csv": "Baixar CSV",
        "methodology_limitations": "Metodologia e limitações",
        "methodology_text": "Os pontos representam ocorrências publicadas no GBIF e filtradas pelo limite oficial da porção brasileira da Região Hidrográfica do Paraná. As contagens refletem coleta e publicação, não abundância biológica. A fonte atual é uma amostra de 5.000 registros do pré-filtro; comparações ecológicas exigem a base integral e controle do esforço amostral.",
        "footer": "FishScope · Dados de ocorrências fornecidos pelo GBIF.",
        "source_public_sample": "Amostra pública",
        "source_postgresql": "PostgreSQL",
        "source_csv": "CSV",
        "fallback_postgresql_csv": "PostgreSQL indisponível; exibindo os CSVs processados.",
        "fallback_database_csv": "DATABASE_URL ausente; exibindo os CSVs processados.",
        "fallback_public_sample": "PostgreSQL de produção indisponível; exibindo a amostra pública redistribuível em modo somente leitura.",
        "query_limited": "Consulta limitada a {shown} de {total} registros; use filtros ou uma consulta analítica para conjuntos maiores.",
        "progress_cache": "Consultando o cache PostgreSQL.",
        "progress_gbif": "Consultando ocorrências no GBIF.",
        "progress_collecting": "Coletando ocorrências: {collected}/{total}.",
        "progress_normalizing": "Normalizando táxons e ocorrências.",
        "progress_postgresql": "Atualizando o cache PostgreSQL.",
        "progress_complete": "Atualização concluída: {count} registros salvos.",
    },
    "en": {
        "language_selector": "Idioma / Language",
        "language_pt": "Português",
        "language_en": "English",
        "app_name": "FishScope",
        "home": "Home",
        "explore": "Explore",
        "compare": "Compare",
        "about": "About",
        "app_caption": "A platform for exploring and analyzing fish occurrence records.",
        "hero_title": "Explore fish occurrence records around the world.",
        "hero_description": "Explore species, geographic distributions, and records over time using public GBIF data.",
        "start_exploring": "Start exploring",
        "main_features": "Main features",
        "occurrence_map": "Occurrence map",
        "occurrence_map_description": "View the geographic distribution of records.",
        "temporal_analysis": "Temporal analysis",
        "temporal_analysis_description": "Explore how records are distributed over the years.",
        "data_quality": "Data quality",
        "data_quality_description": "Understand the coverage and limitations of the analyzed information.",
        "data_source": "Data provided by [GBIF](https://www.gbif.org/).",
        "compare_intro": "Country comparison remains available in the **Comparison** tab on the Explore page.",
        "compare_note": "This organization preserves the existing analysis while the comparison experience is prepared as a standalone page.",
        "open_comparison": "Open comparison in Explore",
        "about_intro": "A platform for exploring and analyzing public fish occurrence records provided by GBIF.",
        "in_development": "Project under development.",
        "filters": "Filters",
        "country": "Country",
        "select_country": "Select a country",
        "select_country_to_begin": "Select a country to begin.",
        "species": "Species",
        "origin": "Origin",
        "period": "Period",
        "record_type": "Record type",
        "administrative_unit": "Administrative unit",
        "all_species": "All species",
        "all_available_period": "All available periods",
        "all_classifications": "All classifications",
        "all_record_types": "All record types",
        "all_units": "All units",
        "apply_filters": "Apply filters",
        "clear_filters": "Clear filters",
        "advanced_filters": "Advanced filters",
        "data_administration": "Data administration",
        "active_filters": "Active filters",
        "records_found": "{count} records found",
        "selected_species_count": "{count} species selected",
        "selected_record_types_count": "{count} record types selected",
        "update_gbif": "Update data from GBIF",
        "update_help": "Set DATABASE_WRITE_URL to enable updates.",
        "update_disabled": "Updates disabled: write credentials are not configured.",
        "update_complete": "Update completed: {count} records.",
        "update_failed": "The data could not be updated: {message}",
        "unexpected_update_error": "Unexpected update failure.",
        "update_unavailable": "Update unavailable: set DATABASE_WRITE_URL with PostgreSQL write credentials. Regular queries only use DATABASE_URL.",
        "data_unavailable": "Data unavailable: {message}",
        "source_unavailable_error": "The data source is unavailable.",
        "selected_country": "Selected country: {name} ({code})",
        "parana_region_description": "Occurrences published for the Brazilian portion of the Paraná Hydrographic Region",
        "active_source": "Active source: {source}",
        "occurrences": "Occurrences",
        "covered_period": "Period",
        "last_update": "Last update",
        "source": "Source",
        "not_available": "Not available",
        "empty_filters": "No occurrences are available for {name} ({code}) with the selected filters.",
        "overview": "Overview",
        "map": "Map",
        "temporal": "Temporal",
        "comparison": "Comparison",
        "report": "Report",
        "quality": "Quality",
        "data": "Data",
        "native": "Native",
        "introduced": "Introduced",
        "conflicting": "Conflicting",
        "unknown": "Unknown",
        "not_informed": "Not informed",
        "most_recorded_species": "Most recorded species",
        "species_by_origin": "Species by origin",
        "map_view": "Map view",
        "map_points": "Points by species",
        "map_heat": "Heat map",
        "map_clusters": "Spatial aggregation",
        "map_aggregated": "<b>{map_occurrence_count} aggregated occurrences</b><br/>{map_species_count} species",
        "map_nearby": "<b>{elevationValue} nearby occurrences</b>",
        "map_responsive": "To keep the map responsive, {records} records were aggregated into up to {cells} spatial cells.",
        "no_coordinates": "The current selection has no valid coordinates.",
        "details_limited": "The detail selector shows the first {count} occurrences in the selection.",
        "occurrence_details": "Occurrence details",
        "select_occurrence": "Select an occurrence",
        "species_not_informed": "Species not informed",
        "family": "Family",
        "order": "Order",
        "date": "Date",
        "type": "Type",
        "unit": "Unit",
        "locality": "Locality",
        "informed_administrative_unit": "Reported administrative unit",
        "year": "Year",
        "month": "Month",
        "occurrences_by_year": "Occurrences by year",
        "occurrences_by_month": "Occurrences by month",
        "species_temporal_comparison": "Temporal comparison of the most recorded species",
        "taxonomic_catalog": "Taxonomic catalog",
        "search_scientific_name": "Search by scientific name",
        "scientific_name_placeholder": "Enter genus or species",
        "taxonomic_key": "Taxonomic key",
        "scientific_name": "Scientific name",
        "country_comparison": "Country comparison",
        "first_country": "First country",
        "second_country": "Second country",
        "different_countries": "Select two different countries to compare.",
        "countries_without_data": "No stored data are available for: {countries}. Select the country in the main filter to run its first update.",
        "comparison_period": "Comparison period",
        "species_code": "Species — {code}",
        "occurrences_code": "Occurrences — {code}",
        "temporal_distribution": "Temporal distribution",
        "annual_counts": "Annual counts",
        "country_sample_pct": "% of the country sample",
        "normalized_annual_distribution": "Normalized annual distribution",
        "normalized_metrics": "Normalized metrics and coverage",
        "records_per_species": "Records per species",
        "years_with_records": "Years with records",
        "with_date_pct": "% with date",
        "with_coordinates_pct": "% with coordinates",
        "shared_exclusive_species": "Shared and exclusive species",
        "shared": "Shared",
        "exclusive_code": "Exclusive — {code}",
        "jaccard_similarity": "Jaccard similarity",
        "species_in_both": "Species present in both datasets",
        "exclusive_by_set": "Exclusive species by dataset",
        "methodological_caution": "<b>Methodological caution.</b> More recorded occurrences or species do not mean greater abundance or actual biodiversity. The comparison uses samples of {records_a} records received for {country_a} and {records_b} for {country_b}. Differences also reflect area, temporal coverage, sampling effort, participating institutions, and publication frequency in GBIF. The normalized curve shows the sample's internal distribution and does not fully correct these biases.",
        "automatic_report": "Automatic report",
        "report_description": "The PDF reproduces the current selection and includes a summary, indicators, charts, map, methodology, limitations, source, and generation date.",
        "all_available_years": "All available years",
        "source_update": "Source update",
        "query_summary": "**Query:** {country} · {period} · {occurrences} occurrences · {species} species",
        "preparing_report": "Preparing reproducible report...",
        "download_report": "Download PDF report",
        "report_signature": "The signature included in the PDF identifies the set of GBIF IDs used. To reproduce the report, reapply the recorded filters using the same source.",
        "last_load_usage": "Latest load utilization",
        "received": "Received",
        "used": "Used",
        "discarded": "Discarded",
        "usage": "Utilization",
        "without_species_level": "Without species-level identification: {count} records.",
        "summary_unavailable": "A detailed summary is unavailable for this load. Indicators for the retained records are shown below.",
        "used_record_indicators": "Indicators for retained records",
        "missing_date": "Missing date",
        "monthly_date": "Month-level date only",
        "invalid_coordinates": "Missing/invalid coordinates",
        "potential_duplicate": "Potential duplicate",
        "gbif_issue": "Issue reported by GBIF",
        "potential_outside_country": "Possibly outside the country",
        "missing_locality": "Missing locality",
        "unexpected_unit": "Unexpected unit",
        "day": "Day",
        "precision": "Precision",
        "records": "Records",
        "evidence_distribution": "Distribution by evidence type",
        "date_precision": "Date precision",
        "occurrence_alerts": "Occurrence alerts",
        "taxonomic_alerts": "Taxonomic alerts",
        "gbif_alert_note": "GBIF alerts record potential interpretations and inconsistencies. They do not automatically invalidate an occurrence. Potential duplicate records require review of the sampling event before removal.",
        "search_records": "Search records",
        "search_records_placeholder": "Species, locality, or administrative unit",
        "search_too_long": "The search must contain at most 200 characters.",
        "record_count": "{count} records",
        "table_limited": "The table shows the first {shown} records; the CSV preserves the full filtered selection.",
        "download_csv": "Download CSV",
        "methodology_limitations": "Methodology and limitations",
        "methodology_text": "The points represent occurrences published in GBIF and filtered by the official boundary of the Brazilian portion of the Paraná Hydrographic Region. Counts reflect sampling and publication, not biological abundance. The current source is a sample of 5,000 pre-filter records; ecological comparisons require the complete dataset and control for sampling effort.",
        "footer": "FishScope · Occurrence data provided by GBIF.",
        "source_public_sample": "Public sample",
        "source_postgresql": "PostgreSQL",
        "source_csv": "CSV",
        "fallback_postgresql_csv": "PostgreSQL unavailable; displaying processed CSV files.",
        "fallback_database_csv": "DATABASE_URL missing; displaying processed CSV files.",
        "fallback_public_sample": "Production PostgreSQL unavailable; displaying the redistributable public sample in read-only mode.",
        "query_limited": "Query limited to {shown} of {total} records; use filters or an analytical query for larger datasets.",
        "progress_cache": "Checking the PostgreSQL cache.",
        "progress_gbif": "Querying occurrences in GBIF.",
        "progress_collecting": "Collecting occurrences: {collected}/{total}.",
        "progress_normalizing": "Normalizing taxa and occurrences.",
        "progress_postgresql": "Updating the PostgreSQL cache.",
        "progress_complete": "Update complete: {count} records saved.",
    },
}


def initialize_language() -> None:
    """Garante um idioma válido na sessão atual."""
    if st.session_state.get("language") not in SUPPORTED_LANGUAGES:
        st.session_state["language"] = DEFAULT_LANGUAGE
    if st.session_state.get(LANGUAGE_WIDGET_KEY) not in SUPPORTED_LANGUAGES:
        st.session_state[LANGUAGE_WIDGET_KEY] = st.session_state["language"]


def persist_selected_language() -> None:
    """Copia a escolha do widget para um estado que sobrevive entre páginas."""
    selected = st.session_state.get(LANGUAGE_WIDGET_KEY)
    if selected in SUPPORTED_LANGUAGES:
        st.session_state["language"] = selected


def current_language() -> str:
    """Retorna o código do idioma ativo, usando português como fallback."""
    language = st.session_state.get("language", DEFAULT_LANGUAGE)
    return language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def translate(key: str, language: str = DEFAULT_LANGUAGE, **values: Any) -> str:
    """Traduz uma chave sem depender do estado do Streamlit."""
    selected = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    template = TRANSLATIONS[selected].get(
        key, TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)
    )
    return template.format(**values) if values else template


def t(key: str, **values: Any) -> str:
    """Traduz uma chave usando o idioma persistido na sessão."""
    return translate(key, current_language(), **values)


def language_name(code: str) -> str:
    """Retorna o nome estável de uma opção de idioma."""
    return TRANSLATIONS[DEFAULT_LANGUAGE].get(f"language_{code}", code)


def format_integer(value: int) -> str:
    """Formata inteiros conforme o idioma ativo."""
    formatted = f"{value:,}"
    return formatted if current_language() == "en" else formatted.replace(",", ".")


def translate_source(source: str) -> str:
    """Traduz apenas rótulos conhecidos de fonte, preservando valores técnicos."""
    keys = {
        "Amostra pública": "source_public_sample",
        "PostgreSQL": "source_postgresql",
        "CSV": "source_csv",
    }
    return t(keys[source]) if source in keys else source


def translate_notice(message: str) -> str:
    """Traduz avisos produzidos pela camada de dados sem mudar sua lógica."""
    exact = {
        "PostgreSQL indisponivel; exibindo os CSVs processados.": "fallback_postgresql_csv",
        "DATABASE_URL ausente; exibindo os CSVs processados.": "fallback_database_csv",
        "PostgreSQL de produção indisponível; exibindo a amostra pública redistribuível em modo somente leitura.": "fallback_public_sample",
    }
    if message in exact:
        return t(exact[message])
    if message.startswith("Consulta limitada a "):
        numbers = message.replace(",", "").split()
        if len(numbers) >= 6:
            return t("query_limited", shown=numbers[3], total=numbers[5])
    return message


def translate_progress(message: str) -> str:
    """Traduz mensagens conhecidas do pipeline exibidas no progresso."""
    exact = {
        "Consultando o cache PostgreSQL.": "progress_cache",
        "Consultando ocorrências no GBIF.": "progress_gbif",
        "Normalizando táxons e ocorrências.": "progress_normalizing",
        "Atualizando o cache PostgreSQL.": "progress_postgresql",
    }
    if message in exact:
        return t(exact[message])
    if message.startswith("Coletando ocorrências: "):
        counts = message.removeprefix("Coletando ocorrências: ").removesuffix(".")
        collected, _, total = counts.partition("/")
        return t("progress_collecting", collected=collected, total=total)
    if message.startswith("Atualização concluída: "):
        count = message.removeprefix("Atualização concluída: ").split()[0]
        return t("progress_complete", count=count)
    return message


def translate_error(message: str, fallback_key: str) -> str:
    """Evita misturar mensagens técnicas em português na interface em inglês."""
    if current_language() == DEFAULT_LANGUAGE:
        return message
    exact = {
        "A fonte de dados não está disponível.": "source_unavailable_error",
        "Falha inesperada na atualização.": "unexpected_update_error",
        "A consulta ao GBIF excedeu o tempo limite.": "unexpected_update_error",
        "Não foi possível conectar à API do GBIF.": "unexpected_update_error",
        "A API do GBIF retornou uma resposta JSON inválida.": "unexpected_update_error",
        "A API do GBIF retornou um formato inesperado.": "unexpected_update_error",
    }
    return t(exact.get(message, fallback_key))

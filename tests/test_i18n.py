from unittest.mock import patch

from src.i18n import (
    SUPPORTED_LANGUAGES,
    TRANSLATIONS,
    format_integer,
    translate,
    translate_notice,
    translate_source,
)


def test_catalogos_de_traducao_tem_as_mesmas_chaves():
    assert set(TRANSLATIONS["pt"]) == set(TRANSLATIONS["en"])


def test_traducao_independente_da_sessao():
    assert translate("home", "pt") == "Início"
    assert translate("home", "en") == "Home"
    assert translate("select_country", "pt") == "Selecione um país"
    assert translate("clear_filters", "en") == "Clear filters"
    assert translate("all_available_period", "pt") == "Todo o período disponível"
    assert translate("occurrences_code", "en", code="BR") == "Occurrences — BR"


def test_idiomas_suportados():
    assert SUPPORTED_LANGUAGES == ("pt", "en")


def test_traduz_fonte_e_aviso_sem_alterar_valores_desconhecidos():
    with patch("src.i18n.current_language", return_value="en"):
        assert format_integer(1234) == "1,234"
        assert translate_source("Amostra pública") == "Public sample"
        assert translate_source("GBIF") == "GBIF"
        assert (
            translate_notice(
                "PostgreSQL de produção indisponível; exibindo a amostra pública "
                "redistribuível em modo somente leitura."
            )
            == "Production PostgreSQL unavailable; displaying the redistributable "
            "public sample in read-only mode."
        )

    with patch("src.i18n.current_language", return_value="pt"):
        assert format_integer(1234) == "1.234"

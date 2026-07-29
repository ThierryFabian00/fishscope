import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEM_FONTE_LOCAL = (PROJECT_ROOT / ".env").exists() or (
    PROJECT_ROOT / "data" / "processed" / "ocorrencias_peixes_bacia_parana.csv"
).exists()
TEM_DADOS_SUICA = (
    PROJECT_ROOT / "data" / "processed" / "ocorrencias_peixes_ch.csv"
).exists() and (PROJECT_ROOT / "data" / "processed" / "especies_peixes_ch.csv").exists()


class TestPaginaInicial(unittest.TestCase):
    def test_renderiza_inicio_sem_carregar_dashboard(self):
        app = AppTest.from_file(
            str(PROJECT_ROOT / "app" / "app.py"), default_timeout=30
        )

        app.run()

        self.assertFalse(app.exception)
        self.assertTrue(any(item.label == "Começar a explorar" for item in app.button))
        self.assertEqual(
            [item.value for item in app.subheader],
            ["Mapa de ocorrências", "Análise temporal", "Qualidade dos dados"],
        )
        self.assertFalse(app.tabs)
        self.assertFalse(app.metric)
        self.assertFalse(app.selectbox)

    def test_renderiza_paginas_auxiliares(self):
        comparar = AppTest.from_file(
            str(PROJECT_ROOT / "app" / "pages" / "compare.py")
        ).run()
        sobre = AppTest.from_file(
            str(PROJECT_ROOT / "app" / "pages" / "about.py")
        ).run()

        self.assertFalse(comparar.exception)
        self.assertEqual(comparar.title[0].value, "Comparar")
        self.assertTrue(
            any(
                item.label == "Abrir comparação em Explorar"
                for item in comparar.button
            )
        )
        self.assertFalse(sobre.exception)
        self.assertEqual(sobre.title[0].value, "Sobre")
        self.assertEqual(sobre.subheader[0].value, "FishScope")


@unittest.skipUnless(
    TEM_FONTE_LOCAL,
    "Dashboard exige PostgreSQL configurado ou CSVs processados.",
)
class TestStreamlitApp(unittest.TestCase):
    def test_renderiza_dashboard_sem_excecoes(self):
        app = AppTest.from_file(
            str(PROJECT_ROOT / "app" / "pages" / "1_Explorar.py"),
            default_timeout=90,
        )

        app.run()

        self.assertFalse(app.exception)
        self.assertEqual(app.title[0].value, "FishScope")
        self.assertTrue(
            any(
                item.value
                == "Plataforma para exploração e análise de ocorrências de peixes."
                for item in app.caption
            )
        )
        self.assertEqual(
            [aba.label for aba in app.tabs],
            [
                "Visão geral",
                "Mapa",
                "Temporal",
                "Espécies",
                "Comparação",
                "Relatório",
                "Qualidade",
                "Dados",
            ],
        )
        metricas = {metrica.label: metrica.value for metrica in app.metric}
        self.assertEqual(metricas["Ocorrências"], "3.764")
        self.assertEqual(metricas["Espécies"], "352")
        self.assertEqual(metricas["Fonte"], "PostgreSQL")
        self.assertNotEqual(metricas["Última atualização"], "Não disponível")
        self.assertEqual(metricas["Recebidos"], "5.000")
        self.assertEqual(metricas["Aproveitados"], "3.764")
        self.assertEqual(metricas["Descartados"], "1.236")
        self.assertEqual(metricas["Aproveitamento"], "75.3%")
        self.assertEqual(metricas["Duplicidade potencial"], "1.299")
        seletor_pais = next(item for item in app.selectbox if item.label == "País")
        self.assertEqual(seletor_pais.value, "BR")
        self.assertEqual(app.radio[0].label, "Visualização do mapa")
        self.assertEqual(app.radio[0].value, "Pontos por espécie")
        self.assertEqual(
            app.radio[0].options,
            ["Pontos por espécie", "Mapa de calor", "Agrupamento espacial"],
        )
        self.assertTrue(
            any(item.label == "Detalhes de uma ocorrência" for item in app.selectbox)
        )
        self.assertEqual(app.text_input[0].label, "Buscar por nome científico")
        self.assertTrue(any(item.label == "Primeiro país" for item in app.selectbox))
        self.assertTrue(any(item.label == "Segundo país" for item in app.selectbox))
        self.assertIn("Compartilhadas", metricas)
        self.assertTrue(
            any(
                item.label == "Baixar relatório PDF"
                for item in app.get("download_button")
            )
        )

        app.radio[0].set_value("Mapa de calor").run()
        self.assertFalse(app.exception)
        app.radio[0].set_value("Agrupamento espacial").run()
        self.assertFalse(app.exception)

        opcoes_especies = app.multiselect[0].options
        self.assertGreaterEqual(len(opcoes_especies), 2)
        app.multiselect[0].set_value(opcoes_especies[:2]).run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.multiselect[0].value), 2)
        metricas_filtradas = {metrica.label: metrica.value for metrica in app.metric}
        self.assertEqual(metricas_filtradas["Espécies"], "2")
        self.assertLess(int(metricas_filtradas["Ocorrências"].replace(".", "")), 3764)

        app.multiselect[0].set_value([]).run()
        for rotulo in ("Origem", "Tipo de registro", "Unidade administrativa"):
            seletor = next(item for item in app.multiselect if item.label == rotulo)
            self.assertGreater(len(seletor.options), 0)
            seletor.set_value([seletor.options[0]]).run()
            self.assertFalse(app.exception)
            seletor_atual = next(
                item for item in app.multiselect if item.label == rotulo
            )
            self.assertEqual(len(seletor_atual.value), 1)
            seletor_atual.set_value([]).run()

        periodo = next(item for item in app.slider if item.label == "Período")
        periodo.set_range(periodo.min, periodo.min).run()
        self.assertFalse(app.exception)
        periodo_atual = next(item for item in app.slider if item.label == "Período")
        self.assertEqual(list(periodo_atual.value), [periodo.min, periodo.min])
        periodo_atual.set_range(periodo_atual.min, periodo_atual.max).run()

        seletor_pais = next(item for item in app.selectbox if item.label == "País")
        seletor_pais.set_value("CH").run()

        self.assertFalse(app.exception)
        self.assertEqual(app.title[0].value, "FishScope")
        if TEM_DADOS_SUICA:
            metricas_suica = {metrica.label: metrica.value for metrica in app.metric}
            self.assertEqual(metricas_suica["Ocorrências"], "4.802")
            self.assertEqual(metricas_suica["Espécies"], "61")
            self.assertEqual(len(app.multiselect[0].options), 61)
            self.assertFalse(app.info)
        else:
            self.assertTrue(any("Suíça (CH)" in item.value for item in app.info))


if __name__ == "__main__":
    unittest.main()

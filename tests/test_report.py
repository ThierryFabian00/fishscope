import re
import unittest
from datetime import datetime, timezone

import pandas as pd

from src.dashboard_data import normalizar_dados
from src.report import assinatura_registros, gerar_relatorio_pdf


def ocorrencias_relatorio() -> pd.DataFrame:
    return normalizar_dados(
        pd.DataFrame(
            [
                {
                    "gbif_id": 20,
                    "species_key": "B",
                    "canonical_name": "Species beta",
                    "family": "Betaidae",
                    "order_name": "Betaformes",
                    "origin_status": "INTRODUCED",
                    "iucn_category": "LC",
                    "event_date": "2022-03-01",
                    "date_precision": "DAY",
                    "event_year": 2022,
                    "event_month": 3,
                    "decimal_latitude": -23.1,
                    "decimal_longitude": -51.2,
                    "state_province": "PR",
                    "locality": "Rio Beta",
                    "basis_of_record": "HUMAN_OBSERVATION",
                    "taxonomic_issues": "",
                    "occurrence_issues": "",
                },
                {
                    "gbif_id": 10,
                    "species_key": "A",
                    "canonical_name": "Species alpha",
                    "family": "Alphaidae",
                    "order_name": "Alphaformes",
                    "origin_status": "NATIVE",
                    "iucn_category": "LC",
                    "event_date": "2021-02-01",
                    "date_precision": "MONTH",
                    "event_year": 2021,
                    "event_month": 2,
                    "decimal_latitude": -22.7,
                    "decimal_longitude": -50.9,
                    "state_province": "SP",
                    "locality": "Rio Alpha",
                    "basis_of_record": "PRESERVED_SPECIMEN",
                    "taxonomic_issues": "",
                    "occurrence_issues": "COORDINATE_ROUNDED",
                },
            ]
        )
    )


class TestRelatorioPDF(unittest.TestCase):
    def setUp(self):
        self.dados = ocorrencias_relatorio()

    def test_assinatura_independe_da_ordem_dos_registros(self):
        assinatura = assinatura_registros(self.dados)
        invertidos = self.dados.iloc[::-1].reset_index(drop=True)

        self.assertEqual(assinatura, assinatura_registros(invertidos))
        self.assertEqual(len(assinatura), 16)

    def test_gera_pdf_reproduzivel_com_tres_paginas(self):
        pdf = gerar_relatorio_pdf(
            self.dados,
            pais_nome="Brasil",
            pais_codigo="BR",
            fonte="Teste",
            filtros={
                "País": "Brasil (BR)",
                "Espécies": "Todas as espécies",
                "Período": "2021–2022",
            },
            gerado_em=datetime(2026, 7, 26, 12, 0, tzinfo=timezone.utc),
        )

        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertIn(b"FishScope", pdf)
        self.assertGreater(len(pdf), 20_000)
        self.assertGreaterEqual(len(re.findall(rb"/Type /Page\b", pdf)), 3)

    def test_rejeita_recorte_vazio(self):
        with self.assertRaisesRegex(ValueError, "sem ocorrências"):
            gerar_relatorio_pdf(
                self.dados.iloc[0:0],
                pais_nome="Brasil",
                pais_codigo="BR",
                fonte="Teste",
                filtros={},
            )


if __name__ == "__main__":
    unittest.main()

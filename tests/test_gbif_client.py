import unittest
from unittest.mock import Mock

import requests

from src.config import TIMEOUT_GBIF_SEGUNDOS
from src.gbif_client import ErroGBIF, criar_sessao, requisitar_json


class TestClienteGBIF(unittest.TestCase):
    def test_configura_retentativas_com_backoff(self):
        sessao = criar_sessao(tentativas=4, backoff=1.25)
        retentativas = sessao.get_adapter("https://").max_retries

        self.assertEqual(retentativas.total, 4)
        self.assertEqual(retentativas.backoff_factor, 1.25)
        self.assertIn(503, retentativas.status_forcelist)

    def test_converte_timeout_em_erro_controlado(self):
        sessao = Mock()
        sessao.get.side_effect = requests.Timeout()

        with self.assertRaisesRegex(ErroGBIF, "tempo limite"):
            requisitar_json(sessao, "https://api.gbif.org/v1/test", {})

        sessao.get.assert_called_once_with(
            "https://api.gbif.org/v1/test",
            params={},
            timeout=TIMEOUT_GBIF_SEGUNDOS,
        )

    def test_converte_api_indisponivel_em_erro_controlado(self):
        sessao = Mock()
        sessao.get.side_effect = requests.ConnectionError("serviço indisponível")

        with self.assertRaisesRegex(ErroGBIF, "Não foi possível conectar"):
            requisitar_json(sessao, "https://api.gbif.org/v1/test", {})

    def test_informa_codigo_do_erro_http(self):
        sessao = Mock()
        resposta = Mock(status_code=503)
        sessao.get.return_value.raise_for_status.side_effect = requests.HTTPError(
            response=resposta
        )

        with self.assertRaisesRegex(ErroGBIF, "erro HTTP 503"):
            requisitar_json(sessao, "https://api.gbif.org/v1/test", {})


if __name__ == "__main__":
    unittest.main()

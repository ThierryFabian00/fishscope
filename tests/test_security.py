import io
import logging
import unittest

from src.security import FiltroSegredos, mensagem_erro_segura, sanitizar_texto


class TestSeguranca(unittest.TestCase):
    def test_remove_credenciais_de_url_e_segredos_nomeados(self):
        texto = (
            "falha em postgresql://alice:senha-super-secreta@db:5432/base "
            "password=outra-senha token:abc123"
        )

        seguro = sanitizar_texto(texto)

        self.assertIn("postgresql://alice:***@db:5432/base", seguro)
        self.assertIn("password=***", seguro)
        self.assertIn("token=***", seguro)
        for segredo in ("senha-super-secreta", "outra-senha", "abc123"):
            self.assertNotIn(segredo, seguro)

    def test_filtro_de_logging_nao_registra_senha(self):
        saida = io.StringIO()
        manipulador = logging.StreamHandler(saida)
        manipulador.addFilter(FiltroSegredos())
        logger = logging.getLogger("teste.seguranca")
        logger.handlers = [manipulador]
        logger.propagate = False
        logger.setLevel(logging.INFO)

        logger.error("conexão %s", "postgresql://bob:segredo@localhost/base")

        self.assertIn("postgresql://bob:***@localhost/base", saida.getvalue())
        self.assertNotIn("segredo", saida.getvalue())

    def test_mensagem_vazia_usa_fallback_controlado(self):
        self.assertEqual(
            mensagem_erro_segura(RuntimeError(""), "Falha controlada."),
            "Falha controlada.",
        )


if __name__ == "__main__":
    unittest.main()

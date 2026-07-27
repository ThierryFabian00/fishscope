"""Redação de segredos antes de exibir ou registrar mensagens de erro."""

import logging
import re
from typing import Any

PADRAO_CREDENCIAL_URL = re.compile(
    r"(?P<scheme>[a-z][a-z0-9+.-]*://)(?P<user>[^\s:/@]+):(?P<secret>[^\s@]+)@",
    flags=re.IGNORECASE,
)
PADRAO_SEGREDO_NOMEADO = re.compile(
    r"(?P<name>password|passwd|pwd|secret|token)\s*[=:]\s*(?P<secret>[^\s,;]+)",
    flags=re.IGNORECASE,
)


def sanitizar_texto(valor: Any) -> str:
    texto = str(valor)
    texto = PADRAO_CREDENCIAL_URL.sub(
        lambda item: f"{item.group('scheme')}{item.group('user')}:***@", texto
    )
    return PADRAO_SEGREDO_NOMEADO.sub(lambda item: f"{item.group('name')}=***", texto)


def mensagem_erro_segura(erro: BaseException, padrao: str) -> str:
    mensagem = sanitizar_texto(erro).strip()
    return mensagem or padrao


class FiltroSegredos(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = sanitizar_texto(record.getMessage())
        record.args = ()
        if record.exc_text:
            record.exc_text = sanitizar_texto(record.exc_text)
        return True

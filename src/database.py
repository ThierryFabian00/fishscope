"""Configuração compartilhada para acesso ao PostgreSQL."""

import os
import re
from dataclasses import dataclass
from pathlib import Path

from src.config import ARQUIVO_ENV, SCHEMA_PADRAO, carregar_ambiente


def validar_schema(schema: str) -> str:
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", schema):
        raise ValueError(
            "Schema invalido. Use apenas letras minusculas, numeros e underscore."
        )
    return schema


@dataclass(frozen=True)
class ConfiguracaoBanco:
    database_url: str | None
    schema: str
    database_write_url: str | None = None

    @classmethod
    def do_ambiente(
        cls,
        caminho: Path = ARQUIVO_ENV,
        schema: str | None = None,
    ) -> "ConfiguracaoBanco":
        carregar_ambiente(caminho)
        return cls(
            database_url=os.getenv("DATABASE_URL"),
            schema=validar_schema(schema or os.getenv("DB_SCHEMA", SCHEMA_PADRAO)),
            database_write_url=os.getenv("DATABASE_WRITE_URL"),
        )

    def exigir_url(self) -> str:
        if not self.database_url:
            raise ValueError(
                "DATABASE_URL nao definida. Crie .env a partir de .env.example."
            )
        return self.database_url

    def exigir_url_escrita(self) -> str:
        if not self.database_write_url:
            raise ValueError(
                "DATABASE_WRITE_URL não definida. A atualização exige uma "
                "credencial PostgreSQL de escrita separada."
            )
        return self.database_write_url

"""
Utilitários compartilhados pelos testes.
"""

import re
from pathlib import Path

import pytest

SCHEMA_SQL = Path(__file__).resolve().parents[2] / "schema.sql"


def colunas_do_schema(tabela: str) -> dict[str, dict]:
    """
    Lê o CREATE TABLE da tabela no schema.sql (a transcrição da Apostila IV) e devolve, para cada
    coluna: tipo, tamanho/precisão, se aceita nulo e o valor padrão.
    """
    texto = SCHEMA_SQL.read_text(encoding="utf-8")
    bloco = re.search(rf"CREATE TABLE {tabela} \((.*?)\n\);", texto, re.S)
    assert bloco, f"tabela {tabela} não encontrada no schema.sql"

    colunas = {}
    for linha in bloco.group(1).splitlines():
        linha = linha.split("--")[0].strip().rstrip(",")
        m = re.match(r"([a-z_]+)\s+([A-Z]+)(?:\((\d+)(?:,(\d+))?\))?(.*)", linha)
        if not m or m.group(1) in {"constraint", "primary"} or linha.startswith("CONSTRAINT"):
            continue
        nome, tipo, tamanho, escala, resto = m.groups()
        padrao = re.search(r"DEFAULT\s+(\S+)", resto)
        colunas[nome] = {
            "tipo": tipo,
            "tamanho": int(tamanho) if tamanho else None,
            "escala": int(escala) if escala else None,
            "nulo": "NOT NULL" not in resto and "PRIMARY KEY" not in resto,
            "padrao": padrao.group(1) if padrao else None,
        }
    return colunas


@pytest.fixture(autouse=True)
def _hash_de_senha_rapido_nos_testes(settings):
    """
    O hash de senha de verdade (PBKDF2) é lento de propósito. Nos testes usamos um rápido, só para
    a suíte não demorar; o sistema real continua com o padrão do Django
    (test_rnf12_sistema_usa_o_hash_de_senha_forte_do_django garante isso).
    """
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

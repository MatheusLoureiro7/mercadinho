"""
Utilitários compartilhados pelos testes.
"""

import re
from pathlib import Path

import pytest
from django.db import connection

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


# Tipo no schema.sql → como o PostgreSQL descreve em information_schema.columns
TIPOS_POSTGRES = {
    "SERIAL": "integer",
    "INTEGER": "integer",
    "SMALLINT": "smallint",
    "VARCHAR": "character varying",
    "NUMERIC": "numeric",
    "BOOLEAN": "boolean",
    "DATE": "date",
    "TIMESTAMPTZ": "timestamp with time zone",
    "TEXT": "text",
    "JSONB": "jsonb",
}


def colunas_no_banco(tabela: str) -> dict[str, dict]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name, data_type, character_maximum_length, numeric_precision,
                   numeric_scale, is_nullable, column_default, is_identity
              FROM information_schema.columns
             WHERE table_schema = 'public' AND table_name = %s
            """,
            [tabela],
        )
        return {
            nome: {
                "tipo": tipo,
                "tamanho": tamanho or precisao,
                "escala": escala,
                "nulo": nulo == "YES",
                "padrao": padrao,
                "identidade": identidade == "YES",
            }
            for nome, tipo, tamanho, precisao, escala, nulo, padrao, identidade in cursor.fetchall()
        }


def restricoes(tabela: str) -> set[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT conname FROM pg_constraint WHERE conrelid = %s::regclass",
            [tabela],
        )
        return {linha[0] for linha in cursor.fetchall()}


def divergencias_do_schema(tabela: str) -> list[str]:
    """
    Compara a tabela criada pelas migrações com o CREATE TABLE do schema.sql (Apostila IV) e
    devolve a lista do que difere: colunas a mais ou a menos, tipo, tamanho, casas decimais,
    obrigatoriedade e valor padrão. Lista vazia = igual à apostila.
    """
    esperado, real = colunas_do_schema(tabela), colunas_no_banco(tabela)
    erros = [f"coluna fora da apostila: {c}" for c in sorted(set(real) - set(esperado))]
    erros += [f"coluna da apostila ausente: {c}" for c in sorted(set(esperado) - set(real))]
    for nome in sorted(set(esperado) & set(real)):
        e, r = esperado[nome], real[nome]
        if r["tipo"] != TIPOS_POSTGRES[e["tipo"]]:
            erros.append(f"{nome}: tipo {r['tipo']}, apostila {e['tipo']}")
        if e["tamanho"] and r["tamanho"] != e["tamanho"]:
            erros.append(f"{nome}: tamanho {r['tamanho']}, apostila {e['tamanho']}")
        if e["escala"] is not None and r["escala"] != e["escala"]:
            erros.append(f"{nome}: casas decimais {r['escala']}, apostila {e['escala']}")
        if r["nulo"] != e["nulo"]:
            erros.append(f"{nome}: aceita nulo? {r['nulo']}, apostila {e['nulo']}")
        if e["tipo"] == "SERIAL":
            # SERIAL e IDENTITY são o mesmo inteiro sequencial; o Django gera IDENTITY.
            if not (r["identidade"] or (r["padrao"] or "").startswith("nextval")):
                erros.append(f"{nome}: sem sequência")
        elif (r["padrao"] or "").lower() != (e["padrao"] or "").lower():
            erros.append(f"{nome}: padrão {r['padrao']}, apostila {e['padrao']}")
    return erros


def indices(tabela: str) -> dict[str, str]:
    """Nome → definição (CREATE INDEX ...) de cada índice da tabela."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT indexname, indexdef FROM pg_indexes WHERE tablename = %s", [tabela])
        return dict(cursor.fetchall())


@pytest.fixture(autouse=True)
def _hash_de_senha_rapido_nos_testes(settings):
    """
    O hash de senha de verdade (PBKDF2) é lento de propósito. Nos testes usamos um rápido, só para
    a suíte não demorar; o sistema real continua com o padrão do Django
    (test_rnf12_sistema_usa_o_hash_de_senha_forte_do_django garante isso).
    """
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

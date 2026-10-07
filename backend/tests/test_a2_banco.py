"""
Tarefa A2 — o banco de dados está no ar e a ferramenta de migração funciona.

Precisa do PostgreSQL rodando: docker compose up -d
"""

from io import StringIO

import pytest
from django.core.management import call_command
from django.db import connection


@pytest.mark.django_db
def test_a2_conecta_no_postgresql():
    # Apostila IV: PostgreSQL. Nunca SQLite, nem "só para testar".
    assert connection.vendor == "postgresql"
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,)


@pytest.mark.django_db
def test_a2_versao_do_postgresql_suporta_coluna_gerada():
    # fechamento_caixa.diferenca é GENERATED ALWAYS AS ... STORED (RN15): exige PostgreSQL 12+.
    assert connection.pg_version >= 120000


@pytest.mark.django_db
def test_a2_nao_ha_migracao_pendente():
    # Todo model alterado precisa vir acompanhado da sua migração no mesmo commit.
    saida = StringIO()
    call_command("makemigrations", "--check", "--dry-run", stdout=saida)
    assert "No changes detected" in saida.getvalue()

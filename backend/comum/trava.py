"""
Trava entre processos — revisão X1, item 16.

A importação e os avisos conferem ("o dia já entrou?", "já avisei hoje?") e depois gravam. Duas
rodadas ao mesmo tempo (o cron e alguém rodando o comando à mão) conferiam juntas e gravavam em
dobro. A trava é do próprio PostgreSQL (pg_advisory_xact_lock), sem tabela nem dependência nova:
quem chega depois espera a transação de quem chegou antes terminar, e então confere de novo.

    with transaction.atomic():
        travar("importacao_das_vendas")
        ... confere e grava ...
"""

from django.db import connection


def travar(nome: str) -> None:
    """Espera a vez. Só vale dentro de transaction.atomic(): solta sozinha no fim da transação."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", [nome])

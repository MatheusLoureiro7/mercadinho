"""
Tarefa C4 — RN01: a view de saldo, copiada literalmente do schema.sql (Apostila IV).
O teste test_rn01_view_de_saldo_e_identica_a_do_schema confere que continua igual.
"""

import django.db.models.deletion
from django.db import migrations, models

CRIAR_VIEW = """
CREATE VIEW vw_estoque_atual AS
SELECT
    p.id                AS produto_id,
    p.nome              AS produto_nome,
    p.unidade_medida,
    p.estoque_minimo,
    COALESCE(SUM(
        CASE m.tipo
            WHEN 'ENTRADA' THEN  m.quantidade
            WHEN 'AJUSTE'  THEN  m.quantidade
            WHEN 'VENDA'   THEN -m.quantidade
            WHEN 'PERDA'   THEN -m.quantidade
        END
    ), 0)               AS saldo
FROM produto p
LEFT JOIN movimentacao m ON m.produto_id = p.id
GROUP BY p.id, p.nome, p.unidade_medida, p.estoque_minimo;

COMMENT ON VIEW vw_estoque_atual IS
    'RN01. Todo número desta view pode ser explicado linha a linha pelas movimentações que o geraram.';
"""


class Migration(migrations.Migration):
    dependencies = [
        ("cadastro", "0001_initial"),
        ("estoque", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(CRIAR_VIEW, reverse_sql="DROP VIEW vw_estoque_atual;"),
        migrations.CreateModel(
            name="EstoqueAtual",
            fields=[
                (
                    "produto",
                    models.OneToOneField(
                        db_column="produto_id",
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        primary_key=True,
                        related_name="estoque_atual",
                        serialize=False,
                        to="cadastro.produto",
                    ),
                ),
                ("produto_nome", models.CharField(max_length=160)),
                ("unidade_medida", models.CharField(max_length=10)),
                ("estoque_minimo", models.DecimalField(decimal_places=3, max_digits=12, null=True)),
                ("saldo", models.DecimalField(decimal_places=3, max_digits=14)),
            ],
            options={"db_table": "vw_estoque_atual", "managed": False},
        ),
    ]

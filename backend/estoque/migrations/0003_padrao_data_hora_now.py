"""
Revisão X1, item 19 (16/11/2026): o padrão de movimentacao.data_hora é NOW(), como no schema.sql.

A 0001 foi editada depois de aplicada (para usar `Agora()`, que é NOW()); o banco criado antes
ficou com statement_timestamp(). Num banco criado do zero esta migração não muda nada.
"""

from django.db import migrations

ACERTA_O_PADRAO = "ALTER TABLE movimentacao ALTER COLUMN data_hora SET DEFAULT NOW()"


class Migration(migrations.Migration):
    dependencies = [("estoque", "0002_vw_estoque_atual")]

    operations = [migrations.RunSQL(ACERTA_O_PADRAO, reverse_sql=migrations.RunSQL.noop)]

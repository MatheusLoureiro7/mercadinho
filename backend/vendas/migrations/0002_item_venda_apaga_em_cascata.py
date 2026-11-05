"""
schema.sql: item_venda.venda_id ... REFERENCES venda(id) ON DELETE CASCADE.

O Django 5 cria a chave estrangeira sem ação no banco (o CASCADE dele acontece só no Python).
Esta migração recria a chave com ON DELETE CASCADE, para valer também fora do Django, como na
Apostila IV. O nome da chave é gerado pelo Django; por isso é procurado no catálogo.
"""

from django.db import migrations

TROCAR_ACAO = """
DO $$
DECLARE nome text;
BEGIN
    SELECT conname INTO nome FROM pg_constraint
     WHERE conrelid = 'item_venda'::regclass AND contype = 'f' AND confrelid = 'venda'::regclass;
    EXECUTE format('ALTER TABLE item_venda DROP CONSTRAINT %I', nome);
    EXECUTE format(
        'ALTER TABLE item_venda ADD CONSTRAINT %I FOREIGN KEY (venda_id) REFERENCES venda(id) '
        'ON DELETE {acao} DEFERRABLE INITIALLY DEFERRED', nome);
END $$;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("vendas", "0001_vendas"),
    ]

    operations = [
        migrations.RunSQL(
            TROCAR_ACAO.format(acao="CASCADE"),
            reverse_sql=TROCAR_ACAO.format(acao="NO ACTION"),
        ),
    ]

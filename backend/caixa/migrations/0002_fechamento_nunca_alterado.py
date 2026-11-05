"""
RN15: "Não existe UPDATE nem DELETE nesta tabela. A API só aceita INSERT." (Apostila I)

A API já não oferece alterar nem apagar; este gatilho garante o mesmo no próprio banco, para
ninguém "corrigir" um fechamento por fora do sistema. Correção é sempre um registro novo.
"""

from django.db import migrations

CRIAR = """
CREATE FUNCTION fechamento_caixa_nunca_alterado() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'RN15: fechamento de caixa não se altera nem se apaga; registre um novo.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tg_fechamento_nunca_alterado
    BEFORE UPDATE OR DELETE ON fechamento_caixa
    FOR EACH ROW EXECUTE FUNCTION fechamento_caixa_nunca_alterado();
"""

DESFAZER = """
DROP TRIGGER tg_fechamento_nunca_alterado ON fechamento_caixa;
DROP FUNCTION fechamento_caixa_nunca_alterado();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("caixa", "0001_fechamento_caixa"),
    ]

    operations = [migrations.RunSQL(CRIAR, reverse_sql=DESFAZER)]

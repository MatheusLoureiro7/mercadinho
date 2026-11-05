"""
Caixa — fechamento de caixa. Tarefa I1.

Tabela (schema.sql): fechamento_caixa — colunas, tipos e padrões exatamente como na Apostila IV.
Regra: RN15 — a diferença é calculada pelo banco (coluna gerada), nunca digitada; o registro nunca é
alterado nem apagado: correção é um registro novo. O banco recusa UPDATE e DELETE (migração 0002).
"""

from django.conf import settings
from django.db import models
from django.db.models import F

from comum.sql import Agora


class FechamentoCaixa(models.Model):
    data = models.DateField()
    valor_sistema = models.DecimalField(max_digits=12, decimal_places=2)
    valor_contado = models.DecimalField(max_digits=12, decimal_places=2)
    diferenca = models.GeneratedField(
        expression=F("valor_contado") - F("valor_sistema"),
        output_field=models.DecimalField(max_digits=12, decimal_places=2),
        db_persist=True,
    )
    registrado_por = models.ForeignKey(  # RN15: "com data e responsável"
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="fechamentos",
        db_column="registrado_por",  # schema.sql: a coluna se chama registrado_por, sem _id
    )
    registrado_em = models.DateTimeField(db_default=Agora())

    class Meta:
        db_table = "fechamento_caixa"

    def __str__(self):
        return f"Fechamento de {self.data:%d/%m/%Y}: diferença {self.diferenca}"

"""
Comum — parâmetros das regras. Tarefa F1 (L21: a tabela parametro não tinha tarefa no roteiro).

Tabela (schema.sql): parametro — exatamente como na Apostila IV.
"Números das regras que NÃO ficam fixos no código" (Apostila I, seção 7). Os valores iniciais
ainda não foram validados com o cliente.
"""

from django.db import models
from django.utils import timezone

from comum.sql import Agora


class Parametro(models.Model):
    chave = models.CharField(max_length=60, primary_key=True)
    valor = models.CharField(max_length=80)
    descricao = models.CharField(max_length=200, null=True, blank=True)  # noqa: DJ001 — nulo no schema.sql
    atualizado_em = models.DateTimeField(db_default=Agora())

    class Meta:
        db_table = "parametro"
        ordering = ["chave"]

    def __str__(self):
        return f"{self.chave} = {self.valor}"

    def save(self, *args, **kwargs):
        if self.pk is not None and not self._state.adding:
            self.atualizado_em = timezone.now()
        super().save(*args, **kwargs)

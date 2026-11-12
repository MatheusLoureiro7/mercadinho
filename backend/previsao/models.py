"""
Previsão — consumo diário e previsão por produto.

Tabelas (schema.sql): consumo_diario, previsao_produto.
Regras: RN06–RN09, RN11.

Os models entram nas tarefas G1, G3 do docs/ROTEIRO.md, com os nomes exatos do schema.sql.
"""

from django.db import models
from django.db.models import Q

from cadastro.models import Produto


class ConsumoDiario(models.Model):
    """
    Quanto cada produto vendeu em cada dia da loja — tarefa G1. Dado derivado: a rotina de
    agregação (`previsao.agregacao`) regrava a partir das vendas, e pode ser apagado sem perda.

    RN11: só entra venda; perda fica de fora. Só dia com venda vira linha.
    `dia_semana` (L27): 0 = domingo … 6 = sábado, como o EXTRACT(DOW) do PostgreSQL.
    """

    pk = models.CompositePrimaryKey("produto_id", "data")
    # Sem índice próprio: a chave primária já começa por produto_id.
    produto = models.ForeignKey(
        Produto, on_delete=models.PROTECT, db_index=False, related_name="consumo_diario"
    )
    data = models.DateField()
    quantidade_vendida = models.DecimalField(max_digits=12, decimal_places=3, db_default=0)
    dia_semana = models.SmallIntegerField()  # RN07

    class Meta:
        db_table = "consumo_diario"
        constraints = [
            models.CheckConstraint(condition=Q(dia_semana__gte=0, dia_semana__lte=6), name="ck_consumo_dia"),
        ]

    def __str__(self):
        return f"{self.produto} vendeu {self.quantidade_vendida} em {self.data:%d/%m/%Y}"


class PrevisaoProduto(models.Model):
    """
    O resultado da previsão de cada produto, regravado na rodada das 03h00 — tarefa G3. Dado
    derivado, como consumo_diario: pode ser apagado e recalculado (`previsao.projecao`).

    `consumo_por_dia_semana` (RN07): {"0": "5.000", … "6": "26.000"}, 0 = domingo (L27), valor em
    texto para não perder as casas decimais. `calculado_em` nulo = ainda aprendendo (RN09, G4).
    """

    produto = models.OneToOneField(
        Produto, on_delete=models.PROTECT, primary_key=True, related_name="previsao"
    )
    consumo_medio_diario = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)  # RN06
    consumo_por_dia_semana = models.JSONField(null=True, blank=True)  # RN07
    dias_ate_acabar = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True)
    ponto_pedido = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)  # RN08
    sugestao_compra = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)  # RF11
    calculado_em = models.DateTimeField(null=True, blank=True)  # RN09: nulo = ainda aprendendo

    class Meta:
        db_table = "previsao_produto"

    def __str__(self):
        return f"Previsão de {self.produto}"

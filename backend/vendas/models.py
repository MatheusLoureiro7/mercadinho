"""
Vendas — venda, item de venda e importação do caixa. Tarefa E2.

Tabelas (schema.sql): venda, item_venda, importacao_pdv — colunas, tipos, padrões e restrições
exatamente como na Apostila IV, seção 6. Regras que usam estas tabelas: RN01 e RN02 (baixa por
venda, E3), e o consumo da previsão, que lê só a movimentação VENDA (RN11, G1).

O sistema NÃO registra venda pela tela: venda só nasce do arquivo exportado pelo caixa da loja
(importador, fluxograma 04). O caixa continua sendo o caixa (R05); o sistema só lê o arquivo.
"""

from django.db import models
from django.db.models import Q

from cadastro.models import Produto


class Venda(models.Model):
    """Uma venda registrada no caixa da loja, trazida pelo importador (E3)."""

    data_hora = models.DateTimeField()
    valor_total = models.DecimalField(max_digits=12, decimal_places=2)
    forma_pagamento = models.CharField(max_length=30, null=True, blank=True)  # noqa: DJ001 — opcional no schema.sql

    class Meta:
        db_table = "venda"

    def __str__(self):
        return f"Venda {self.pk} de {self.data_hora:%d/%m/%Y %H:%M}"


class ItemVenda(models.Model):
    """
    Uma linha do arquivo do caixa. `produto` fica nulo quando a linha não casou com nenhum produto
    cadastrado (E4); a linha pendente NÃO trava as demais (fluxograma 04).
    """

    # schema.sql: ON DELETE CASCADE — garantido no banco pela migração 0002.
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(
        Produto, on_delete=models.PROTECT, null=True, blank=True, related_name="itens_venda"
    )
    quantidade = models.DecimalField(max_digits=12, decimal_places=3)
    preco = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "item_venda"

    def __str__(self):
        return f"{self.quantidade} de {self.produto or 'produto não casado'}"


class ImportacaoPdv(models.Model):
    """Cada arquivo do caixa lido pelo importador, com o resultado da leitura (E3, E5)."""

    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        OK = "OK", "Concluída"
        PARCIAL = "PARCIAL", "Concluída com linhas pendentes"
        ERRO = "ERRO", "Com erro"

    arquivo_nome = models.CharField(max_length=200)
    data_referencia = models.DateField()
    linhas_lidas = models.IntegerField(db_default=0)
    linhas_erro = models.IntegerField(db_default=0)
    status = models.CharField(max_length=12, choices=Status.choices, db_default=Status.PENDENTE)
    processado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "importacao_pdv"
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=["PENDENTE", "OK", "PARCIAL", "ERRO"]), name="ck_imp_status"
            ),
        ]

    def __str__(self):
        return f"Importação de {self.arquivo_nome} ({self.status})"

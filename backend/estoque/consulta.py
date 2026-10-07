"""
Visão de estoque por produto e por lote — tarefa F1 (RF07, RN01, RN16).

"Ver o saldo por produto e por categoria, com destaque para o que está abaixo do mínimo e o que
está vencendo." O saldo vem da vw_estoque_atual (RN01); nada aqui grava coisa alguma.

Sem objeto novo no banco: o schema.sql tem uma única view, a de saldo. A visão por produto e por
lote são consultas sobre ela e sobre `lote`, usadas pela API de consulta (F2) e pela tela (F3).
"""

from datetime import date, timedelta

from django.db import models
from django.db.models import (
    BooleanField,
    Case,
    Count,
    F,
    Func,
    IntegerField,
    OuterRef,
    QuerySet,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce

from cadastro.models import Produto
from comum.parametros import dias_aviso_validade
from estoque.models import Lote


class Situacao(models.TextChoices):
    VENCIDO = "VENCIDO", "Vencido"  # RN16: bloqueado para venda, destacado na tela
    VENCENDO = "VENCENDO", "Vencendo"  # RN05/RF07: vence em dias_aviso_validade dias ou menos
    OK = "OK", "Dentro da validade"
    SEM_VALIDADE = "SEM_VALIDADE", "Sem validade"


def _limite_vencendo(hoje: date) -> date:
    return hoje + timedelta(days=dias_aviso_validade(produto=None))


def _conta(lotes: QuerySet) -> Coalesce:
    contagem = lotes.values("produto").annotate(total=Count("pk")).values("total")
    return Coalesce(Subquery(contagem, output_field=IntegerField()), 0)


def posicao_por_produto(*, hoje: date) -> QuerySet[Produto]:
    """
    Um item por produto, em ordem de categoria e nome, com:
    saldo (RN01) · abaixo_do_minimo (RF07) · lotes_vencidos (RN16) · lotes_vencendo (RF07) ·
    proxima_validade (a validade mais próxima entre os lotes com saldo).
    """
    limite = _limite_vencendo(hoje)
    com_saldo = Lote.objects.filter(produto=OuterRef("pk"), quantidade_atual__gt=0)
    return (
        Produto.objects.select_related("categoria")
        .annotate(
            saldo=F("estoque_atual__saldo"),
            abaixo_do_minimo=Case(
                When(
                    estoque_minimo__isnull=False,
                    estoque_atual__saldo__lt=F("estoque_minimo"),
                    then=Value(True),
                ),
                default=Value(False),
                output_field=BooleanField(),
            ),
            lotes_vencidos=_conta(com_saldo.filter(data_validade__lt=hoje)),
            lotes_vencendo=_conta(com_saldo.filter(data_validade__gte=hoje, data_validade__lte=limite)),
            proxima_validade=Subquery(
                com_saldo.filter(data_validade__isnull=False)
                .order_by("data_validade")
                .values("data_validade")[:1]
            ),
        )
        .order_by("categoria__nome", "nome")
    )


def posicao_por_lote(*, hoje: date) -> QuerySet[Lote]:
    """
    Os lotes que ainda têm mercadoria, do que vence primeiro para o que vence por último (sem
    validade no fim), com: situacao (VENCIDO, VENCENDO, OK, SEM_VALIDADE) e dias_para_vencer
    (negativo = já venceu há tantos dias).
    """
    limite = _limite_vencendo(hoje)
    return (
        Lote.objects.filter(quantidade_atual__gt=0)
        .select_related("produto__categoria", "fornecedor")
        .annotate(
            situacao=Case(
                When(data_validade__isnull=True, then=Value(Situacao.SEM_VALIDADE)),
                When(data_validade__lt=hoje, then=Value(Situacao.VENCIDO)),
                When(data_validade__lte=limite, then=Value(Situacao.VENCENDO)),
                default=Value(Situacao.OK),
                output_field=models.CharField(),
            ),
            # date − date no PostgreSQL dá o número de dias (inteiro).
            dias_para_vencer=Func(
                F("data_validade"),
                Value(hoje),
                arg_joiner=" - ",
                template="(%(expressions)s)",
                output_field=IntegerField(),
            ),
        )
        .order_by(F("data_validade").asc(nulls_last=True), "data_entrada", "id")
    )

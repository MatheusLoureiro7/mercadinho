"""
Fechamento de caixa — tarefa I1. RN15, RF12, fluxograma 06.

Decisões do grupo em 05/11/2026 (lacuna L12):
- valor apurado = soma das vendas do dia pagas em DINHEIRO (a gaveta só tem dinheiro);
- o fechamento é do DIA ANTERIOR: as vendas entram às 03h00 do dia seguinte (E3). A esposa conta o
  dinheiro à noite e registra na manhã seguinte. Sem as vendas daquele dia, o fechamento é recusado:
  o apurado sairia zero e a "diferença" seria falsa.

Decisão do grupo em 16/11/2026 (revisão X1, item 6): a esposa pode escolher o dia do caixa — ontem,
se não disser nada; qualquer dia anterior cujas vendas já entraram (o sábado registrado na segunda);
nunca hoje nem o futuro, porque as vendas do dia só entram na madrugada seguinte.

RN15: a diferença é calculada pelo banco (coluna gerada); correção é sempre um registro novo.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import Lower, Trim
from django.utils import timezone

from cadastro.models import Usuario
from caixa.models import FechamentoCaixa
from comum.erros import ErroDeRegraDeNegocio
from vendas.models import ImportacaoPdv, Venda

DINHEIRO = "dinheiro"


def dia_do_fechamento() -> date:
    """O dia anterior, no horário da loja (nunca o CURRENT_DATE do banco, que está em UTC)."""
    return timezone.localdate() - timedelta(days=1)


def vendas_importadas(dia: date) -> bool:
    return ImportacaoPdv.objects.filter(
        data_referencia=dia, status__in=[ImportacaoPdv.Status.OK, ImportacaoPdv.Status.PARCIAL]
    ).exists()


def valor_apurado(dia: date) -> Decimal:
    """Soma das vendas do dia (horário da loja) pagas em dinheiro."""
    total = (
        Venda.objects.filter(data_hora__date=dia)
        .alias(pagamento=Lower(Trim("forma_pagamento")))
        .filter(pagamento=DINHEIRO)
        .aggregate(total=Sum("valor_total"))["total"]
    )
    return (total or Decimal("0")).quantize(Decimal("0.01"))


def apurado_do_fechamento(dia: date | None = None) -> tuple[date, Decimal]:
    dia = dia or dia_do_fechamento()
    if dia >= timezone.localdate():
        raise ErroDeRegraDeNegocio(
            "RN15",
            f"O caixa de {dia:%d/%m/%Y} só pode ser fechado depois que as vendas do dia entrarem no "
            "sistema, na madrugada seguinte. Escolha um dia que já passou.",
            campo="data",
        )
    if not vendas_importadas(dia):
        raise ErroDeRegraDeNegocio(
            "RN15",
            f"As vendas de {dia:%d/%m/%Y} ainda não entraram no sistema, então não há valor apurado "
            "para conferir. Confira se a planilha do caixa desse dia foi salva na pasta e tente "
            "depois das 03h00.",
        )
    return dia, valor_apurado(dia)


def registrar_fechamento(
    *, valor_contado: Decimal, usuario: Usuario | None, data: date | None = None
) -> FechamentoCaixa:
    dia, apurado = apurado_do_fechamento(data)
    fechamento = FechamentoCaixa.objects.create(
        data=dia, valor_sistema=apurado, valor_contado=valor_contado, registrado_por=usuario
    )
    fechamento.refresh_from_db()  # traz a diferença calculada pelo banco e o registrado_em
    return fechamento

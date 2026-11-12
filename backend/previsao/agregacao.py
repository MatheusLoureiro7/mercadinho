"""
Rotina de agregação do consumo diário — tarefa G1. Operação 03, passos 2 e 3 (RN11).

    agregar_consumo_recente()        a rodada das 03h00: os últimos 30 dias, até ontem
    agregar_consumo(inicio, fim)     regrava um período qualquer (ex.: o histórico inteiro)

O consumo é lido só por `previsao.consumo` (RN11: só VENDA, perda fica de fora). A tabela é dado
derivado (Apostila IV, seção 3): o período é apagado e regravado inteiro, numa transação. Por isso
rodar duas vezes não duplica, e a venda que entrou depois — o item pendente casado pelo sobrinho
(E4), ou uma planilha atrasada — aparece na rodada seguinte, desde que seja dos últimos 30 dias.

Por que 30 dias até ontem: 30 é a janela da média (RN06), então tudo o que a previsão usa é
refeito todo dia; e hoje fica de fora porque as vendas de hoje só entram às 03h00 de amanhã.
"""

from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone

from previsao.consumo import vendido_por_produto_e_dia
from previsao.models import ConsumoDiario

JANELA_DIAS = 30  # RN06: a média é dos últimos 30 dias


def dia_da_semana(dia: date) -> int:
    """L27: 0 = domingo … 6 = sábado, como o EXTRACT(DOW) do PostgreSQL."""
    return dia.isoweekday() % 7


def janela_recente(hoje: date | None = None) -> tuple[date, date]:
    ontem = (hoje or timezone.localdate()) - timedelta(days=1)
    return ontem - timedelta(days=JANELA_DIAS - 1), ontem


def agregar_consumo(inicio: date, fim: date) -> int:
    """Regrava consumo_diario de `inicio` a `fim`, os dois incluídos. Devolve quantas linhas gravou."""
    vendido = vendido_por_produto_e_dia(inicio, fim)
    with transaction.atomic():
        ConsumoDiario.objects.filter(data__gte=inicio, data__lte=fim).delete()
        ConsumoDiario.objects.bulk_create(
            ConsumoDiario(
                produto_id=produto_id, data=dia, quantidade_vendida=total, dia_semana=dia_da_semana(dia)
            )
            for (produto_id, dia), total in vendido.items()
        )
    return len(vendido)


def agregar_consumo_recente() -> int:
    return agregar_consumo(*janela_recente())

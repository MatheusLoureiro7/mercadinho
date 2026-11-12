"""
Balanço da semana — tarefa I3 (RF13). Tela da esposa (GESTAO, RN14).

    balanco = balanco_da_semana(dia)     a semana (segunda a domingo) que contém `dia`

Decisão do grupo sobre a lacuna L16 (12/11/2026):
    resultado = vendas da semana (a preço de venda: o valor que o caixa registrou)
              − perdas da semana (a preço de custo: o custo do lote; sem ele, o do produto)
O custo da mercadoria vendida não entra: seria controle financeiro, fora do escopo. RN11: perda é
linha separada, nunca somada às vendas.

Adotado na I3, a confirmar pelo grupo (docs/ACOMPANHAMENTO.md, 12/11/2026):
- semana de segunda a domingo; sem dia escolhido, a semana de ontem — as vendas de hoje só entram
  às 03h00 de amanhã;
- dia já passado sem a planilha do caixa importada é avisado, como no fechamento (I1): sem isso o
  balanço sairia menor sem ninguém saber por quê;
- perda sem custo cadastrado não entra no valor e é contada à parte, em vez de virar zero calado.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from caixa.fechamento import vendas_importadas
from estoque.models import Movimentacao
from vendas.models import Venda

CENTAVO = Decimal("0.01")


@dataclass(frozen=True)
class PerdaDoProduto:
    produto_nome: str
    unidade_medida: str
    quantidade: Decimal
    valor: Decimal | None  # das perdas com custo; None se nenhuma tem
    sem_custo: bool  # alguma perda do produto ficou fora do valor por falta de custo


@dataclass(frozen=True)
class Balanco:
    inicio: date
    fim: date
    ate: date  # o último dia da semana que já terminou (a semana de ontem ainda está em andamento)
    vendas_total: Decimal
    cupons: int
    vendas_por_dia: list[tuple[date, Decimal, int]]
    perdas: list[PerdaDoProduto]
    perdas_total: Decimal
    perdas_sem_custo: int  # produtos com perda sem custo cadastrado (fora do valor)
    resultado: Decimal
    dias_sem_vendas: list[date]


def semana_de(dia: date) -> tuple[date, date]:
    segunda = dia - timedelta(days=dia.weekday())
    return segunda, segunda + timedelta(days=6)


def ontem() -> date:
    return timezone.localdate() - timedelta(days=1)


def _vendas_por_dia(inicio: date, fim: date) -> list[tuple[date, Decimal, int]]:
    linhas = (
        Venda.objects.filter(data_hora__date__gte=inicio, data_hora__date__lte=fim)
        .annotate(dia=TruncDate("data_hora", tzinfo=timezone.get_current_timezone()))
        .values("dia")
        .annotate(total=Sum("valor_total"), cupons=Count("id"))
        .order_by()
    )
    por_dia = {linha["dia"]: (linha["total"], linha["cupons"]) for linha in linhas}
    dias = [inicio + timedelta(days=n) for n in range((fim - inicio).days + 1)]
    return [(dia, *por_dia.get(dia, (Decimal("0.00"), 0))) for dia in dias]


def _custo(perda: Movimentacao) -> Decimal | None:
    if perda.lote is not None and perda.lote.custo_unitario is not None:
        return perda.lote.custo_unitario
    return perda.produto.preco_custo


def _perdas(inicio: date, fim: date) -> list[PerdaDoProduto]:
    perdas = Movimentacao.objects.filter(
        tipo=Movimentacao.Tipo.PERDA, data_hora__date__gte=inicio, data_hora__date__lte=fim
    ).select_related("produto", "lote")
    quantidade = defaultdict(Decimal)
    valor: dict[int, Decimal | None] = {}
    sem_custo = set()
    produtos = {}
    for perda in perdas:
        produtos[perda.produto_id] = perda.produto
        quantidade[perda.produto_id] += perda.quantidade
        custo = _custo(perda)
        if custo is not None:
            valor[perda.produto_id] = (valor.get(perda.produto_id) or Decimal(0)) + perda.quantidade * custo
        else:
            valor.setdefault(perda.produto_id, None)
            sem_custo.add(perda.produto_id)
    itens = [
        PerdaDoProduto(
            produto_nome=produto.nome,
            unidade_medida=produto.unidade_medida,
            quantidade=quantidade[pk].normalize(),
            valor=None if valor[pk] is None else valor[pk].quantize(CENTAVO, rounding=ROUND_HALF_UP),
            sem_custo=pk in sem_custo,
        )
        for pk, produto in produtos.items()
    ]
    # Da perda que mais pesou para a que menos pesou; sem custo, no fim, por nome.
    return sorted(itens, key=lambda item: (item.valor is None, -(item.valor or 0), item.produto_nome))


def balanco_da_semana(dia: date | None = None) -> Balanco:
    inicio, fim = semana_de(dia or ontem())
    ate = min(fim, ontem())
    vendas_por_dia = _vendas_por_dia(inicio, fim)
    vendas_total = sum((total for _, total, _ in vendas_por_dia), Decimal("0.00"))
    perdas = _perdas(inicio, fim)
    perdas_total = sum((item.valor for item in perdas if item.valor is not None), Decimal("0.00"))
    return Balanco(
        inicio=inicio,
        fim=fim,
        ate=ate,
        vendas_total=vendas_total,
        cupons=sum(cupons for _, _, cupons in vendas_por_dia),
        vendas_por_dia=vendas_por_dia,
        perdas=perdas,
        perdas_total=perdas_total,
        perdas_sem_custo=sum(1 for item in perdas if item.sem_custo),
        resultado=vendas_total - perdas_total,
        dias_sem_vendas=[
            inicio + timedelta(days=n)
            for n in range((ate - inicio).days + 1)
            if not vendas_importadas(inicio + timedelta(days=n))
        ],
    )

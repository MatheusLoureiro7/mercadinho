"""
Gravação da previsão — tarefa G3. Operação 03, passos 4 e 5 (RN06, RN07, RN08, RF11).

    calcular_previsao()     regrava previsao_produto para todos os produtos; devolve quantos

Para cada produto, a partir do consumo da G2 (`previsao.calculo`) e do saldo de hoje (RN01):
- dias_ate_acabar: o saldo gasto dia a dia, a partir de hoje, com o consumo de cada dia
  (`Consumo.do_dia`, RN07), com a fração do último dia. Sem consumo, nulo: não acaba.
- ponto_pedido (RN08) = média × prazo × (1 + estoque_seguranca_pct ÷ 100) — a fórmula conferida
  contra o exemplo da apostila (8 kg/dia, 3 dias, 20 % → 28,8 kg).
- sugestao_compra (RF11) — decisão do grupo sobre a lacuna L15 (12/11/2026): o que o produto vai
  vender no prazo de entrega + 7 dias, contados de hoje, menos o saldo; nunca negativa; o pedido
  mínimo do fornecedor não entra.
Sem fornecedor padrão não há prazo de entrega: ponto de pedido e sugestão ficam nulos.

RN09 (G4): produto com menos de `historico_minimo_dias` dias de histórico — COUNT(DISTINCT data)
em consumo_diario, o histórico inteiro, só dias com venda — fica com a linha toda nula, inclusive
`calculado_em`: é o "ainda aprendendo", e nenhum número sai para tela ou aviso.
"""

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from cadastro.models import Produto
from comum.parametros import parametro_inteiro
from estoque.saldo import saldos_de_todos
from previsao.calculo import MILESIMO, Consumo, consumo_de_todos
from previsao.models import ConsumoDiario, PrevisaoProduto

DIAS_ALEM_DO_PRAZO = 7  # L15, decisão do grupo em 12/11/2026
DECIMO = Decimal("0.1")  # dias_ate_acabar é NUMERIC(8,1)
MAIOR_NUMERO_DE_DIAS = Decimal("9999999.9")


def dias_ate_acabar(saldo: Decimal, consumo: Consumo, hoje: date) -> Decimal | None:
    if saldo <= 0:
        return Decimal("0.0")
    semana = sum((consumo.do_dia(hoje + timedelta(days=n)) for n in range(7)), Decimal(0))
    if semana <= 0:
        return None
    # As semanas inteiras de uma vez (o consumo se repete a cada 7 dias); a última, dia a dia.
    semanas = max(int(saldo // semana) - 1, 0)
    restante, dias = saldo - semanas * semana, semanas * 7
    while restante > consumo.do_dia(hoje + timedelta(days=dias)):
        restante -= consumo.do_dia(hoje + timedelta(days=dias))
        dias += 1
    total = dias + restante / consumo.do_dia(hoje + timedelta(days=dias))
    return min(total.quantize(DECIMO, rounding=ROUND_HALF_UP), MAIOR_NUMERO_DE_DIAS)


def ponto_pedido(consumo: Consumo, prazo: int, seguranca_pct: int) -> Decimal:
    no_prazo = consumo.medio_diario * prazo
    return (no_prazo + no_prazo * seguranca_pct / 100).quantize(MILESIMO, rounding=ROUND_HALF_UP)


def sugestao_compra(saldo: Decimal, consumo: Consumo, prazo: int, hoje: date) -> Decimal:
    vai_vender = sum(
        (consumo.do_dia(hoje + timedelta(days=n)) for n in range(prazo + DIAS_ALEM_DO_PRAZO)), Decimal(0)
    )
    return max(vai_vender - saldo, Decimal(0)).quantize(MILESIMO, rounding=ROUND_HALF_UP)


def _previsao(produto: Produto, consumo: Consumo, saldo: Decimal, seguranca_pct: int, hoje: date, agora):
    fornecedor = produto.fornecedor_padrao
    prazo = fornecedor.prazo_entrega_dias if fornecedor else None
    return PrevisaoProduto(
        produto=produto,
        consumo_medio_diario=consumo.medio_diario,
        consumo_por_dia_semana={
            str(s): f"{media:.3f}" for s, media in sorted(consumo.por_dia_semana.items())
        },
        dias_ate_acabar=dias_ate_acabar(saldo, consumo, hoje),
        ponto_pedido=None if prazo is None else ponto_pedido(consumo, prazo, seguranca_pct),
        sugestao_compra=None if prazo is None else sugestao_compra(saldo, consumo, prazo, hoje),
        calculado_em=agora,
    )


def dias_de_historico() -> dict[int, int]:
    """RN09: em quantos dias cada produto vendeu, no histórico inteiro de consumo_diario."""
    linhas = ConsumoDiario.objects.values("produto_id").annotate(dias=Count("data", distinct=True)).order_by()
    return {linha["produto_id"]: linha["dias"] for linha in linhas}


def calcular_previsao() -> int:
    agora = timezone.now()
    hoje = timezone.localdate(agora)
    seguranca_pct = parametro_inteiro("estoque_seguranca_pct")
    minimo = parametro_inteiro("historico_minimo_dias")
    historico = dias_de_historico()
    consumos = consumo_de_todos()
    saldos = saldos_de_todos()
    previsoes = [
        _previsao(
            produto, consumos[produto.pk], saldos.get(produto.pk, Decimal(0)), seguranca_pct, hoje, agora
        )
        if historico.get(produto.pk, 0) >= minimo
        else PrevisaoProduto(produto=produto)  # RN09: ainda aprendendo
        for produto in Produto.objects.select_related("fornecedor_padrao").filter(pk__in=consumos)
    ]
    campos = [campo.name for campo in PrevisaoProduto._meta.concrete_fields if not campo.primary_key]
    with transaction.atomic():
        PrevisaoProduto.objects.bulk_create(
            previsoes, update_conflicts=True, unique_fields=["produto"], update_fields=campos
        )
    return len(previsoes)

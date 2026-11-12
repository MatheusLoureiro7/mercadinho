"""
Consumo médio e por dia da semana — tarefa G2. Operação 03, passo 4 (RN06, RN07).

    consumo = consumo_do_produto(produto)
    consumo.medio_diario          RN06: vendido nos últimos 30 dias ÷ 30
    consumo.por_dia_semana        RN07: {0 (domingo) … 6 (sábado): média daquele dia}
    consumo.do_dia(dia)           o consumo que a projeção usa para aquele dia (G3)

Os últimos 30 dias são os da rodada da G1: até ontem, lidos de consumo_diario (só VENDA, RN11).
A média de um dia da semana divide pelas vezes que o dia aparece na janela (4 ou 5), contando o
dia sem venda como zero — o mesmo critério da RN06, que divide sempre por 30.

RN07, decisão do grupo sobre a lacuna L02 (12/11/2026): a diferença é relevante quando a média do
dia da semana é ≥ 1,5 × a média geral; aí a projeção daquele dia usa a média do dia, que é a maior
das duas. Nos outros dias, a média geral — inclusive no dia mais fraco: o domingo parado não
derruba a projeção. É assim que, na quinta, a projeção da cerveja já conta os 26 do sábado.

O histórico mínimo (RN09, G4) não é decidido aqui: este módulo só calcula.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Sum

from cadastro.models import Produto
from previsao.agregacao import JANELA_DIAS, dia_da_semana, janela_recente
from previsao.models import ConsumoDiario

FATOR_DIA_RELEVANTE = Decimal("1.5")  # L02, decisão do grupo em 12/11/2026
MILESIMO = Decimal("0.001")  # NUMERIC(12,3), como as quantidades


@dataclass(frozen=True)
class Consumo:
    medio_diario: Decimal
    por_dia_semana: dict[int, Decimal]
    dias_relevantes: frozenset[int]  # dias da semana ≥ 1,5 × a média geral (RN07)

    def do_dia(self, dia: date) -> Decimal:
        semana = dia_da_semana(dia)
        return self.por_dia_semana[semana] if semana in self.dias_relevantes else self.medio_diario


def _vezes_de_cada_dia(inicio: date, fim: date) -> dict[int, int]:
    vezes = defaultdict(int)
    for n in range((fim - inicio).days + 1):
        vezes[dia_da_semana(inicio + timedelta(days=n))] += 1
    return vezes


def _consumo(vendido_por_dia_semana: dict[int, Decimal], vezes: dict[int, int]) -> Consumo:
    total = sum(vendido_por_dia_semana.values(), Decimal(0))
    media_geral = total / JANELA_DIAS
    medias = {semana: vendido_por_dia_semana.get(semana, Decimal(0)) / vezes[semana] for semana in range(7)}
    # Comparação antes de arredondar: 2,9995 não passa por 3 só por causa das casas.
    relevantes = frozenset(
        s for s, media in medias.items() if total > 0 and media >= FATOR_DIA_RELEVANTE * media_geral
    )
    return Consumo(
        medio_diario=media_geral.quantize(MILESIMO, rounding=ROUND_HALF_UP),
        por_dia_semana={s: media.quantize(MILESIMO, rounding=ROUND_HALF_UP) for s, media in medias.items()},
        dias_relevantes=relevantes,
    )


def _vendido_por_produto_e_dia_semana(inicio: date, fim: date, **filtro) -> dict[int, dict[int, Decimal]]:
    linhas = (
        ConsumoDiario.objects.filter(data__gte=inicio, data__lte=fim, **filtro)
        .values("produto_id", "dia_semana")
        .annotate(total=Sum("quantidade_vendida"))
        .order_by()
    )
    vendido = defaultdict(dict)
    for linha in linhas:
        vendido[linha["produto_id"]][linha["dia_semana"]] = linha["total"]
    return vendido


def consumo_do_produto(produto: Produto | int) -> Consumo:
    produto_id = produto.pk if isinstance(produto, Produto) else produto
    inicio, fim = janela_recente()
    vendido = _vendido_por_produto_e_dia_semana(inicio, fim, produto_id=produto_id)
    return _consumo(vendido.get(produto_id, {}), _vezes_de_cada_dia(inicio, fim))


def consumo_de_todos() -> dict[int, Consumo]:
    """Todos os produtos cadastrados em duas consultas — para a rodada das 03h00 (G3)."""
    inicio, fim = janela_recente()
    vezes = _vezes_de_cada_dia(inicio, fim)
    vendido = _vendido_por_produto_e_dia_semana(inicio, fim)
    return {pk: _consumo(vendido.get(pk, {}), vezes) for pk in Produto.objects.values_list("pk", flat=True)}

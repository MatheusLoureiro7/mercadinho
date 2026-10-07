"""
Base de consumo — RN11, tarefa D2.

> Movimentações do tipo PERDA reduzem o estoque, mas são excluídas da base de cálculo de consumo
> e de previsão.

É a ÚNICA porta para "quanto se vendeu". A tabela consumo_diario (G1), o consumo médio (RN06, RN07)
e os avisos de ruptura (RN08, RN10) leem o consumo daqui — nunca de movimentacao direto. Um teste
(test_rn11_previsao_e_avisos_so_leem_movimentacao_pela_base_de_consumo) falha se previsao/ ou
alertas/ tocarem em movimentação por fora deste arquivo.

Por quê: se a perda entrasse, quanto mais produto estraga, mais o sistema manda comprar — o erro
se alimenta sozinho.
"""

from datetime import date
from decimal import Decimal

from django.db.models import QuerySet, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from cadastro.models import Produto
from estoque.models import Movimentacao


def movimentacoes_de_consumo() -> QuerySet[Movimentacao]:
    """RN11: só VENDA. PERDA, ENTRADA e AJUSTE ficam de fora da base de consumo."""
    return Movimentacao.objects.filter(tipo=Movimentacao.Tipo.VENDA)


def _vendas_do_periodo(produto: Produto | int, inicio: date, fim: date) -> QuerySet[Movimentacao]:
    produto_id = produto.pk if isinstance(produto, Produto) else produto
    # __date usa o fuso da loja (America/Sao_Paulo): a venda das 22h30 é do dia da loja, não do UTC.
    return movimentacoes_de_consumo().filter(
        produto_id=produto_id, data_hora__date__gte=inicio, data_hora__date__lte=fim
    )


def vendido_no_periodo(produto: Produto | int, inicio: date, fim: date) -> Decimal:
    """Total vendido do produto entre `inicio` e `fim`, os dois dias incluídos."""
    total = _vendas_do_periodo(produto, inicio, fim).aggregate(total=Sum("quantidade"))["total"]
    return total or Decimal("0")


def vendido_por_dia(produto: Produto | int, inicio: date, fim: date) -> dict[date, Decimal]:
    """
    Quanto o produto vendeu em cada dia da loja do período — exatamente o que a tabela
    consumo_diario guarda (produto, data, quantidade_vendida). Dia sem venda não aparece.
    """
    linhas = (
        _vendas_do_periodo(produto, inicio, fim)
        .annotate(dia=TruncDate("data_hora", tzinfo=timezone.get_current_timezone()))
        .values("dia")
        .annotate(total=Sum("quantidade"))
        .order_by("dia")
    )
    return {linha["dia"]: linha["total"] for linha in linhas}

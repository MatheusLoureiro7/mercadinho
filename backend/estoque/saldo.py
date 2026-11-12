"""
Saldo de estoque — RN01, tarefa C4.

O saldo de um produto é sempre a soma das suas movimentações, lida da view vw_estoque_atual.
Toda parte do sistema que precisa do saldo (consulta de estoque, previsão, avisos) passa por aqui.
"""

from decimal import Decimal

from cadastro.models import Produto
from estoque.models import EstoqueAtual


def saldo_do_produto(produto: Produto | int) -> Decimal:
    """Saldo atual: Σ ENTRADA + Σ AJUSTE − Σ VENDA − Σ PERDA. Produto sem movimentação: 0."""
    produto_id = produto.pk if isinstance(produto, Produto) else produto
    return EstoqueAtual.objects.values_list("saldo", flat=True).get(produto_id=produto_id)


def saldos_de_todos() -> dict[int, Decimal]:
    """O saldo de cada produto numa consulta só — para a rodada da previsão (G3)."""
    return dict(EstoqueAtual.objects.values_list("produto_id", "saldo"))

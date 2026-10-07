"""
Ordem de saída dos lotes — RN02 (FIFO por validade), com o desempate decidido na L13.

Usada pela perda (D1, vencidos incluídos) e pela baixa por venda (E3, vencidos de fora — RN16).
"""

from datetime import date

from django.db.models import F, Q, QuerySet

from cadastro.models import Produto
from estoque.models import Lote


def lotes_em_ordem_de_validade(produto: Produto, *, hoje: date, incluir_vencidos: bool) -> QuerySet[Lote]:
    """
    Lotes com saldo do produto, do que vence primeiro para o que vence por último.

    - RN02: ordena por data_validade — "nunca por id, nunca por data_entrada" como critério principal.
    - L13: mesma validade → sai antes o que entrou antes, depois o de cadastro mais antigo; lote sem
      validade (não perecível) sai por último.
    - RN16: `incluir_vencidos=False` deixa de fora o lote com validade anterior a hoje — é o caso da
      venda. A perda inclui, porque é por ela que o vencido sai.
    """
    lotes = Lote.objects.filter(produto=produto, quantidade_atual__gt=0)
    if not incluir_vencidos:
        lotes = lotes.filter(Q(data_validade__isnull=True) | Q(data_validade__gte=hoje))
    return lotes.order_by(F("data_validade").asc(nulls_last=True), "data_entrada", "id")

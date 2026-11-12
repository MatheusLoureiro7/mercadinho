"""
Casar o produto do caixa com o produto cadastrado — tarefa E4. Operação 04, passo 6: a linha que
não casou na importação fica pendente, e "o sobrinho resolve depois, na tela de importação".

    casar_item(item_id, produto)

Decisão do grupo (12/11/2026, lacuna L26): o modelo de dados não muda. `item_venda` não guarda o
nome escrito na planilha, então o item pendente é mostrado com data, hora, quantidade e preço, e o
sobrinho confere na planilha dele. Ao casar, a baixa é a mesma da importação (passo 8): na hora da
venda, do lote que vence primeiro (RN01, RN02), sem lote vencido no dia da venda (RN16).

A importação (`importacao_pdv`) não muda de situação: ela registra o que aconteceu na leitura, e
nem tem ligação com a venda no modelo de dados.
"""

from django.db import transaction
from django.db.models import QuerySet

from cadastro.models import Produto
from comum.erros import ErroDeRegraDeNegocio
from vendas.importacao import baixar_venda_do_estoque
from vendas.models import ItemVenda


def itens_pendentes() -> QuerySet[ItemVenda]:
    """Itens que a importação não conseguiu casar, do mais antigo ao mais novo."""
    return (
        ItemVenda.objects.filter(produto__isnull=True)
        .select_related("venda")
        .order_by("venda__data_hora", "id")
    )


def casar_item(item_id: int, produto: Produto) -> ItemVenda:
    """Grava o produto no item pendente e baixa a venda do estoque. Item inexistente: DoesNotExist."""
    with transaction.atomic():
        item = ItemVenda.objects.select_for_update().select_related("venda").get(pk=item_id)
        if item.produto_id is not None:
            raise ErroDeRegraDeNegocio(
                None,
                f"Esta venda já foi ligada ao produto {item.produto.nome}. Atualize a tela para ver "
                "o que ainda falta.",
                campo="produto",
            )
        item.produto = produto
        item.save(update_fields=["produto"])
        baixar_venda_do_estoque(produto, item.quantidade, item.preco, item.venda.data_hora)
    return item

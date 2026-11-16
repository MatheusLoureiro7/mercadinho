"""
Entrada de mercadoria — operação 02 da Apostila IV, tarefa C2 (RF03, RN01).

Cada carga que chega vira um lote e uma movimentação ENTRADA, gravados numa transação só:
"Nunca existe lote sem a movimentação que explica o saldo."
Antes de gravar, as regras de validade (RN04, passos 3 a 5 — tarefa C3).

Venda a mais (decisão do grupo, 16/11/2026, revisão X1 item 3): a venda maior que o estoque grava
a sobra sem lote (E3), e o saldo fica abaixo da soma dos lotes. A carga seguinte desconta essa
diferença do lote novo — aquelas unidades já tinham sido vendidas — e saldo e lotes voltam a bater.
A movimentação ENTRADA continua com a quantidade inteira: o saldo segue sendo só a soma delas (RN01).
"""

from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from alertas.servicos import cancelar_aviso_de_ruptura_pendente
from cadastro.models import Fornecedor, Produto, Usuario
from estoque.models import Lote, Movimentacao
from estoque.regras import validade_do_lote
from estoque.saldo import saldo_do_produto


def _vendido_sem_lote(produto: Produto) -> Decimal:
    """Quanto a soma dos lotes passa do saldo: a venda a mais que ainda não saiu de nenhum lote."""
    lotes = Lote.objects.select_for_update().filter(produto=produto)
    soma = sum(lotes.values_list("quantidade_atual", flat=True), Decimal(0))
    return max(soma - saldo_do_produto(produto), Decimal(0))


def registrar_entrada(
    *,
    produto: Produto,
    quantidade: Decimal,
    usuario: Usuario | None,
    fornecedor: Fornecedor | None = None,
    custo_unitario: Decimal | None = None,
    data_validade: date | None = None,
    origem: str = "TELA",
) -> Lote:
    data_entrada = timezone.localdate()  # dia da loja, nunca o CURRENT_DATE (UTC) do banco

    # Passos 2 a 5: lê o produto e aplica a RN04. Se recusar, nada é gravado.
    data_validade = validade_do_lote(
        produto, data_entrada=data_entrada, data_validade=data_validade, hoje=data_entrada
    )

    # Passos 6 a 8: lote e movimentação juntos. Se a movimentação falhar, o lote é desfeito.
    with transaction.atomic():
        ja_vendido = min(_vendido_sem_lote(produto), quantidade)
        lote = Lote.objects.create(
            produto=produto,
            fornecedor=fornecedor,
            quantidade_inicial=quantidade,
            quantidade_atual=quantidade - ja_vendido,
            custo_unitario=custo_unitario,
            data_entrada=data_entrada,
            data_validade=data_validade,
        )
        Movimentacao.objects.create(
            produto=produto,
            lote=lote,
            usuario=usuario,
            tipo=Movimentacao.Tipo.ENTRADA,
            quantidade=quantidade,
            preco_unitario=custo_unitario,
            origem=origem,
        )

    # Passo 10: só depois de confirmada a entrada.
    cancelar_aviso_de_ruptura_pendente(produto)
    return lote

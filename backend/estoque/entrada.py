"""
Entrada de mercadoria — operação 02 da Apostila IV, tarefa C2 (RF03, RN01).

Cada carga que chega vira um lote e uma movimentação ENTRADA, gravados numa transação só:
"Nunca existe lote sem a movimentação que explica o saldo."
Antes de gravar, as regras de validade (RN04, passos 3 a 5 — tarefa C3).
"""

from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from alertas.servicos import cancelar_aviso_de_ruptura_pendente
from cadastro.models import Fornecedor, Produto, Usuario
from estoque.models import Lote, Movimentacao
from estoque.regras import validade_do_lote


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
        lote = Lote.objects.create(
            produto=produto,
            fornecedor=fornecedor,
            quantidade_inicial=quantidade,
            quantidade_atual=quantidade,
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

"""
Registro de perda — RF04, fluxograma 03, tarefa D1 (RN01, RN02, RN11, RN16).

"O que venceu, quebrou ou estragou sai do estoque com o motivo anotado."

- RN01: cada lote afetado ganha uma linha PERDA em movimentação, e o lote tem a quantidade
  baixada — tudo numa transação só.
- L20: com lote informado (o sobrinho sabe qual estragou), sai dele; sem lote, sai pela ordem de
  validade (RN02), começando pelos vencidos.
- RN16: a perda ignora o bloqueio de lote vencido — é por ela que o vencido sai.
- RN11: fica registrada como PERDA; a base de consumo considera só VENDA (D2, G1).
"""

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from cadastro.models import Produto, Usuario
from comum.erros import ErroDeRegraDeNegocio
from estoque.fifo import lotes_em_ordem_de_validade
from estoque.models import Lote, Movimentacao


def _quantidade_na_loja(valor: Decimal, produto: Produto) -> str:
    return f"{valor:.3f}".replace(".", ",") + f" {produto.unidade_medida}"


@transaction.atomic
def registrar_perda(
    *,
    produto: Produto,
    quantidade: Decimal,
    motivo: str,
    usuario: Usuario | None,
    lote: Lote | None = None,
    origem: str = "TELA",
) -> list[Movimentacao]:
    if lote is not None:
        if lote.produto_id != produto.pk:
            raise ErroDeRegraDeNegocio(None, "Esse lote não é desse produto.", campo="lote")
        lotes = [Lote.objects.select_for_update().get(pk=lote.pk)]
        if quantidade > lotes[0].quantidade_atual:
            raise ErroDeRegraDeNegocio(
                None,
                f"Esse lote só tem {_quantidade_na_loja(lotes[0].quantidade_atual, produto)}.",
                campo="quantidade",
            )
    else:
        hoje = timezone.localdate()
        lotes = list(
            lotes_em_ordem_de_validade(produto, hoje=hoje, incluir_vencidos=True).select_for_update()
        )
        disponivel = sum((item.quantidade_atual for item in lotes), Decimal("0"))
        if quantidade > disponivel:
            raise ErroDeRegraDeNegocio(
                None,
                f"Só há {_quantidade_na_loja(disponivel, produto)} de {produto.nome} no estoque.",
                campo="quantidade",
            )

    agora = timezone.now()
    perdas = []
    restante = quantidade
    for item in lotes:
        if restante <= 0:
            break
        baixa = min(restante, item.quantidade_atual)
        item.quantidade_atual -= baixa
        item.save(update_fields=["quantidade_atual"])
        perdas.append(
            Movimentacao.objects.create(
                produto=produto,
                lote=item,
                usuario=usuario,
                tipo=Movimentacao.Tipo.PERDA,
                quantidade=baixa,
                motivo=motivo,
                origem=origem,
                data_hora=agora,
            )
        )
        restante -= baixa
    return perdas

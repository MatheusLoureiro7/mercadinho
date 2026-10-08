"""
Controle de estado do aviso — tarefa H1.

    PENDENTE ──segurar──▶ SEGURADO            janela de silêncio (RN12)
    PENDENTE/SEGURADO ──enviar──▶ ENVIADO     todos com o mesmo enviado_em (RN13)
    PENDENTE/SEGURADO ──cancelar──▶ CANCELADO chegou mercadoria (operação 02, passo 10)
    ENVIADO e CANCELADO não mudam mais.

Cada transição é um UPDATE condicional ao estado de origem, dentro de uma transação: vale o estado
gravado no banco, não o objeto na memória — a rodada das 03h00 e uma entrada de mercadoria podem
mexer no mesmo aviso ao mesmo tempo. É tudo ou nada: se um dos avisos não puder mudar, nenhum muda.
"""

from collections.abc import Iterable
from datetime import datetime

from django.db import transaction

from alertas.models import Alerta

_ABERTOS = (Alerta.Status.PENDENTE, Alerta.Status.SEGURADO)


class TransicaoDeAvisoInvalida(Exception):
    """O aviso não está num estado que permita a mudança pedida."""


class _NemTodos(Exception):
    """Interna: desfaz a transação quando nem todos os avisos podiam mudar."""


def _mudar(avisos: Iterable[Alerta], *, origens, **campos) -> int:
    ids = {aviso.pk for aviso in avisos}
    if not ids:
        return 0
    try:
        with transaction.atomic():
            mudados = Alerta.objects.filter(pk__in=ids, status__in=origens).update(**campos)
            if mudados != len(ids):
                raise _NemTodos  # algum aviso já estava noutro estado: desfaz tudo (nada pela metade)
    except _NemTodos:
        presos = sorted(
            Alerta.objects.filter(pk__in=ids).exclude(status__in=origens).values_list("pk", "status")
        )
        raise TransicaoDeAvisoInvalida(
            f"Avisos fora de {', '.join(origens)}: {presos}. Destino pedido: {campos['status']}."
        ) from None
    return mudados


def segurar(avisos: Iterable[Alerta]) -> int:
    """RN12: o aviso gerado na janela de silêncio fica retido e sai na próxima janela de envio."""
    return _mudar(avisos, origens=(Alerta.Status.PENDENTE,), status=Alerta.Status.SEGURADO)


def enviar(avisos: Iterable[Alerta], *, quando: datetime) -> int:
    """RN13: os avisos da mensagem agrupada saem juntos, com o mesmo enviado_em."""
    return _mudar(avisos, origens=_ABERTOS, status=Alerta.Status.ENVIADO, enviado_em=quando)


def cancelar(avisos: Iterable[Alerta]) -> int:
    """O aviso deixou de valer antes de sair (ex.: chegou a mercadoria — operação 02, passo 10)."""
    return _mudar(avisos, origens=_ABERTOS, status=Alerta.Status.CANCELADO)


def cancelar_os_abertos(consulta) -> int:
    """
    Cancela, de uma vez, os avisos da consulta que ainda estiverem abertos (PENDENTE ou SEGURADO)
    no momento do UPDATE. Não falha se algum já tiver saído ou sido cancelado por outro processo:
    é para quem quer "cancelar o que ainda vale", como a entrada de mercadoria (operação 02, passo
    10), que roda depois da sua transação e não pode quebrar por causa de um aviso.
    """
    return consulta.filter(status__in=_ABERTOS).update(status=Alerta.Status.CANCELADO)

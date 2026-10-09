"""
Resposta do dono ao aviso — tarefa H7. Operação 03, passos 13 e 14.

Decisões do grupo (09/10/2026): só o aviso de "vai acabar" (RUPTURA) ganha botão, e só "Sim, pedir"
— o que a especificação cita. Como a RN13 junta vários avisos numa mensagem, cada aviso de ruptura
vira um botão próprio, que leva o número do aviso ("pedir:<id>").

A resposta só é gravada se o aviso for de ruptura, já tiver sido enviado e o clique vier do chat do
DONO ativo que o recebeu. Grava uma vez; clicar de novo não muda nada. Quem chega aqui já passou
pela conferência do segredo do Telegram (comum/permissoes.py, SoOTelegram).
"""

import logging
import re

from alertas.canal import FalhaNoEnvio
from alertas.models import Alerta
from cadastro.models import Usuario

logger = logging.getLogger("mercadinho.avisos")

RESPOSTA_PEDIR = "Sim, pedir"  # alerta.resposta_usuario (VARCHAR(40)) — operação 03, passo 13
_DADO_PEDIR = re.compile(r"pedir:(\d{1,9})")


def botoes_da_mensagem(avisos: list[Alerta]) -> list[tuple[str, str]]:
    """Um botão (texto, dado) por aviso de ruptura, na ordem da mensagem."""
    return [
        (f"{RESPOSTA_PEDIR}: {aviso.produto.nome}", f"pedir:{aviso.pk}")
        for aviso in avisos
        if aviso.tipo == Alerta.Tipo.RUPTURA
    ]


def registrar_resposta(chat_id: str, dado: str) -> str:
    """Passo 14. Devolve o texto curto que o Sr. João vê ao tocar no botão."""
    encontrado = _DADO_PEDIR.fullmatch(dado or "")
    if not encontrado:
        return "Não entendi esse botão."
    aviso = (
        Alerta.objects.select_related("produto")
        .filter(
            pk=int(encontrado.group(1)),
            tipo=Alerta.Tipo.RUPTURA,
            status=Alerta.Status.ENVIADO,
            destinatario__papel=Usuario.Papel.DONO,
            destinatario__ativo=True,
            destinatario__telegram_chat_id=str(chat_id),
        )
        .first()
    )
    if aviso is None:
        return "Este aviso não vale mais."
    gravou = Alerta.objects.filter(pk=aviso.pk, resposta_usuario__isnull=True).update(
        resposta_usuario=RESPOSTA_PEDIR
    )
    if not gravou:
        return f"Já estava anotado: pedir {aviso.produto.nome}."
    return f"Anotado: pedir {aviso.produto.nome}."


def receber_atualizacao(atualizacao, canal) -> None:
    """Passo 13. Só o clique em botão interessa; o resto é ignorado em silêncio."""
    clique = atualizacao.get("callback_query") if isinstance(atualizacao, dict) else None
    if not isinstance(clique, dict) or not clique.get("id"):
        return
    chat = ((clique.get("message") or {}).get("chat") or {}).get("id")
    if chat is None:
        return
    texto = registrar_resposta(str(chat), str(clique.get("data") or ""))
    try:
        canal.responder_botao(clique["id"], texto)
    except FalhaNoEnvio as erro:  # a resposta já está gravada; a confirmação na tela é cortesia
        logger.warning("Confirmação do botão não chegou ao Telegram: %s", erro)

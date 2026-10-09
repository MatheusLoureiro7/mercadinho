"""
Vincular o celular do dono ao usuário — tarefa H6. Preenche usuario.telegram_chat_id.

Decisão do grupo (08/10/2026): a equipe roda `manage.py vincular_telegram --login joao` na
instalação; o comando mostra um código de uso único e o Sr. João o manda ao bot. O Telegram não
deixa mandar mensagem por número de telefone: só para o chat de quem já falou com o bot — por isso
o código. A leitura é pelo getUpdates, que funciona sem o sistema estar publicado (D05).

- Só o DONO recebe aviso (schema.sql: "só o DONO recebe aviso"; RN14, Telegram só para o DONO).
- Só vale mensagem em conversa particular com o bot, com o código exato.
- O vínculo só é gravado se a confirmação chegar ao celular: o chat certo é provado na hora.
"""

import secrets
import time

from django.db import transaction

from alertas.canal import CanalDeAviso
from cadastro.models import Usuario

ESPERA_MAXIMA_SEGUNDOS = 25  # cada pergunta ao Telegram espera no máximo isto por mensagem nova


def gerar_codigo() -> str:
    """Seis dígitos ao acaso (secrets: imprevisível), mostrados só no terminal da equipe."""
    return f"{secrets.randbelow(1_000_000):06d}"


def conferir_quem_recebe(usuario: Usuario) -> None:
    """Recusa com ValueError quem não pode receber aviso pelo Telegram."""
    if usuario.papel != Usuario.Papel.DONO:
        raise ValueError(f"Só o dono recebe aviso pelo Telegram; {usuario.login} é {usuario.papel}.")
    if not usuario.ativo:
        raise ValueError(f"O usuário {usuario.login} está desativado.")


def _e_o_codigo(texto: str | None, codigo: str) -> bool:
    texto = (texto or "").strip()
    return texto in {codigo, f"/start {codigo}"}


def esperar_o_codigo(canal, codigo: str, *, prazo_segundos: float) -> str | None:
    """
    Lê as mensagens mandadas ao bot até chegar o código, numa conversa particular. Devolve o chat
    de quem mandou, ou None se o prazo acabar. Mensagem de outro código ou de grupo é ignorada.
    """
    limite = time.monotonic() + prazo_segundos
    desde = None
    while (restante := limite - time.monotonic()) > 0:
        espera = max(1, min(int(restante), ESPERA_MAXIMA_SEGUNDOS))
        for atualizacao in canal.ler_mensagens(desde, espera):
            desde = atualizacao["update_id"] + 1  # o Telegram não devolve de novo o que já foi lido
            mensagem = atualizacao.get("message") or {}
            chat = mensagem.get("chat") or {}
            if chat.get("type") == "private" and _e_o_codigo(mensagem.get("text"), codigo):
                return str(chat["id"])
    return None


def vincular(usuario: Usuario, chat_id: str, canal: CanalDeAviso) -> None:
    """Grava o chat no usuário e manda a confirmação; se ela não sair (FalhaNoEnvio), nada é gravado."""
    conferir_quem_recebe(usuario)
    usuario.telegram_chat_id = chat_id
    with transaction.atomic():
        usuario.save(update_fields=["telegram_chat_id"])
        canal.enviar(
            usuario,
            f"Pronto, {usuario.nome}! Os avisos do mercado vão chegar aqui: "
            "o que está para vencer e o que vai acabar.",
        )

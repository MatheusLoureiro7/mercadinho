"""
Canal Telegram — tarefa H5. Operação 03, passo 11.

Implementa CanalDeAviso.enviar(destinatario, mensagem) (D04) com o método sendMessage da API de
bots do Telegram. Só biblioteca padrão (urllib): nenhuma dependência nova (CLAUDE.md).

- O token do bot vem do .env (TELEGRAM_BOT_TOKEN) e faz parte do endereço da API: por isso nenhum
  erro daqui carrega o endereço nem a exceção original (RNF12).
- O chat do destinatário é usuario.telegram_chat_id, ligado na H6 (alertas/vinculo.py), que usa
  nome_do_bot (getMe) e ler_mensagens (getUpdates).
- Texto puro, sem parse_mode: um "*" ou "_" no nome de um produto não faz o Telegram recusar.
- Mensagem acima de LIMITE_DA_MENSAGEM é dividida entre linhas, na ordem (limite do Telegram).
"""

import json
import urllib.error
import urllib.request

from django.conf import settings

from alertas.notificacao import FalhaNoEnvio
from cadastro.models import Usuario

LIMITE_DA_MENSAGEM = 4096  # caracteres por mensagem, limite da API do Telegram
TEMPO_LIMITE_SEGUNDOS = 15


def dividir(texto: str, limite: int = LIMITE_DA_MENSAGEM) -> list[str]:
    """Partes de até `limite` caracteres, sem cortar linha (só a linha maior que o limite é cortada)."""
    partes: list[str] = []
    atual = ""
    for linha in texto.split("\n"):
        while len(linha) > limite:  # linha sozinha maior que o limite: único caso em que se corta
            if atual:
                partes.append(atual)
                atual = ""
            partes.append(linha[:limite])
            linha = linha[limite:]
        candidato = f"{atual}\n{linha}" if atual else linha
        if len(candidato) > limite:
            partes.append(atual)
            candidato = linha
        atual = candidato
    if atual or not partes:
        partes.append(atual)
    return partes


class CanalTelegram:
    def __init__(self, token: str, endereco: str = "https://api.telegram.org"):
        self._token = (token or "").strip()
        if not endereco.startswith(("https://", "http://")):  # nada de file:// ou esquema estranho
            raise ValueError(f"Endereço da API do Telegram inválido: {endereco!r}")
        self._endereco = endereco.rstrip("/")

    @classmethod
    def configurado(cls) -> "CanalTelegram":
        """O canal com o token e o endereço do .env (core/settings.py)."""
        return cls(token=settings.TELEGRAM_BOT_TOKEN, endereco=settings.TELEGRAM_API_ENDERECO)

    def enviar(self, destinatario: Usuario, mensagem: str) -> None:
        chat = (destinatario.telegram_chat_id or "").strip()
        if not chat:
            raise FalhaNoEnvio(f"{destinatario.login} ainda não ligou o celular ao sistema (tarefa H6).")
        for parte in dividir(mensagem):
            self._chamar("sendMessage", {"chat_id": chat, "text": parte})

    def nome_do_bot(self) -> str:
        """O usuário do bot (@...), para o link t.me que leva o código (H6)."""
        return self._chamar("getMe", {})["result"]["username"]

    def ler_mensagens(self, desde: int | None, espera: int) -> list[dict]:
        """
        getUpdates: as mensagens mandadas ao bot a partir de `desde` (update_id). Espera até `espera`
        segundos por uma mensagem nova antes de devolver a lista vazia (long polling).
        """
        dados = {"timeout": espera, "allowed_updates": ["message"]}
        if desde is not None:
            dados["offset"] = desde
        return self._chamar("getUpdates", dados, tempo_limite=espera + TEMPO_LIMITE_SEGUNDOS)["result"]

    def _chamar(self, metodo: str, dados: dict, tempo_limite: int = TEMPO_LIMITE_SEGUNDOS) -> dict:
        if not self._token:
            raise FalhaNoEnvio("O bot do Telegram não está configurado: preencha TELEGRAM_BOT_TOKEN no .env.")
        pedido = urllib.request.Request(  # noqa: S310 — esquema conferido no __init__
            f"{self._endereco}/bot{self._token}/{metodo}",
            data=json.dumps(dados).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        # "from None" em todos os casos: a exceção original guarda o endereço, que contém o token.
        try:
            with urllib.request.urlopen(pedido, timeout=tempo_limite) as resposta:  # noqa: S310 — endereço fixo do .env
                corpo = _json(resposta.read())
        except urllib.error.HTTPError as erro:
            with erro:
                motivo = _json(erro.read()).get("description") or erro.reason
            raise FalhaNoEnvio(f"O Telegram recusou a mensagem ({erro.code}): {motivo}") from None
        except (urllib.error.URLError, OSError) as erro:
            motivo = getattr(erro, "reason", None) or type(erro).__name__
            raise FalhaNoEnvio(f"Não foi possível falar com o Telegram: {motivo}") from None
        if not corpo.get("ok"):
            raise FalhaNoEnvio(f"O Telegram recusou a mensagem: {corpo.get('description') or 'sem motivo'}")
        return corpo


def _json(dados: bytes) -> dict:
    try:
        corpo = json.loads(dados or b"{}")
    except ValueError:
        return {}
    return corpo if isinstance(corpo, dict) else {}

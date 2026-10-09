"""
A interface do canal de aviso — decisão D04: "CanalDeAviso.enviar(destinatario, mensagem)".

Trocar Telegram por e-mail é uma classe nova, não uma reescrita. Separado em módulo próprio para
o serviço de notificação (H4) e o de respostas (H7) usarem sem um importar o outro.
"""

from collections.abc import Sequence
from typing import Protocol

from cadastro.models import Usuario


class FalhaNoEnvio(Exception):
    """O canal não conseguiu entregar (sem internet, sem celular ligado, canal recusou). Texto para o log."""


class CanalDeAviso(Protocol):
    def enviar(self, destinatario: Usuario, mensagem: str, botoes: Sequence[tuple[str, str]] = ()) -> None:
        """
        Entrega a mensagem. `botoes` são pares (texto, dado) que a pessoa pode tocar para responder
        (H7, "Sim, pedir"); um canal que não tenha botão pode ignorá-los.
        """

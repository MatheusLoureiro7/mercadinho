"""
Serviço de notificação — tarefa H4. Operação 03, passos 9 a 12.

- RN12: dentro de uma janela de silêncio (horário da loja, tabela parametro) nada sai; os avisos
  PENDENTE passam a SEGURADO e saem na primeira rodada fora da janela. A verificação é na hora do
  ENVIO, não da geração.
- RN13: fora da janela, todos os avisos PENDENTE e SEGURADO de cada pessoa saem numa mensagem só,
  por urgência (Alerta.objects.por_urgencia), com UMA chamada ao canal; todos ficam ENVIADO com o
  mesmo enviado_em.

O canal é qualquer objeto com enviar(destinatario, mensagem) — a interface CanalDeAviso da D04
(Telegram: alertas/telegram.py, H5). Se o canal falhar com FalhaNoEnvio, a transação daquela pessoa
é desfeita — nada fica marcado como enviado, a próxima rodada tenta de novo — e as outras pessoas
recebem normalmente. Qualquer outro erro é defeito e não é engolido.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, time
from typing import Protocol

from django.db import transaction
from django.utils import timezone

from alertas import estados
from alertas.models import Alerta
from cadastro.models import Usuario
from comum.parametros import parametro

logger = logging.getLogger("mercadinho.avisos")

# Chaves da tabela parametro (schema.sql), no formato "HH:MM-HH:MM".
JANELAS_DE_SILENCIO = ("janela_silencio_manha", "janela_silencio_tarde")


class FalhaNoEnvio(Exception):
    """O canal não conseguiu entregar (sem internet, sem celular ligado, canal recusou). Texto para o log."""


class CanalDeAviso(Protocol):
    """D04: por onde o aviso chega. Trocar Telegram por e-mail é uma classe nova, não uma reescrita."""

    def enviar(self, destinatario: Usuario, mensagem: str) -> None: ...


@dataclass(frozen=True)
class ResultadoDoEnvio:
    enviados: int = 0  # avisos marcados ENVIADO
    mensagens: int = 0  # chamadas ao canal (uma por pessoa — RN13)
    segurados: int = 0  # avisos retidos na janela de silêncio (RN12)
    falhas: int = 0  # pessoas cuja mensagem não saiu (os avisos ficam para a próxima rodada)


def _faixa(texto: str) -> tuple[time, time]:
    inicio, fim = (time.fromisoformat(parte.strip()) for parte in texto.split("-"))
    return inicio, fim


def em_silencio(momento: datetime) -> bool:
    """
    RN12: o momento cai numa janela de silêncio? Horário local da loja. A faixa inclui o começo e
    não inclui o fim: "entre 10h30 e 13h" — às 13h00 o pico acabou e o aviso já pode sair.
    """
    hora = timezone.localtime(momento).time()
    return any(inicio <= hora < fim for inicio, fim in (_faixa(parametro(c)) for c in JANELAS_DE_SILENCIO))


def montar_mensagem(itens: list[str]) -> str:
    """RN13: um texto só, com os avisos numerados na ordem de urgência (vocabulário da loja, RNF10)."""
    linhas = [f"{posicao}. {item}" for posicao, item in enumerate(itens, start=1)]
    titulo = "Aviso do mercado:" if len(itens) == 1 else f"Avisos do mercado ({len(itens)}):"
    return "\n".join([titulo, *linhas])


def enviar_avisos(canal: CanalDeAviso) -> ResultadoDoEnvio:
    """Uma rodada do serviço de notificação. Pode ser chamada quantas vezes for preciso no dia."""
    agora = timezone.now()
    # Aviso sem destinatário (sem DONO cadastrado, H2) não tem para quem ir: fica PENDENTE, não some.
    abertos = Alerta.objects.a_enviar().filter(destinatario__isnull=False)

    if em_silencio(agora):
        with transaction.atomic():
            pendentes = list(abertos.filter(status=Alerta.Status.PENDENTE).select_for_update())
            return ResultadoDoEnvio(segurados=estados.segurar(pendentes))

    enviados = mensagens = falhas = 0
    for destinatario_id in abertos.values_list("destinatario_id", flat=True).distinct().order_by():
        try:
            with transaction.atomic():
                # Trava os avisos desta pessoa: uma entrada de mercadoria que queira cancelar um deles
                # espera o envio terminar, e nada sai pela metade.
                avisos = list(
                    abertos.filter(destinatario_id=destinatario_id).select_for_update().por_urgencia()
                )
                if not avisos:
                    continue
                canal.enviar(avisos[0].destinatario, montar_mensagem([aviso.mensagem for aviso in avisos]))
                enviados += estados.enviar(avisos, quando=agora)
                mensagens += 1
        except FalhaNoEnvio as erro:
            falhas += 1
            logger.warning("Avisos não enviados para o usuário %s: %s", destinatario_id, erro)
    return ResultadoDoEnvio(enviados=enviados, mensagens=mensagens, falhas=falhas)

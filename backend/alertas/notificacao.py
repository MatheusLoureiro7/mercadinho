"""
Serviço de notificação — tarefa H4. Operação 03, passos 9 a 12.

- RN12: dentro de uma janela de silêncio (horário da loja, tabela parametro) nada sai; os avisos
  PENDENTE passam a SEGURADO e saem na primeira rodada fora da janela. A verificação é na hora do
  ENVIO, não da geração.
- RN13: fora da janela, todos os avisos PENDENTE e SEGURADO de cada pessoa saem numa mensagem só,
  por urgência (Alerta.objects.por_urgencia), com UMA chamada ao canal; todos ficam ENVIADO com o
  mesmo enviado_em.

O canal é qualquer objeto com enviar(destinatario, mensagem) — a interface CanalDeAviso da D04
(Telegram: alertas/telegram.py, H5). Se o canal falhar com FalhaNoEnvio, o que não saiu fica para a
próxima rodada, e as outras pessoas recebem normalmente. Qualquer outro erro é defeito e não é
engolido.

Mensagem maior que o limite do canal (`limite_da_mensagem`; Telegram, 4096 caracteres) é dividida
AQUI, sempre entre um aviso e outro, e cada parte que sai marca os seus avisos como enviados (revisão
X1, item 17). Antes, o canal dividia: se a parte 1 saía e a 2 falhava, nada ficava marcado e a parte
1 era repetida na rodada seguinte. Para quem lê, nada muda: o título na primeira parte e a
numeração seguida.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, time

from django.db import transaction
from django.utils import timezone

from alertas import estados
from alertas.canal import CanalDeAviso, FalhaNoEnvio  # noqa: F401 — reexportados (H4, H5)
from alertas.models import Alerta
from alertas.respostas import botoes_da_mensagem
from comum.parametros import parametro

logger = logging.getLogger("mercadinho.avisos")

# Chaves da tabela parametro (schema.sql), no formato "HH:MM-HH:MM".
JANELAS_DE_SILENCIO = ("janela_silencio_manha", "janela_silencio_tarde")


@dataclass(frozen=True)
class ResultadoDoEnvio:
    enviados: int = 0  # avisos marcados ENVIADO
    mensagens: int = 0  # chamadas ao canal: uma por pessoa (RN13), uma por parte se passar do limite
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


def _titulo(quantos: int) -> str:
    return "Aviso do mercado:" if quantos == 1 else f"Avisos do mercado ({quantos}):"


def montar_mensagem(itens: list[str]) -> str:
    """RN13: um texto só, com os avisos numerados na ordem de urgência (vocabulário da loja, RNF10)."""
    linhas = [f"{posicao}. {item}" for posicao, item in enumerate(itens, start=1)]
    return "\n".join([_titulo(len(itens)), *linhas])


def _partes(avisos: list[Alerta], limite: int | None) -> list[tuple[str, list[Alerta]]]:
    """A mensagem da RN13 em partes de até `limite` caracteres, cortadas só entre avisos."""
    partes: list[tuple[str, list[Alerta]]] = []
    texto, da_parte = _titulo(len(avisos)), []
    for posicao, aviso in enumerate(avisos, start=1):
        linha = f"{posicao}. {aviso.mensagem}"
        if limite and da_parte and len(texto) + 1 + len(linha) > limite:
            partes.append((texto, da_parte))
            texto, da_parte = linha, [aviso]
        else:
            texto, da_parte = f"{texto}\n{linha}", [*da_parte, aviso]
    partes.append((texto, da_parte))
    return partes


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
    limite = getattr(canal, "limite_da_mensagem", None)
    for destinatario_id in abertos.values_list("destinatario_id", flat=True).distinct().order_by():
        with transaction.atomic():
            # Trava os avisos desta pessoa: uma entrada de mercadoria que queira cancelar um deles
            # espera o envio terminar.
            avisos = list(
                abertos.filter(destinatario_id=destinatario_id)
                .select_related("produto", "destinatario")
                .select_for_update(of=("self",))  # trava só os avisos, não o produto nem a pessoa
                .por_urgencia()
            )
            for texto, da_parte in _partes(avisos, limite) if avisos else []:
                try:
                    canal.enviar(
                        avisos[0].destinatario,
                        texto,
                        botoes=botoes_da_mensagem(da_parte),  # H7: "Sim, pedir" na parte do aviso
                    )
                except FalhaNoEnvio as erro:
                    # O que já saiu fica marcado; desta parte em diante, na próxima rodada.
                    falhas += 1
                    logger.warning("Avisos não enviados para o usuário %s: %s", destinatario_id, erro)
                    break
                enviados += estados.enviar(da_parte, quando=agora)
                mensagens += 1
    return ResultadoDoEnvio(enviados=enviados, mensagens=mensagens, falhas=falhas)

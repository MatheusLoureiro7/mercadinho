"""
Rodada diária — tarefa G5. Apostila IV, comunicação nº 4 (agendador, 03h00) e operação 03.

    falhas = rodar(saida)

Roda os passos na ordem da Apostila IV — importação → previsão → regras → notificação. Um passo
que falha não impede os seguintes: o aviso de validade não depende da planilha do caixa, e a
previsão roda com as vendas que já entraram (é dado derivado; a rodada de amanhã refaz). O erro
vai para o log, com o rastro, e o nome do passo volta na lista de falhas.

Quem dispara é o cron do computador da loja (decisão do grupo, 12/11/2026; D05), com as linhas
que o comando `agenda_cron` escreve a partir da tabela de parâmetros.

Rodada perdida (decisão do grupo, 16/11/2026, revisão X1 item 11): ao terminar — com ou sem falha —
a rodada anota o dia em ARQUIVO_ULTIMA_RODADA. De hora em hora, `rodada_diaria --se-faltar` roda só
se a de hoje não aconteceu (o notebook fechado às 03h00). E o fim de semana (RN10), que se avalia na
quinta, é avaliado na primeira rodada de sexta ou de sábado se a quinta não rodou.
"""

import logging
from datetime import date, timedelta

from django.conf import settings
from django.core.management import call_command
from django.utils import timezone

from alertas.ruptura import gerar_avisos_de_ruptura
from alertas.validade import gerar_avisos_de_validade
from previsao.agregacao import agregar_consumo_recente
from previsao.projecao import calcular_previsao

logger = logging.getLogger("mercadinho.rodada")

QUINTA, SEXTA, SABADO = 4, 5, 6  # isoweekday


def ultima_rodada() -> date | None:
    try:
        return date.fromisoformat(settings.ARQUIVO_ULTIMA_RODADA.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        return None


def anotar_rodada(dia: date) -> None:
    settings.ARQUIVO_ULTIMA_RODADA.parent.mkdir(parents=True, exist_ok=True)
    settings.ARQUIVO_ULTIMA_RODADA.write_text(dia.isoformat(), encoding="utf-8")


def avaliar_fim_de_semana(hoje: date, ultima: date | None) -> bool:
    """RN10 na quinta; na sexta ou no sábado, só se a quinta desta semana não rodou."""
    dia = hoje.isoweekday()
    if dia == QUINTA:
        return True
    if dia not in (SEXTA, SABADO):
        return False
    quinta = hoje - timedelta(days=dia - QUINTA)
    return ultima is None or ultima < quinta


def _importar_vendas(saida):
    call_command("importar_vendas", stdout=saida)


def _agregar_consumo(saida):
    saida.write(f"{agregar_consumo_recente()} linha(s) de consumo gravada(s).")


def _calcular_previsao(saida):
    saida.write(f"Previsão de {calcular_previsao()} produto(s).")


def _avisos_de_validade(saida):
    saida.write(f"{len(gerar_avisos_de_validade())} aviso(s) de validade novo(s).")


def _avisos_de_ruptura(saida):
    fim_de_semana = avaliar_fim_de_semana(timezone.localdate(), ultima_rodada())
    avisos = gerar_avisos_de_ruptura(avaliar_fim_de_semana=fim_de_semana)
    saida.write(f"{len(avisos)} aviso(s) de vai acabar ou de fim de semana novo(s).")


def _enviar_avisos(saida):
    call_command("enviar_avisos", stdout=saida)


PASSOS = [
    ("Importação das vendas do caixa", _importar_vendas),  # operação 04
    ("Consumo de cada dia", _agregar_consumo),  # G1, RN11
    ("Previsão de cada produto", _calcular_previsao),  # G2–G4: RN06–RN09, RF11
    ("Avisos de validade", _avisos_de_validade),  # H2, RN05
    ("Avisos de vai acabar e de fim de semana", _avisos_de_ruptura),  # H3, RN08, RN10
    ("Envio dos avisos pelo Telegram", _enviar_avisos),  # H5, RN12, RN13
]


def rodar(saida) -> list[str]:
    falhas = []
    for nome, passo in PASSOS:
        try:
            passo(saida)
        except Exception as erro:
            logger.exception("Rodada diária: o passo '%s' falhou.", nome)
            saida.write(f"{nome}: FALHOU — {erro}")
            falhas.append(nome)
        else:
            saida.write(f"{nome}: ok")
    anotar_rodada(timezone.localdate())
    return falhas

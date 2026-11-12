"""
Rodada diária — tarefa G5. Apostila IV, comunicação nº 4 (agendador, 03h00) e operação 03.

    falhas = rodar(saida)

Roda os passos na ordem da Apostila IV — importação → previsão → regras → notificação. Um passo
que falha não impede os seguintes: o aviso de validade não depende da planilha do caixa, e a
previsão roda com as vendas que já entraram (é dado derivado; a rodada de amanhã refaz). O erro
vai para o log, com o rastro, e o nome do passo volta na lista de falhas.

Quem dispara é o cron do computador da loja (decisão do grupo, 12/11/2026; D05), com as linhas
que o comando `agenda_cron` escreve a partir da tabela de parâmetros.
"""

import logging

from django.core.management import call_command

from alertas.validade import gerar_avisos_de_validade
from previsao.agregacao import agregar_consumo_recente
from previsao.projecao import calcular_previsao

logger = logging.getLogger("mercadinho.rodada")


def _importar_vendas(saida):
    call_command("importar_vendas", stdout=saida)


def _agregar_consumo(saida):
    saida.write(f"{agregar_consumo_recente()} linha(s) de consumo gravada(s).")


def _calcular_previsao(saida):
    saida.write(f"Previsão de {calcular_previsao()} produto(s).")


def _avisos_de_validade(saida):
    saida.write(f"{len(gerar_avisos_de_validade())} aviso(s) de validade novo(s).")


def _enviar_avisos(saida):
    call_command("enviar_avisos", stdout=saida)


PASSOS = [
    ("Importação das vendas do caixa", _importar_vendas),  # operação 04
    ("Consumo de cada dia", _agregar_consumo),  # G1, RN11
    ("Previsão de cada produto", _calcular_previsao),  # G2–G4: RN06–RN09, RF11
    ("Avisos de validade", _avisos_de_validade),  # H2, RN05
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
    return falhas

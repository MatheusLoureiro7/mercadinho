"""
Rodada do serviço de notificação — tarefa H5. Operação 03, passos 9 a 12.

    python backend/manage.py enviar_avisos

Junta os avisos abertos de cada pessoa numa mensagem só (RN13) e manda pelo Telegram; dentro da
janela de silêncio só segura (RN12). Pode rodar quantas vezes for preciso no dia: o agendador (G5)
chama às 03h00, depois da geração dos avisos, e de novo ao fim de cada janela de silêncio para
soltar os segurados. Termina com erro (código 1) se a mensagem de alguém não saiu — os avisos dessa
pessoa ficam para a próxima rodada.
"""

from django.core.management.base import BaseCommand, CommandError

from alertas.notificacao import enviar_avisos
from alertas.telegram import CanalTelegram


class Command(BaseCommand):
    help = "Envia os avisos abertos pelo Telegram, respeitando a janela de silêncio (RN12, RN13)."

    def handle(self, *args, **opcoes):
        resultado = enviar_avisos(CanalTelegram.configurado())
        if resultado.segurados:
            self.stdout.write(
                f"Horário de movimento: {resultado.segurados} aviso(s) segurado(s) para depois."
            )
        self.stdout.write(f"{resultado.enviados} aviso(s) enviado(s) em {resultado.mensagens} mensagem(ns).")
        if resultado.falhas:
            raise CommandError(
                f"A mensagem de {resultado.falhas} pessoa(s) não saiu; os avisos ficam para a "
                "próxima rodada. O motivo está no log."
            )

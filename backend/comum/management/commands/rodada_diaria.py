"""
Rodada diária — tarefa G5. O que o cron chama às 03h00 (Apostila IV, comunicação nº 4).

    python backend/manage.py rodada_diaria
    python backend/manage.py rodada_diaria --se-faltar    de hora em hora: só se a de hoje não rodou

Importação das vendas → consumo de cada dia → previsão → avisos de validade → envio pelo Telegram.
Um passo que falha não impede os outros; a rodada termina com erro (código 1) dizendo quais
falharam, e o motivo fica no log.
"""

from datetime import time

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from comum.parametros import parametro
from comum.rodada import rodar, ultima_rodada


class Command(BaseCommand):
    help = "Roda a rodada diária: importação, consumo, previsão e avisos (operação 03)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--se-faltar",
            action="store_true",
            help="Só roda se a rodada de hoje ainda não aconteceu e já passou da hora dela (X1, item 11).",
        )

    def handle(self, *args, **opcoes):
        dia = timezone.localdate()
        if opcoes["se_faltar"]:
            if ultima_rodada() == dia:
                self.stdout.write(f"A rodada de {dia:%d/%m/%Y} já aconteceu.")
                return
            hora, minuto = (int(parte) for parte in parametro("hora_rodada_diaria").split(":"))
            if timezone.localtime().time() < time(hora, minuto):
                self.stdout.write(f"Ainda não é hora da rodada de {dia:%d/%m/%Y}.")
                return
            self.stdout.write(f"A rodada de {dia:%d/%m/%Y} não tinha acontecido: rodando agora.")
        falhas = rodar(self.stdout)
        if falhas:
            raise CommandError(
                f"Rodada de {dia:%d/%m/%Y} com falha em: {', '.join(falhas)}. O motivo está no log."
            )
        self.stdout.write(f"Rodada de {dia:%d/%m/%Y} concluída.")

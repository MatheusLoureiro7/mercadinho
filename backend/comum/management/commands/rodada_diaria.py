"""
Rodada diária — tarefa G5. O que o cron chama às 03h00 (Apostila IV, comunicação nº 4).

    python backend/manage.py rodada_diaria

Importação das vendas → consumo de cada dia → previsão → avisos de validade → envio pelo Telegram.
Um passo que falha não impede os outros; a rodada termina com erro (código 1) dizendo quais
falharam, e o motivo fica no log.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from comum.rodada import rodar


class Command(BaseCommand):
    help = "Roda a rodada diária: importação, consumo, previsão e avisos (operação 03)."

    def handle(self, *args, **opcoes):
        dia = timezone.localdate()
        falhas = rodar(self.stdout)
        if falhas:
            raise CommandError(
                f"Rodada de {dia:%d/%m/%Y} com falha em: {', '.join(falhas)}. O motivo está no log."
            )
        self.stdout.write(f"Rodada de {dia:%d/%m/%Y} concluída.")

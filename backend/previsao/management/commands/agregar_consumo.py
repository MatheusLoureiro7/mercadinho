"""
Agregação do consumo diário — tarefa G1. Operação 03, passos 2 e 3; segundo passo da rodada diária.

    python backend/manage.py agregar_consumo                       os últimos 30 dias, até ontem
    python backend/manage.py agregar_consumo --desde 2026-06-01    do dia indicado até ontem

A ordem da rodada das 03h00 (G5) é: importação → previsão → regras → notificação.
"""

from datetime import date

from django.core.management.base import BaseCommand, CommandError

from previsao.agregacao import agregar_consumo, janela_recente


class Command(BaseCommand):
    help = "Soma as vendas de cada produto em cada dia (consumo_diario, RN11)."

    def add_arguments(self, parser):
        parser.add_argument("--desde", help="Primeiro dia a refazer, no formato AAAA-MM-DD.")

    def handle(self, *args, **opcoes):
        inicio, fim = janela_recente()
        if opcoes["desde"]:
            try:
                inicio = date.fromisoformat(opcoes["desde"])
            except ValueError as erro:
                raise CommandError("Use a data de --desde no formato AAAA-MM-DD.") from erro
        linhas = agregar_consumo(inicio, fim)
        self.stdout.write(f"Consumo de {inicio:%d/%m/%Y} a {fim:%d/%m/%Y}: {linhas} linha(s) gravada(s).")

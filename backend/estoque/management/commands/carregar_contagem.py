"""
Inventário de partida — tarefa J3. Formato: docs/FORMATO-PLANILHA-CONTAGEM.md.

    python backend/manage.py carregar_contagem docs/exemplos/contagem-de-partida.xlsx

Cada linha contada vira um lote com a sua entrada (origem INVENTARIO), pela mesma regra da tela de
Entrada de mercadoria (RN04). Se alguma linha estiver errada, nada é lançado: o comando lista todas
e termina com erro (código 1). Produto que já tinha estoque é mantido: rodar de novo não duplica.
"""

from django.core.management.base import BaseCommand, CommandError

from estoque.inventario import PlanilhaIlegivel, carregar_contagem


class Command(BaseCommand):
    help = "Lança a contagem física de partida como entrada de mercadoria (J3)."

    def add_arguments(self, parser):
        parser.add_argument("planilha", help="Caminho da planilha .xlsx")

    def handle(self, *args, **opcoes):
        try:
            resultado = carregar_contagem(opcoes["planilha"])
        except PlanilhaIlegivel as erro:
            raise CommandError(str(erro)) from erro

        if resultado.erros:
            for erro in resultado.erros:
                self.stdout.write(f"{erro.aba}, linha {erro.linha}, {erro.coluna}: {erro.mensagem}")
            raise CommandError(
                f"{len(resultado.erros)} linha(s) com problema. Nada foi gravado: "
                "corrija a planilha e rode de novo."
            )
        self.stdout.write(
            f"{resultado.lotes} lote(s) lançado(s). Contados com zero: {resultado.zerados}. "
            f"Já tinham estoque e foram mantidos: {resultado.mantidos}."
        )

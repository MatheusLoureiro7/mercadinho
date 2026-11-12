"""
Carga inicial dos produtos — tarefa J2. Formato: docs/FORMATO-PLANILHA-PRODUTOS.md.

    python backend/manage.py carregar_produtos docs/exemplos/produtos-iniciais.xlsx

Lê as abas Categorias, Fornecedores e Produtos e cadastra o que ainda não existe, pelas mesmas
regras da tela de Produtos. Se alguma linha estiver errada, nada é gravado: o comando lista todas
(aba, linha e coluna) e termina com erro (código 1). Rodar de novo não duplica.
"""

from django.core.management.base import BaseCommand, CommandError

from cadastro.carga import PlanilhaIlegivel, carregar_planilha


class Command(BaseCommand):
    help = "Carrega categorias, fornecedores e produtos de uma planilha do Excel (J2)."

    def add_arguments(self, parser):
        parser.add_argument("planilha", help="Caminho da planilha .xlsx")

    def handle(self, *args, **opcoes):
        try:
            resultado = carregar_planilha(opcoes["planilha"])
        except PlanilhaIlegivel as erro:
            raise CommandError(str(erro)) from erro

        if resultado.erros:
            for erro in resultado.erros:
                self.stdout.write(f"{erro.aba}, linha {erro.linha}, {erro.coluna}: {erro.mensagem}")
            raise CommandError(
                f"{len(resultado.erros)} linha(s) com problema. Nada foi gravado: "
                "corrija a planilha e rode de novo."
            )

        criados, mantidos = resultado.criados, resultado.mantidos
        self.stdout.write(
            f"{criados['categorias']} categoria(s), {criados['fornecedores']} fornecedor(es) e "
            f"{criados['produtos']} produto(s) novo(s). Já estavam cadastrados e foram mantidos: "
            f"{mantidos['categorias']} categoria(s), {mantidos['fornecedores']} fornecedor(es) e "
            f"{mantidos['produtos']} produto(s)."
        )

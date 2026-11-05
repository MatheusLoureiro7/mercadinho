"""
Importação das vendas do caixa — tarefa E3. Operação 04; primeiro passo da rodada diária.

    python backend/manage.py importar_vendas

Importa, em ordem de nome, as planilhas .xlsx da pasta PASTA_VENDAS_CAIXA (.env) que ainda não
entraram. A ordem da rodada das 03h00 (G5) é: importação → previsão → regras → notificação.
Termina com erro (código 1) se alguma planilha não pôde ser lida — as outras entram mesmo assim.
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from vendas.importacao import importar_planilha
from vendas.models import ImportacaoPdv


class Command(BaseCommand):
    help = "Importa as planilhas novas de vendas do caixa (operação 04)."

    def handle(self, *args, **opcoes):
        if not settings.PASTA_VENDAS_CAIXA:
            raise CommandError("Configure no .env a pasta das planilhas do caixa (PASTA_VENDAS_CAIXA).")
        pasta = Path(settings.PASTA_VENDAS_CAIXA)
        if not pasta.is_dir():
            raise CommandError(f"A pasta {pasta} não existe (PASTA_VENDAS_CAIXA).")

        ja_importadas = set(
            ImportacaoPdv.objects.filter(
                status__in=[ImportacaoPdv.Status.OK, ImportacaoPdv.Status.PARCIAL]
            ).values_list("arquivo_nome", flat=True)
        )
        novas = sorted(p for p in pasta.glob("*.xlsx") if p.name not in ja_importadas)
        if not novas:
            self.stdout.write("Nenhuma planilha nova para importar.")
            return

        com_erro = []
        for caminho in novas:
            importacao = importar_planilha(caminho)
            self.stdout.write(
                f"{caminho.name}: {importacao.get_status_display()} — {importacao.linhas_lidas} linha(s) "
                f"lida(s), {importacao.linhas_erro} pendente(s) ou com erro."
            )
            if importacao.status == ImportacaoPdv.Status.ERRO:
                com_erro.append(caminho.name)
        if com_erro:
            raise CommandError(f"Não foi possível ler: {', '.join(com_erro)}. O motivo está no log.")

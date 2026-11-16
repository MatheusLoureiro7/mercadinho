"""
Importação das vendas do caixa — tarefa E3. Operação 04; primeiro passo da rodada diária.

    python backend/manage.py importar_vendas

Importa, em ordem de nome, as planilhas .xlsx da pasta PASTA_VENDAS_CAIXA (.env) que ainda não
entraram: as de nome novo e as regravadas depois da última importação com o mesmo nome (o caixa que
salva sempre `vendas.xlsx`). Planilha cujas vendas já entraram é avisada e pulada (X1, item 1).
A ordem da rodada das 03h00 (G5) é: importação → previsão → regras → notificação.
Termina com erro (código 1) se alguma planilha não pôde ser lida — as outras entram mesmo assim.
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max

from vendas.importacao import ArquivoJaImportado, importar_planilha
from vendas.models import ImportacaoPdv


class Command(BaseCommand):
    help = "Importa as planilhas novas de vendas do caixa (operação 04)."

    def handle(self, *args, **opcoes):
        if not settings.PASTA_VENDAS_CAIXA:
            raise CommandError("Configure no .env a pasta das planilhas do caixa (PASTA_VENDAS_CAIXA).")
        pasta = Path(settings.PASTA_VENDAS_CAIXA)
        if not pasta.is_dir():
            raise CommandError(f"A pasta {pasta} não existe (PASTA_VENDAS_CAIXA).")

        ultima_importacao = dict(
            ImportacaoPdv.objects.filter(status__in=[ImportacaoPdv.Status.OK, ImportacaoPdv.Status.PARCIAL])
            .values_list("arquivo_nome")
            .annotate(Max("processado_em"))
        )

        def nova(caminho: Path) -> bool:
            importada_em = ultima_importacao.get(caminho.name)
            return importada_em is None or caminho.stat().st_mtime > importada_em.timestamp()

        novas = sorted(p for p in pasta.glob("*.xlsx") if nova(p))
        if not novas:
            self.stdout.write("Nenhuma planilha nova para importar.")
            return

        com_erro = []
        for caminho in novas:
            try:
                importacoes = importar_planilha(caminho)
            except ArquivoJaImportado:
                self.stdout.write(f"{caminho.name}: as vendas desta planilha já tinham entrado.")
                continue
            for importacao in importacoes:
                dia = f" ({importacao.data_referencia:%d/%m/%Y})" if len(importacoes) > 1 else ""
                self.stdout.write(
                    f"{caminho.name}{dia}: {importacao.get_status_display()} — {importacao.linhas_lidas} "
                    f"linha(s) lida(s), {importacao.linhas_erro} pendente(s) ou com erro."
                )
            if any(importacao.status == ImportacaoPdv.Status.ERRO for importacao in importacoes):
                com_erro.append(caminho.name)
        if com_erro:
            raise CommandError(f"Não foi possível ler: {', '.join(com_erro)}. O motivo está no log.")

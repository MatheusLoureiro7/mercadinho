"""
Linhas do crontab da rodada diária — tarefa G5 (decisão do grupo, 12/11/2026: cron, sem dependência
nova). Os horários vêm da tabela de parâmetros, nunca do programa:

- `hora_rodada_diaria` (03:00): a rodada inteira (`rodada_diaria`);
- o fim de cada janela de silêncio (13:00 e 18:00): `enviar_avisos` de novo, para soltar o que
  ficou segurado no horário de movimento (RN12).

    python backend/manage.py agenda_cron              mostra as linhas
    crontab -e                                        cole as linhas no fim do arquivo

O cron usa o fuso do computador: ele precisa estar no horário de São Paulo, e ligado às 03h00.
Mudou um horário na tabela de parâmetros? Gere as linhas de novo e troque no crontab.
"""

import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from comum.parametros import parametro

JANELAS_DE_SILENCIO = {"janela_silencio_manha": "da manhã", "janela_silencio_tarde": "da tarde"}


def _minuto_e_hora(texto: str) -> str:
    hora, minuto = (int(parte) for parte in texto.strip().split(":"))
    return f"{minuto} {hora}"


class Command(BaseCommand):
    help = "Mostra as linhas do crontab da rodada diária, com os horários da tabela de parâmetros."

    def handle(self, *args, **opcoes):
        log = settings.RAIZ_REPOSITORIO / "logs" / "rodada.log"
        manage = settings.BASE_DIR / "manage.py"

        def linha(quando: str, comando: str) -> str:
            chamada = f'"{sys.executable}" "{manage}" {comando}'
            return f'{quando} * * * cd "{settings.BASE_DIR}" && {chamada} >> "{log}" 2>&1'

        self.stdout.write(
            f"# Mercado do Sr. João — rodada diária (G5). Gerado em {timezone.localdate():%d/%m/%Y} "
            "por: python backend/manage.py agenda_cron"
        )
        self.stdout.write(linha(_minuto_e_hora(parametro("hora_rodada_diaria")), "rodada_diaria"))
        for chave, periodo in JANELAS_DE_SILENCIO.items():
            fim = parametro(chave).split("-")[1]
            self.stdout.write(f"# fim do horário de movimento {periodo}: solta os avisos segurados (RN12)")
            self.stdout.write(linha(_minuto_e_hora(fim), "enviar_avisos"))

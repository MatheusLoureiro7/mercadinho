"""
Avisa o Telegram para onde mandar as respostas do dono — tarefa H7.

    python backend/manage.py configurar_webhook --url https://<endereço do sistema>/api/telegram/
    python backend/manage.py configurar_webhook --remover

Só funciona com o sistema publicado na internet com HTTPS (decisão D05, onde o sistema vai rodar).
Precisa de TELEGRAM_BOT_TOKEN e TELEGRAM_WEBHOOK_SEGREDO no .env. Com o webhook ligado, o
vincular_telegram (H6) não lê mensagens: remova, vincule e ligue de novo.
"""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from alertas.canal import FalhaNoEnvio
from alertas.telegram import CanalTelegram


class Command(BaseCommand):
    help = "Liga (ou remove) o webhook do Telegram que recebe o 'Sim, pedir' do dono (H7)."

    def add_arguments(self, parser):
        grupo = parser.add_mutually_exclusive_group(required=True)
        grupo.add_argument("--url", help="https://<endereço do sistema>/api/telegram/")
        grupo.add_argument("--remover", action="store_true")

    def handle(self, *args, url, remover, **opcoes):
        canal = CanalTelegram.configurado()
        try:
            if remover:
                canal.desligar_webhook()
                self.stdout.write("Webhook removido: o Telegram não manda mais as respostas para o sistema.")
                return
            if not url.startswith("https://"):
                raise CommandError("O Telegram só aceita endereço https:// para o webhook.")
            if not settings.TELEGRAM_WEBHOOK_SEGREDO:
                raise CommandError("Preencha TELEGRAM_WEBHOOK_SEGREDO no .env antes de ligar o webhook.")
            canal.ligar_webhook(url, settings.TELEGRAM_WEBHOOK_SEGREDO)
        except FalhaNoEnvio as erro:
            raise CommandError(str(erro)) from None
        self.stdout.write(f"Webhook ligado: as respostas do dono vão para {url}")

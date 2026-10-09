"""
Liga o celular do dono ao usuário dele — tarefa H6. Feito uma vez, na instalação (ou ao trocar
de celular), como o criar_usuario:

    python backend/manage.py vincular_telegram --login joao

Mostra um código e o link do bot; o Sr. João manda o código ao bot pelo celular; o sistema grava o
chat dele e manda uma confirmação. Precisa do TELEGRAM_BOT_TOKEN no .env (H5).
"""

from django.core.management.base import BaseCommand, CommandError

from alertas import vinculo
from alertas.notificacao import FalhaNoEnvio
from alertas.telegram import CanalTelegram
from cadastro.models import Usuario

SEGUNDOS_POR_MINUTO = 60


class Command(BaseCommand):
    help = "Liga o celular do dono ao usuário dele, para os avisos chegarem pelo Telegram (H6)."

    def add_arguments(self, parser):
        parser.add_argument("--login", required=True)
        parser.add_argument("--minutos", type=int, default=5, help="quanto tempo o código vale (padrão 5)")

    def handle(self, *args, login, minutos, **opcoes):
        try:
            usuario = Usuario.objects.get(login=login)
        except Usuario.DoesNotExist:
            raise CommandError(f"Não existe usuário com o login {login!r}.") from None
        try:
            vinculo.conferir_quem_recebe(usuario)
        except ValueError as erro:
            raise CommandError(str(erro)) from None

        canal = CanalTelegram.configurado()
        try:
            bot = canal.nome_do_bot()
            codigo = vinculo.gerar_codigo()
            self.stdout.write(
                f"No celular de {usuario.nome}, abra o Telegram e mande ao bot @{bot} esta mensagem:\n\n"
                f"    /start {codigo}\n\n"
                f"Ou abra este link no celular e toque em Iniciar: https://t.me/{bot}?start={codigo}\n"
                f"Esperando a mensagem (até {minutos} minuto(s))..."
            )
            chat = vinculo.esperar_o_codigo(canal, codigo, prazo_segundos=minutos * SEGUNDOS_POR_MINUTO)
            if chat is None:
                raise CommandError(
                    f"O código não chegou em {minutos} minuto(s). Rode o comando de novo para gerar outro."
                )
            vinculo.vincular(usuario, chat, canal)
        except FalhaNoEnvio as erro:
            raise CommandError(str(erro)) from None
        self.stdout.write(
            f"Pronto: o celular de {usuario.nome} está ligado. A confirmação foi enviada para ele."
        )

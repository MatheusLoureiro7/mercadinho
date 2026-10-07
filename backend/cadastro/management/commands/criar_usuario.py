"""
Cria um dos três usuários do sistema (RN14) — tarefa A4, decisão da L14 (docs/LACUNAS.md).

    python backend/manage.py criar_usuario --login sobrinho --nome "Sobrinho" --papel OPERACAO

A senha é pedida no terminal, duas vezes, e nunca aparece na tela nem no histórico do terminal.
Para trocar a senha depois: python backend/manage.py changepassword <login>
"""

from getpass import getpass

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cadastro.models import Usuario


class Command(BaseCommand):
    help = "Cria um usuário do sistema: DONO, GESTAO ou OPERACAO (RN14)."

    def add_arguments(self, parser):
        parser.add_argument("--login", required=True)
        parser.add_argument("--nome", required=True)
        parser.add_argument("--papel", required=True, help="DONO, GESTAO ou OPERACAO")

    def handle(self, *args, login, nome, papel, **opcoes):
        papel = papel.upper()
        if papel not in Usuario.Papel.values:
            raise CommandError("Papel inválido. Use DONO, GESTAO ou OPERACAO (RN14).")
        if Usuario.objects.filter(login=login).exists():
            raise CommandError(f"Já existe um usuário com o login '{login}'.")

        senha = getpass("Senha: ")
        if senha != getpass("Repita a senha: "):
            raise CommandError("As senhas não conferem. Nada foi gravado.")
        try:
            validate_password(senha, Usuario(login=login, nome=nome, papel=papel))
        except ValidationError as erro:
            raise CommandError(" ".join(erro.messages)) from erro

        with transaction.atomic():
            Usuario.objects.create_user(login=login, senha=senha, nome=nome, papel=papel)
        self.stdout.write(self.style.SUCCESS(f"Usuário '{login}' criado com o papel {papel}."))

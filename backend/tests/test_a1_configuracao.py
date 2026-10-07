"""
Tarefa A1 — a configuração do projeto obedece ao que a especificação fixa.
"""

from django.apps import apps
from django.conf import settings

APPS_DO_SISTEMA = ["comum", "cadastro", "estoque", "vendas", "previsao", "alertas", "caixa"]


def test_a1_banco_e_postgresql():
    # Apostila IV, figura 2 e seção 3: PostgreSQL. Nunca SQLite.
    assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"


def test_a1_fuso_e_horario_da_loja():
    # RN12: as janelas de silêncio são em horário local da loja.
    assert settings.TIME_ZONE == "America/Sao_Paulo"
    assert settings.USE_TZ is True


def test_a1_idioma_portugues():
    assert settings.LANGUAGE_CODE == "pt-br"


def test_a1_todos_os_apps_do_sistema_estao_instalados():
    for nome in APPS_DO_SISTEMA:
        assert apps.is_installed(nome), f"app {nome} não está instalado"


def test_a1_nao_ha_templates_django():
    # Apostila IV, seção 3: o painel é estático e só fala com a API.
    assert settings.TEMPLATES == []

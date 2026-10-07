"""
Configuração do Django — Sistema de Gestão de Estoque e Compras (Mercado do Sr. João).

Todo valor que muda entre máquinas vem de variável de ambiente (arquivo .env na raiz do
repositório; modelo em .env.example). Nada de senha ou chave escrita aqui.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # pasta backend/
RAIZ_REPOSITORIO = BASE_DIR.parent

load_dotenv(RAIZ_REPOSITORIO / ".env")


def _bool_env(nome: str, padrao: bool = False) -> bool:
    return os.environ.get(nome, str(padrao)).strip().lower() in {"1", "true", "sim", "yes"}


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
DEBUG = _bool_env("DJANGO_DEBUG", False)

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "chave-apenas-para-desenvolvimento-local"  # noqa: S105
    else:
        raise RuntimeError("Defina DJANGO_SECRET_KEY no arquivo .env.")

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()
]


INSTALLED_APPS = [
    # Infraestrutura do framework. Ver docs/LACUNAS.md, L09: as tabelas internas do Django não
    # fazem parte das 14 tabelas da Apostila IV, e o uso do modelo de usuário do Django ainda
    # depende de decisão do grupo (tarefa A4).
    "django.contrib.contenttypes",
    "django.contrib.auth",
    # Apps do sistema — estrutura do CLAUDE.md, uma por área da Apostila IV.
    "comum",
    "cadastro",
    "estoque",
    "vendas",
    "previsao",
    "alertas",
    "caixa",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

# Não há templates: o painel web é estático e só conversa com a API (Apostila IV, seção 3).
TEMPLATES = []

WSGI_APPLICATION = "core.wsgi.application"


# Banco de dados — PostgreSQL, fixado pela Apostila IV. Nunca SQLite, nem "só para testar".
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB", "mercadinho"),
        "USER": os.environ.get("POSTGRES_USER", "mercadinho"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}


# Idioma e fuso — as janelas de silêncio da RN12 são em horário local da loja.
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"  # schema.sql usa SERIAL (inteiro), não BIGSERIAL

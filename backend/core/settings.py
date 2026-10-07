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
    # fazem parte das 14 tabelas da Apostila IV. O modelo de usuário sobre a tabela `usuario`
    # entra na B1 (decisão da L09, 06/10/2026).
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
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
    "comum.registro.RegistroDeRequisicao",  # primeiro: mede o tempo da requisição inteira
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

# Não há templates: o painel web é estático e só conversa com a API (Apostila IV, seção 3).
TEMPLATES = []

WSGI_APPLICATION = "core.wsgi.application"


# API REST — tarefa A3.
REST_FRAMEWORK = {
    # Só JSON: sem a página navegável do DRF, que depende de templates.
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_CONTENT_NEGOTIATION_CLASS": "comum.negociacao.SempreJson",
    # A tarefa A4 troca estas duas linhas: token assinado e verificação do papel (RN14) antes de
    # qualquer operação. Até lá não existe nenhum endpoint com dado da loja.
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "EXCEPTION_HANDLER": "comum.erros.tratar_excecao",
    # Dinheiro e quantidade saem como texto ("12.500"), nunca como float (CLAUDE.md).
    "COERCE_DECIMAL_TO_STRING": True,
}


# Usuário do sistema: a tabela `usuario` da Apostila IV (decisão da L09, tarefa B1).
AUTH_USER_MODEL = "cadastro.Usuario"


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


# Registro de log — tarefa A3.
# Console sempre; arquivo em LOG_ARQUIVO (rotação a cada 5 MB, guarda os 5 últimos). Deixe
# LOG_ARQUIVO vazio no .env para gravar só no console.
LOG_NIVEL = os.environ.get("LOG_NIVEL", "INFO").upper()
LOG_ARQUIVO = os.environ.get("LOG_ARQUIVO", "logs/mercadinho.log").strip()
if LOG_ARQUIVO and not Path(LOG_ARQUIVO).is_absolute():
    LOG_ARQUIVO = str(RAIZ_REPOSITORIO / LOG_ARQUIVO)  # relativo à raiz do repositório

_manipuladores_log = {
    "console": {"class": "logging.StreamHandler", "formatter": "padrao"},
}
if LOG_ARQUIVO:
    Path(LOG_ARQUIVO).parent.mkdir(parents=True, exist_ok=True)
    _manipuladores_log["arquivo"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": LOG_ARQUIVO,
        "maxBytes": 5 * 1024 * 1024,
        "backupCount": 5,
        "encoding": "utf-8",
        "formatter": "padrao",
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "padrao": {
            "format": "{asctime} {levelname:<7} {name} {message}",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style": "{",
        },
    },
    "handlers": _manipuladores_log,
    "root": {"handlers": list(_manipuladores_log), "level": "WARNING"},
    "loggers": {
        "mercadinho": {"level": LOG_NIVEL},
        # O Django registra cada 4xx de novo; a linha do mercadinho.requisicao já basta.
        "django.request": {"level": "ERROR"},
    },
}

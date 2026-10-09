"""
Utilitários compartilhados pelos testes.
"""

import importlib.util
import json
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from wsgiref.simple_server import WSGIRequestHandler, make_server

import pytest
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIHandler
from django.db import connection, connections

RAIZ = Path(__file__).resolve().parents[2]
SCHEMA_SQL = RAIZ / "schema.sql"


def colunas_do_schema(tabela: str) -> dict[str, dict]:
    """
    Lê o CREATE TABLE da tabela no schema.sql (a transcrição da Apostila IV) e devolve, para cada
    coluna: tipo, tamanho/precisão, se aceita nulo e o valor padrão.
    """
    texto = SCHEMA_SQL.read_text(encoding="utf-8")
    bloco = re.search(rf"CREATE TABLE {tabela} \((.*?)\n\);", texto, re.S)
    assert bloco, f"tabela {tabela} não encontrada no schema.sql"

    colunas = {}
    for linha in bloco.group(1).splitlines():
        linha = linha.split("--")[0].strip().rstrip(",")
        m = re.match(r"([a-z_]+)\s+([A-Z]+)(?:\((\d+)(?:,(\d+))?\))?(.*)", linha)
        if not m or m.group(1) in {"constraint", "primary"} or linha.startswith("CONSTRAINT"):
            continue
        nome, tipo, tamanho, escala, resto = m.groups()
        padrao = re.search(r"DEFAULT\s+(\S+)", resto)
        colunas[nome] = {
            "tipo": tipo,
            "tamanho": int(tamanho) if tamanho else None,
            "escala": int(escala) if escala else None,
            "nulo": "NOT NULL" not in resto and "PRIMARY KEY" not in resto,
            "padrao": padrao.group(1) if padrao else None,
        }
    return colunas


# Tipo no schema.sql → como o PostgreSQL descreve em information_schema.columns
TIPOS_POSTGRES = {
    "SERIAL": "integer",
    "INTEGER": "integer",
    "SMALLINT": "smallint",
    "VARCHAR": "character varying",
    "NUMERIC": "numeric",
    "BOOLEAN": "boolean",
    "DATE": "date",
    "TIMESTAMPTZ": "timestamp with time zone",
    "TEXT": "text",
    "JSONB": "jsonb",
}


def colunas_no_banco(tabela: str) -> dict[str, dict]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT column_name, data_type, character_maximum_length, numeric_precision,
                   numeric_scale, is_nullable, column_default, is_identity
              FROM information_schema.columns
             WHERE table_schema = 'public' AND table_name = %s
            """,
            [tabela],
        )
        return {
            nome: {
                "tipo": tipo,
                "tamanho": tamanho or precisao,
                "escala": escala,
                "nulo": nulo == "YES",
                "padrao": padrao,
                "identidade": identidade == "YES",
            }
            for nome, tipo, tamanho, precisao, escala, nulo, padrao, identidade in cursor.fetchall()
        }


def restricoes(tabela: str) -> set[str]:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT conname FROM pg_constraint WHERE conrelid = %s::regclass",
            [tabela],
        )
        return {linha[0] for linha in cursor.fetchall()}


def _sem_conversao(padrao: str | None) -> str:
    """O PostgreSQL devolve o padrão de texto com a conversão de tipo ('TELEGRAM'::character
    varying); o schema.sql escreve só 'TELEGRAM'. É o mesmo padrão (achado na H1)."""
    return re.sub(r"::[a-z ]+$", "", (padrao or "").lower())


def divergencias_do_schema(tabela: str) -> list[str]:
    """
    Compara a tabela criada pelas migrações com o CREATE TABLE do schema.sql (Apostila IV) e
    devolve a lista do que difere: colunas a mais ou a menos, tipo, tamanho, casas decimais,
    obrigatoriedade e valor padrão. Lista vazia = igual à apostila.
    """
    esperado, real = colunas_do_schema(tabela), colunas_no_banco(tabela)
    erros = [f"coluna fora da apostila: {c}" for c in sorted(set(real) - set(esperado))]
    erros += [f"coluna da apostila ausente: {c}" for c in sorted(set(esperado) - set(real))]
    for nome in sorted(set(esperado) & set(real)):
        e, r = esperado[nome], real[nome]
        if r["tipo"] != TIPOS_POSTGRES[e["tipo"]]:
            erros.append(f"{nome}: tipo {r['tipo']}, apostila {e['tipo']}")
        if e["tamanho"] and r["tamanho"] != e["tamanho"]:
            erros.append(f"{nome}: tamanho {r['tamanho']}, apostila {e['tamanho']}")
        if e["escala"] is not None and r["escala"] != e["escala"]:
            erros.append(f"{nome}: casas decimais {r['escala']}, apostila {e['escala']}")
        if r["nulo"] != e["nulo"]:
            erros.append(f"{nome}: aceita nulo? {r['nulo']}, apostila {e['nulo']}")
        if e["tipo"] == "SERIAL":
            # SERIAL e IDENTITY são o mesmo inteiro sequencial; o Django gera IDENTITY.
            if not (r["identidade"] or (r["padrao"] or "").startswith("nextval")):
                erros.append(f"{nome}: sem sequência")
        elif _sem_conversao(r["padrao"]) != _sem_conversao(e["padrao"]):
            erros.append(f"{nome}: padrão {r['padrao']}, apostila {e['padrao']}")
    return erros


def indices(tabela: str) -> dict[str, str]:
    """Nome → definição (CREATE INDEX ...) de cada índice da tabela."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT indexname, indexdef FROM pg_indexes WHERE tablename = %s", [tabela])
        return dict(cursor.fetchall())


@pytest.fixture(autouse=True)
def _hash_de_senha_rapido_nos_testes(settings):
    """
    O hash de senha de verdade (PBKDF2) é lento de propósito. Nos testes usamos um rápido, só para
    a suíte não demorar; o sistema real continua com o padrão do Django
    (test_rnf12_sistema_usa_o_hash_de_senha_forte_do_django garante isso).
    """
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


# --- Testes de tela (tarefa C6) ------------------------------------------------------------------
# O painel de verdade no navegador, falando com a API de verdade, que grava no banco de teste:
#
#     navegador → frontend/servir.py → API (Django) → PostgreSQL
#
# Os testes marcados com @pytest.mark.tela usam `page` (pytest-playwright) e a fixture `painel`.
# Antes da primeira vez, em cada máquina:  playwright install chromium


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    # O computador da loja: tela de 1024 px, português, horário de São Paulo.
    return {
        **browser_context_args,
        "viewport": {"width": 1024, "height": 768},
        "locale": "pt-BR",
        "timezone_id": "America/Sao_Paulo",
    }


class _ApiSemRegistro(WSGIRequestHandler):
    def log_message(self, *args):
        pass


def _no_fundo(servidor) -> str:
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{servidor.server_address[1]}"


def carregar_servir():
    """O frontend/servir.py como módulo (ele não é um pacote Python)."""
    especificacao = importlib.util.spec_from_file_location("servir", RAIZ / "frontend" / "servir.py")
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def pytest_collection_modifyitems(config, items):
    """
    O Playwright síncrono deixa um laço assíncrono aberto enquanto o navegador existir (até o fim
    da sessão de testes), e o Django passa a recusar o ORM achando que está em código assíncrono.
    É o caso previsto pela documentação do Playwright para Django: liberar com
    DJANGO_ALLOW_ASYNC_UNSAFE — só quando a execução tem teste de tela; o sistema não tem código
    assíncrono e nada muda fora dos testes.

    Os testes de tela rodam por último: depois que o navegador abre, o Django guarda as conexões
    num contexto diferente, e um teste comum rodando depois deixaria uma conexão aberta (o banco de
    teste não poderia ser apagado no fim). De quebra, os testes rápidos dão resultado primeiro.
    """
    de_tela = [item for item in items if item.get_closest_marker("tela")]
    if de_tela:
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        items[:] = [item for item in items if not item.get_closest_marker("tela")] + de_tela


def _regravar_parametros_iniciais():
    """
    Os 7 valores da tabela `parametro` (L21) são gravados por migração. Um teste com transação de
    verdade esvazia o banco ao terminar, e o seguinte ficaria sem eles (a consulta de lotes falha
    sem o "3 dias" da RN05 — achado na D3). A restauração automática do Django não serve aqui: com
    o laço do Playwright aberto, a conexão do teste é outro objeto. Roda de novo a própria função
    da migração (que não duplica o que já existe).
    """
    from django.apps import apps

    importlib.import_module("comum.migrations.0002_parametros_iniciais").criar(apps, schema_editor=None)


@pytest.fixture
def painel(transactional_db):
    """
    Sobe a API (a aplicação WSGI do Django) e o servir.py na frente dela; devolve o endereço do
    painel. O banco é o de teste, com transação de verdade, porque a API roda em outra thread.
    """
    _regravar_parametros_iniciais()
    cache.clear()  # zera o limite de 10 logins por minuto (RNF12) entre um teste e outro

    api = make_server("127.0.0.1", 0, WSGIHandler(), handler_class=_ApiSemRegistro)
    servidor_do_painel = carregar_servir().criar_servidor(porta=0, endereco_api=_no_fundo(api))
    endereco = _no_fundo(servidor_do_painel)
    yield endereco
    for servidor in (servidor_do_painel, api):
        servidor.shutdown()
        servidor.server_close()
    # Com o laço do Playwright aberto, a conexão que o próprio teste usou (para montar e conferir
    # dados) não é fechada pelo pytest-django; sem isto, o banco de teste não poderia ser apagado.
    connections.close_all()


def entrar_pelo_login(page, painel: str, login: str, senha: str):
    """Entra no sistema pela tela de Login, como a pessoa faz."""
    page.goto(painel + "/login.html")
    page.fill("#campo-login", login)
    page.fill("#campo-senha", senha)
    page.click("#botao-entrar")


def guardar_sessao(page, painel: str, usuario):
    """Inicia a sessão sem passar pelo formulário de Login (que tem o seu próprio teste): guarda o
    token como a tela de Login guardaria (js/sessao.js)."""
    from comum.autenticacao import gerar_token  # depois do Django configurado

    page.goto(painel + "/login.html")
    page.evaluate(
        "([token]) => sessionStorage.setItem('mercadinho.token', token)",
        [gerar_token(usuario)],
    )


def abrir_tela(page, painel: str, usuario, tela: str):
    """Abre uma tela já com a sessão iniciada e espera ela conferir a sessão e montar o menu."""
    guardar_sessao(page, painel, usuario)
    page.goto(f"{painel}/{tela}")
    page.wait_for_selector("#menu a")  # a tela conferiu a sessão com a API e montou o menu


# ------------------------------------------------------------------------------------------------
# Telegram de mentira (H5, H6): a API de bots na própria máquina. O HTTP é de verdade, só o
# endereço muda — CanalTelegram(token=..., endereco=<este>).
# ------------------------------------------------------------------------------------------------


class _TelegramDeMentira(BaseHTTPRequestHandler):
    recebidas: list = []  # toda chamada: caminho, tipo, corpo
    respostas: list = []  # (código, corpo) forçados, um por chamada; vazio = comportamento normal
    atualizacoes: list = []  # o que o getUpdates devolve (mensagens mandadas ao bot)
    usuario_do_bot = "MercadoSrJoaoBot"

    def do_POST(self):
        tamanho = int(self.headers.get("Content-Length") or 0)
        corpo = json.loads(self.rfile.read(tamanho) or b"{}")
        self.recebidas.append(
            {"caminho": self.path, "tipo": self.headers.get("Content-Type"), "corpo": corpo}
        )
        if self.respostas:
            codigo, resposta = self.respostas.pop(0)
        else:
            codigo, resposta = (
                200,
                {"ok": True, "result": self._resultado(self.path.rsplit("/", 1)[-1], corpo)},
            )
        dados = json.dumps(resposta).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def _resultado(self, metodo, corpo):
        if metodo == "getMe":
            return {"id": 1, "is_bot": True, "username": self.usuario_do_bot}
        if metodo == "getUpdates":
            desde = corpo.get("offset") or 0
            return [a for a in self.atualizacoes if a["update_id"] >= desde]
        return {}

    def log_message(self, *args):
        pass


@pytest.fixture
def telegram():
    """(endereço, classe do servidor) — a classe guarda recebidas, respostas e atualizacoes."""
    _TelegramDeMentira.recebidas = []
    _TelegramDeMentira.respostas = []
    _TelegramDeMentira.atualizacoes = []
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), _TelegramDeMentira)
    threading.Thread(target=servidor.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True).start()
    yield f"http://127.0.0.1:{servidor.server_address[1]}", _TelegramDeMentira
    servidor.shutdown()
    servidor.server_close()

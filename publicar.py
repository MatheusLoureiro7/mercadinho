"""
Esteira de publicação em ambiente de teste — tarefa A5 (decisão D05: o computador do Matheus).

    python publicar.py                  atualiza, confere, testa e, se tudo passar, publica
    python publicar.py --sem-atualizar  publica o que está na pasta, sem git pull
    python publicar.py --parar          para a API e o painel publicados

Rode com o ambiente do projeto ativado (.venv): o script usa o mesmo Python para tudo.

Decisão do grupo (13/11/2026): só a biblioteca padrão e o servidor do próprio Django, sem
dependência nova — o uso previsto é a demonstração. Um servidor de produção ficaria para outra
decisão do grupo.

A ordem protege o que está no ar. Primeiro o que não mexe nele: código, dependências, banco, padrão
do código (ruff) e TODOS os testes (que usam um banco próprio). Só se tudo passar: a migração do
banco de verdade e a troca dos servidores — API em 127.0.0.1:8000 e painel em 127.0.0.1:8090,
o painel repassando /api/ para a API (L25). Passo que falha para a esteira e o sistema publicado
continua como estava. Cada publicação vai para logs/publicacoes.log; a saída dos servidores, para
logs/api.log e logs/painel.log.
"""

import argparse
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PASTA_ESTADO = RAIZ / ".publicacao"  # o número de cada servidor no ar (fora do git)
PASTA_LOGS = RAIZ / "logs"
REGISTRO = PASTA_LOGS / "publicacoes.log"
PY = sys.executable
PAINEL = "http://127.0.0.1:8090"
ESPERA_SEGUNDOS = 30

# O que precisa dar certo antes de mexer no que está no ar, nesta ordem.
CONFERENCIAS = [
    ("Atualizar o código", ["git", "pull", "--ff-only"]),
    ("Instalar as dependências", [PY, "-m", "pip", "install", "--quiet", "-r", "requirements-dev.txt"]),
    ("Subir o banco", ["docker", "compose", "up", "-d", "--wait"]),
    ("Conferir o padrão do código", [PY, "-m", "ruff", "check", "."]),
    ("Conferir o formato do código", [PY, "-m", "ruff", "format", "--check", "."]),
    ("Rodar todos os testes", [PY, "-m", "pytest", "-q"]),
]
MIGRACAO = ("Aplicar as migrações no banco", [PY, "backend/manage.py", "migrate", "--noinput"])
SERVIDORES = [
    ("api", [PY, "backend/manage.py", "runserver", "127.0.0.1:8000", "--noreload"]),
    ("painel", [PY, str(Path("frontend") / "servir.py")]),
]
ENDERECOS = [PAINEL + "/login.html", PAINEL + "/api/"]


class Maquina:
    """O terminal e os processos de verdade. Os testes trocam por uma de mentira."""

    def rodar(self, comando: list[str]) -> int:
        return subprocess.run(comando, cwd=RAIZ).returncode  # noqa: S603 — comandos fixos deste arquivo

    def iniciar(self, nome: str, comando: list[str], log: Path) -> int:
        separado = (
            {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS}
            if os.name == "nt"
            else {"start_new_session": True}
        )
        with open(log, "a", encoding="utf-8") as saida:
            processo = subprocess.Popen(  # noqa: S603 — comandos fixos deste arquivo
                comando, cwd=RAIZ, stdout=saida, stderr=subprocess.STDOUT, **separado
            )
        return processo.pid

    def parar(self, pid: int) -> None:
        try:
            os.kill(pid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError, OSError):
            pass  # já tinha parado

    def respondeu(self, endereco: str) -> bool:
        try:
            with urllib.request.urlopen(endereco, timeout=3) as resposta:  # noqa: S310 — http://127.0.0.1 fixo
                return resposta.status < 500
        except urllib.error.HTTPError as erro:
            return erro.code < 500  # 401 da API sem login também é "no ar"
        except (urllib.error.URLError, OSError):
            return False

    def commit(self) -> str:
        resultado = subprocess.run(  # noqa: S603 — comando fixo
            ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607 — o git do PATH, como no passo 1
            cwd=RAIZ,
            capture_output=True,
            text=True,
        )
        return resultado.stdout.strip() or "sem commit"


def _registrar(texto: str) -> None:
    REGISTRO.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRO, "a", encoding="utf-8") as registro:
        registro.write(f"{datetime.now():%d/%m/%Y %H:%M} · {texto}\n")


def _avisar(texto: str) -> None:
    print(texto, flush=True)


def parar_servidores(maquina) -> None:
    for nome, _ in SERVIDORES:
        arquivo = PASTA_ESTADO / f"{nome}.pid"
        if arquivo.exists():
            maquina.parar(int(arquivo.read_text().strip() or 0))
            arquivo.unlink()


def iniciar_servidores(maquina) -> None:
    PASTA_ESTADO.mkdir(parents=True, exist_ok=True)
    PASTA_LOGS.mkdir(parents=True, exist_ok=True)
    for nome, comando in SERVIDORES:
        pid = maquina.iniciar(nome, comando, PASTA_LOGS / f"{nome}.log")
        (PASTA_ESTADO / f"{nome}.pid").write_text(str(pid))


def esperar_resposta(maquina) -> bool:
    limite = time.monotonic() + ESPERA_SEGUNDOS
    while True:
        if all(maquina.respondeu(endereco) for endereco in ENDERECOS):
            return True
        if time.monotonic() >= limite:
            return False
        time.sleep(1)


def principal(argumentos: list[str] | None = None, maquina=None) -> int:
    leitor = argparse.ArgumentParser(description="Publica o sistema no computador do Matheus (A5).")
    leitor.add_argument("--sem-atualizar", action="store_true", help="não faz git pull")
    leitor.add_argument("--parar", action="store_true", help="só para a API e o painel publicados")
    opcoes = leitor.parse_args(argumentos)
    maquina = maquina or Maquina()

    if opcoes.parar:
        parar_servidores(maquina)
        _avisar("API e painel parados.")
        _registrar("parado")
        return 0

    passos = [p for p in CONFERENCIAS if not (opcoes.sem_atualizar and p[1][0] == "git")] + [MIGRACAO]
    for numero, (nome, comando) in enumerate(passos, start=1):
        _avisar(f"[{numero}/{len(passos) + 1}] {nome}…")
        if maquina.rodar(comando) != 0:
            _avisar(f"Parou em: {nome}. Nada foi publicado; o sistema no ar continua como estava.")
            _registrar(f"NÃO publicado — falhou em: {nome} (commit {maquina.commit()})")
            return 1

    _avisar(f"[{len(passos) + 1}/{len(passos) + 1}] Trocar a API e o painel…")
    parar_servidores(maquina)
    iniciar_servidores(maquina)
    if not esperar_resposta(maquina):
        _avisar("A API ou o painel não respondeu. Veja logs/api.log e logs/painel.log.")
        _registrar(f"publicado, mas não respondeu (commit {maquina.commit()})")
        return 1

    _avisar(f"Publicado. Painel em {PAINEL}/ — API em http://127.0.0.1:8000/api/")
    _registrar(f"publicado (commit {maquina.commit()})")
    return 0


if __name__ == "__main__":
    sys.exit(principal())

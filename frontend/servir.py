"""
Servidor do painel para desenvolvimento — tarefa B7, decisão L25 (docs/LACUNAS.md).

O painel e a API ficam na MESMA ORIGEM: o navegador só conhece um endereço, o painel chama
sempre "/api/..." e não existe CORS para configurar. Este script faz isso na máquina do grupo:

    /api/...    → repassado para a API (Django), do jeito que veio
    /           → leva para a tela de Login
    o resto     → arquivo estático da pasta frontend/

Em produção (decisão D05) o servidor web faz o mesmo papel. Só biblioteca padrão do Python:
nenhuma dependência nova (CLAUDE.md). O painel continua separado do servidor da API, como na
Apostila IV, figura 2 — este script não conhece banco, ORM nem regra de negócio.

Uso:
    python frontend/servir.py                    # http://127.0.0.1:8090 → API em 127.0.0.1:8000
    python frontend/servir.py --porta 8091 --api http://127.0.0.1:8001
"""

import argparse
import http.client
import json
import urllib.parse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PASTA_DO_PAINEL = Path(__file__).resolve().parent

# Cabeçalhos que não atravessam o repasse. X-Forwarded-For é tirado de propósito: o limite de
# tentativas de login (RNF12) não pode ser burlado com um endereço inventado pelo navegador.
_NAO_REPASSAR = {
    "connection",
    "keep-alive",
    "proxy-connection",
    "transfer-encoding",
    "te",
    "trailer",
    "upgrade",
    "host",
    "x-forwarded-for",
    "x-real-ip",
    "forwarded",
}

# Mesmo formato de erro da API (backend/comum/erros.py), para a tela mostrar sem tratamento à parte.
_API_FORA_DO_AR = {
    "erro": {
        "codigo": "sistema_fora_do_ar",
        "mensagem": "O sistema não está respondendo. Confira se ele está ligado e tente de novo.",
    }
}


class PainelHandler(SimpleHTTPRequestHandler):
    endereco_api: urllib.parse.SplitResult  # preenchido por criar_servidor()

    # ------------------------------------------------------------------ estático

    def do_GET(self):
        if self._e_da_api():
            return self._repassar()
        if urllib.parse.urlsplit(self.path).path == "/":
            self.send_response(302)
            self.send_header("Location", "/login.html")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None
        return super().do_GET()

    def do_HEAD(self):
        return self._repassar() if self._e_da_api() else super().do_HEAD()

    def end_headers(self):
        if not self._e_da_api():
            # Sem cache: a tela nova aparece logo depois de atualizar o código (desenvolvimento).
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    # ------------------------------------------------------------------ API

    def do_POST(self):
        return self._repassar() if self._e_da_api() else self.send_error(405)

    def do_PUT(self):
        return self._repassar() if self._e_da_api() else self.send_error(405)

    def do_PATCH(self):
        return self._repassar() if self._e_da_api() else self.send_error(405)

    def do_DELETE(self):
        return self._repassar() if self._e_da_api() else self.send_error(405)

    def do_OPTIONS(self):
        return self._repassar() if self._e_da_api() else self.send_error(405)

    def _e_da_api(self) -> bool:
        return self.path == "/api" or self.path.startswith("/api/")

    def _repassar(self):
        tamanho = int(self.headers.get("Content-Length") or 0)
        corpo = self.rfile.read(tamanho) if tamanho else None
        cabecalhos = {
            nome: valor for nome, valor in self.headers.items() if nome.lower() not in _NAO_REPASSAR
        }
        cabecalhos["Host"] = self.endereco_api.netloc

        conexao = http.client.HTTPConnection(
            self.endereco_api.hostname, self.endereco_api.port or 80, timeout=30
        )
        try:
            conexao.request(self.command, self.path, body=corpo, headers=cabecalhos)
            resposta = conexao.getresponse()
            dados = resposta.read()
        except OSError:
            return self._responder_json(502, _API_FORA_DO_AR)
        finally:
            conexao.close()

        self.send_response(resposta.status, resposta.reason)
        for nome, valor in resposta.getheaders():
            if nome.lower() not in _NAO_REPASSAR and nome.lower() not in {"content-length", "server", "date"}:
                self.send_header(nome, valor)
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(dados)
        return None

    def _responder_json(self, codigo: int, corpo: dict):
        dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)


class ServidorDoPainel(ThreadingHTTPServer):
    # O padrão do Python aceita só 5 conexões na fila. Uma tela pede uns dez módulos JS de uma vez;
    # com a máquina ocupada a fila estoura, um módulo volta "conexão recusada" e o navegador não roda
    # nenhum — a tela abre sem menu (achado na J1, a falha intermitente dos testes de tela).
    request_queue_size = 128


def criar_servidor(porta: int = 8090, endereco_api: str = "http://127.0.0.1:8000") -> ThreadingHTTPServer:
    """Monta o servidor (sem iniciar). Só aceita conexão da própria máquina (RNF12)."""
    # Uma classe por servidor, para cada um guardar o seu endereço de API.
    classe = type("PainelHandler", (PainelHandler,), {"endereco_api": urllib.parse.urlsplit(endereco_api)})
    handler = partial(classe, directory=str(PASTA_DO_PAINEL))
    return ServidorDoPainel(("127.0.0.1", porta), handler)


def main():
    argumentos = argparse.ArgumentParser(description="Serve o painel e repassa /api/ para o Django.")
    argumentos.add_argument("--porta", type=int, default=8090)
    argumentos.add_argument("--api", default="http://127.0.0.1:8000", help="endereço da API (Django)")
    opcoes = argumentos.parse_args()

    servidor = criar_servidor(opcoes.porta, opcoes.api)
    print(f"Painel em http://127.0.0.1:{opcoes.porta}/  ·  API repassada para {opcoes.api}")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()

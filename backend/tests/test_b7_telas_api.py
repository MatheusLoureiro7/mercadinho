"""
Tarefa B7 — ligar as telas à API e tratar os erros na tela.

- Mensagens: o que a API devolve aparece direto na tela, então tem de estar no vocabulário da loja
  (RNF10). A tradução padrão do DRF ("Este campo pode não estar em branco.") não serve.
- Mesma origem (decisão L25): o painel chama sempre "/api/..." no mesmo endereço em que é servido.
  Em desenvolvimento, `frontend/servir.py` entrega os arquivos estáticos e repassa /api/ para o
  Django — só biblioteca padrão do Python, sem CORS e sem dependência nova.
- Telas: o painel não acessa o banco e não usa mais dados de exemplo; todo acesso passa por
  `js/api.js`, e o menu de cada perfil vem da tabela da RN14 (`ACESSO_POR_TELA`).
"""

import importlib.util
import json
import re
import threading
import urllib.error
import urllib.request
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from wsgiref.simple_server import WSGIRequestHandler, make_server

import pytest
from django.core.handlers.wsgi import WSGIHandler

from cadastro.models import Categoria, Produto, Usuario
from comum.autenticacao import gerar_token
from comum.permissoes import ACESSO_POR_TELA
from estoque.models import Lote

RAIZ = Path(__file__).resolve().parents[2]
FRONTEND = RAIZ / "frontend"
SENHA = "Mercado#2026"


# ------------------------------------------------------------------------------------------------
# 1. Mensagens da API no vocabulário da loja (anotado na B6)
# ------------------------------------------------------------------------------------------------


@pytest.fixture
def operacao_cabecalho(db):
    usuario = Usuario.objects.create_user(login="sobrinho", senha=SENHA, nome="Sobrinho", papel="OPERACAO")
    return {"HTTP_AUTHORIZATION": f"Bearer {gerar_token(usuario)}"}


@pytest.fixture
def operacao(client, operacao_cabecalho):
    def post(url, dados):
        return client.post(url, dados, content_type="application/json", **operacao_cabecalho)

    return post


@pytest.mark.parametrize(
    ("url", "esperada"),
    [
        ("/api/fornecedores/", "Preencha o nome do fornecedor."),
        ("/api/produtos/", "Preencha o nome do produto."),
        ("/api/categorias/", "Preencha o nome da categoria."),
    ],
)
def test_b7_nome_em_branco_tem_mensagem_da_loja(operacao, url, esperada):
    resposta = operacao(url, {"nome": "", "prazo_entrega_dias": 1})

    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"]["nome"] == [esperada]


def test_b7_produto_sem_unidade_escolhida_tem_mensagem_da_loja(operacao):
    # A tela manda "" quando a pessoa não escolhe nada na lista de unidades.
    categoria = Categoria.objects.create(nome="Secos e molhados")

    dados = {"nome": "Arroz 5 kg", "categoria": categoria.pk, "unidade_medida": ""}

    resposta = operacao("/api/produtos/", dados)

    assert resposta.json()["erro"]["campos"]["unidade_medida"] == ["Escolha a unidade: KG, UN, L ou PCT."]


def test_b7_pedido_minimo_invalido_tem_mensagem_da_loja(operacao):
    dados = {"nome": "Atacadão", "prazo_entrega_dias": 2, "pedido_minimo": "abc"}

    resposta = operacao("/api/fornecedores/", dados)

    assert resposta.json()["erro"]["campos"]["pedido_minimo"] == [
        "Informe o pedido mínimo só com números, por exemplo 500.00."
    ]


# Busca por nome sem diferença de acento: a tela de Produtos (B5) promete achar "Feijão" digitando
# "feijao" — e quem digita no computador da loja nem sempre acerta o acento.


@pytest.fixture
def produtos_com_acento(db):
    secos = Categoria.objects.create(nome="Secos e molhados")
    for nome in ("Feijão carioca 1 kg", "Açúcar refinado 1 kg", "Arroz 5 kg"):
        Produto.objects.create(nome=nome, categoria=secos, unidade_medida="PCT")


def _nomes(resposta, chave="nome"):
    return [item[chave] for item in resposta.json()]


@pytest.mark.parametrize("digitado", ["feijao", "FEIJÃO", "Feijão", "eijao car"])
def test_b7_busca_de_produto_nao_diferencia_acento(client, operacao_cabecalho, produtos_com_acento, digitado):
    resposta = client.get("/api/produtos/", {"busca": digitado}, **operacao_cabecalho)

    assert _nomes(resposta) == ["Feijão carioca 1 kg"]


def test_b7_busca_sem_acento_acha_cedilha(client, operacao_cabecalho, produtos_com_acento):
    resposta = client.get("/api/produtos/", {"busca": "acucar"}, **operacao_cabecalho)

    assert _nomes(resposta) == ["Açúcar refinado 1 kg"]


def test_b7_busca_na_consulta_de_estoque_nao_diferencia_acento(
    client, operacao_cabecalho, produtos_com_acento
):
    resposta = client.get("/api/estoque/", {"busca": "feijao"}, **operacao_cabecalho)

    assert _nomes(resposta) == ["Feijão carioca 1 kg"]


def test_b7_busca_de_lote_nao_diferencia_acento(client, operacao_cabecalho, produtos_com_acento):
    feijao = Produto.objects.get(nome__startswith="Feij")
    Lote.objects.create(
        produto=feijao, quantidade_inicial=10, quantidade_atual=10, data_entrada=date(2026, 10, 1)
    )

    resposta = client.get("/api/estoque/lotes/", {"busca": "feijao"}, **operacao_cabecalho)

    assert _nomes(resposta, "produto_id") == [feijao.pk]


# ------------------------------------------------------------------------------------------------
# 2. frontend/servir.py — painel e API na mesma origem (L25)
# ------------------------------------------------------------------------------------------------


def _carregar_servir():
    especificacao = importlib.util.spec_from_file_location("servir", FRONTEND / "servir.py")
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def _em_segundo_plano(servidor):
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{servidor.server_address[1]}"


class _ApiDeMentira(BaseHTTPRequestHandler):
    """Faz o papel do Django: registra o que chegou e responde o que o teste mandar."""

    recebidas: list = []
    resposta = (200, {"ok": True})

    def _responder(self):
        tamanho = int(self.headers.get("Content-Length") or 0)
        self.recebidas.append(
            {
                "metodo": self.command,
                "caminho": self.path,
                "cabecalhos": dict(self.headers),
                "corpo": self.rfile.read(tamanho).decode() if tamanho else "",
            }
        )
        codigo, corpo = self.resposta
        dados = json.dumps(corpo).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    do_GET = do_POST = do_PATCH = _responder

    def log_message(self, *args):  # silêncio nos testes
        pass


@pytest.fixture
def api_de_mentira():
    _ApiDeMentira.recebidas = []
    _ApiDeMentira.resposta = (200, {"ok": True})
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), _ApiDeMentira)
    endereco = _em_segundo_plano(servidor)
    yield endereco, _ApiDeMentira
    servidor.shutdown()
    servidor.server_close()


@pytest.fixture
def painel(api_de_mentira):
    """O servir.py ligado na API de mentira. Devolve o endereço do painel."""
    endereco_api, _ = api_de_mentira
    servidor = _carregar_servir().criar_servidor(porta=0, endereco_api=endereco_api)
    endereco = _em_segundo_plano(servidor)
    yield endereco
    servidor.shutdown()
    servidor.server_close()


def _pedir(url, metodo="GET", corpo=None, cabecalhos=None):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    pedido = urllib.request.Request(url, data=dados, method=metodo, headers=cabecalhos or {})  # noqa: S310
    if dados is not None:
        pedido.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(pedido, timeout=5) as resposta:  # noqa: S310 — localhost do teste
            # Os cabeçalhos ficam no objeto do urllib: nome sem diferença de maiúscula e minúscula.
            return resposta.status, resposta.headers, resposta.read()
    except urllib.error.HTTPError as erro:
        return erro.code, erro.headers, erro.read()


class _SemSeguirRedirecionamento(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def test_b7_servir_repassa_a_api_com_o_token_e_os_filtros(painel, api_de_mentira):
    _, api = api_de_mentira

    codigo, cabecalhos, corpo = _pedir(
        painel + "/api/produtos/?busca=feijao", cabecalhos={"Authorization": "Bearer abc"}
    )

    assert codigo == 200
    assert json.loads(corpo) == {"ok": True}
    assert cabecalhos["Content-Type"] == "application/json"
    assert api.recebidas[0]["caminho"] == "/api/produtos/?busca=feijao"
    assert api.recebidas[0]["cabecalhos"]["Authorization"] == "Bearer abc"


def test_b7_servir_repassa_o_corpo_e_devolve_a_recusa_como_veio(painel, api_de_mentira):
    _, api = api_de_mentira
    recusa = {"erro": {"codigo": "validacao", "mensagem": "Confira os campos destacados.", "campos": {}}}
    api.resposta = (400, recusa)

    codigo, _, corpo = _pedir(painel + "/api/fornecedores/7/", metodo="PATCH", corpo={"nome": ""})

    assert codigo == 400
    assert json.loads(corpo) == recusa
    assert api.recebidas[0]["metodo"] == "PATCH"
    assert json.loads(api.recebidas[0]["corpo"]) == {"nome": ""}


def test_b7_servir_nao_repassa_endereco_inventado_pelo_navegador(painel, api_de_mentira):
    # RNF12: o limite de tentativas de login não pode ser burlado fingindo outro endereço.
    _, api = api_de_mentira

    _pedir(painel + "/api/sessoes/", metodo="POST", corpo={}, cabecalhos={"X-Forwarded-For": "10.9.9.9"})

    assert "X-Forwarded-For" not in api.recebidas[0]["cabecalhos"]


def test_b7_servir_com_a_api_desligada_responde_no_formato_de_erro_da_api():
    servidor = _carregar_servir().criar_servidor(porta=0, endereco_api="http://127.0.0.1:9")  # nada ouvindo
    endereco = _em_segundo_plano(servidor)
    try:
        codigo, _, corpo = _pedir(endereco + "/api/produtos/")
    finally:
        servidor.shutdown()
        servidor.server_close()

    assert codigo == 502
    erro = json.loads(corpo)["erro"]
    assert erro["codigo"] == "sistema_fora_do_ar"
    assert "não está respondendo" in erro["mensagem"]


def test_b7_servir_entrega_as_telas(painel):
    codigo, cabecalhos, corpo = _pedir(painel + "/login.html")

    assert codigo == 200
    assert cabecalhos["Content-Type"].startswith("text/html")
    assert b"<form" in corpo


def test_b7_servir_endereco_raiz_leva_ao_login(painel):
    abridor = urllib.request.build_opener(_SemSeguirRedirecionamento)
    with pytest.raises(urllib.error.HTTPError) as redirecionamento:
        abridor.open(painel + "/", timeout=5)

    assert redirecionamento.value.code == 302
    assert redirecionamento.value.headers["Location"] == "/login.html"


def test_b7_servir_nao_entrega_arquivo_fora_da_pasta_do_painel(painel):
    codigo, _, corpo = _pedir(painel + "/../pyproject.toml")
    codigo_codificado, _, corpo_codificado = _pedir(painel + "/%2e%2e/pyproject.toml")

    assert codigo == 404 and b"ruff" not in corpo
    assert codigo_codificado == 404 and b"ruff" not in corpo_codificado


def test_b7_servir_so_aceita_conexao_da_propria_maquina():
    # RNF12: o servidor de desenvolvimento não fica exposto na rede da loja.
    servidor = _carregar_servir().criar_servidor(porta=0, endereco_api="http://127.0.0.1:8000")
    try:
        assert servidor.server_address[0] == "127.0.0.1"
    finally:
        servidor.server_close()


class _SemRegistro(WSGIRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture
def api_django(transactional_db):
    """A API de verdade (a aplicação WSGI do Django) num servidor de teste, ouvindo em 127.0.0.1."""
    servidor = make_server("127.0.0.1", 0, WSGIHandler(), handler_class=_SemRegistro)
    endereco = _em_segundo_plano(servidor)
    yield endereco
    servidor.shutdown()
    servidor.server_close()


def test_b7_login_pelo_painel_chega_na_api_de_verdade(api_django):
    # Ponta a ponta: painel (servir.py) → API (Django) → banco. Mesma origem, sem CORS.
    Usuario.objects.create_user(login="esposa", senha=SENHA, nome="Esposa", papel="GESTAO")
    servidor = _carregar_servir().criar_servidor(porta=0, endereco_api=api_django)
    endereco = _em_segundo_plano(servidor)
    try:
        codigo, _, corpo = _pedir(endereco + "/api/sessoes/", "POST", {"login": "esposa", "senha": SENHA})
        token = json.loads(corpo)["token"]
        codigo_atual, _, corpo_atual = _pedir(
            endereco + "/api/sessoes/atual/", cabecalhos={"Authorization": f"Bearer {token}"}
        )
    finally:
        servidor.shutdown()
        servidor.server_close()

    assert codigo == 201
    assert codigo_atual == 200
    assert json.loads(corpo_atual)["telas"] == ["consulta_estoque", "fechamento_caixa", "balanco_semana"]


# ------------------------------------------------------------------------------------------------
# 3. As telas falam com a API — e só com a API
# ------------------------------------------------------------------------------------------------

TELAS_PRONTAS = ["produtos.html", "fornecedores.html"]


def _js(nome):
    return (FRONTEND / "js" / nome).read_text(encoding="utf-8")


def test_b7_dados_de_exemplo_sairam_do_painel():
    assert not (FRONTEND / "js" / "dados-de-exemplo.js").exists()
    for arquivo in FRONTEND.rglob("*.js"):
        assert "dados-de-exemplo" not in arquivo.read_text(encoding="utf-8"), arquivo.name


def test_b7_so_o_api_js_chama_fetch():
    # Uma porta só para a API: token, sessão vencida e "sem conexão" tratados num lugar.
    quem_chama = [a.name for a in (FRONTEND / "js").glob("*.js") if "fetch(" in a.read_text(encoding="utf-8")]

    assert quem_chama == ["api.js"]


def test_b7_api_js_usa_caminho_relativo_da_mesma_origem():
    codigo = _js("api.js")

    assert '"/api/' in codigo
    assert not re.search(r"https?://", codigo), "endereço fixo da API quebra a mesma origem (L25)"


def test_b7_token_fica_so_enquanto_a_aba_estiver_aberta():
    # Computador da loja é compartilhado: fechou o navegador, saiu do sistema.
    codigo = _js("sessao.js")

    assert "sessionStorage" in codigo
    assert "localStorage" not in codigo


def test_b7_menu_do_painel_tem_todas_as_telas_da_rn14():
    # O menu vem de /api/sessoes/atual/ (lista de chaves); o painel só precisa do nome e do endereço.
    codigo = _js("sessao.js")
    chaves_no_painel = set(re.findall(r"^\s{2}(\w+): \{ nome:", codigo, flags=re.MULTILINE))

    assert chaves_no_painel == set(ACESSO_POR_TELA)


@pytest.mark.parametrize("tela", TELAS_PRONTAS)
def test_b7_tela_pronta_exige_login(tela):
    script = re.search(r'<script type="module" src="js/(\w+)\.js">', (FRONTEND / tela).read_text("utf-8"))

    assert script, f"{tela} sem script de módulo"
    assert 'from "./sessao.js"' in _js(script.group(1) + ".js")


@pytest.mark.parametrize("tela", TELAS_PRONTAS)
def test_b7_menu_da_tela_nao_e_mais_fixo_no_html(tela):
    html = (FRONTEND / tela).read_text(encoding="utf-8")

    assert 'href="#"' not in html, "item de menu sem tela; o menu vem do perfil (RN14)"


def test_b7_tela_de_login_tem_os_campos_da_api():
    html = (FRONTEND / "login.html").read_text(encoding="utf-8")

    assert re.search(r'<input[^>]+name="login"[^>]+autocomplete="username"', html)
    assert re.search(r'<input[^>]+name="senha"[^>]+type="password"|type="password"[^>]+name="senha"', html)
    assert 'autocomplete="current-password"' in html  # WCAG 2.2: gerenciador de senha e colar

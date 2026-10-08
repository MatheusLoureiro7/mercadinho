"""
Tarefa C5 — tela de Entrada de mercadoria (RF03, operação 02, fluxograma 02).

A tela envia o lote para POST /api/lotes/ (C2) e mostra o que a API responde; a validade calculada
e a recusa de validade vencida são da API (RN04, C3), nunca da tela. Aqui se testa:

- as mensagens que a tela mostra direto, no vocabulário da loja (RNF10);
- o contrato entre a tela e a API: os campos que a tela envia são os que a API recebe;
- a tela no menu do perfil e protegida pelo login (RN14).

O comportamento na tela (digitar, salvar, recusar) é conferido no navegador, contra a API real.
"""

import re
from pathlib import Path

import pytest

from cadastro.models import Categoria, Produto, Usuario
from comum.autenticacao import gerar_token
from estoque.serializers import EntradaDeLoteSerializer

RAIZ = Path(__file__).resolve().parents[2]
FRONTEND = RAIZ / "frontend"
TELA = FRONTEND / "entrada-mercadoria.html"
SCRIPT = FRONTEND / "js" / "entrada-mercadoria.js"


@pytest.fixture
def post(client, db):
    usuario = Usuario.objects.create_user(
        login="sobrinho", senha="Mercado#2026", nome="Sobrinho", papel="OPERACAO"
    )
    cabecalho = {"HTTP_AUTHORIZATION": f"Bearer {gerar_token(usuario)}"}
    return lambda dados: client.post("/api/lotes/", dados, content_type="application/json", **cabecalho)


@pytest.fixture
def arroz(db):
    secos = Categoria.objects.create(nome="Secos e molhados")
    return Produto.objects.create(nome="Arroz 5 kg", categoria=secos, unidade_medida="PCT")


# ------------------------------------------------------------------------------------------------
# Mensagens que a tela mostra direto
# ------------------------------------------------------------------------------------------------


def test_c5_custo_digitado_errado_tem_mensagem_da_loja(post, arroz):
    resposta = post({"produto": arroz.pk, "quantidade": "10", "custo_unitario": "dez reais"})

    assert resposta.json()["erro"]["campos"]["custo_unitario"] == [
        "Informe o custo só com números, por exemplo 12.90."
    ]


def test_c5_validade_incompleta_tem_mensagem_da_loja(post, arroz):
    # Navegador antigo sem calendário: a pessoa digita a data à mão.
    resposta = post({"produto": arroz.pk, "quantidade": "10", "data_validade": "25/10"})

    assert resposta.json()["erro"]["campos"]["data_validade"] == [
        "Informe a validade completa: dia, mês e ano."
    ]


# ------------------------------------------------------------------------------------------------
# Contrato tela × API
# ------------------------------------------------------------------------------------------------


def _campos_da_tela() -> set[str]:
    bloco = re.search(r"const CAMPOS = \{(.*?)\n\};", SCRIPT.read_text(encoding="utf-8"), flags=re.S)
    assert bloco, "entrada-mercadoria.js sem o mapa CAMPOS"
    return set(re.findall(r"^\s{2}(\w+): \{", bloco.group(1), flags=re.MULTILINE))


def test_c5_tela_envia_exatamente_os_campos_da_api():
    # RF03: produto, quantidade, custo, fornecedor e validade. Nem um a mais (a data de entrada é
    # sempre o dia da loja, decidido pela API), nem um a menos.
    assert _campos_da_tela() == set(EntradaDeLoteSerializer().fields)


def test_c5_tela_tem_um_campo_para_cada_dado_do_lote():
    html = TELA.read_text(encoding="utf-8")
    for campo in _campos_da_tela():
        assert f'id="erro-{campo}"' in html, f"campo {campo} sem lugar para o erro embaixo dele"


def test_c5_tela_nao_tem_data_de_entrada():
    # C2: a data de entrada não pode ser escolhida — é sempre hoje, no horário da loja.
    assert "data_entrada" not in TELA.read_text(encoding="utf-8")


def test_c5_lista_do_dia_usa_o_dia_da_loja():
    # "Hoje" é o de São Paulo, não o do relógio em UTC (CLAUDE.md), também na tela.
    assert "America/Sao_Paulo" in SCRIPT.read_text(encoding="utf-8")


# ------------------------------------------------------------------------------------------------
# Menu e acesso (RN14)
# ------------------------------------------------------------------------------------------------


def test_c5_tela_entra_no_menu_do_sobrinho():
    sessao = (FRONTEND / "js" / "sessao.js").read_text(encoding="utf-8")

    esperado = (
        r'entrada_mercadoria: \{ nome: "Entrada de mercadoria", endereco: "entrada-mercadoria\.html" \}'
    )

    assert re.search(esperado, sessao)


def test_c5_tela_exige_login_e_o_perfil_da_entrada():
    assert 'src="js/entrada-mercadoria.js"' in TELA.read_text(encoding="utf-8")
    assert 'entrarNaTela("entrada_mercadoria")' in SCRIPT.read_text(encoding="utf-8")


def test_c5_todo_endereco_do_menu_existe():
    sessao = (FRONTEND / "js" / "sessao.js").read_text(encoding="utf-8")
    for endereco in re.findall(r'endereco: "([\w.-]+)"', sessao):
        assert (FRONTEND / endereco).exists(), endereco

"""
Tarefa C6 — integração e teste do fluxo completo da entrada de mercadoria.

De ponta a ponta, no navegador: a pessoa usa a tela (C5), a tela fala com a API (C2), a API aplica
as regras (RN04, C3; RN01, C4) e grava no banco. Cada teste confere o que aparece na tela E o que
ficou gravado — lote, movimentação e saldo.

As seis situações do fluxograma 02 (Apostila II) — cada losango pelo "sim" e pelo "não":

    perecível?                sim → test_c6_rn04_perecivel_*        não → test_c6_rn04_nao_perecivel_*
    validade informada?       sim → *_com_validade_*                não → *_sem_validade_*
    validade antes de hoje?   sim → *_vencida_e_recusada_*          não → *_de_hoje_e_aceita

Pular estes testes (mais lentos, abrem navegador): pytest -m "not tela"
"""

import re
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from django.utils import timezone
from playwright.sync_api import expect

from cadastro.models import Categoria, Fornecedor, Produto, Usuario
from estoque.models import Lote, Movimentacao
from estoque.regras import MENSAGEM_RN04
from estoque.saldo import saldo_do_produto
from tests.conftest import abrir_tela, entrar_pelo_login

pytestmark = pytest.mark.tela

SENHA = "Mercado#2026"
TELA = "entrada-mercadoria.html"
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


def _usuario(login, nome, papel):
    return Usuario.objects.create_user(login=login, senha=SENHA, nome=nome, papel=papel)


@pytest.fixture
def loja(painel):
    """O cadastro mínimo da loja, criado depois que a API subiu (banco com transação de verdade)."""
    acougue = Categoria.objects.create(nome="Açougue", perecivel_padrao=True)
    secos = Categoria.objects.create(nome="Secos e molhados")
    boi_bom = Fornecedor.objects.create(nome="Frigorífico Boi Bom", prazo_entrega_dias=3)
    atacadao = Fornecedor.objects.create(nome="Atacadão Central", prazo_entrega_dias=2)
    return {
        "sobrinho": _usuario("sobrinho", "Sobrinho", "OPERACAO"),
        "esposa": _usuario("esposa", "Esposa", "GESTAO"),
        "frango": Produto.objects.create(
            nome="Frango resfriado 1 kg",
            categoria=acougue,
            unidade_medida="KG",
            perecivel=True,
            durabilidade_dias=4,
            fornecedor_padrao=boi_bom,
        ),
        "alcatra": Produto.objects.create(
            nome="Alcatra", categoria=acougue, unidade_medida="KG", perecivel=True, durabilidade_dias=3
        ),
        "arroz": Produto.objects.create(
            nome="Arroz 5 kg", categoria=secos, unidade_medida="PCT", fornecedor_padrao=atacadao
        ),
        "boi_bom": boi_bom,
        "atacadao": atacadao,
    }


@pytest.fixture
def tela(page, painel, loja):
    """A tela de Entrada aberta pelo sobrinho, pronta para registrar."""
    abrir_tela(page, painel, loja["sobrinho"], TELA)
    page.wait_for_selector("#corpo-tabela tr")
    return page


def _registrar(page, *, procurar, quantidade, validade=None, custo=None):
    page.fill("#campo-procurar", procurar)
    page.fill("#campo-quantidade", quantidade)
    if custo is not None:
        page.fill("#campo-custo", custo)
    if validade is not None:
        page.fill("#campo-validade", validade.isoformat())
    page.click("#botao-salvar")


def _confirmado(page):
    expect(page.locator("#sucesso")).to_be_visible()


def _recusado(page):
    expect(page.locator("#resumo-de-erros")).to_be_visible()


def _br(data):
    return data.strftime("%d/%m/%Y")


def _hoje():
    return timezone.localdate()  # o dia da loja, como a API (CLAUDE.md)


# ------------------------------------------------------------------------------------------------
# As seis situações do fluxograma 02
# ------------------------------------------------------------------------------------------------


def test_c6_rn04_perecivel_sem_validade_grava_a_calculada(tela, loja):
    _registrar(tela, procurar="frango", quantidade="12,5")

    _confirmado(tela)
    validade = _hoje() + timedelta(days=4)  # entrada + durabilidade
    expect(tela.locator("#sucesso-texto")).to_contain_text(f"Validade calculada: {_br(validade)}.")
    lote = Lote.objects.get(produto=loja["frango"])
    assert lote.data_validade == validade
    assert lote.quantidade_inicial == Decimal("12.500")


def test_c6_rn04_perecivel_com_validade_grava_a_informada(tela, loja):
    validade = _hoje() + timedelta(days=2)

    _registrar(tela, procurar="frango", quantidade="5", validade=validade)

    _confirmado(tela)
    expect(tela.locator("#sucesso-texto")).not_to_contain_text("calculada")
    assert Lote.objects.get(produto=loja["frango"]).data_validade == validade


def test_c6_rn04_nao_perecivel_sem_validade_grava_sem_validade(tela, loja):
    _registrar(tela, procurar="arroz", quantidade="20")

    _confirmado(tela)
    assert Lote.objects.get(produto=loja["arroz"]).data_validade is None
    expect(tela.locator("#corpo-tabela tr").first).to_contain_text("Sem validade")


def test_c6_rn04_nao_perecivel_com_validade_grava_a_informada(tela, loja):
    validade = _hoje() + timedelta(days=180)

    _registrar(tela, procurar="arroz", quantidade="20", validade=validade)

    _confirmado(tela)
    assert Lote.objects.get(produto=loja["arroz"]).data_validade == validade


def test_c6_rn04_validade_vencida_e_recusada_e_nada_e_gravado(tela, loja):
    _registrar(tela, procurar="frango", quantidade="12,5", validade=_hoje() - timedelta(days=1))

    _recusado(tela)
    expect(tela.locator("#erro-data_validade")).to_have_text(MENSAGEM_RN04)
    expect(tela.locator("#campo-quantidade")).to_have_value("12,5")  # o digitado fica (fluxograma 02)
    assert not Lote.objects.exists()
    assert not Movimentacao.objects.exists()


def test_c6_rn04_validade_de_hoje_e_aceita(tela, loja):
    _registrar(tela, procurar="frango", quantidade="1", validade=_hoje())

    _confirmado(tela)
    assert Lote.objects.get(produto=loja["frango"]).data_validade == _hoje()


# ------------------------------------------------------------------------------------------------
# O que a entrada grava (RN01) e o que a tela mostra depois
# ------------------------------------------------------------------------------------------------


def test_c6_rn01_entrada_pela_tela_grava_lote_e_movimentacao_juntos(tela, loja):
    _registrar(tela, procurar="frango", quantidade="12,5", custo="9,80")

    _confirmado(tela)
    lote = Lote.objects.get()
    movimentacao = Movimentacao.objects.get()
    assert movimentacao.lote == lote
    assert movimentacao.tipo == Movimentacao.Tipo.ENTRADA
    assert movimentacao.quantidade == lote.quantidade_inicial == lote.quantidade_atual == Decimal("12.500")
    assert movimentacao.preco_unitario == lote.custo_unitario == Decimal("9.80")
    assert movimentacao.usuario == loja["sobrinho"]  # quem registrou, pelo login da tela
    assert movimentacao.origem == "TELA"
    assert lote.fornecedor == loja["boi_bom"]  # o fornecedor de costume veio com o produto
    assert lote.data_entrada == _hoje()


def test_c6_rn01_saldo_mostrado_e_o_derivado_das_movimentacoes(tela, loja):
    _registrar(tela, procurar="frango", quantidade="12,5")
    _confirmado(tela)
    _registrar(tela, procurar="frango", quantidade="10")
    _confirmado(tela)

    assert saldo_do_produto(loja["frango"]) == Decimal("22.5")
    expect(tela.locator("#sucesso-texto")).to_contain_text("Agora tem 22,5 KG em estoque.")


def test_c6_lista_do_dia_mostra_o_que_foi_registrado(tela, loja):
    _registrar(tela, procurar="frango", quantidade="12,5", custo="9,80")
    _confirmado(tela)

    primeira = tela.locator("#corpo-tabela tr").first
    expect(primeira).to_contain_text("Frango resfriado 1 kg")
    expect(primeira).to_contain_text("12,5 KG")
    expect(primeira).to_contain_text(_br(_hoje() + timedelta(days=4)))
    expect(primeira).to_contain_text("Frigorífico Boi Bom")
    expect(primeira).to_contain_text("R$ 9,80")
    expect(tela.locator("#titulo-lista")).to_have_text(f"Entradas de hoje · {_br(_hoje())}")


def test_c6_lista_do_dia_nao_mostra_entrada_de_ontem(page, painel, loja):
    ontem = _hoje() - timedelta(days=1)
    lote = Lote.objects.create(
        produto=loja["arroz"], quantidade_inicial=5, quantidade_atual=5, data_entrada=ontem
    )

    abrir_tela(page, painel, loja["sobrinho"], TELA)

    expect(page.locator("#corpo-tabela")).to_contain_text("Nenhuma entrada registrada hoje.")
    assert lote.pk  # existe, mas é de ontem


def test_c6_fornecedor_fica_para_o_proximo_produto_da_mesma_carga(tela, loja):
    tela.fill("#campo-procurar", "frango")
    tela.select_option("#campo-fornecedor", label="Atacadão Central")
    _registrar(tela, procurar="frango", quantidade="10")
    _confirmado(tela)
    _registrar(tela, procurar="alcatra", quantidade="3")  # alcatra não tem fornecedor de costume
    _confirmado(tela)

    fornecedores = set(Lote.objects.values_list("fornecedor__nome", flat=True))
    assert fornecedores == {"Atacadão Central"}


def test_c6_recusa_da_api_nao_grava_e_mantem_o_digitado(tela, loja):
    _registrar(tela, procurar="arroz", quantidade="0", custo="21,00")

    _recusado(tela)
    mensagem = "A quantidade que chegou tem de ser maior que zero."
    expect(tela.locator("#erro-quantidade")).to_have_text(mensagem)
    expect(tela.locator("#campo-custo")).to_have_value("21,00")
    assert not Lote.objects.exists()


# X1, item 13 (decisão do grupo, 16/11/2026): "1.000" sem vírgula pode ser mil ou 1,000 — a tela
# recusa e pede para reescrever, em vez de gravar 1 lata no lugar de mil.

AMBIGUO = "Não dá para saber se é mil ou um: escreva 1000 para mil, ou 1,5 para um e meio."


def test_x1_quantidade_1_000_sem_virgula_e_recusada_e_nada_e_gravado(tela, loja):
    _registrar(tela, procurar="arroz", quantidade="1.000")

    _recusado(tela)
    expect(tela.locator("#erro-quantidade")).to_have_text(AMBIGUO)
    expect(tela.locator("#campo-quantidade")).to_have_value("1.000")
    assert not Lote.objects.exists()


def test_x1_quantidade_reescrita_sem_ponto_e_aceita(tela, loja):
    _registrar(tela, procurar="arroz", quantidade="1000")

    _confirmado(tela)
    assert Lote.objects.get(produto=loja["arroz"]).quantidade_inicial == 1000


@pytest.mark.parametrize(
    "digitado, para_api",
    [
        ("1.000", "AMBIGUO"),
        ("12.500", "AMBIGUO"),
        ("1.000.000", "AMBIGUO"),
        ("1.000,5", "1000.5"),  # com vírgula, o ponto é de milhar
        ("1,5", "1.5"),
        ("12.90", "12.90"),  # duas casas: só pode ser centavo
        ("2.5", "2.5"),
        ("1000", "1000"),
        ("", "VAZIO"),
    ],
)
def test_x1_regras_da_conversao_do_numero_digitado(tela, digitado, para_api):
    resultado = tela.evaluate(
        """async (digitado) => {
            const f = await import("./js/formatos.js");
            if (f.numerosAmbiguos({ campo: digitado })) return "AMBIGUO";
            const numero = f.numeroParaApi(digitado);
            return numero === null ? "VAZIO" : numero;
        }""",
        digitado,
    )
    assert resultado == para_api


def test_x1_toda_tela_que_converte_numero_confere_o_ambiguo():
    for script in sorted((FRONTEND / "js").glob("*.js")):
        texto = script.read_text(encoding="utf-8")
        if "numeroParaApi(" in texto and script.name != "formatos.js":
            assert "numerosAmbiguos(" in texto, script.name


# ------------------------------------------------------------------------------------------------
# Acesso (RN14) e o caminho completo desde o Login
# ------------------------------------------------------------------------------------------------


def test_c6_do_login_a_entrada_registrada(page, painel, loja):
    entrar_pelo_login(page, painel, "sobrinho", SENHA)
    page.click('#menu a[href="entrada-mercadoria.html"]')
    expect(page.locator('#menu a[aria-current="page"]')).to_have_text("Entrada de mercadoria")

    _registrar(page, procurar="arroz", quantidade="20")

    _confirmado(page)
    assert Movimentacao.objects.get().usuario == loja["sobrinho"]


def test_c6_rn14_outro_perfil_nao_abre_a_entrada(page, painel, loja):
    entrar_pelo_login(page, painel, "esposa", SENHA)
    page.wait_for_url(re.compile(r"consulta-estoque\.html$"))  # a tela do perfil dela (F3)

    page.goto(f"{painel}/{TELA}")

    # Levada de volta à tela do perfil, com o recado — sem ver nada da Entrada.
    page.wait_for_url(re.compile(r"consulta-estoque\.html$"))
    recado = "O seu perfil não tem acesso à tela de Entrada de mercadoria."
    expect(page.locator("#recado")).to_have_text(recado)

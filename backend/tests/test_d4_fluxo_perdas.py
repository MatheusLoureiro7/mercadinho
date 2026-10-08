"""
Tarefa D4 — integração e teste do fluxo de perdas.

De ponta a ponta, no navegador: o sobrinho usa a tela de Avarias e quebras (D3), a tela fala com a
API (D1), a API aplica as regras e grava. Cada teste confere a tela E o que ficou gravado — a
movimentação PERDA, o lote, o saldo e o consumo.

Os losangos do fluxograma 03 (Apostila II), cada um pelo "sim" e pelo "não" (Apostila IV):

    tem motivo? (RF04)               sim → test_d4_rf04_com_motivo_*       não → test_d4_rf04_sem_motivo_*
    escolheu o lote? (L20)           sim → test_d4_l20_lote_escolhido_*    não → test_d4_rn02_sem_lote_*
    a quantidade cabe?               sim → (os de cima)                    não → test_d4_*_maior_que_*
    o lote está vencido? (RN16)      sim → test_d4_rn16_vencido_*          não → test_d4_rn16_lote_bom_*

E o que a perda NÃO pode fazer: virar consumo (RN11) nem escrever saldo (RN01).

Pular estes testes (abrem navegador): pytest -m "not tela"
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from playwright.sync_api import expect

from cadastro.models import Categoria, Produto, Usuario
from estoque.entrada import registrar_entrada
from estoque.models import Lote, Movimentacao
from estoque.saldo import saldo_do_produto
from estoque.serializers import MENSAGEM_SEM_MOTIVO
from previsao.consumo import vendido_no_periodo
from tests.conftest import abrir_tela, entrar_pelo_login, guardar_sessao

pytestmark = pytest.mark.tela

SENHA = "Mercado#2026"
TELA = "avarias.html"


def _hoje():
    return timezone.localdate()  # o dia da loja, como a API (CLAUDE.md)


@pytest.fixture
def loja(painel):
    """
    Iogurte com três lotes, como na Apostila I: um vencido ontem (3 UN), um que vence em 2 dias
    (6 UN) e um bom (10 UN). Frango com 40 kg, para o exemplo da RN11.
    """
    frios = Categoria.objects.create(nome="Frios", perecivel_padrao=True)
    acougue = Categoria.objects.create(nome="Açougue", perecivel_padrao=True)
    sobrinho = Usuario.objects.create_user(login="sobrinho", senha=SENHA, nome="Sobrinho", papel="OPERACAO")
    iogurte = Produto.objects.create(
        nome="Iogurte natural", categoria=frios, unidade_medida="UN", perecivel=True, durabilidade_dias=15
    )
    frango = Produto.objects.create(
        nome="Frango resfriado 1 kg",
        categoria=acougue,
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=4,
    )
    hoje = _hoje()
    bom = registrar_entrada(produto=iogurte, quantidade=Decimal("10"), usuario=sobrinho)
    vencido = registrar_entrada(
        produto=iogurte, quantidade=Decimal("3"), usuario=sobrinho, data_validade=hoje
    )
    Lote.objects.filter(pk=vencido.pk).update(data_validade=hoje - timedelta(days=1))  # venceu ontem
    vencendo = registrar_entrada(
        produto=iogurte, quantidade=Decimal("6"), usuario=sobrinho, data_validade=hoje + timedelta(days=2)
    )
    registrar_entrada(produto=frango, quantidade=Decimal("40"), usuario=sobrinho)
    return {
        "sobrinho": sobrinho,
        "iogurte": iogurte,
        "frango": frango,
        "bom": bom,
        "vencido": vencido,
        "vencendo": vencendo,
    }


@pytest.fixture
def tela(page, painel, loja):
    abrir_tela(page, painel, loja["sobrinho"], TELA)
    page.wait_for_selector("#corpo-tabela tr")
    return page


def _registrar(page, *, procurar, quantidade, motivo, lote=None):
    page.fill("#campo-procurar", procurar)
    expect(page.locator("#lista-de-lotes input[value='']")).to_be_attached()  # os lotes chegaram
    if lote is not None:
        page.check(f"#lista-de-lotes input[value='{lote.pk}']")
    page.fill("#campo-quantidade", quantidade)
    page.fill("#campo-motivo", motivo)
    page.click("#botao-salvar")


def _confirmado(page):
    expect(page.locator("#sucesso")).to_be_visible()


def _recusado(page):
    expect(page.locator("#resumo-de-erros")).to_be_visible()


def _perdas():
    return Movimentacao.objects.filter(tipo=Movimentacao.Tipo.PERDA)


def _atual(lote):
    lote.refresh_from_db()
    return lote.quantidade_atual


# ------------------------------------------------------------------------------------------------
# Tem motivo? (RF04)
# ------------------------------------------------------------------------------------------------


def test_d4_rf04_com_motivo_a_perda_baixa_o_saldo_e_fica_anotada(tela, loja):
    # Apostila I: 10 kg de frango "estragou no balcão" → o saldo cai 10 kg.
    _registrar(tela, procurar="frango", quantidade="10", motivo="Estragou no balcão")

    _confirmado(tela)
    assert saldo_do_produto(loja["frango"]) == Decimal("30")
    perda = _perdas().get()
    assert perda.motivo == "Estragou no balcão"
    assert perda.quantidade == Decimal("10")
    assert perda.usuario == loja["sobrinho"]  # quem registrou, pelo login da tela
    assert perda.origem == "TELA"
    expect(tela.locator("#sucesso-texto")).to_contain_text("Agora tem 30 KG em estoque.")


def test_d4_rf04_sem_motivo_e_recusada_e_nada_e_gravado(tela, loja):
    _registrar(tela, procurar="frango", quantidade="10", motivo="")

    _recusado(tela)
    expect(tela.locator("#erro-motivo")).to_have_text(MENSAGEM_SEM_MOTIVO)
    expect(tela.locator("#campo-quantidade")).to_have_value("10")  # o digitado fica
    assert not _perdas().exists()
    assert saldo_do_produto(loja["frango"]) == Decimal("40")


def test_d4_rf04_motivo_so_com_espacos_tambem_e_recusado(tela, loja):
    _registrar(tela, procurar="frango", quantidade="1", motivo="   ")

    expect(tela.locator("#erro-motivo")).to_have_text(MENSAGEM_SEM_MOTIVO)
    assert not _perdas().exists()


# ------------------------------------------------------------------------------------------------
# Escolheu o lote? (L20)
# ------------------------------------------------------------------------------------------------


def test_d4_l20_lote_escolhido_a_perda_sai_so_dele(tela, loja):
    _registrar(tela, procurar="iogurte", quantidade="2", motivo="Quebrou", lote=loja["bom"])

    _confirmado(tela)
    assert _atual(loja["bom"]) == Decimal("8")
    assert _atual(loja["vencido"]) == Decimal("3")  # nem o vencido, que sairia primeiro na ordem
    assert _atual(loja["vencendo"]) == Decimal("6")
    assert _perdas().get().lote_id == loja["bom"].pk


def test_d4_rn02_sem_lote_sai_pela_ordem_de_validade_vencido_primeiro(tela, loja):
    _registrar(tela, procurar="iogurte", quantidade="4", motivo="Estragou na geladeira")

    _confirmado(tela)
    expect(tela.locator("#sucesso-texto")).to_contain_text("Saiu de 2 lotes, pela ordem de validade.")
    assert _atual(loja["vencido"]) == Decimal("0")  # 3 do vencido (RN16: perda o alcança)...
    assert _atual(loja["vencendo"]) == Decimal("5")  # ...e 1 do que vence a seguir (RN02)
    assert _atual(loja["bom"]) == Decimal("10")
    # RN01: uma movimentação por lote afetado, cada uma explicando a sua parte do saldo
    por_lote = dict(_perdas().values_list("lote_id", "quantidade"))
    assert por_lote == {loja["vencido"].pk: Decimal("3"), loja["vencendo"].pk: Decimal("1")}


# ------------------------------------------------------------------------------------------------
# A quantidade cabe?
# ------------------------------------------------------------------------------------------------


def test_d4_perda_maior_que_o_lote_escolhido_e_recusada(tela, loja):
    _registrar(tela, procurar="iogurte", quantidade="5", motivo="Venceu", lote=loja["vencido"])

    _recusado(tela)
    expect(tela.locator("#erro-quantidade")).to_have_text("Esse lote só tem 3 UN.")
    assert not _perdas().exists()
    assert _atual(loja["vencido"]) == Decimal("3")


def test_d4_perda_maior_que_o_estoque_e_recusada(tela, loja):
    _registrar(tela, procurar="iogurte", quantidade="20", motivo="Estragou")

    _recusado(tela)
    expect(tela.locator("#erro-quantidade")).to_have_text("Só há 19 UN de Iogurte natural no estoque.")
    assert not _perdas().exists()
    assert saldo_do_produto(loja["iogurte"]) == Decimal("19")


# ------------------------------------------------------------------------------------------------
# O lote está vencido? (RN16)
# ------------------------------------------------------------------------------------------------


def test_d4_rn16_vencido_sai_como_perda_pela_tela(tela, loja):
    # Apostila I: iogurte vencido aparece destacado e sai pela tela de avarias, com motivo.
    tela.fill("#campo-procurar", "iogurte")
    opcao_do_vencido = tela.locator("#lista-de-lotes label").nth(1)
    expect(opcao_do_vencido).to_contain_text("Vencido há 1 dia")

    _registrar(tela, procurar="iogurte", quantidade="3", motivo="Venceu", lote=loja["vencido"])

    _confirmado(tela)
    assert _atual(loja["vencido"]) == Decimal("0")
    tela.fill("#campo-procurar", "")
    tela.fill("#campo-procurar", "iogurte")
    expect(tela.locator("#lista-de-lotes label")).to_have_count(3)  # o vencido zerado saiu da lista


def test_d4_rn16_lote_bom_tambem_sai_como_perda(tela, loja):
    _registrar(tela, procurar="iogurte", quantidade="1", motivo="Quebrou", lote=loja["vencendo"])

    _confirmado(tela)
    assert _atual(loja["vencendo"]) == Decimal("5")


# ------------------------------------------------------------------------------------------------
# O que a perda não pode fazer (RN11, RN01)
# ------------------------------------------------------------------------------------------------


def test_d4_rn11_frango_que_foi_fora_nao_vira_consumo(tela, loja):
    # Especificação (perdas): vendidos 6 kg e 10 kg vão fora → saldo cai 16 kg, consumo do dia 6 kg.
    # A venda entra direto no banco: a importação das vendas é o bloco E (aguarda D01).
    Movimentacao.objects.create(
        produto=loja["frango"], tipo=Movimentacao.Tipo.VENDA, quantidade=Decimal("6"), origem="IMPORTACAO_PDV"
    )

    _registrar(tela, procurar="frango", quantidade="10", motivo="Foi fora")

    _confirmado(tela)
    assert saldo_do_produto(loja["frango"]) == Decimal("24")  # 40 − 6 − 10
    assert vendido_no_periodo(loja["frango"], _hoje(), _hoje()) == Decimal("6")


def test_d4_rn01_saldo_continua_igual_a_soma_dos_lotes(tela, loja):
    _registrar(tela, procurar="iogurte", quantidade="4", motivo="Estragou")
    _confirmado(tela)
    _registrar(tela, procurar="iogurte", quantidade="2", motivo="Quebrou", lote=loja["bom"])
    _confirmado(tela)

    soma_dos_lotes = sum(lote.quantidade_atual for lote in Lote.objects.filter(produto=loja["iogurte"]))
    assert saldo_do_produto(loja["iogurte"]) == soma_dos_lotes == Decimal("13")
    expect(tela.locator("#sucesso-texto")).to_contain_text("Agora tem 13 UN em estoque.")


def test_d4_caderno_de_hoje_mostra_cada_lote_que_saiu(tela, loja):
    _registrar(tela, procurar="iogurte", quantidade="4", motivo="Estragou na geladeira")
    _confirmado(tela)

    linhas = tela.locator("#corpo-tabela tr")
    expect(linhas).to_have_count(2)  # uma linha por movimentação (RN01)
    expect(tela.locator("#corpo-tabela")).to_contain_text("Estragou na geladeira")
    expect(tela.locator("#corpo-tabela")).to_contain_text("Sobrinho")


# ------------------------------------------------------------------------------------------------
# Do Login à perda, e quem não pode (RN14)
# ------------------------------------------------------------------------------------------------


def test_d4_do_login_a_perda_registrada(page, painel, loja):
    entrar_pelo_login(page, painel, "sobrinho", SENHA)
    page.click('#menu a[href="avarias.html"]')
    expect(page.locator('#menu a[aria-current="page"]')).to_have_text("Avarias e quebras")

    _registrar(page, procurar="frango", quantidade="2,5", motivo="Estragou")

    _confirmado(page)
    assert _perdas().get().quantidade == Decimal("2.5")  # quilo fracionado, digitado com vírgula


@pytest.mark.parametrize("papel", ["DONO", "GESTAO"])
def test_d4_rn14_dono_e_esposa_nao_registram_perda(page, painel, loja, papel):
    pessoa = Usuario.objects.create_user(login=papel.lower(), senha=SENHA, nome=papel, papel=papel)
    guardar_sessao(page, painel, pessoa)

    page.goto(f"{painel}/{TELA}")

    expect(page.locator("#recado")).to_have_text("O seu perfil não tem acesso à tela de Avarias e quebras.")
    assert not _perdas().exists()

"""
Tarefa I3 — relatório de balanço semanal (RF13). Tela "Balanço da semana", da esposa (GESTAO, RN14):
"vendas, perdas e resultado do período, com as perdas separadas das vendas".

Decisão do grupo (12/11/2026, lacuna L16): resultado = vendas da semana (a preço de venda, o que o
caixa registrou) − perdas da semana (a preço de custo: o custo do lote; sem ele, o preço de custo do
produto). O custo da mercadoria vendida não entra — seria controle financeiro, fora do escopo.
RN11: as perdas aparecem em linha separada, nunca misturadas às vendas.

Adotado na I3 (a confirmar pelo grupo):
- semana de segunda a domingo; a tela abre na semana de ontem (as vendas de hoje só entram às 03h00);
- dia da semana já passado sem a planilha do caixa importada é avisado (como no fechamento, I1);
- perda sem custo cadastrado não entra no valor e é avisada, em vez de virar zero calado.

    GET /api/balancos/?semana=AAAA-MM-DD   (qualquer dia da semana; sem o filtro, a semana de ontem)

Losangos, pelo "sim" e pelo "não":
    a perda tem custo no lote?        sim → *_custo_do_lote_*     não → *_custo_do_produto_*
    o produto tem preço de custo?     sim → *_custo_do_produto_*  não → *_sem_custo_*
    as vendas do dia entraram?        sim → sem aviso             não → *_dia_sem_vendas_*
    a semana já começou?              sim → balanço               não → *_semana_futura_*
"""

import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from playwright.sync_api import expect

from cadastro.models import Categoria, Produto, Usuario
from caixa.balanco import balanco_da_semana, semana_de
from comum.autenticacao import gerar_token
from estoque.models import Lote, Movimentacao
from tests.conftest import abrir_tela
from vendas.models import ImportacaoPdv, Venda

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
TELA = "balanco-semana.html"
SAO_PAULO = ZoneInfo("America/Sao_Paulo")
SENHA = "Mercado#2026"
QUINTA = datetime(2026, 11, 12, 9, 0, tzinfo=SAO_PAULO)  # semana de seg 09/11 a dom 15/11


@pytest.fixture(autouse=True)
def quinta_12_11():
    with patch("django.utils.timezone.now", return_value=QUINTA):
        yield


def _venda(valor, dia, hora=10, minuto=0):
    return Venda.objects.create(
        data_hora=datetime(dia.year, dia.month, dia.day, hora, minuto, tzinfo=SAO_PAULO),
        valor_total=Decimal(valor),
        forma_pagamento="PIX",
    )


def _importado(*dias):
    for dia in dias:
        ImportacaoPdv.objects.create(arquivo_nome=f"vendas-{dia}.xlsx", data_referencia=dia, status="OK")


def _produto(nome, preco_custo=None, unidade="KG"):
    categoria, _ = Categoria.objects.get_or_create(nome="Açougue")
    return Produto.objects.create(
        categoria=categoria, nome=nome, unidade_medida=unidade, preco_custo=preco_custo
    )


def _perda(produto, quantidade, dia, custo_do_lote=None, hora=15):
    lote = Lote.objects.create(
        produto=produto,
        quantidade_inicial=Decimal("50"),
        quantidade_atual=Decimal("50"),
        data_entrada=date(2026, 11, 1),
        custo_unitario=None if custo_do_lote is None else Decimal(custo_do_lote),
    )
    return Movimentacao.objects.create(
        produto=produto,
        lote=lote,
        tipo="PERDA",
        quantidade=Decimal(quantidade),
        motivo="Estragou",
        data_hora=datetime(dia.year, dia.month, dia.day, hora, 0, tzinfo=SAO_PAULO),
    )


SEGUNDA, TERCA, QUARTA = date(2026, 11, 9), date(2026, 11, 10), date(2026, 11, 11)


# --- Semana ---------------------------------------------------------------------------------------


@pytest.mark.parametrize("dia", [SEGUNDA, QUARTA, date(2026, 11, 15)])
def test_i3_semana_vai_de_segunda_a_domingo(dia):
    assert semana_de(dia) == (SEGUNDA, date(2026, 11, 15))


# --- Vendas, perdas, resultado --------------------------------------------------------------------


@pytest.mark.django_db
def test_i3_vendas_da_semana_somam_o_que_o_caixa_registrou():
    _importado(SEGUNDA, TERCA, QUARTA)
    _venda("100.00", SEGUNDA)
    _venda("50.50", TERCA)
    _venda("30.00", QUARTA, 22, 30)  # 22h30 de quarta: é da quarta, não da quinta (UTC)
    _venda("999.00", date(2026, 11, 8))  # domingo da semana anterior
    balanco = balanco_da_semana()
    assert (balanco.inicio, balanco.fim) == (SEGUNDA, date(2026, 11, 15))
    assert balanco.vendas_total == Decimal("180.50")
    assert balanco.cupons == 3
    assert [(dia, total, cupons) for dia, total, cupons in balanco.vendas_por_dia][:3] == [
        (SEGUNDA, Decimal("100.00"), 1),
        (TERCA, Decimal("50.50"), 1),
        (QUARTA, Decimal("30.00"), 1),
    ]
    assert len(balanco.vendas_por_dia) == 7


@pytest.mark.django_db
def test_rn11_perda_aparece_separada_e_nao_soma_nas_vendas():
    _importado(SEGUNDA, TERCA, QUARTA)
    _venda("100.00", SEGUNDA)
    _perda(_produto("Frango resfriado 1 kg"), "10", TERCA, custo_do_lote="9.50")
    balanco = balanco_da_semana()
    assert balanco.vendas_total == Decimal("100.00")
    assert balanco.perdas_total == Decimal("95.00")
    assert balanco.resultado == Decimal("5.00")


@pytest.mark.django_db
def test_l16_perda_a_preco_de_custo_do_lote():
    _perda(_produto("Presunto", preco_custo="40.00"), "0.5", TERCA, custo_do_lote="32.00")
    assert balanco_da_semana().perdas_total == Decimal("16.00")


@pytest.mark.django_db
def test_l16_lote_sem_custo_usa_o_preco_de_custo_do_produto():
    _perda(_produto("Presunto", preco_custo="40.00"), "0.5", TERCA)
    assert balanco_da_semana().perdas_total == Decimal("20.00")


@pytest.mark.django_db
def test_l16_perda_sem_custo_nenhum_nao_entra_no_valor_e_e_avisada():
    _perda(_produto("Iogurte", unidade="UN"), "3", TERCA)
    _perda(_produto("Presunto", preco_custo="40.00"), "0.5", TERCA)
    balanco = balanco_da_semana()
    assert balanco.perdas_total == Decimal("20.00")
    assert balanco.perdas_sem_custo == 1
    iogurte = next(item for item in balanco.perdas if item.produto_nome == "Iogurte")
    assert iogurte.valor is None and iogurte.quantidade == Decimal("3")


@pytest.mark.django_db
def test_l16_produto_com_parte_das_perdas_sem_custo_e_avisado():
    presunto = _produto("Presunto")
    _perda(presunto, "1", SEGUNDA, custo_do_lote="30.00")
    _perda(presunto, "2", TERCA)
    balanco = balanco_da_semana()
    (item,) = balanco.perdas
    assert (item.quantidade, item.valor, item.sem_custo) == (Decimal("3"), Decimal("30.00"), True)
    assert balanco.perdas_sem_custo == 1


@pytest.mark.django_db
def test_i3_perdas_por_produto_somam_a_semana_e_vem_da_maior_para_a_menor():
    frango = _produto("Frango resfriado 1 kg", preco_custo="10.00")
    _perda(frango, "2", SEGUNDA)
    _perda(frango, "3", QUARTA)
    _perda(_produto("Presunto", preco_custo="40.00"), "0.5", TERCA)
    _perda(frango, "100", date(2026, 11, 16))  # semana seguinte
    perdas = [(item.produto_nome, item.quantidade, item.valor) for item in balanco_da_semana().perdas]
    assert perdas == [
        ("Frango resfriado 1 kg", Decimal("5"), Decimal("50.00")),
        ("Presunto", Decimal("0.5"), Decimal("20.00")),
    ]


@pytest.mark.django_db
def test_i3_resultado_pode_ser_negativo():
    _venda("10.00", SEGUNDA)
    _perda(_produto("Frango", preco_custo="10.00"), "3", SEGUNDA)
    assert balanco_da_semana().resultado == Decimal("-20.00")


@pytest.mark.django_db
def test_i3_venda_e_entrada_nao_contam_como_perda():
    frango = _produto("Frango", preco_custo="10.00")
    Movimentacao.objects.create(produto=frango, tipo="ENTRADA", quantidade=Decimal("20"))
    Movimentacao.objects.create(produto=frango, tipo="VENDA", quantidade=Decimal("5"))
    assert balanco_da_semana().perdas == []


# --- Dias sem vendas importadas -------------------------------------------------------------------


@pytest.mark.django_db
def test_i3_dia_sem_vendas_importadas_e_avisado_so_ate_ontem():
    _importado(SEGUNDA, QUARTA)
    balanco = balanco_da_semana()
    assert balanco.dias_sem_vendas == [TERCA]  # quinta (hoje) em diante ainda não acabou
    assert balanco.ate == QUARTA


@pytest.mark.django_db
def test_i3_semana_passada_inteira_importada_nao_avisa():
    dias = [date(2026, 11, 2 + n) for n in range(7)]
    _importado(*dias)
    balanco = balanco_da_semana(date(2026, 11, 4))
    assert balanco.dias_sem_vendas == [] and balanco.ate == date(2026, 11, 8)


@pytest.mark.django_db
def test_i3_importacao_com_erro_nao_conta_como_vendas_que_entraram():
    ImportacaoPdv.objects.create(arquivo_nome="x.xlsx", data_referencia=SEGUNDA, status="ERRO")
    _importado(TERCA, QUARTA)
    assert balanco_da_semana().dias_sem_vendas == [SEGUNDA]


# --- API ------------------------------------------------------------------------------------------


@pytest.fixture
def api(client, db):
    usuarios = {
        papel: Usuario.objects.create_user(login=papel.lower(), senha=SENHA, nome=papel, papel=papel)
        for papel in ("DONO", "GESTAO", "OPERACAO")
    }

    def ler(filtros="", papel="GESTAO"):
        return client.get(
            f"/api/balancos/{filtros}", HTTP_AUTHORIZATION=f"Bearer {gerar_token(usuarios[papel])}"
        )

    return ler


def test_i3_api_devolve_o_balanco_da_semana_de_ontem(api):
    _importado(SEGUNDA, TERCA, QUARTA)
    _venda("100.00", SEGUNDA)
    _perda(_produto("Frango resfriado 1 kg"), "2", TERCA, custo_do_lote="9.50")
    dados = api().json()
    assert (dados["inicio"], dados["fim"], dados["ate"]) == ("2026-11-09", "2026-11-15", "2026-11-11")
    assert (dados["vendas_total"], dados["perdas_total"], dados["resultado"]) == ("100.00", "19.00", "81.00")
    assert dados["cupons"] == 1 and dados["perdas_sem_custo"] == 0 and dados["dias_sem_vendas"] == []
    assert dados["vendas_por_dia"][0] == {"data": "2026-11-09", "total": "100.00", "cupons": 1}
    assert dados["perdas"] == [
        {
            "produto_nome": "Frango resfriado 1 kg",
            "unidade_medida": "KG",
            "quantidade": "2",
            "valor": "19.00",
            "sem_custo": False,
        }
    ]


def test_i3_api_escolhe_a_semana_por_qualquer_dia_dela(api):
    assert api("?semana=2026-11-04").json()["inicio"] == "2026-11-02"


def test_i3_api_semana_futura_e_recusada(api):
    resposta = api("?semana=2026-11-16")
    assert resposta.status_code == 400
    assert "ainda não começou" in resposta.json()["erro"]["campos"]["semana"][0]


def test_i3_api_data_invalida_e_recusada(api):
    assert api("?semana=16/11/2026").status_code == 400


@pytest.mark.parametrize("papel", ["DONO", "OPERACAO"])
def test_rn14_so_gestao_ve_o_balanco(api, papel):
    assert api(papel=papel).status_code == 403


# --- Tela -----------------------------------------------------------------------------------------


def test_i3_tela_entra_no_menu_da_esposa():
    sessao = (FRONTEND / "js" / "sessao.js").read_text(encoding="utf-8")
    assert 'balanco_semana: { nome: "Balanço da semana", endereco: "balanco-semana.html" }' in sessao


def test_i3_tela_exige_login_e_o_perfil_do_balanco():
    html = (FRONTEND / TELA).read_text(encoding="utf-8")
    script = re.search(r'src="js/([\w-]+)\.js"', html).group(1)
    assert 'entrarNaTela("balanco_semana")' in (FRONTEND / "js" / f"{script}.js").read_text(encoding="utf-8")


def test_i3_tela_so_le_nao_grava_nada():
    script = (FRONTEND / "js" / "balanco-semana.js").read_text(encoding="utf-8")
    assert "api.criar" not in script and "api.alterar" not in script


@pytest.fixture
def esposa(painel):
    return Usuario.objects.create_user(login="esposa", senha=SENHA, nome="Dona Maria", papel="GESTAO")


@pytest.mark.tela
def test_i3_tela_mostra_vendas_perdas_e_resultado_separados(page, painel, esposa):
    _importado(SEGUNDA, TERCA, QUARTA)
    _venda("3240.00", SEGUNDA)
    _perda(_produto("Frango resfriado 1 kg"), "10", TERCA, custo_do_lote="9.50")
    abrir_tela(page, painel, esposa, TELA)
    expect(page.locator("#titulo-semana")).to_contain_text("09/11 a 15/11/2026")
    expect(page.locator("#valor-vendas")).to_have_text("R$ 3.240,00")
    expect(page.locator("#valor-perdas")).to_have_text("R$ 95,00")
    expect(page.locator("#valor-resultado")).to_have_text("R$ 3.145,00")
    expect(page.locator("#corpo-perdas")).to_contain_text("Frango resfriado 1 kg")
    expect(page.locator("#corpo-perdas")).to_contain_text("10 KG")
    expect(page.locator("#corpo-vendas tr").first).to_contain_text("R$ 3.240,00")


@pytest.mark.tela
def test_i3_tela_avisa_o_dia_cujas_vendas_nao_entraram(page, painel, esposa):
    _importado(SEGUNDA, QUARTA)
    abrir_tela(page, painel, esposa, TELA)
    expect(page.locator("#aviso-dias")).to_contain_text("10/11")
    terca = page.locator("#corpo-vendas tr").nth(1)
    expect(terca).to_contain_text("não entrou")
    expect(terca).not_to_contain_text("R$ 0,00")


@pytest.mark.tela
def test_i3_tela_avisa_perda_sem_custo(page, painel, esposa):
    _importado(SEGUNDA, TERCA, QUARTA)
    _perda(_produto("Iogurte", unidade="UN"), "3", TERCA)
    abrir_tela(page, painel, esposa, TELA)
    expect(page.locator("#corpo-perdas")).to_contain_text("sem custo cadastrado")
    expect(page.locator("#aviso-custo")).to_be_visible()


@pytest.mark.tela
def test_i3_tela_volta_para_a_semana_anterior_e_nao_passa_da_atual(page, painel, esposa):
    _venda("70.00", date(2026, 11, 3))
    abrir_tela(page, painel, esposa, TELA)
    expect(page.locator("#titulo-semana")).to_contain_text("09/11 a 15/11/2026")
    expect(page.locator("#botao-anterior")).to_be_enabled()  # o balanço terminou de carregar
    expect(page.locator("#botao-proxima")).to_be_disabled()
    page.click("#botao-anterior")
    expect(page.locator("#titulo-semana")).to_contain_text("02/11 a 08/11/2026")
    expect(page.locator("#valor-vendas")).to_have_text("R$ 70,00")
    expect(page.locator("#botao-proxima")).to_be_enabled()


@pytest.mark.tela
def test_i3_no_celular_nada_fica_escondido_a_direita(page, painel, esposa):
    from tests.test_telas_no_celular import _ESCONDIDO_A_DIREITA, CELULAR

    _importado(SEGUNDA, QUARTA)
    _venda("3240.00", SEGUNDA)
    _perda(_produto("Iogurte natural 170 g", unidade="UN"), "6", TERCA)
    page.set_viewport_size(CELULAR)
    abrir_tela(page, painel, esposa, TELA)
    page.wait_for_selector("#corpo-perdas tr th")
    expect(page.get_by_role("button", name="Semana anterior")).to_be_in_viewport(ratio=1)
    assert page.evaluate(_ESCONDIDO_A_DIREITA) == []

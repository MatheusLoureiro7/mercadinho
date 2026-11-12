"""
Tarefa E4 — casar o produto do caixa com o produto cadastrado. Operação 04, passo 6: "linha sem
produto correspondente fica pendente de revisão [...] o sobrinho resolve depois, na tela de
importação".

Decisão do grupo (12/11/2026, lacuna L26): o modelo de dados NÃO muda. `item_venda` não guarda o
nome escrito na planilha, então o item pendente aparece com data, hora, quantidade e preço; o
sobrinho confere na planilha dele e escolhe o produto. Ao casar, a baixa acontece como se tivesse
casado na importação: na hora da venda, do lote que vence primeiro (RN01, RN02), sem lote que já
estava vencido no dia da venda (RN16).

Losangos, pelo "sim" e pelo "não":
    item ainda pendente?     sim → *_casar_grava_o_produto_*          não → *_item_ja_casado_*
    produto existe?          sim → *_casar_grava_o_produto_*          não → *_produto_que_nao_existe_*
    estoque cobre a venda?   sim → baixa só dos lotes                 não → *_venda_maior_que_o_estoque_*
    lote vencido na data?    sim → *_rn16_vencido_antes_*             não → *_rn16_ainda_valia_*
    papel OPERACAO?          sim → os demais testes                   não → *_rn14_*
"""

from datetime import date, datetime, time, timedelta
from decimal import Decimal
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from openpyxl import Workbook

from cadastro.models import Categoria, Produto, Usuario
from comum.autenticacao import gerar_token
from comum.erros import ErroDeRegraDeNegocio
from estoque.models import Lote, Movimentacao
from estoque.saldo import saldo_do_produto
from previsao.consumo import vendido_no_periodo
from vendas.conciliacao import casar_item, itens_pendentes
from vendas.importacao import importar_planilha
from vendas.models import ImportacaoPdv, ItemVenda, Venda

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
DIA = date(2026, 11, 5)
HORA_DA_VENDA = datetime(2026, 11, 5, 8, 14, tzinfo=SAO_PAULO)
HOJE_DE_MANHA = datetime(2026, 11, 12, 9, 0, tzinfo=SAO_PAULO)
URL = "/api/itens-pendentes/"


@pytest.fixture(autouse=True)
def manha_de_12_11():
    with patch("django.utils.timezone.now", return_value=HOJE_DE_MANHA):
        yield


@pytest.fixture
def frango(db):
    acougue = Categoria.objects.create(nome="Açougue", perecivel_padrao=True)
    return Produto.objects.create(
        categoria=acougue,
        nome="Frango resfriado 1 kg",
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=4,
    )


def _lote(produto, quantidade, validade, entrada=DIA - timedelta(days=2)):
    lote = Lote.objects.create(
        produto=produto,
        quantidade_inicial=Decimal(quantidade),
        quantidade_atual=Decimal(quantidade),
        data_entrada=entrada,
        data_validade=validade,
    )
    Movimentacao.objects.create(produto=produto, lote=lote, tipo="ENTRADA", quantidade=Decimal(quantidade))
    return lote


def _pendente(quantidade="1.275", preco="21.90", data_hora=HORA_DA_VENDA):
    venda = Venda.objects.create(data_hora=data_hora, valor_total=Decimal("27.92"), forma_pagamento="PIX")
    return ItemVenda.objects.create(
        venda=venda, produto=None, quantidade=Decimal(quantidade), preco=Decimal(preco)
    )


def _vendas(produto):
    return Movimentacao.objects.filter(produto=produto, tipo="VENDA").order_by("id")


@pytest.fixture
def api(client, db):
    usuarios = {
        papel: Usuario.objects.create_user(login=papel.lower(), senha="Mercado#2026", nome=papel, papel=papel)
        for papel in ("DONO", "GESTAO", "OPERACAO")
    }

    def chamar(metodo, url=URL, dados=None, papel="OPERACAO"):
        cabecalho = {"HTTP_AUTHORIZATION": f"Bearer {gerar_token(usuarios[papel])}"}
        return getattr(client, metodo)(url, dados, content_type="application/json", **cabecalho)

    return chamar


# --- Serviço --------------------------------------------------------------------------------------


def test_e4_lista_so_os_itens_sem_produto_do_mais_antigo_ao_mais_novo(frango):
    # Criados fora da ordem da hora, para a lista não sair certa por acaso na ordem do id.
    meio = _pendente(data_hora=HORA_DA_VENDA + timedelta(hours=1))
    cedo = _pendente()
    tarde = _pendente(data_hora=HORA_DA_VENDA + timedelta(hours=2))
    casado = _pendente()
    casado.produto = frango
    casado.save()
    assert list(itens_pendentes()) == [cedo, meio, tarde]


def test_e4_casar_grava_o_produto_e_baixa_do_lote_que_vence_primeiro(frango):
    tarde = _lote(frango, "5", DIA + timedelta(days=4))
    cedo = _lote(frango, "1", DIA + timedelta(days=2))
    item = _pendente(quantidade="1.275")

    casar_item(item.pk, frango)

    item.refresh_from_db()
    assert item.produto == frango
    baixas = [(m.lote_id, m.quantidade, m.data_hora, m.origem) for m in _vendas(frango)]
    assert baixas == [
        (cedo.pk, Decimal("1.000"), HORA_DA_VENDA, "IMPORTACAO_PDV"),
        (tarde.pk, Decimal("0.275"), HORA_DA_VENDA, "IMPORTACAO_PDV"),
    ]
    cedo.refresh_from_db()
    tarde.refresh_from_db()
    assert (cedo.quantidade_atual, tarde.quantidade_atual) == (Decimal("0"), Decimal("4.725"))
    assert saldo_do_produto(frango) == Decimal("4.725")  # RN01: saldo derivado das movimentações
    assert list(itens_pendentes()) == []


def test_e4_movimentacao_leva_o_preco_da_planilha(frango):
    _lote(frango, "5", DIA + timedelta(days=4))
    casar_item(_pendente(preco="21.90").pk, frango)
    assert _vendas(frango).get().preco_unitario == Decimal("21.90")


def test_e4_rn16_vencido_antes_do_dia_da_venda_nao_sai(frango):
    vencido = _lote(frango, "5", DIA - timedelta(days=1))
    bom = _lote(frango, "5", DIA + timedelta(days=3))
    casar_item(_pendente(quantidade="2").pk, frango)
    assert [m.lote_id for m in _vendas(frango)] == [bom.pk]
    vencido.refresh_from_db()
    assert vencido.quantidade_atual == Decimal("5")


def test_e4_rn16_ainda_valia_no_dia_da_venda_mesmo_vencido_hoje(frango):
    # Venceu em 07/11 — hoje (12/11) está vencido, mas na venda de 05/11 ainda valia.
    valia = _lote(frango, "5", DIA + timedelta(days=2))
    casar_item(_pendente(quantidade="2").pk, frango)
    assert [m.lote_id for m in _vendas(frango)] == [valia.pk]


def test_e4_venda_maior_que_o_estoque_grava_a_sobra_sem_lote(frango):
    lote = _lote(frango, "1", DIA + timedelta(days=3))
    casar_item(_pendente(quantidade="1.5").pk, frango)
    assert [(m.lote_id, m.quantidade) for m in _vendas(frango)] == [
        (lote.pk, Decimal("1.000")),
        (None, Decimal("0.500")),
    ]
    assert saldo_do_produto(frango) == Decimal("-0.500")


def test_e4_item_ja_casado_e_recusado_e_nao_baixa_de_novo(frango):
    _lote(frango, "5", DIA + timedelta(days=3))
    item = _pendente(quantidade="1")
    casar_item(item.pk, frango)

    with pytest.raises(ErroDeRegraDeNegocio, match="já foi"):
        casar_item(item.pk, frango)
    assert _vendas(frango).count() == 1


def test_e4_rn11_venda_casada_depois_conta_no_consumo_do_dia_da_venda(frango):
    _lote(frango, "5", DIA + timedelta(days=3))
    casar_item(_pendente(quantidade="2").pk, frango)
    assert vendido_no_periodo(frango, DIA, DIA) == Decimal("2")
    assert vendido_no_periodo(frango, DIA + timedelta(days=1), DIA + timedelta(days=7)) == Decimal("0")


def test_e4_ponta_a_ponta_planilha_com_nome_desconhecido_e_casada_depois(tmp_path, frango):
    _lote(frango, "5", DIA + timedelta(days=3))
    livro = Workbook()
    livro.active.append(["Cupom", "Data", "Hora", "Produto", "Quantidade", "Preço unitário", "Pagamento"])
    livro.active.append([1021, DIA, time(8, 14), "Frango congelado", 2, 21.9, "PIX"])
    caminho = tmp_path / "vendas-2026-11-05.xlsx"
    livro.save(caminho)

    assert importar_planilha(caminho).status == ImportacaoPdv.Status.PARCIAL
    assert saldo_do_produto(frango) == Decimal("5")

    casar_item(itens_pendentes().get().pk, frango)
    assert saldo_do_produto(frango) == Decimal("3")


# --- API ------------------------------------------------------------------------------------------


def test_e4_api_lista_os_pendentes_com_data_hora_quantidade_e_preco(api, frango):
    item = _pendente()
    resposta = api("get")
    assert resposta.status_code == 200
    assert resposta.json() == [
        {
            "id": item.pk,
            "venda": item.venda_id,
            "data_hora": "2026-11-05T08:14:00-03:00",
            "quantidade": "1.275",
            "preco": "21.90",
        }
    ]


def test_e4_api_casar_grava_e_devolve_o_item_com_o_produto(api, frango):
    _lote(frango, "5", DIA + timedelta(days=3))
    item = _pendente(quantidade="2")
    resposta = api("post", f"{URL}{item.pk}/casar/", {"produto": frango.pk})
    assert resposta.status_code == 200
    assert resposta.json()["produto"] == frango.pk
    assert resposta.json()["produto_nome"] == "Frango resfriado 1 kg"
    assert saldo_do_produto(frango) == Decimal("3")
    assert api("get").json() == []


def test_e4_api_item_ja_casado_responde_erro_de_regra(api, frango):
    item = _pendente()
    api("post", f"{URL}{item.pk}/casar/", {"produto": frango.pk})
    resposta = api("post", f"{URL}{item.pk}/casar/", {"produto": frango.pk})
    assert resposta.status_code == 400
    assert "já foi" in resposta.json()["erro"]["mensagem"]
    assert _vendas(frango).count() == 1


@pytest.mark.parametrize("dados", [{}, {"produto": 99999}, {"produto": "frango"}])
def test_e4_api_produto_que_nao_existe_e_recusado(api, frango, dados):
    item = _pendente()
    resposta = api("post", f"{URL}{item.pk}/casar/", dados)
    assert resposta.status_code == 400
    assert "produto" in resposta.json()["erro"]["campos"]
    item.refresh_from_db()
    assert item.produto is None


def test_e4_api_item_que_nao_existe_responde_404(api, frango):
    assert api("post", f"{URL}99999/casar/", {"produto": frango.pk}).status_code == 404


@pytest.mark.parametrize("papel", ["DONO", "GESTAO"])
def test_rn14_so_operacao_ve_e_casa_os_itens_pendentes(api, frango, papel):
    item = _pendente()
    assert api("get", papel=papel).status_code == 403
    assert api("post", f"{URL}{item.pk}/casar/", {"produto": frango.pk}, papel=papel).status_code == 403
    item.refresh_from_db()
    assert item.produto is None

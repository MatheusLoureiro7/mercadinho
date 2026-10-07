"""
Tarefa C2 — API de entrada de lote (RF03, operação 02 da Apostila IV).

RF03: "Cada carga que chega vira um lote, com quantidade, custo, fornecedor e data de validade."
Operação 02, passos 6 a 8: lote e movimentação ENTRADA gravados numa transação só (RN01) —
"Nunca existe lote sem a movimentação que explica o saldo."
As regras de validade (RN04, passos 3 a 5) são a tarefa C3.
"""

from datetime import date, timedelta
from decimal import Decimal
from unittest import mock

import pytest
from django.utils import timezone

from cadastro.models import Categoria, Fornecedor, Produto, Usuario
from comum.autenticacao import gerar_token
from estoque.entrada import registrar_entrada
from estoque.models import Lote, Movimentacao
from estoque.saldo import saldo_do_produto

URL = "/api/lotes/"


@pytest.fixture
def usuarios(db):
    return {
        papel: Usuario.objects.create_user(login=papel.lower(), senha="Mercado#2026", nome=papel, papel=papel)
        for papel in ("DONO", "GESTAO", "OPERACAO")
    }


@pytest.fixture
def api(client, usuarios):
    class ClienteLogado:
        def __init__(self, papel):
            self.cabecalho = {"HTTP_AUTHORIZATION": f"Bearer {gerar_token(usuarios[papel])}"}

        def get(self, url):
            return client.get(url, **self.cabecalho)

        def post(self, dados):
            return client.post(URL, dados, content_type="application/json", **self.cabecalho)

        def patch(self, url, dados):
            return client.patch(url, dados, content_type="application/json", **self.cabecalho)

        def delete(self, url):
            return client.delete(url, **self.cabecalho)

    return ClienteLogado


@pytest.fixture
def boi_bom(db):
    return Fornecedor.objects.create(nome="Frigorífico Boi Bom", prazo_entrega_dias=3)


@pytest.fixture
def frango(db, boi_bom):
    acougue = Categoria.objects.create(nome="Açougue", perecivel_padrao=True)
    return Produto.objects.create(
        categoria=acougue,
        fornecedor_padrao=boi_bom,
        nome="Frango resfriado 1 kg",
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=4,
    )


@pytest.fixture
def arroz(db):
    secos = Categoria.objects.create(nome="Secos e molhados")
    return Produto.objects.create(categoria=secos, nome="Arroz 5 kg", unidade_medida="PCT")


def _validade(dias=4):
    return (timezone.localdate() + timedelta(days=dias)).isoformat()


# --- Passos 6 a 8: lote + movimentação, juntos -----------------------------------------------------


def test_c2_entrada_grava_o_lote_e_a_movimentacao_que_o_explica(api, frango, boi_bom, usuarios):
    resposta = api("OPERACAO").post(
        {
            "produto": frango.pk,
            "fornecedor": boi_bom.pk,
            "quantidade": "40",
            "custo_unitario": "8.50",
            "data_validade": _validade(),
        }
    )
    assert resposta.status_code == 201

    lote = Lote.objects.get()
    assert lote.quantidade_inicial == lote.quantidade_atual == Decimal("40")
    assert lote.custo_unitario == Decimal("8.50")
    assert lote.fornecedor == boi_bom

    mov = Movimentacao.objects.get()
    assert (mov.tipo, mov.produto, mov.lote, mov.quantidade) == ("ENTRADA", frango, lote, Decimal("40"))
    assert mov.usuario == usuarios["OPERACAO"]  # quem registrou
    assert mov.origem == "TELA"
    assert mov.preco_unitario == Decimal("8.50")


def test_rn01_falha_na_movimentacao_desfaz_o_lote(frango, usuarios):
    # Operação 02, passo 7: "Se a segunda falhar, a primeira é desfeita."
    with (
        mock.patch.object(Movimentacao.objects, "create", side_effect=RuntimeError("falha simulada")),
        pytest.raises(RuntimeError),
    ):
        registrar_entrada(produto=frango, quantidade=Decimal("40"), usuario=usuarios["OPERACAO"])
    assert not Lote.objects.exists()
    assert not Movimentacao.objects.exists()


def test_rn01_entrada_com_sucesso_deixa_lote_e_movimentacao(frango, usuarios):
    lote = registrar_entrada(produto=frango, quantidade=Decimal("40"), usuario=usuarios["OPERACAO"])
    assert Movimentacao.objects.filter(lote=lote, tipo="ENTRADA").count() == 1


def test_rn01_entrada_aumenta_o_saldo(api, frango):
    api("OPERACAO").post({"produto": frango.pk, "quantidade": "40", "data_validade": _validade()})
    api("OPERACAO").post({"produto": frango.pk, "quantidade": "12.5", "data_validade": _validade()})
    assert saldo_do_produto(frango) == Decimal("52.5")


# --- Passo 9: avisa que o saldo mudou ------------------------------------------------------------


def test_c2_resposta_traz_o_saldo_novo_do_produto(api, frango):
    api("OPERACAO").post({"produto": frango.pk, "quantidade": "10", "data_validade": _validade()})
    corpo = (
        api("OPERACAO").post({"produto": frango.pk, "quantidade": "30", "data_validade": _validade()}).json()
    )
    assert corpo["saldo_produto"] == "40.000"
    assert corpo["produto_nome"] == "Frango resfriado 1 kg"


# --- Passo 10: cancela aviso de ruptura pendente -------------------------------------------------


def test_c2_entrada_pede_o_cancelamento_do_aviso_de_ruptura(frango, usuarios):
    with mock.patch("estoque.entrada.cancelar_aviso_de_ruptura_pendente") as cancelar:
        registrar_entrada(produto=frango, quantidade=Decimal("40"), usuario=usuarios["OPERACAO"])
    cancelar.assert_called_once_with(frango)


def test_c2_entrada_que_falhou_nao_cancela_aviso(frango, usuarios):
    with (
        mock.patch("estoque.entrada.cancelar_aviso_de_ruptura_pendente") as cancelar,
        mock.patch.object(Movimentacao.objects, "create", side_effect=RuntimeError("falha simulada")),
        pytest.raises(RuntimeError),
    ):
        registrar_entrada(produto=frango, quantidade=Decimal("40"), usuario=usuarios["OPERACAO"])
    cancelar.assert_not_called()


# --- Data de entrada ------------------------------------------------------------------------------


def test_c2_data_de_entrada_e_hoje_no_horario_da_loja(api, frango):
    api("OPERACAO").post({"produto": frango.pk, "quantidade": "5", "data_validade": _validade()})
    assert Lote.objects.get().data_entrada == timezone.localdate()


def test_c2_data_de_entrada_nao_pode_ser_escolhida(api, frango):
    resposta = api("OPERACAO").post(
        {"produto": frango.pk, "quantidade": "5", "data_validade": _validade(), "data_entrada": "2020-01-01"}
    )
    assert resposta.status_code == 201
    assert Lote.objects.get().data_entrada == timezone.localdate()


def test_c2_depois_das_21h_a_data_de_entrada_continua_sendo_hoje(frango, usuarios):
    # 22h30 em São Paulo = 01h30 do dia seguinte em UTC. A entrada é do dia da loja.
    noite = timezone.make_aware(timezone.datetime(2026, 9, 21, 22, 30))
    with mock.patch("django.utils.timezone.now", return_value=noite):
        lote = registrar_entrada(produto=frango, quantidade=Decimal("1"), usuario=usuarios["OPERACAO"])
    assert lote.data_entrada == date(2026, 9, 21)


# --- Validações de entrada -----------------------------------------------------------------------


def test_c2_produto_e_quantidade_sao_obrigatorios(api, db):
    resposta = api("OPERACAO").post({})
    assert resposta.status_code == 400
    assert set(resposta.json()["erro"]["campos"]) == {"produto", "quantidade"}
    assert not Lote.objects.exists()


@pytest.mark.parametrize("quantidade", ["0", "-5"])
def test_c2_quantidade_zero_ou_negativa_e_recusada(api, arroz, quantidade):
    resposta = api("OPERACAO").post({"produto": arroz.pk, "quantidade": quantidade})
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"] == {
        "quantidade": ["A quantidade que chegou tem de ser maior que zero."]
    }
    assert not Lote.objects.exists()


def test_c2_quantidade_em_quilo_fracionado_e_aceita(api, frango):
    resposta = api("OPERACAO").post(
        {"produto": frango.pk, "quantidade": "12.345", "data_validade": _validade()}
    )
    assert resposta.status_code == 201
    assert Lote.objects.get().quantidade_inicial == Decimal("12.345")


def test_c2_quantidade_com_mais_de_tres_casas_e_recusada(api, arroz):
    resposta = api("OPERACAO").post({"produto": arroz.pk, "quantidade": "1.2345"})
    assert resposta.status_code == 400
    assert "quantidade" in resposta.json()["erro"]["campos"]


def test_c2_produto_inexistente_e_recusado(api, db):
    resposta = api("OPERACAO").post({"produto": 9999, "quantidade": "5"})
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"] == {"produto": ["Esse produto não existe."]}


def test_c2_fornecedor_inexistente_e_recusado(api, arroz):
    resposta = api("OPERACAO").post({"produto": arroz.pk, "quantidade": "5", "fornecedor": 9999})
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"] == {"fornecedor": ["Esse fornecedor não existe."]}


def test_c2_custo_negativo_e_recusado(api, arroz):
    resposta = api("OPERACAO").post({"produto": arroz.pk, "quantidade": "5", "custo_unitario": "-1"})
    assert resposta.status_code == 400
    assert "custo_unitario" in resposta.json()["erro"]["campos"]


def test_c2_so_produto_e_quantidade_bastam_para_nao_perecivel(api, arroz):
    # RNF05: entrada rápida — custo e fornecedor são opcionais.
    resposta = api("OPERACAO").post({"produto": arroz.pk, "quantidade": "20"})
    assert resposta.status_code == 201
    lote = Lote.objects.get()
    assert lote.fornecedor is None
    assert lote.custo_unitario is None


# --- Passo 11: a lista do dia ---------------------------------------------------------------------


def test_c2_lista_do_dia_mostra_as_entradas_de_hoje(api, frango, arroz):
    api("OPERACAO").post({"produto": arroz.pk, "quantidade": "20"})
    api("OPERACAO").post({"produto": frango.pk, "quantidade": "40", "data_validade": _validade()})
    ontem = Lote.objects.create(
        produto=arroz,
        quantidade_inicial=1,
        quantidade_atual=1,
        data_entrada=timezone.localdate() - timedelta(days=1),
    )
    hoje = timezone.localdate().isoformat()
    lista = api("OPERACAO").get(f"{URL}?data_entrada={hoje}").json()
    assert [lote["produto_nome"] for lote in lista] == [
        "Frango resfriado 1 kg",
        "Arroz 5 kg",
    ]  # mais recente primeiro
    assert ontem.pk not in [lote["id"] for lote in lista]


def test_c2_lista_filtra_por_produto(api, frango, arroz):
    api("OPERACAO").post({"produto": arroz.pk, "quantidade": "20"})
    api("OPERACAO").post({"produto": frango.pk, "quantidade": "40", "data_validade": _validade()})
    lista = api("OPERACAO").get(f"{URL}?produto={arroz.pk}").json()
    assert [lote["produto_nome"] for lote in lista] == ["Arroz 5 kg"]


def test_c2_filtro_de_data_invalido_e_recusado(api, db):
    resposta = api("OPERACAO").get(f"{URL}?data_entrada=ontem")
    assert resposta.status_code == 400
    assert "data_entrada" in resposta.json()["erro"]["campos"]


def test_c2_consulta_um_lote(api, arroz):
    lote_id = api("OPERACAO").post({"produto": arroz.pk, "quantidade": "20"}).json()["id"]
    corpo = api("OPERACAO").get(f"{URL}{lote_id}/").json()
    assert corpo["quantidade_inicial"] == "20.000"
    assert corpo["quantidade_atual"] == "20.000"


# --- Lote não se edita nem se apaga ---------------------------------------------------------------


def test_rn01_lote_nao_pode_ser_editado(api, arroz):
    # Mudar a quantidade do lote desalinharia o saldo (RN01): correção é por perda ou ajuste.
    lote_id = api("OPERACAO").post({"produto": arroz.pk, "quantidade": "20"}).json()["id"]
    assert api("OPERACAO").patch(f"{URL}{lote_id}/", {"quantidade_atual": "5"}).status_code == 405
    assert Lote.objects.get().quantidade_atual == Decimal("20")


def test_rn01_lote_nao_pode_ser_apagado(api, arroz):
    lote_id = api("OPERACAO").post({"produto": arroz.pk, "quantidade": "20"}).json()["id"]
    assert api("OPERACAO").delete(f"{URL}{lote_id}/").status_code == 405
    assert Lote.objects.filter(pk=lote_id).exists()


# --- RN14 -----------------------------------------------------------------------------------------


@pytest.mark.parametrize("papel", ["DONO", "GESTAO"])
def test_rn14_so_operacao_registra_entrada(api, arroz, papel):
    assert api(papel).post({"produto": arroz.pk, "quantidade": "20"}).status_code == 403
    assert api(papel).get(URL).status_code == 403
    assert not Lote.objects.exists()
    assert not Movimentacao.objects.exists()

"""
Tarefa D1 — API de registro de perda, com motivo obrigatório.

RF04: "O que venceu, quebrou ou estragou sai do estoque com o motivo anotado."
Fluxograma 03 (registro de perda): RN01, RN02, RN11 · tabelas movimentacao e lote.
RN16: lote vencido não sai por venda — "a saída só é possível registrando perda".
L20: com lote informado, sai dele; sem lote, sai pela ordem de validade (RN02), vencidos incluídos.
"""

from datetime import date, datetime
from decimal import Decimal
from unittest import mock

import pytest
from django.utils import timezone

from cadastro.models import Categoria, Produto, Usuario
from comum.autenticacao import gerar_token
from comum.erros import ErroDeRegraDeNegocio
from estoque.fifo import lotes_em_ordem_de_validade
from estoque.models import Lote, Movimentacao
from estoque.perda import registrar_perda
from estoque.saldo import saldo_do_produto

URL = "/api/perdas/"
HOJE = date(2026, 9, 21)


@pytest.fixture(autouse=True)
def no_dia_21_09():
    meio_dia = timezone.make_aware(datetime(2026, 9, 21, 12, 0))
    with mock.patch("django.utils.timezone.now", return_value=meio_dia):
        yield


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

        def get(self, url=URL):
            return client.get(url, **self.cabecalho)

        def post(self, dados):
            return client.post(URL, dados, content_type="application/json", **self.cabecalho)

        def delete(self, url):
            return client.delete(url, **self.cabecalho)

    return ClienteLogado


@pytest.fixture
def frios(db):
    return Categoria.objects.create(nome="Frios", perecivel_padrao=True)


@pytest.fixture
def iogurte(frios):
    return Produto.objects.create(
        categoria=frios, nome="Iogurte natural", unidade_medida="UN", perecivel=True, durabilidade_dias=15
    )


@pytest.fixture
def presunto(frios):
    return Produto.objects.create(
        categoria=frios, nome="Presunto", unidade_medida="KG", perecivel=True, durabilidade_dias=7
    )


def _lote(produto, quantidade, validade, entrada=date(2026, 9, 10)):
    """Lote já com a movimentação de ENTRADA que o explica (RN01)."""
    lote = Lote.objects.create(
        produto=produto,
        quantidade_inicial=Decimal(quantidade),
        quantidade_atual=Decimal(quantidade),
        data_entrada=entrada,
        data_validade=validade,
    )
    Movimentacao.objects.create(produto=produto, lote=lote, tipo="ENTRADA", quantidade=Decimal(quantidade))
    return lote


# --- RF04: motivo obrigatório ---------------------------------------------------------------------


def test_d1_perda_com_motivo_e_registrada(api, presunto, usuarios):
    lote = _lote(presunto, "5", date(2026, 9, 28))
    resposta = api("OPERACAO").post({"produto": presunto.pk, "quantidade": "1.5", "motivo": "Caiu no chão"})
    assert resposta.status_code == 201
    mov = Movimentacao.objects.get(tipo="PERDA")
    assert (mov.produto, mov.lote, mov.quantidade, mov.motivo) == (
        presunto,
        lote,
        Decimal("1.5"),
        "Caiu no chão",
    )
    assert (mov.usuario, mov.origem) == (usuarios["OPERACAO"], "TELA")


@pytest.mark.parametrize("motivo", [None, "", "   "])
def test_d1_perda_sem_motivo_e_recusada(api, presunto, motivo):
    _lote(presunto, "5", date(2026, 9, 28))
    dados = {"produto": presunto.pk, "quantidade": "1"}
    if motivo is not None:
        dados["motivo"] = motivo
    resposta = api("OPERACAO").post(dados)
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"] == {
        "motivo": ["Anote o motivo da perda: venceu, quebrou, estragou…"]
    }
    assert not Movimentacao.objects.filter(tipo="PERDA").exists()


def test_d1_motivo_e_gravado_sem_espacos_nas_pontas(api, presunto):
    _lote(presunto, "5", date(2026, 9, 28))
    api("OPERACAO").post({"produto": presunto.pk, "quantidade": "1", "motivo": "  Venceu  "})
    assert Movimentacao.objects.get(tipo="PERDA").motivo == "Venceu"


# --- RN01: saldo e lote --------------------------------------------------------------------------


def test_rn01_perda_reduz_o_saldo_e_o_lote(api, presunto):
    lote = _lote(presunto, "5", date(2026, 9, 28))
    corpo = api("OPERACAO").post({"produto": presunto.pk, "quantidade": "2", "motivo": "Estragou"}).json()
    lote.refresh_from_db()
    assert lote.quantidade_atual == Decimal("3")
    assert saldo_do_produto(presunto) == Decimal("3")
    assert corpo["saldo_produto"] == "3.000"


def test_rn11_perda_entra_como_perda_e_nao_como_venda(api, presunto):
    # RN11: a perda reduz o estoque, mas fica registrada como PERDA — a base de consumo (D2/G1)
    # considera só VENDA.
    _lote(presunto, "5", date(2026, 9, 28))
    api("OPERACAO").post({"produto": presunto.pk, "quantidade": "2", "motivo": "Estragou"})
    assert not Movimentacao.objects.filter(tipo="VENDA").exists()
    assert Movimentacao.objects.filter(tipo="PERDA").count() == 1


# --- L20: de qual lote sai -----------------------------------------------------------------------


def test_l20_perda_sai_do_lote_informado(api, presunto):
    mais_velho = _lote(presunto, "5", date(2026, 9, 28))
    o_que_estragou = _lote(presunto, "5", date(2026, 10, 5))
    api("OPERACAO").post(
        {"produto": presunto.pk, "lote": o_que_estragou.pk, "quantidade": "2", "motivo": "Mofou"}
    )
    mais_velho.refresh_from_db()
    o_que_estragou.refresh_from_db()
    assert (mais_velho.quantidade_atual, o_que_estragou.quantidade_atual) == (Decimal("5"), Decimal("3"))


def test_l20_sem_lote_sai_pela_ordem_de_validade(api, presunto):
    # RN02: dois lotes de presunto, um vence 28/09 e outro 05/10 → sai do de 28/09.
    vence_05_10 = _lote(presunto, "5", date(2026, 10, 5))
    vence_28_09 = _lote(presunto, "5", date(2026, 9, 28))
    api("OPERACAO").post({"produto": presunto.pk, "quantidade": "2", "motivo": "Estragou"})
    vence_28_09.refresh_from_db()
    vence_05_10.refresh_from_db()
    assert (vence_28_09.quantidade_atual, vence_05_10.quantidade_atual) == (Decimal("3"), Decimal("5"))


def test_l20_perda_maior_que_um_lote_continua_no_proximo_com_uma_linha_por_lote(api, presunto):
    primeiro = _lote(presunto, "2", date(2026, 9, 28))
    segundo = _lote(presunto, "5", date(2026, 10, 5))
    api("OPERACAO").post({"produto": presunto.pk, "quantidade": "3.5", "motivo": "Freezer desligou"})
    perdas = list(
        Movimentacao.objects.filter(tipo="PERDA").order_by("id").values_list("lote_id", "quantidade")
    )
    # RN01: cada linha explica uma mudança — uma por lote afetado.
    assert perdas == [(primeiro.pk, Decimal("2")), (segundo.pk, Decimal("1.5"))]
    assert saldo_do_produto(presunto) == Decimal("3.5")


def test_l20_lote_de_outro_produto_e_recusado(api, presunto, iogurte):
    lote_de_iogurte = _lote(iogurte, "10", date(2026, 10, 1))
    _lote(presunto, "5", date(2026, 9, 28))
    resposta = api("OPERACAO").post(
        {"produto": presunto.pk, "lote": lote_de_iogurte.pk, "quantidade": "1", "motivo": "Estragou"}
    )
    assert resposta.status_code == 400
    assert "lote" in resposta.json()["erro"]["campos"]
    assert not Movimentacao.objects.filter(tipo="PERDA").exists()


# --- Não dá para perder o que não existe ---------------------------------------------------------


def test_d1_perda_maior_que_o_lote_informado_e_recusada(api, presunto):
    lote = _lote(presunto, "2", date(2026, 9, 28))
    _lote(presunto, "5", date(2026, 10, 5))
    resposta = api("OPERACAO").post(
        {"produto": presunto.pk, "lote": lote.pk, "quantidade": "3", "motivo": "Estragou"}
    )
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"]["quantidade"] == ["Esse lote só tem 2,000 KG."]
    lote.refresh_from_db()
    assert lote.quantidade_atual == Decimal("2")


def test_d1_perda_maior_que_o_estoque_e_recusada_e_nada_muda(api, presunto):
    lote = _lote(presunto, "2", date(2026, 9, 28))
    resposta = api("OPERACAO").post({"produto": presunto.pk, "quantidade": "2.5", "motivo": "Estragou"})
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"]["quantidade"] == ["Só há 2,000 KG de Presunto no estoque."]
    lote.refresh_from_db()
    assert lote.quantidade_atual == Decimal("2")
    assert not Movimentacao.objects.filter(tipo="PERDA").exists()


def test_d1_perda_de_tudo_zera_o_lote(api, presunto):
    lote = _lote(presunto, "2", date(2026, 9, 28))
    assert (
        api("OPERACAO").post({"produto": presunto.pk, "quantidade": "2", "motivo": "Venceu"}).status_code
        == 201
    )
    lote.refresh_from_db()
    assert lote.quantidade_atual == Decimal("0")


@pytest.mark.parametrize("quantidade", ["0", "-1"])
def test_d1_quantidade_zero_ou_negativa_e_recusada(api, presunto, quantidade):
    _lote(presunto, "5", date(2026, 9, 28))
    resposta = api("OPERACAO").post({"produto": presunto.pk, "quantidade": quantidade, "motivo": "Estragou"})
    assert resposta.status_code == 400
    assert "quantidade" in resposta.json()["erro"]["campos"]


def test_d1_produto_e_quantidade_sao_obrigatorios(api, db):
    resposta = api("OPERACAO").post({"motivo": "Estragou"})
    assert resposta.status_code == 400
    assert set(resposta.json()["erro"]["campos"]) == {"produto", "quantidade"}


# --- RN16: lote vencido sai por perda ------------------------------------------------------------


def test_rn16_lote_vencido_sai_pela_tela_de_avarias(api, iogurte):
    # Apostila I: "lote de iogurte vencido em 20/09 ... sai pela tela de avarias com motivo" (hoje 21/09).
    vencido = _lote(iogurte, "6", date(2026, 9, 20))
    resposta = api("OPERACAO").post(
        {"produto": iogurte.pk, "lote": vencido.pk, "quantidade": "6", "motivo": "Venceu"}
    )
    assert resposta.status_code == 201
    vencido.refresh_from_db()
    assert vencido.quantidade_atual == Decimal("0")


def test_rn16_sem_lote_a_perda_comeca_pelo_vencido(api, iogurte):
    bom = _lote(iogurte, "10", date(2026, 10, 1))
    vencido = _lote(iogurte, "6", date(2026, 9, 20))
    api("OPERACAO").post({"produto": iogurte.pk, "quantidade": "6", "motivo": "Venceu"})
    vencido.refresh_from_db()
    bom.refresh_from_db()
    assert (vencido.quantidade_atual, bom.quantidade_atual) == (Decimal("0"), Decimal("10"))


# --- L13: desempate do FIFO -----------------------------------------------------------------------


def test_l13_mesma_validade_sai_primeiro_o_que_entrou_antes(presunto):
    depois = _lote(presunto, "1", date(2026, 9, 28), entrada=date(2026, 9, 15))
    antes = _lote(presunto, "1", date(2026, 9, 28), entrada=date(2026, 9, 12))
    assert list(lotes_em_ordem_de_validade(presunto, hoje=HOJE, incluir_vencidos=True)) == [antes, depois]


def test_l13_lote_sem_validade_sai_por_ultimo(db):
    secos = Categoria.objects.create(nome="Secos e molhados")
    arroz = Produto.objects.create(categoria=secos, nome="Arroz 5 kg", unidade_medida="PCT")
    sem_validade = _lote(arroz, "5", None)
    com_validade = _lote(arroz, "5", date(2027, 3, 1))
    assert list(lotes_em_ordem_de_validade(arroz, hoje=HOJE, incluir_vencidos=True)) == [
        com_validade,
        sem_validade,
    ]


def test_rn16_ordem_de_venda_deixa_os_vencidos_de_fora(iogurte):
    _lote(iogurte, "6", date(2026, 9, 20))
    bom = _lote(iogurte, "10", date(2026, 10, 1))
    vence_hoje = _lote(iogurte, "2", HOJE)  # vence hoje ainda pode ser vendido
    assert list(lotes_em_ordem_de_validade(iogurte, hoje=HOJE, incluir_vencidos=False)) == [vence_hoje, bom]


def test_l13_lote_zerado_fica_de_fora(presunto):
    zerado = _lote(presunto, "1", date(2026, 9, 25))
    zerado.quantidade_atual = Decimal("0")
    zerado.save()
    assert zerado not in lotes_em_ordem_de_validade(presunto, hoje=HOJE, incluir_vencidos=True)


# --- O serviço, sem a API ------------------------------------------------------------------------


def test_d1_servico_recusa_quantidade_maior_que_o_estoque(presunto):
    _lote(presunto, "1", date(2026, 9, 28))
    with pytest.raises(ErroDeRegraDeNegocio):
        registrar_perda(produto=presunto, quantidade=Decimal("2"), motivo="Estragou", usuario=None)


def test_d1_servico_tudo_ou_nada(presunto):
    # Se a gravação falhar no meio (segundo lote), nada do que foi feito no primeiro fica.
    primeiro = _lote(presunto, "1", date(2026, 9, 28))
    _lote(presunto, "5", date(2026, 10, 5))
    criar = Movimentacao.objects.create
    chamadas = []

    def falha_na_segunda(**campos):
        chamadas.append(campos)
        if len(chamadas) == 2:
            raise RuntimeError("falha simulada")
        return criar(**campos)

    with (
        mock.patch.object(Movimentacao.objects, "create", side_effect=falha_na_segunda),
        pytest.raises(RuntimeError),
    ):
        registrar_perda(produto=presunto, quantidade=Decimal("3"), motivo="Freezer", usuario=None)
    primeiro.refresh_from_db()
    assert primeiro.quantidade_atual == Decimal("1")
    assert not Movimentacao.objects.filter(tipo="PERDA").exists()


# --- Lista das perdas (o caderno de avarias) ------------------------------------------------------


def test_d1_lista_as_perdas_mais_recentes_primeiro(api, presunto, iogurte):
    _lote(presunto, "5", date(2026, 9, 28))
    _lote(iogurte, "5", date(2026, 10, 1))
    api("OPERACAO").post({"produto": presunto.pk, "quantidade": "1", "motivo": "Caiu"})
    api("OPERACAO").post({"produto": iogurte.pk, "quantidade": "2", "motivo": "Estufou"})
    lista = api("OPERACAO").get().json()
    assert [(p["produto_nome"], p["motivo"], p["quantidade"]) for p in lista] == [
        ("Iogurte natural", "Estufou", "2.000"),
        ("Presunto", "Caiu", "1.000"),
    ]


def test_d1_lista_mostra_so_perdas(api, presunto):
    _lote(presunto, "5", date(2026, 9, 28))  # uma ENTRADA
    assert api("OPERACAO").get().json() == []


def test_d1_lista_filtra_por_dia_e_produto(api, presunto, iogurte):
    _lote(presunto, "5", date(2026, 9, 28))
    _lote(iogurte, "5", date(2026, 10, 1))
    api("OPERACAO").post({"produto": presunto.pk, "quantidade": "1", "motivo": "Caiu"})
    api("OPERACAO").post({"produto": iogurte.pk, "quantidade": "2", "motivo": "Estufou"})
    assert len(api("OPERACAO").get(f"{URL}?data=2026-09-21").json()) == 2
    assert api("OPERACAO").get(f"{URL}?data=2026-09-20").json() == []
    assert [p["produto_nome"] for p in api("OPERACAO").get(f"{URL}?produto={iogurte.pk}").json()] == [
        "Iogurte natural"
    ]


def test_d1_perda_registrada_nao_se_apaga(api, presunto):
    _lote(presunto, "5", date(2026, 9, 28))
    perda_id = (
        api("OPERACAO")
        .post({"produto": presunto.pk, "quantidade": "1", "motivo": "Caiu"})
        .json()["perdas"][0]["id"]
    )
    assert api("OPERACAO").delete(f"{URL}{perda_id}/").status_code == 405
    assert Movimentacao.objects.filter(pk=perda_id).exists()


# --- RN14 ----------------------------------------------------------------------------------------


@pytest.mark.parametrize("papel", ["DONO", "GESTAO"])
def test_rn14_so_operacao_registra_perda(api, presunto, papel):
    _lote(presunto, "5", date(2026, 9, 28))
    assert api(papel).post({"produto": presunto.pk, "quantidade": "1", "motivo": "Caiu"}).status_code == 403
    assert api(papel).get().status_code == 403
    assert not Movimentacao.objects.filter(tipo="PERDA").exists()

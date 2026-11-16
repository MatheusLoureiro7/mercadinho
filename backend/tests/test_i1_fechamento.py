"""
Tarefa I1 — tabela de fechamento de caixa e cálculo da diferença. RN15, RF12, fluxograma 06.

"A diferença de caixa é o valor contado menos o valor apurado pelo sistema. Ela é registrada com
data e responsável. Correções geram um novo registro; o anterior nunca é apagado." (RN15)

Decisões do grupo em 05/11/2026 (lacuna L12):
- o valor apurado é a soma das vendas do dia pagas em DINHEIRO — a gaveta só tem dinheiro;
- o fechamento é do DIA ANTERIOR: as vendas só entram às 03h00 do dia seguinte (E3), então a
  esposa conta à noite e registra na manhã seguinte. Se as vendas daquele dia não entraram, o
  fechamento é recusado.

Losangos do fluxograma 06, pelo "sim" e pelo "não":
    vendas do dia já importadas?   sim → *_registra_*              não → *_vendas_nao_importadas_*
    caixa bateu?                   sim → *_caixa_bateu_*            não → *_rn15_exemplo_da_apostila_*
"""

import re
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.db import DatabaseError, connection, transaction
from playwright.sync_api import expect

from cadastro.models import Usuario
from caixa.fechamento import dia_do_fechamento, registrar_fechamento, valor_apurado
from caixa.models import FechamentoCaixa
from comum.autenticacao import gerar_token
from comum.erros import ErroDeRegraDeNegocio
from tests.conftest import abrir_tela, divergencias_do_schema
from vendas.models import ImportacaoPdv, Venda

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
ONTEM = date(2026, 11, 4)
MANHA_DE_HOJE = datetime(2026, 11, 5, 8, 0, tzinfo=SAO_PAULO)
URL = "/api/fechamentos/"
SENHA = "Mercado#2026"


@pytest.fixture(autouse=True)
def manha_de_05_11():
    with patch("django.utils.timezone.now", return_value=MANHA_DE_HOJE):
        yield


@pytest.fixture
def esposa(db):
    return Usuario.objects.create_user(login="esposa", senha=SENHA, nome="Dona Maria", papel="GESTAO")


def _importado(dia=ONTEM, status="OK"):
    return ImportacaoPdv.objects.create(arquivo_nome=f"vendas-{dia}.xlsx", data_referencia=dia, status=status)


def _venda(valor, pagamento="Dinheiro", quando=datetime(2026, 11, 4, 10, 0, tzinfo=SAO_PAULO)):
    return Venda.objects.create(data_hora=quando, valor_total=Decimal(valor), forma_pagamento=pagamento)


@pytest.fixture
def dia_de_3240(db):
    """O exemplo da RN15: o sistema apura R$ 3.240,00."""
    _importado()
    _venda("3000.00")
    _venda("240.00")
    return ONTEM


# --- O banco confere com a Apostila IV ------------------------------------------------------------


@pytest.mark.django_db
def test_i1_tabela_igual_ao_schema():
    assert divergencias_do_schema("fechamento_caixa") == []


@pytest.mark.django_db
def test_rn15_diferenca_e_coluna_gerada_pelo_banco():
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT attgenerated FROM pg_attribute WHERE attrelid = 'fechamento_caixa'::regclass "
            "AND attname = 'diferenca'"
        )
        assert cursor.fetchone() == ("s",)  # GENERATED ALWAYS AS (...) STORED


def test_rn15_banco_calcula_a_diferenca_mesmo_fora_do_sistema(esposa):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO fechamento_caixa (data, valor_sistema, valor_contado) "
            "VALUES ('2026-11-04', 3240, 3215) RETURNING diferenca"
        )
        assert cursor.fetchone() == (Decimal("-25.00"),)


def test_rn15_banco_nao_deixa_alterar_o_fechamento(dia_de_3240, esposa):
    fechamento = registrar_fechamento(valor_contado=Decimal("3215.00"), usuario=esposa)
    with pytest.raises(DatabaseError), transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("UPDATE fechamento_caixa SET valor_contado = 3240 WHERE id = %s", [fechamento.pk])


def test_rn15_banco_nao_deixa_apagar_o_fechamento(dia_de_3240, esposa):
    fechamento = registrar_fechamento(valor_contado=Decimal("3215.00"), usuario=esposa)
    with pytest.raises(DatabaseError), transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("DELETE FROM fechamento_caixa WHERE id = %s", [fechamento.pk])
    assert FechamentoCaixa.objects.filter(pk=fechamento.pk).exists()


# --- RN15 -----------------------------------------------------------------------------------------


def test_rn15_exemplo_da_apostila_apura_3240_conta_3215_registra_menos_25(dia_de_3240, esposa):
    fechamento = registrar_fechamento(valor_contado=Decimal("3215.00"), usuario=esposa)
    fechamento.refresh_from_db()
    assert (fechamento.valor_sistema, fechamento.valor_contado) == (Decimal("3240.00"), Decimal("3215.00"))
    assert fechamento.diferenca == Decimal("-25.00")
    assert fechamento.data == ONTEM
    assert fechamento.registrado_por == esposa  # "com data e responsável"
    assert fechamento.registrado_em is not None


def test_rn15_caixa_bateu_diferenca_zero(dia_de_3240, esposa):
    fechamento = registrar_fechamento(valor_contado=Decimal("3240.00"), usuario=esposa)
    fechamento.refresh_from_db()
    assert fechamento.diferenca == Decimal("0.00")


def test_rn15_sobra_no_caixa_e_diferenca_positiva(dia_de_3240, esposa):
    fechamento = registrar_fechamento(valor_contado=Decimal("3250.50"), usuario=esposa)
    fechamento.refresh_from_db()
    assert fechamento.diferenca == Decimal("10.50")


def test_rn15_contar_de_novo_gera_registro_novo_e_o_anterior_fica(dia_de_3240, esposa):
    primeiro = registrar_fechamento(valor_contado=Decimal("3215.00"), usuario=esposa)
    segundo = registrar_fechamento(valor_contado=Decimal("3240.00"), usuario=esposa)
    assert FechamentoCaixa.objects.count() == 2
    primeiro.refresh_from_db()
    assert primeiro.valor_contado == Decimal("3215.00") and segundo.pk != primeiro.pk


# --- O valor apurado (L12) ------------------------------------------------------------------------


def test_l12_apurado_soma_so_as_vendas_em_dinheiro(db):
    _venda("100.00", "Dinheiro")
    _venda("50.00", "  DINHEIRO ")
    _venda("70.00", "PIX")
    _venda("30.00", "Cartão de débito")
    assert valor_apurado(ONTEM) == Decimal("150.00")


def test_l12_apurado_e_so_do_dia_no_horario_da_loja(db):
    _venda("100.00", quando=datetime(2026, 11, 4, 22, 30, tzinfo=SAO_PAULO))  # em UTC já é dia 5
    _venda("40.00", quando=datetime(2026, 11, 3, 23, 50, tzinfo=SAO_PAULO))
    _venda("60.00", quando=datetime(2026, 11, 5, 0, 10, tzinfo=SAO_PAULO))
    assert valor_apurado(ONTEM) == Decimal("100.00")


@pytest.mark.parametrize("pagamento", ["Espécie", "especie", " Em  ESPÉCIE ", "dinheiro"])
def test_x1_especie_tambem_conta_como_dinheiro(db, pagamento):
    """X1, item 7 (decisão do grupo, 16/11/2026): "dinheiro", "espécie" e "em espécie"."""
    _venda("80.00", pagamento)
    assert valor_apurado(ONTEM) == Decimal("80.00")


@pytest.mark.parametrize("pagamento", ["Cartão + dinheiro", "Dinheiro/troco", "PIX"])
def test_x1_texto_que_so_contem_a_palavra_nao_conta_como_dinheiro(db, pagamento):
    _venda("80.00", pagamento)
    assert valor_apurado(ONTEM) == Decimal("0.00")


@pytest.mark.parametrize("pagamento", [None, "", "   "])
def test_x1_venda_sem_forma_de_pagamento_recusa_o_fechamento_do_dia(esposa, pagamento):
    """X1, item 7: sem a forma de pagamento, o apurado sairia menor e a sobra seria falsa (RN15)."""
    _importado()
    _venda("100.00", "Dinheiro")
    _venda("20.00", pagamento)
    with pytest.raises(ErroDeRegraDeNegocio, match="1 venda de 04/11/2026 veio sem a forma de pagamento"):
        registrar_fechamento(valor_contado=Decimal("120.00"), usuario=esposa)
    assert not FechamentoCaixa.objects.exists()


def test_l12_dia_sem_venda_em_dinheiro_apura_zero(db):
    _venda("70.00", "PIX")
    assert valor_apurado(ONTEM) == Decimal("0.00")


@pytest.mark.parametrize(
    "agora, dia",
    [
        (datetime(2026, 11, 5, 0, 30, tzinfo=SAO_PAULO), date(2026, 11, 4)),
        (datetime(2026, 11, 5, 23, 59, tzinfo=SAO_PAULO), date(2026, 11, 4)),  # em UTC já é dia 6
    ],
)
def test_l12_fechamento_e_do_dia_anterior_no_horario_da_loja(agora, dia):
    with patch("django.utils.timezone.now", return_value=agora):
        assert dia_do_fechamento() == dia


def test_l12_vendas_nao_importadas_recusa_e_nada_e_gravado(esposa):
    with pytest.raises(ErroDeRegraDeNegocio, match="04/11/2026"):
        registrar_fechamento(valor_contado=Decimal("10.00"), usuario=esposa)
    assert not FechamentoCaixa.objects.exists()


def test_l12_importacao_com_erro_nao_conta_como_importada(esposa):
    _importado(status="ERRO")
    with pytest.raises(ErroDeRegraDeNegocio):
        registrar_fechamento(valor_contado=Decimal("10.00"), usuario=esposa)


def test_l12_importacao_parcial_conta_como_importada(esposa):
    _importado(status="PARCIAL")
    _venda("10.00")
    assert registrar_fechamento(valor_contado=Decimal("10.00"), usuario=esposa).valor_sistema == Decimal(
        "10.00"
    )


# --- API ------------------------------------------------------------------------------------------


@pytest.fixture
def api(client, esposa):
    def chamar(metodo, url=URL, dados=None, usuario=esposa):
        cabecalho = {"HTTP_AUTHORIZATION": f"Bearer {gerar_token(usuario)}"} if usuario else {}
        return getattr(client, metodo)(url, dados, content_type="application/json", **cabecalho)

    return chamar


def test_i1_api_apurado_traz_o_dia_e_o_valor(api, dia_de_3240):
    resposta = api("get", URL + "apurado/")
    assert resposta.status_code == 200
    assert resposta.json() == {"data": "2026-11-04", "valor_sistema": "3240.00"}


def test_i1_api_apurado_sem_vendas_importadas_explica_o_motivo(api, esposa):
    resposta = api("get", URL + "apurado/")
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["regra"] == "RN15"
    assert "04/11/2026" in resposta.json()["erro"]["mensagem"]


def test_i1_api_registra_e_devolve_o_registro(api, dia_de_3240):
    resposta = api("post", dados={"valor_contado": "3215.00"})
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert {k: corpo[k] for k in ("data", "valor_sistema", "valor_contado", "diferenca")} == {
        "data": "2026-11-04",
        "valor_sistema": "3240.00",
        "valor_contado": "3215.00",
        "diferenca": "-25.00",
    }
    assert corpo["registrado_por_nome"] == "Dona Maria" and corpo["registrado_em"]


def test_rn15_api_ignora_apurado_e_diferenca_mandados_pela_tela(api, dia_de_3240):
    dados = {"valor_contado": "3215.00", "valor_sistema": "3215.00", "diferenca": "0"}
    corpo = api("post", dados=dados).json()
    assert (corpo["valor_sistema"], corpo["diferenca"], corpo["data"]) == ("3240.00", "-25.00", "2026-11-04")


# X1, item 6 (decisão do grupo, 16/11/2026): a esposa escolhe o dia do caixa — ontem, se não disser
# nada; qualquer dia anterior cujas vendas já entraram; nunca hoje nem o futuro.


@pytest.fixture
def sabado_esquecido(db):
    _importado(dia=date(2026, 10, 31))
    _venda("50.00", quando=datetime(2026, 10, 31, 9, 0, tzinfo=SAO_PAULO))
    return date(2026, 10, 31)


def test_x1_api_apurado_de_um_dia_anterior_escolhido(api, sabado_esquecido):
    resposta = api("get", URL + "apurado/?data=2026-10-31")
    assert resposta.json() == {"data": "2026-10-31", "valor_sistema": "50.00"}


def test_x1_api_fecha_um_dia_anterior_escolhido(api, sabado_esquecido):
    corpo = api("post", dados={"valor_contado": "60.00", "data": "2026-10-31"}).json()
    assert (corpo["data"], corpo["valor_sistema"], corpo["diferenca"]) == ("2026-10-31", "50.00", "10.00")


@pytest.mark.parametrize("dia", ["2026-11-05", "2026-11-06"])
def test_x1_api_caixa_de_hoje_ou_do_futuro_e_recusado(api, dia):
    _importado(dia=date.fromisoformat(dia))
    resposta = api("post", dados={"valor_contado": "60.00", "data": dia})
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["regra"] == "RN15"
    assert "depois que as vendas do dia entrarem" in resposta.json()["erro"]["mensagem"]
    assert api("get", URL + f"apurado/?data={dia}").status_code == 400
    assert not FechamentoCaixa.objects.exists()


def test_x1_api_dia_escolhido_sem_vendas_importadas_diz_qual_dia(api, esposa):
    resposta = api("get", URL + "apurado/?data=2026-10-30")
    assert resposta.status_code == 400 and "30/10/2026" in resposta.json()["erro"]["mensagem"]


def test_x1_api_dia_do_caixa_em_formato_errado_aponta_o_campo(api, sabado_esquecido):
    assert "data" in api("get", URL + "apurado/?data=31/10/2026").json()["erro"]["campos"]
    resposta = api("post", dados={"valor_contado": "60.00", "data": "31/10/2026"})
    assert resposta.status_code == 400 and "data" in resposta.json()["erro"]["campos"]


@pytest.mark.parametrize(
    "valor, mensagem",
    [
        (None, "obrigatório"),
        ("-1.00", "negativo"),
        ("10.123", "centavos"),
        ("dez", "número"),
    ],
)
def test_i1_api_dinheiro_contado_invalido_e_recusado_no_campo(api, dia_de_3240, valor, mensagem):
    dados = {} if valor is None else {"valor_contado": valor}
    resposta = api("post", dados=dados)
    assert resposta.status_code == 400
    assert mensagem in " ".join(resposta.json()["erro"]["campos"]["valor_contado"])
    assert not FechamentoCaixa.objects.exists()


def test_i1_api_lista_do_dia_mais_novo_primeiro(api, dia_de_3240):
    api("post", dados={"valor_contado": "3215.00"})
    api("post", dados={"valor_contado": "3240.00"})
    resposta = api("get", URL + "?data=2026-11-04")
    assert [r["valor_contado"] for r in resposta.json()] == ["3240.00", "3215.00"]
    assert api("get", URL + "?data=2026-11-03").json() == []


def test_i1_api_lista_com_data_invalida_aponta_o_campo(api):
    resposta = api("get", URL + "?data=04/11/2026")
    assert resposta.status_code == 400 and "data" in resposta.json()["erro"]["campos"]


@pytest.mark.parametrize("metodo", ["put", "patch", "delete"])
def test_rn15_api_nao_altera_nem_apaga(api, dia_de_3240, metodo):
    fechamento = registrar_fechamento(valor_contado=Decimal("3215.00"), usuario=Usuario.objects.get())
    resposta = api(metodo, f"{URL}{fechamento.pk}/", {"valor_contado": "3240.00"})
    assert resposta.status_code in (404, 405)
    fechamento.refresh_from_db()
    assert fechamento.valor_contado == Decimal("3215.00")


@pytest.mark.parametrize("papel", ["DONO", "OPERACAO"])
def test_rn14_so_a_esposa_registra_o_fechamento(api, dia_de_3240, papel):
    outro = Usuario.objects.create_user(login=papel.lower(), senha=SENHA, nome=papel, papel=papel)
    assert api("post", dados={"valor_contado": "3215.00"}, usuario=outro).status_code == 403
    assert api("get", URL + "apurado/", usuario=outro).status_code == 403
    assert not FechamentoCaixa.objects.exists()


def test_rn14_fechamento_sem_login_e_recusado(api, dia_de_3240):
    assert api("post", dados={"valor_contado": "3215.00"}, usuario=None).status_code == 401


# --- Pela tela, de ponta a ponta ------------------------------------------------------------------


@pytest.fixture
def esposa_na_tela(painel):
    return Usuario.objects.create_user(login="esposa", senha=SENHA, nome="Dona Maria", papel="GESTAO")


@pytest.mark.tela
def test_i1_pela_tela_a_esposa_fecha_o_caixa_de_ontem(page, painel, esposa_na_tela):
    _importado(dia=date(2026, 11, 4))
    _venda("3240.00")
    with patch("django.utils.timezone.now", return_value=MANHA_DE_HOJE):
        page.clock.set_fixed_time(MANHA_DE_HOJE)
        abrir_tela(page, painel, esposa_na_tela, "fechamento-caixa.html")
        expect(page.locator("#titulo-formulario")).to_contain_text("04/11/2026")
        expect(page.locator("#valor-apurado")).to_have_text("R$ 3.240,00")
        page.fill("#campo-contado", "3.215,00")
        page.click("#botao-salvar")
        expect(page.locator("#sucesso")).to_contain_text("Faltam R$ 25,00 no caixa.")
        expect(page.locator("#corpo-tabela")).to_contain_text("Dona Maria")
    assert FechamentoCaixa.objects.get().diferenca == Decimal("-25.00")


@pytest.mark.tela
def test_i1_pela_tela_vendas_nao_importadas_avisa_e_trava(page, painel, esposa_na_tela):
    with patch("django.utils.timezone.now", return_value=MANHA_DE_HOJE):
        page.clock.set_fixed_time(MANHA_DE_HOJE)
        abrir_tela(page, painel, esposa_na_tela, "fechamento-caixa.html")
        expect(page.locator("#indisponivel")).to_contain_text(re.compile(r"vendas de 04/11/2026"))
        expect(page.locator("#botao-salvar")).to_be_disabled()


@pytest.mark.tela
def test_x1_pela_tela_a_esposa_fecha_o_caixa_de_um_dia_que_ficou_para_tras(page, painel, esposa_na_tela):
    """X1, item 6: o sábado 31/10 fechado na quinta 05/11; ontem (04/11) não teve vendas importadas."""
    _importado(dia=date(2026, 10, 31))
    _venda("50.00", quando=datetime(2026, 10, 31, 9, 0, tzinfo=SAO_PAULO))
    with patch("django.utils.timezone.now", return_value=MANHA_DE_HOJE):
        page.clock.set_fixed_time(MANHA_DE_HOJE)
        abrir_tela(page, painel, esposa_na_tela, "fechamento-caixa.html")
        expect(page.locator("#campo-dia")).to_have_value("2026-11-04")
        expect(page.locator("#indisponivel")).to_contain_text("vendas de 04/11/2026")
        expect(page.locator("#botao-salvar")).to_be_disabled()

        page.fill("#campo-dia", "2026-10-31")
        expect(page.locator("#valor-apurado")).to_have_text("R$ 50,00")
        expect(page.locator("#titulo-formulario")).to_contain_text("31/10/2026")
        expect(page.locator("#indisponivel")).to_be_hidden()
        page.fill("#campo-contado", "50,00")
        page.click("#botao-salvar")
        expect(page.locator("#sucesso")).to_contain_text("O caixa bateu.")
        expect(page.locator("#corpo-tabela")).to_contain_text("Dona Maria")
    assert FechamentoCaixa.objects.get().data == date(2026, 10, 31)

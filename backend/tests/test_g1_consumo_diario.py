"""
Tarefa G1 — tabela de consumo diário e rotina de agregação. Operação 03, passos 2 e 3: "motor de
previsão lê as vendas do dia anterior · grava consumo_diario · RN11: PERDA fica de fora da soma".

- A tabela `consumo_diario` igual ao schema.sql: chave (produto_id, data), dia_semana de 0 a 6.
- Dia da semana (lacuna L27, adotado na G1): 0 = domingo … 6 = sábado, como o EXTRACT(DOW) do
  PostgreSQL — o banco que a Apostila IV fixa, e a única numeração que cabe no CHECK 0 a 6 sem
  conversão.
- Só dia com venda vira linha (como `previsao.consumo.vendido_por_dia`, D2): RN06 divide sempre
  por 30, então o dia sem linha conta como zero; e RN09 conta os dias de histórico por
  COUNT(DISTINCT data).
- Dado derivado pode ser apagado e recalculado (Apostila IV, seção 3): a rotina regrava o período
  inteiro, então rodar duas vezes não duplica, e a venda casada depois (E4) entra na rodada
  seguinte. A rodada diária regrava os últimos 30 dias até ONTEM — hoje ainda não foi importado.

Losangos, pelo "sim" e pelo "não":
    movimentação é VENDA?        sim → soma                     não → *_rn11_*, *_entrada_e_ajuste_*
    o dia teve venda?            sim → linha                    não → *_dia_sem_venda_*
    já havia linha no período?   sim → *_rodar_de_novo_*        não → *_soma_as_vendas_*
    dia dentro da janela?        sim → regrava                  não → *_fora_da_janela_*
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from io import StringIO
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.core.management import call_command
from django.db import IntegrityError, transaction

from cadastro.models import Categoria, Produto
from estoque.models import Movimentacao
from previsao.agregacao import agregar_consumo, agregar_consumo_recente
from previsao.models import ConsumoDiario
from tests.conftest import divergencias_do_schema, restricoes

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
HOJE = date(2026, 11, 12)  # quinta-feira
ONTEM = HOJE - timedelta(days=1)
MADRUGADA = datetime(2026, 11, 12, 3, 0, tzinfo=SAO_PAULO)


@pytest.fixture(autouse=True)
def madrugada_de_12_11():
    with patch("django.utils.timezone.now", return_value=MADRUGADA):
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


@pytest.fixture
def arroz(db):
    secos = Categoria.objects.create(nome="Secos e molhados")
    return Produto.objects.create(categoria=secos, nome="Arroz 5 kg", unidade_medida="PCT")


def _mov(produto, quantidade, dia, hora=10, minuto=0, tipo="VENDA"):
    return Movimentacao.objects.create(
        produto=produto,
        tipo=tipo,
        quantidade=Decimal(quantidade),
        data_hora=datetime(dia.year, dia.month, dia.day, hora, minuto, tzinfo=SAO_PAULO),
        motivo="Estragou" if tipo == "PERDA" else None,
    )


def _consumo(produto):
    return {
        (linha.data, linha.quantidade_vendida, linha.dia_semana)
        for linha in ConsumoDiario.objects.filter(produto=produto)
    }


# --- Tabela ---------------------------------------------------------------------------------------


@pytest.mark.django_db
def test_g1_tabela_consumo_diario_igual_ao_schema():
    assert divergencias_do_schema("consumo_diario") == []
    assert "ck_consumo_dia" in restricoes("consumo_diario")


def test_g1_chave_e_produto_e_data(frango):
    ConsumoDiario.objects.create(produto=frango, data=ONTEM, quantidade_vendida=1, dia_semana=3)
    with pytest.raises(IntegrityError), transaction.atomic():
        ConsumoDiario.objects.create(produto=frango, data=ONTEM, quantidade_vendida=2, dia_semana=3)


def test_g1_dia_semana_fora_de_0_a_6_e_recusado_pelo_banco(frango):
    with pytest.raises(IntegrityError), transaction.atomic():
        ConsumoDiario.objects.create(produto=frango, data=ONTEM, quantidade_vendida=1, dia_semana=7)


# --- Agregação ------------------------------------------------------------------------------------


def test_g1_soma_as_vendas_do_dia_por_produto(frango, arroz):
    _mov(frango, "1.275", ONTEM, 8)
    _mov(frango, "2", ONTEM, 17)
    _mov(arroz, "3", ONTEM, 9)
    assert agregar_consumo(ONTEM, ONTEM) == 2
    assert _consumo(frango) == {(ONTEM, Decimal("3.275"), 3)}
    assert _consumo(arroz) == {(ONTEM, Decimal("3.000"), 3)}


def test_rn11_perda_nao_entra_no_consumo_diario(frango):
    # O exemplo da RN11: 10 kg de frango vão fora; o consumo do dia continua sendo só o vendido.
    _mov(frango, "3", ONTEM)
    _mov(frango, "10", ONTEM, tipo="PERDA")
    agregar_consumo(ONTEM, ONTEM)
    assert _consumo(frango) == {(ONTEM, Decimal("3.000"), 3)}


def test_g1_entrada_e_ajuste_nao_entram_no_consumo(frango):
    _mov(frango, "20", ONTEM, tipo="ENTRADA")
    _mov(frango, "1", ONTEM, tipo="AJUSTE")
    assert agregar_consumo(ONTEM, ONTEM) == 0
    assert _consumo(frango) == set()


def test_g1_dia_sem_venda_nao_gera_linha(frango):
    _mov(frango, "2", ONTEM - timedelta(days=2))
    agregar_consumo(ONTEM - timedelta(days=2), ONTEM)
    assert {data for data, _, _ in _consumo(frango)} == {ONTEM - timedelta(days=2)}


def test_g1_venda_das_22h30_conta_no_dia_da_loja_e_nao_no_dia_do_utc(frango):
    # 22h30 em São Paulo já é o dia seguinte em UTC.
    _mov(frango, "2", ONTEM, 22, 30)
    agregar_consumo(ONTEM, HOJE)
    assert _consumo(frango) == {(ONTEM, Decimal("2.000"), 3)}


@pytest.mark.parametrize(
    "dia, dia_semana",
    [
        (date(2026, 11, 8), 0),  # domingo
        (date(2026, 11, 9), 1),  # segunda
        (date(2026, 11, 11), 3),  # quarta
        (date(2026, 11, 14), 6),  # sábado
    ],
)
def test_g1_dia_semana_domingo_e_zero_e_sabado_e_seis(frango, dia, dia_semana):
    _mov(frango, "1", dia)
    agregar_consumo(dia, dia)
    assert ConsumoDiario.objects.get(produto=frango, data=dia).dia_semana == dia_semana


def test_g1_rodar_de_novo_nao_duplica_e_pega_a_venda_casada_depois(frango):
    _mov(frango, "2", ONTEM)
    agregar_consumo(ONTEM, ONTEM)
    agregar_consumo(ONTEM, ONTEM)
    assert _consumo(frango) == {(ONTEM, Decimal("2.000"), 3)}

    _mov(frango, "1.5", ONTEM, 15)  # venda pendente casada pelo sobrinho (E4)
    agregar_consumo(ONTEM, ONTEM)
    assert _consumo(frango) == {(ONTEM, Decimal("3.500"), 3)}


def test_g1_linha_que_ficou_sem_venda_some_ao_recalcular(frango, arroz):
    # Dado derivado: a rotina regrava o período a partir das vendas, não mantém sobra antiga.
    ConsumoDiario.objects.create(produto=arroz, data=ONTEM, quantidade_vendida=9, dia_semana=3)
    _mov(frango, "2", ONTEM)
    agregar_consumo(ONTEM, ONTEM)
    assert _consumo(arroz) == set()
    assert _consumo(frango) == {(ONTEM, Decimal("2.000"), 3)}


# --- Rodada diária --------------------------------------------------------------------------------


def test_g1_rodada_diaria_agrega_os_ultimos_30_dias_ate_ontem(frango):
    _mov(frango, "1", ONTEM)
    _mov(frango, "4", ONTEM - timedelta(days=29))
    _mov(frango, "7", HOJE, 1)  # hoje ainda não terminou: fica para a rodada de amanhã
    assert agregar_consumo_recente() == 2
    assert {data for data, _, _ in _consumo(frango)} == {ONTEM, ONTEM - timedelta(days=29)}


def test_g1_rodada_diaria_nao_mexe_no_que_esta_fora_da_janela(frango):
    antigo = ONTEM - timedelta(days=30)
    ConsumoDiario.objects.create(produto=frango, data=antigo, quantidade_vendida=5, dia_semana=2)
    agregar_consumo_recente()
    assert _consumo(frango) == {(antigo, Decimal("5.000"), 2)}


def test_g1_comando_agrega_e_diz_quantas_linhas(frango):
    _mov(frango, "2", ONTEM)
    saida = StringIO()
    call_command("agregar_consumo", stdout=saida)
    assert "1 linha" in saida.getvalue()
    assert "13/10/2026 a 11/11/2026" in saida.getvalue()
    assert _consumo(frango) == {(ONTEM, Decimal("2.000"), 3)}


def test_g1_comando_desde_refaz_o_historico_inteiro(frango):
    antigo = date(2026, 6, 1)
    _mov(frango, "3", antigo)
    _mov(frango, "2", ONTEM)
    call_command("agregar_consumo", "--desde", "2026-06-01", stdout=StringIO())
    assert {data for data, _, _ in _consumo(frango)} == {antigo, ONTEM}


def test_g1_comando_com_data_invalida_avisa(db):
    from django.core.management.base import CommandError

    with pytest.raises(CommandError, match="AAAA-MM-DD"):
        call_command("agregar_consumo", "--desde", "01/06/2026", stdout=StringIO())

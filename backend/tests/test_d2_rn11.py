"""
Tarefa D2 — RN11: perda não conta como consumo.

> Movimentações do tipo PERDA reduzem o estoque, mas são excluídas da base de cálculo de consumo
> e de previsão.

"Esta é a regra mais fácil de quebrar sem perceber. Se falhar, quanto mais produto estraga, mais
o sistema manda comprar — o erro se alimenta sozinho." (docs/REGRAS-NEGOCIO.md)

A base de consumo existe num lugar só, previsao/consumo.py, que filtra tipo = 'VENDA'. A tabela
consumo_diario (G1) e o motor de previsão (G2) só podem ler o consumo por ela — o último teste
deste arquivo garante isso lendo o código.
"""

import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from django.utils import timezone

from cadastro.models import Categoria, Produto
from estoque.models import Movimentacao
from estoque.saldo import saldo_do_produto
from previsao.consumo import movimentacoes_de_consumo, vendido_no_periodo, vendido_por_dia

DIA = date(2026, 9, 21)


def _quando(dia: date, hora: int = 12, minuto: int = 0):
    return timezone.make_aware(datetime(dia.year, dia.month, dia.day, hora, minuto))


@pytest.fixture
def acougue(db):
    return Categoria.objects.create(nome="Açougue", perecivel_padrao=True)


@pytest.fixture
def frango(acougue):
    return Produto.objects.create(
        categoria=acougue,
        nome="Frango resfriado 1 kg",
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=4,
    )


@pytest.fixture
def alcatra(acougue):
    return Produto.objects.create(
        categoria=acougue, nome="Alcatra", unidade_medida="KG", perecivel=True, durabilidade_dias=3
    )


def _mov(produto, tipo, quantidade, quando, motivo=None):
    return Movimentacao.objects.create(
        produto=produto,
        tipo=tipo,
        quantidade=Decimal(quantidade),
        data_hora=quando,
        motivo=motivo or ("Estragou" if tipo == "PERDA" else None),
    )


# --- O exemplo da Apostila I ----------------------------------------------------------------------


def test_rn11_frango_que_vai_fora_reduz_o_saldo_mas_nao_o_consumo(frango):
    # "10 kg de frango vão fora. O saldo cai 10 kg; o consumo do dia continua sendo só o vendido."
    _mov(frango, "ENTRADA", "40", _quando(DIA, 7))
    _mov(frango, "VENDA", "6", _quando(DIA, 11))
    _mov(frango, "PERDA", "10", _quando(DIA, 15), motivo="Freezer desligou")
    assert saldo_do_produto(frango) == Decimal("24")  # 40 − 6 − 10: a perda reduz o estoque
    assert vendido_por_dia(frango, DIA, DIA) == {DIA: Decimal("6")}  # o consumo é só o vendido


@pytest.mark.parametrize("perdido", ["0", "10", "100"])
def test_rn11_quanto_mais_estraga_o_consumo_nao_aumenta(frango, perdido):
    # O erro que "se alimenta sozinho": se a perda contasse, mais estrago = mais compra.
    _mov(frango, "ENTRADA", "200", _quando(DIA, 7))
    _mov(frango, "VENDA", "8", _quando(DIA, 11))
    if perdido != "0":
        _mov(frango, "PERDA", perdido, _quando(DIA, 15))
    assert vendido_no_periodo(frango, DIA, DIA) == Decimal("8")


# --- Só VENDA entra -------------------------------------------------------------------------------


@pytest.mark.parametrize("tipo", ["ENTRADA", "AJUSTE", "PERDA"])
def test_rn11_so_venda_entra_na_base_de_consumo(frango, tipo):
    _mov(frango, tipo, "50", _quando(DIA))
    assert vendido_no_periodo(frango, DIA, DIA) == Decimal("0")
    assert vendido_por_dia(frango, DIA, DIA) == {}


def test_rn11_vendas_do_dia_sao_somadas(frango):
    _mov(frango, "VENDA", "2.5", _quando(DIA, 9))
    _mov(frango, "VENDA", "1.25", _quando(DIA, 17))
    assert vendido_no_periodo(frango, DIA, DIA) == Decimal("3.75")


def test_rn11_base_de_consumo_so_tem_venda(frango):
    for tipo in ("ENTRADA", "VENDA", "PERDA", "AJUSTE"):
        _mov(frango, tipo, "1", _quando(DIA))
    assert set(movimentacoes_de_consumo().values_list("tipo", flat=True)) == {"VENDA"}


# --- Por dia, no dia da loja ----------------------------------------------------------------------


def test_rn11_consumo_e_separado_por_dia(frango):
    _mov(frango, "VENDA", "5", _quando(date(2026, 9, 19)))
    _mov(frango, "VENDA", "7", _quando(date(2026, 9, 20)))
    _mov(frango, "VENDA", "3", _quando(date(2026, 9, 21)))
    assert vendido_por_dia(frango, date(2026, 9, 19), date(2026, 9, 21)) == {
        date(2026, 9, 19): Decimal("5"),
        date(2026, 9, 20): Decimal("7"),
        date(2026, 9, 21): Decimal("3"),
    }


def test_rn11_venda_da_noite_conta_no_dia_da_loja(frango):
    # 22h30 de 21/09 em São Paulo já é 22/09 em UTC — mas a venda foi no sábado da loja.
    _mov(frango, "VENDA", "4", _quando(DIA, 22, 30))
    assert vendido_por_dia(frango, DIA, date(2026, 9, 22)) == {DIA: Decimal("4")}


def test_rn11_periodo_inclui_o_primeiro_e_o_ultimo_dia(frango):
    _mov(frango, "VENDA", "1", _quando(date(2026, 9, 1), 0, 5))
    _mov(frango, "VENDA", "2", _quando(date(2026, 9, 30), 23, 55))
    _mov(frango, "VENDA", "9", _quando(date(2026, 10, 1), 0, 5))  # fora
    assert vendido_no_periodo(frango, date(2026, 9, 1), date(2026, 9, 30)) == Decimal("3")


def test_rn11_produtos_nao_se_misturam(frango, alcatra):
    _mov(frango, "VENDA", "6", _quando(DIA))
    _mov(alcatra, "VENDA", "2", _quando(DIA))
    assert vendido_no_periodo(frango, DIA, DIA) == Decimal("6")
    assert vendido_no_periodo(alcatra, DIA, DIA) == Decimal("2")


def test_rn11_sem_venda_o_consumo_e_zero(frango):
    assert vendido_no_periodo(frango, DIA, DIA) == Decimal("0")


# --- Guarda: ninguém calcula consumo por fora ------------------------------------------------------


def test_rn11_previsao_e_avisos_so_leem_movimentacao_pela_base_de_consumo():
    # Todo cálculo de consumo, previsão e aviso (blocos G e H) tem de passar por previsao/consumo.py.
    # Se alguém consultar Movimentacao direto nesses módulos, pode esquecer o filtro de VENDA e
    # quebrar a RN11 sem perceber — este teste pega isso.
    raiz = Path(__file__).resolve().parents[1]
    permitido = raiz / "previsao" / "consumo.py"
    infratores = []
    for pasta in ("previsao", "alertas"):
        for arquivo in (raiz / pasta).rglob("*.py"):
            if arquivo == permitido or "migrations" in arquivo.parts:
                continue
            if re.search(r"\bMovimentacao\b|\bmovimentacao\b", arquivo.read_text(encoding="utf-8")):
                infratores.append(str(arquivo.relative_to(raiz)))
    assert infratores == [], f"use previsao.consumo em vez de ler movimentacao direto: {infratores}"

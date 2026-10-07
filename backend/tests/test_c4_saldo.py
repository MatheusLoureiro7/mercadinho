"""
Tarefa C4 — RN01: o saldo é sempre derivado das movimentações.

> O saldo em estoque de um produto é sempre o resultado da soma das suas movimentações. Nenhuma
> tela, nenhum processo e nenhum usuário pode escrever um valor de saldo diretamente.

saldo = Σ ENTRADA + Σ AJUSTE − Σ VENDA − Σ PERDA, pela view vw_estoque_atual do schema.sql.
"Se falhar: o estoque passa a mentir sem deixar rastro." (Apostila I)
"""

import re
from decimal import Decimal

import pytest
from django.db import DatabaseError, connection, transaction

from cadastro.models import Categoria, Produto
from estoque.models import EstoqueAtual, Movimentacao
from estoque.saldo import saldo_do_produto
from tests.conftest import SCHEMA_SQL


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
        estoque_minimo=Decimal("10"),
    )


@pytest.fixture
def alcatra(acougue):
    return Produto.objects.create(
        categoria=acougue, nome="Alcatra", unidade_medida="KG", perecivel=True, durabilidade_dias=3
    )


def _mov(produto, tipo, quantidade, motivo=None):
    return Movimentacao.objects.create(
        produto=produto, tipo=tipo, quantidade=Decimal(quantidade), motivo=motivo
    )


# --- A view é a da Apostila IV --------------------------------------------------------------------


@pytest.mark.django_db
def test_rn01_view_de_saldo_e_identica_a_do_schema():
    # Cria a view do schema.sql com outro nome e pede ao PostgreSQL a definição das duas: têm de
    # ser a mesma consulta, palavra por palavra depois de normalizadas pelo próprio banco.
    texto = SCHEMA_SQL.read_text(encoding="utf-8")
    create_view = re.search(r"CREATE VIEW vw_estoque_atual AS.*?;", texto, re.S).group(0)
    referencia = create_view.replace("vw_estoque_atual", "vw_estoque_atual_da_apostila", 1)
    with connection.cursor() as cursor:
        cursor.execute(referencia)
        cursor.execute(
            "SELECT pg_get_viewdef('vw_estoque_atual'), pg_get_viewdef('vw_estoque_atual_da_apostila')"
        )
        nossa, da_apostila = cursor.fetchone()
    assert nossa == da_apostila


@pytest.mark.django_db
def test_rn01_view_tem_as_colunas_do_schema():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_estoque_atual LIMIT 0")
        colunas = [c.name for c in cursor.description]
    assert colunas == ["produto_id", "produto_nome", "unidade_medida", "estoque_minimo", "saldo"]


# --- O cálculo ------------------------------------------------------------------------------------


def test_rn01_exemplo_da_apostila_entrada_40_venda_12_perda_3_saldo_25(frango):
    _mov(frango, "ENTRADA", "40")
    _mov(frango, "VENDA", "12")
    _mov(frango, "PERDA", "3", motivo="Estragou no balcão")
    assert saldo_do_produto(frango) == Decimal("25")
    # ... e as três linhas no histórico.
    historico = list(
        Movimentacao.objects.filter(produto=frango).order_by("id").values_list("tipo", "quantidade")
    )
    assert historico == [("ENTRADA", Decimal("40")), ("VENDA", Decimal("12")), ("PERDA", Decimal("3"))]


def test_rn01_produto_sem_movimentacao_tem_saldo_zero(frango):
    assert saldo_do_produto(frango) == Decimal("0")


@pytest.mark.parametrize(
    ("tipo", "efeito"),
    [("ENTRADA", "10"), ("AJUSTE", "10"), ("VENDA", "-10"), ("PERDA", "-10")],
)
def test_rn01_sinal_de_cada_tipo(frango, tipo, efeito):
    _mov(frango, "ENTRADA", "100")
    _mov(frango, tipo, "10", motivo="Teste" if tipo == "PERDA" else None)
    assert saldo_do_produto(frango) == Decimal("100") + Decimal(efeito)


def test_rn11_perda_reduz_o_saldo(frango):
    # RN11: perda reduz o estoque (só fica fora da base de consumo — isso é a D2/G1).
    _mov(frango, "ENTRADA", "20")
    _mov(frango, "PERDA", "10", motivo="Freezer desligou")
    assert saldo_do_produto(frango) == Decimal("10")


def test_rn01_quilo_fracionado_sem_erro_de_arredondamento(frango):
    # Decimal, nunca float: 0,1 + 0,2 tem de dar exatamente 0,3.
    _mov(frango, "ENTRADA", "0.1")
    _mov(frango, "ENTRADA", "0.2")
    assert saldo_do_produto(frango) == Decimal("0.3")
    _mov(frango, "VENDA", "0.125")
    assert saldo_do_produto(frango) == Decimal("0.175")


def test_rn01_saldo_de_um_produto_nao_mistura_com_outro(frango, alcatra):
    _mov(frango, "ENTRADA", "40")
    _mov(alcatra, "ENTRADA", "15")
    _mov(alcatra, "VENDA", "5")
    assert saldo_do_produto(frango) == Decimal("40")
    assert saldo_do_produto(alcatra) == Decimal("10")


def test_rn01_saldo_vem_sempre_da_soma_atual(frango):
    # Não há valor guardado: cada movimentação nova muda o saldo na hora.
    _mov(frango, "ENTRADA", "10")
    assert saldo_do_produto(frango) == Decimal("10")
    _mov(frango, "VENDA", "4")
    assert saldo_do_produto(frango) == Decimal("6")


def test_rn01_view_traz_os_dados_do_produto(frango):
    _mov(frango, "ENTRADA", "8")
    linha = EstoqueAtual.objects.get(produto=frango)
    assert (linha.produto_nome, linha.unidade_medida) == ("Frango resfriado 1 kg", "KG")
    assert linha.estoque_minimo == Decimal("10")
    assert linha.saldo == Decimal("8")


def test_rn01_todo_produto_aparece_na_view(frango, alcatra):
    assert set(EstoqueAtual.objects.values_list("produto_id", flat=True)) == {frango.pk, alcatra.pk}


# --- Ninguém escreve saldo ------------------------------------------------------------------------


def test_rn01_saldo_nao_pode_ser_gravado_pelo_sistema(frango):
    linha = EstoqueAtual.objects.get(produto=frango)
    linha.saldo = Decimal("999")
    with pytest.raises(TypeError, match="RN01"):
        linha.save()
    with pytest.raises(TypeError, match="RN01"):
        linha.delete()


def test_rn01_saldo_nao_pode_ser_gravado_nem_direto_no_banco(frango):
    with pytest.raises(DatabaseError), transaction.atomic(), connection.cursor() as cursor:
        cursor.execute("UPDATE vw_estoque_atual SET saldo = 999 WHERE produto_id = %s", [frango.pk])

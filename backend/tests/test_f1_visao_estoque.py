"""
Tarefa F1 — visão de estoque por produto e por lote.

RF07: "Ver o saldo por produto e por categoria, com destaque para o que está abaixo do mínimo e o
que está vencendo." RN16: lote vencido é destacado. O saldo vem da vw_estoque_atual (RN01).

Sem objeto novo no banco: o schema.sql tem uma única view (vw_estoque_atual). A visão por produto
e por lote são consultas sobre ela e sobre `lote`.

L21: a tabela `parametro` (schema.sql) nasce aqui, porque "vencendo" usa dias_aviso_validade.
"""

import re
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from cadastro.models import Categoria, Produto
from comum.models import Parametro
from comum.parametros import dias_aviso_validade, parametro_inteiro
from estoque.consulta import Situacao, posicao_por_lote, posicao_por_produto
from estoque.entrada import registrar_entrada
from estoque.models import Lote, Movimentacao
from estoque.perda import registrar_perda
from tests.conftest import SCHEMA_SQL, divergencias_do_schema

HOJE = date(2026, 9, 21)


# =================================================================================================
# L21 — tabela parametro
# =================================================================================================


@pytest.mark.django_db
def test_l21_tabela_parametro_igual_ao_schema():
    assert divergencias_do_schema("parametro") == []


@pytest.mark.django_db
def test_l21_parametros_iniciais_sao_os_do_schema():
    # Os 7 valores do INSERT do schema.sql (Apostila I, seção 7) — nenhum confirmado pelo cliente.
    insert = re.search(
        r"INSERT INTO parametro .*? VALUES(.*?);", SCHEMA_SQL.read_text(encoding="utf-8"), re.S
    )
    esperado = {
        chave: (valor, descricao)
        for chave, valor, descricao in re.findall(r"\('([^']*)',\s*'([^']*)',\s*'([^']*)'\)", insert.group(1))
    }
    assert len(esperado) == 7
    no_banco = {p.chave: (p.valor, p.descricao) for p in Parametro.objects.all()}
    assert no_banco == esperado


@pytest.mark.django_db
def test_l21_parametro_e_lido_do_banco_e_nao_do_codigo():
    assert parametro_inteiro("historico_minimo_dias") == 14
    Parametro.objects.filter(chave="historico_minimo_dias").update(valor="21")
    assert parametro_inteiro("historico_minimo_dias") == 21


@pytest.mark.django_db
def test_l01_dias_de_aviso_de_validade_lido_por_produto():
    # L01: hoje o valor é global (3), mas é lido por produto — quando o grupo decidir "por
    # categoria", muda só esta função.
    assert dias_aviso_validade(produto=None) == 3


# =================================================================================================
# Fixtures
# =================================================================================================


@pytest.fixture
def frios(db):
    return Categoria.objects.create(nome="Frios", perecivel_padrao=True)


@pytest.fixture
def secos(db):
    return Categoria.objects.create(nome="Secos e molhados")


@pytest.fixture
def presunto(frios):
    return Produto.objects.create(
        categoria=frios,
        nome="Presunto",
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=7,
        estoque_minimo=Decimal("3"),
    )


@pytest.fixture
def iogurte(frios):
    return Produto.objects.create(
        categoria=frios, nome="Iogurte natural", unidade_medida="UN", perecivel=True, durabilidade_dias=15
    )


@pytest.fixture
def arroz(secos):
    return Produto.objects.create(
        categoria=secos, nome="Arroz 5 kg", unidade_medida="PCT", estoque_minimo=Decimal("10")
    )


def _lote(produto, quantidade, validade):
    lote = Lote.objects.create(
        produto=produto,
        quantidade_inicial=Decimal(quantidade),
        quantidade_atual=Decimal(quantidade),
        data_entrada=date(2026, 9, 10),
        data_validade=validade,
    )
    Movimentacao.objects.create(produto=produto, lote=lote, tipo="ENTRADA", quantidade=Decimal(quantidade))
    return lote


def _por_produto(**filtros):
    return {p.nome: p for p in posicao_por_produto(hoje=HOJE, **filtros)}


def _por_lote():
    return {lote.pk: lote for lote in posicao_por_lote(hoje=HOJE)}


# =================================================================================================
# Por produto
# =================================================================================================


def test_f1_saldo_por_produto_com_a_categoria(presunto, arroz):
    _lote(presunto, "5", date(2026, 9, 28))
    _lote(arroz, "20", None)
    posicao = _por_produto()
    assert (posicao["Presunto"].saldo, posicao["Presunto"].categoria.nome) == (Decimal("5"), "Frios")
    assert (posicao["Arroz 5 kg"].saldo, posicao["Arroz 5 kg"].categoria.nome) == (
        Decimal("20"),
        "Secos e molhados",
    )


def test_f1_produto_sem_estoque_aparece_com_saldo_zero(presunto):
    assert _por_produto()["Presunto"].saldo == Decimal("0")


def test_f1_saldo_por_produto_e_o_da_view_de_saldo(presunto):
    # RN01: o saldo vem das movimentações, não da soma dos lotes.
    _lote(presunto, "5", date(2026, 9, 28))
    Movimentacao.objects.create(produto=presunto, tipo="AJUSTE", quantidade=Decimal("1"))
    assert _por_produto()["Presunto"].saldo == Decimal("6")


@pytest.mark.parametrize(
    ("saldo", "abaixo"),
    [("2", True), ("3", False), ("4", False)],
    ids=["abaixo", "igual_ao_minimo", "acima"],
)
def test_rf07_destaca_o_que_esta_abaixo_do_minimo(presunto, saldo, abaixo):
    _lote(presunto, saldo, date(2026, 9, 28))  # estoque mínimo do presunto: 3
    assert _por_produto()["Presunto"].abaixo_do_minimo is abaixo


def test_rf07_produto_sem_estoque_minimo_nunca_esta_abaixo(iogurte):
    assert _por_produto()["Iogurte natural"].abaixo_do_minimo is False


def test_rf07_produto_conta_os_lotes_vencendo_e_vencidos(iogurte):
    _lote(iogurte, "6", date(2026, 9, 20))  # vencido
    _lote(iogurte, "4", date(2026, 9, 23))  # vencendo
    _lote(iogurte, "10", date(2026, 10, 1))  # ok
    posicao = _por_produto()["Iogurte natural"]
    assert (posicao.lotes_vencidos, posicao.lotes_vencendo) == (1, 1)
    assert posicao.proxima_validade == date(2026, 9, 20)


def test_f1_lote_zerado_nao_conta_como_vencido(iogurte):
    vencido = _lote(iogurte, "6", date(2026, 9, 20))
    vencido.quantidade_atual = Decimal("0")
    vencido.save()
    posicao = _por_produto()["Iogurte natural"]
    assert (posicao.lotes_vencidos, posicao.proxima_validade) == (0, None)


def test_f1_produtos_em_ordem_de_categoria_e_nome(presunto, iogurte, arroz):
    assert [p.nome for p in posicao_por_produto(hoje=HOJE)] == ["Iogurte natural", "Presunto", "Arroz 5 kg"]


# =================================================================================================
# Por lote
# =================================================================================================


def test_rn16_lote_vencido_e_destacado(iogurte):
    # Apostila I: "lote de iogurte vencido em 20/09 aparece destacado em 21/09".
    vencido = _lote(iogurte, "6", date(2026, 9, 20))
    assert _por_lote()[vencido.pk].situacao == Situacao.VENCIDO


@pytest.mark.parametrize(
    ("dias", "situacao"),
    [(0, Situacao.VENCENDO), (3, Situacao.VENCENDO), (4, Situacao.OK)],
    ids=["vence_hoje", "vence_em_3_dias", "vence_em_4_dias"],
)
def test_rf07_lote_vencendo_usa_o_parametro_de_dias(presunto, dias, situacao):
    # RN05: aviso com N = dias_aviso_validade (3) dias ou menos. Exemplo: vence 24/09, hoje 21/09.
    lote = _lote(presunto, "2", HOJE + timedelta(days=dias))
    assert _por_lote()[lote.pk].situacao == situacao


def test_rf07_mudar_o_parametro_muda_o_que_esta_vencendo(presunto):
    lote = _lote(presunto, "2", HOJE + timedelta(days=5))
    assert _por_lote()[lote.pk].situacao == Situacao.OK
    Parametro.objects.filter(chave="dias_aviso_validade").update(valor="7")
    assert _por_lote()[lote.pk].situacao == Situacao.VENCENDO


def test_f1_lote_sem_validade(arroz):
    lote = _lote(arroz, "20", None)
    linha = _por_lote()[lote.pk]
    assert (linha.situacao, linha.dias_para_vencer) == (Situacao.SEM_VALIDADE, None)


def test_f1_lote_mostra_dias_para_vencer(presunto):
    vence_em_5 = _lote(presunto, "1", date(2026, 9, 26))
    ja_venceu = _lote(presunto, "1", date(2026, 9, 19))
    lotes = _por_lote()
    assert (lotes[vence_em_5.pk].dias_para_vencer, lotes[ja_venceu.pk].dias_para_vencer) == (5, -2)


def test_f1_lote_traz_produto_categoria_e_quantidade(presunto):
    lote = _lote(presunto, "5", date(2026, 9, 28))
    linha = _por_lote()[lote.pk]
    assert (linha.produto.nome, linha.produto.categoria.nome, linha.quantidade_atual) == (
        "Presunto",
        "Frios",
        Decimal("5"),
    )


def test_f1_lote_zerado_nao_aparece_na_posicao(presunto):
    lote = _lote(presunto, "1", date(2026, 9, 28))
    lote.quantidade_atual = Decimal("0")
    lote.save()
    assert lote.pk not in _por_lote()


def test_f1_lotes_em_ordem_de_validade(presunto, iogurte, arroz):
    sem_validade = _lote(arroz, "20", None)
    depois = _lote(presunto, "5", date(2026, 9, 28))
    antes = _lote(iogurte, "6", date(2026, 9, 20))
    assert [lote.pk for lote in posicao_por_lote(hoje=HOJE)] == [antes.pk, depois.pk, sem_validade.pk]


# =================================================================================================
# Coerência: o que está nos lotes bate com o saldo
# =================================================================================================


def test_rn01_soma_dos_lotes_bate_com_o_saldo_depois_de_entradas_e_perdas(presunto):
    # Entrada e perda passam pelos serviços (C2, D1), que mexem no lote e na movimentação juntos.
    hoje_de_verdade = timezone.localdate()
    registrar_entrada(
        produto=presunto,
        quantidade=Decimal("10"),
        usuario=None,
        data_validade=hoje_de_verdade + timedelta(days=5),
    )
    registrar_entrada(
        produto=presunto,
        quantidade=Decimal("4"),
        usuario=None,
        data_validade=hoje_de_verdade + timedelta(days=9),
    )
    registrar_perda(produto=presunto, quantidade=Decimal("12"), motivo="Freezer desligou", usuario=None)
    soma_dos_lotes = sum(lote.quantidade_atual for lote in posicao_por_lote(hoje=hoje_de_verdade))
    assert soma_dos_lotes == _por_produto()["Presunto"].saldo == Decimal("2")

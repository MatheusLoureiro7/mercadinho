"""
Tarefa C1 — tabelas de lote e movimentação.

O banco tem de ser o da Apostila IV (schema.sql): mesmas colunas, tipos, padrões, restrições e
índices. As restrições que o próprio banco garante são testadas pelo caminho "sim" e "não".
As regras que usam estas tabelas vêm depois: RN04 (C3), RN01 e o saldo (C4), RN02 e RN16 (E3/D1).
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.db import IntegrityError, connection, transaction

from cadastro.models import Categoria, Fornecedor, Produto, Usuario
from estoque.models import Lote, Movimentacao
from tests.conftest import divergencias_do_schema, indices, restricoes


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
def lote_frango(frango):
    return Lote.objects.create(
        produto=frango,
        quantidade_inicial=Decimal("40"),
        quantidade_atual=Decimal("40"),
        data_entrada=date(2026, 9, 21),
        data_validade=date(2026, 9, 25),
    )


def _falha_no_banco(funcao):
    with pytest.raises(IntegrityError), transaction.atomic():
        funcao()


def _movimentacao(produto, **campos):
    return Movimentacao.objects.create(
        produto=produto, **{"tipo": "ENTRADA", "quantidade": Decimal("1"), **campos}
    )


# --- O banco confere com a Apostila IV ------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize("tabela", ["lote", "movimentacao"])
def test_c1_tabela_igual_ao_schema(tabela):
    assert divergencias_do_schema(tabela) == []


@pytest.mark.django_db
def test_c1_restricoes_nomeadas_do_schema_existem():
    assert "ck_lote_qtd" in restricoes("lote")
    assert {"ck_mov_tipo", "ck_mov_qtd", "ck_mov_perda_motivo"} <= restricoes("movimentacao")


@pytest.mark.django_db
def test_rn02_indice_fifo_por_validade_so_dos_lotes_com_saldo():
    definicao = indices("lote")["ix_lote_fifo"]
    assert "(produto_id, data_validade)" in definicao
    assert "WHERE (quantidade_atual > (0)" in definicao


@pytest.mark.django_db
def test_c1_indices_de_movimentacao_do_schema_existem():
    assert "(produto_id, data_hora)" in indices("movimentacao")["ix_mov_produto_data"]
    assert "(tipo, data_hora)" in indices("movimentacao")["ix_mov_tipo_data"]  # RN11


# --- Lote ----------------------------------------------------------------------------------------


def test_c1_lote_guarda_quantidade_em_quilo_fracionado(lote_frango):
    lote_frango.quantidade_atual = Decimal("12.345")
    lote_frango.save()
    lote_frango.refresh_from_db()
    assert lote_frango.quantidade_atual == Decimal("12.345")


def test_c1_lote_com_quantidade_atual_negativa_e_recusado(lote_frango):
    lote_frango.quantidade_atual = Decimal("-0.001")
    _falha_no_banco(lote_frango.save)


def test_c1_lote_zerado_e_aceito(lote_frango):
    lote_frango.quantidade_atual = Decimal("0")
    lote_frango.save()


def test_c1_lote_de_nao_perecivel_sem_validade_e_aceito(db):
    secos = Categoria.objects.create(nome="Secos e molhados")
    arroz = Produto.objects.create(categoria=secos, nome="Arroz 5 kg", unidade_medida="PCT")
    lote = Lote.objects.create(produto=arroz, quantidade_inicial=10, quantidade_atual=10)
    assert lote.data_validade is None


def test_c1_lote_aponta_o_fornecedor(frango):
    boi_bom = Fornecedor.objects.create(nome="Frigorífico Boi Bom", prazo_entrega_dias=3)
    lote = Lote.objects.create(produto=frango, fornecedor=boi_bom, quantidade_inicial=5, quantidade_atual=5)
    assert lote.fornecedor.prazo_entrega_dias == 3


def test_c1_data_de_entrada_tem_padrao_no_banco(frango):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO lote (produto_id, quantidade_inicial, quantidade_atual) VALUES (%s, 1, 1) "
            "RETURNING data_entrada = CURRENT_DATE",
            [frango.pk],
        )
        assert cursor.fetchone() == (True,)


# --- Movimentação --------------------------------------------------------------------------------


@pytest.mark.parametrize("tipo", ["ENTRADA", "VENDA", "AJUSTE"])
def test_c1_tipos_de_movimentacao_aceitos(frango, tipo):
    assert _movimentacao(frango, tipo=tipo).pk is not None


def test_c1_perda_com_motivo_e_aceita(frango):
    assert _movimentacao(frango, tipo="PERDA", motivo="Estragou no balcão").pk is not None


def test_c1_tipo_fora_dos_quatro_e_recusado(frango):
    _falha_no_banco(lambda: _movimentacao(frango, tipo="TROCA"))


@pytest.mark.parametrize("quantidade", ["0", "-1"])
def test_c1_quantidade_zero_ou_negativa_e_recusada(frango, quantidade):
    # O sinal vem do tipo (ENTRADA e AJUSTE somam, VENDA e PERDA subtraem), nunca da quantidade.
    _falha_no_banco(lambda: _movimentacao(frango, quantidade=Decimal(quantidade)))


@pytest.mark.parametrize("motivo", [None, "", "   "])
def test_c1_perda_sem_motivo_e_recusada(frango, motivo):
    # Tarefa D1: "registro de perda, com motivo obrigatório" — o banco é a última defesa.
    _falha_no_banco(lambda: _movimentacao(frango, tipo="PERDA", motivo=motivo))


def test_c1_venda_sem_motivo_e_aceita(frango):
    assert _movimentacao(frango, tipo="VENDA").motivo is None


def test_c1_movimentacao_sem_lote_e_aceita(frango):
    # A apostila marca lote_id como "(nulo)".
    assert _movimentacao(frango, lote=None).lote is None


def test_c1_movimentacao_registra_lote_usuario_e_origem(frango, lote_frango):
    sobrinho = Usuario.objects.create_user(login="sobrinho", senha="x", nome="Sobrinho", papel="OPERACAO")
    mov = _movimentacao(
        frango,
        lote=lote_frango,
        usuario=sobrinho,
        quantidade=Decimal("40"),
        preco_unitario="8.50",
        origem="TELA",
    )
    mov.refresh_from_db()
    assert (mov.lote, mov.usuario, mov.origem) == (lote_frango, sobrinho, "TELA")
    assert mov.preco_unitario == Decimal("8.50")


def test_c1_data_e_hora_da_movimentacao_vem_do_banco(frango):
    mov = _movimentacao(frango)
    assert mov.data_hora is not None
    assert mov.data_hora.tzinfo is not None  # TIMESTAMP WITH TIME ZONE


# --- Histórico: nada é apagado -------------------------------------------------------------------


def test_rn01_produto_com_movimentacao_nao_pode_ser_apagado(frango):
    from django.db.models import ProtectedError

    _movimentacao(frango)
    with pytest.raises(ProtectedError):
        frango.delete()


def test_rn01_lote_com_movimentacao_nao_pode_ser_apagado(frango, lote_frango):
    from django.db.models import ProtectedError

    _movimentacao(frango, lote=lote_frango)
    with pytest.raises(ProtectedError):
        lote_frango.delete()


def test_c1_validade_anterior_a_entrada_o_banco_nao_barra(frango):
    # A recusa de validade no passado é da API (RN04, tarefa C3), não do banco: o schema.sql não
    # tem essa restrição. Este teste documenta isso.
    lote = Lote.objects.create(
        produto=frango,
        quantidade_inicial=1,
        quantidade_atual=1,
        data_validade=date.today() - timedelta(days=1),
    )
    assert lote.pk is not None

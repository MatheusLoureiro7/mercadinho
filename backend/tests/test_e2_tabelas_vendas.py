"""
Tarefa E2 — tabelas de venda, item de venda e importação.

O banco tem de ser o da Apostila IV (schema.sql): mesmas colunas, tipos, padrões e restrições.
As restrições que o próprio banco garante são testadas pelo caminho "sim" e "não".
Quem usa estas tabelas vem depois: o importador (E3), o casamento com o produto (E4), a baixa
por venda com FIFO (RN01, RN02 — E3) e o consumo (G1, que lê só movimentação VENDA — RN11).

O sistema NÃO registra venda pela tela: venda só nasce do arquivo do caixa (fluxograma 04).
"""

from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from django.db import IntegrityError, connection, transaction

from cadastro.models import Categoria, Produto
from tests.conftest import divergencias_do_schema, restricoes
from vendas.models import ImportacaoPdv, ItemVenda, Venda

SAO_PAULO = ZoneInfo("America/Sao_Paulo")


@pytest.fixture
def arroz(db):
    secos = Categoria.objects.create(nome="Secos e molhados")
    return Produto.objects.create(categoria=secos, nome="Arroz 5 kg", unidade_medida="PCT")


@pytest.fixture
def venda(db):
    return Venda.objects.create(
        data_hora=datetime(2026, 11, 5, 19, 40, tzinfo=SAO_PAULO), valor_total=Decimal("57.80")
    )


def _falha_no_banco(funcao):
    with pytest.raises(IntegrityError), transaction.atomic():
        funcao()


# --- O banco confere com a Apostila IV ------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize("tabela", ["venda", "item_venda", "importacao_pdv"])
def test_e2_tabela_igual_ao_schema(tabela):
    assert divergencias_do_schema(tabela) == []


@pytest.mark.django_db
def test_e2_restricao_de_status_do_schema_existe():
    assert "ck_imp_status" in restricoes("importacao_pdv")


@pytest.mark.django_db
def test_e2_item_aponta_a_venda_com_apagar_em_cascata_no_banco():
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT confdeltype FROM pg_constraint
             WHERE conrelid = 'item_venda'::regclass AND contype = 'f'
               AND confrelid = 'venda'::regclass
            """
        )
        assert cursor.fetchone() == ("c",)  # ON DELETE CASCADE, como no schema.sql


# --- Venda ---------------------------------------------------------------------------------------


def test_e2_venda_guarda_data_e_hora_da_loja(venda):
    venda.refresh_from_db()
    assert venda.data_hora.astimezone(SAO_PAULO) == datetime(2026, 11, 5, 19, 40, tzinfo=SAO_PAULO)


def test_e2_venda_sem_data_e_hora_e_recusada(db):
    _falha_no_banco(lambda: Venda.objects.create(data_hora=None, valor_total=Decimal("1")))


def test_e2_venda_sem_valor_total_e_recusada(db):
    agora = datetime(2026, 11, 5, 10, 0, tzinfo=SAO_PAULO)
    _falha_no_banco(lambda: Venda.objects.create(data_hora=agora, valor_total=None))


def test_e2_forma_de_pagamento_e_opcional(venda):
    assert venda.forma_pagamento is None


def test_e2_forma_de_pagamento_e_gravada(db):
    venda = Venda.objects.create(
        data_hora=datetime(2026, 11, 5, 10, 0, tzinfo=SAO_PAULO),
        valor_total=Decimal("12.50"),
        forma_pagamento="PIX",
    )
    venda.refresh_from_db()
    assert venda.forma_pagamento == "PIX"


def test_e2_valores_em_dinheiro_sao_decimal(venda):
    venda.refresh_from_db()
    assert venda.valor_total == Decimal("57.80")
    assert isinstance(venda.valor_total, Decimal)


# --- Item de venda --------------------------------------------------------------------------------


def test_e2_item_que_casou_aponta_o_produto(venda, arroz):
    item = ItemVenda.objects.create(
        venda=venda, produto=arroz, quantidade=Decimal("2"), preco=Decimal("28.90")
    )
    assert list(venda.itens.all()) == [item]
    assert item.produto == arroz


def test_e2_item_que_nao_casou_fica_sem_produto(venda):
    """Linha do arquivo que não casou com nenhum produto: produto_id nulo, a linha fica pendente
    e não trava as demais (comentário do schema.sql, fluxograma 04)."""
    item = ItemVenda.objects.create(venda=venda, produto=None, quantidade=Decimal("1"))
    item.refresh_from_db()
    assert item.produto_id is None


def test_e2_item_guarda_quilo_fracionado(venda, arroz):
    item = ItemVenda.objects.create(venda=venda, produto=arroz, quantidade=Decimal("1.275"))
    item.refresh_from_db()
    assert item.quantidade == Decimal("1.275")


def test_e2_item_sem_quantidade_e_recusado(venda, arroz):
    _falha_no_banco(lambda: ItemVenda.objects.create(venda=venda, produto=arroz, quantidade=None))


def test_e2_item_sem_venda_e_recusado(arroz):
    _falha_no_banco(lambda: ItemVenda.objects.create(venda_id=None, produto=arroz, quantidade=Decimal("1")))


def test_e2_preco_do_item_e_opcional(venda, arroz):
    item = ItemVenda.objects.create(venda=venda, produto=arroz, quantidade=Decimal("1"))
    assert item.preco is None


def test_e2_apagar_a_venda_no_banco_apaga_os_itens(venda, arroz):
    ItemVenda.objects.create(venda=venda, produto=arroz, quantidade=Decimal("1"))
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM venda WHERE id = %s", [venda.pk])
    assert not ItemVenda.objects.exists()


def test_e2_produto_com_venda_nao_pode_ser_apagado(venda, arroz):
    """O histórico de vendas não perde o produto (mesmo cuidado da movimentação, RN01)."""
    from django.db.models import ProtectedError

    ItemVenda.objects.create(venda=venda, produto=arroz, quantidade=Decimal("1"))
    with pytest.raises(ProtectedError):
        arroz.delete()


# --- Importação do caixa --------------------------------------------------------------------------


def _importacao(**campos):
    return ImportacaoPdv.objects.create(
        **{"arquivo_nome": "vendas-2026-11-05.xlsx", "data_referencia": date(2026, 11, 5), **campos}
    )


def test_e2_importacao_nasce_pendente_e_zerada(db):
    importacao = _importacao()
    importacao.refresh_from_db()
    assert importacao.status == "PENDENTE"
    assert (importacao.linhas_lidas, importacao.linhas_erro) == (0, 0)
    assert importacao.processado_em is None


def test_e2_padroes_valem_sem_o_django(db):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO importacao_pdv (arquivo_nome, data_referencia) VALUES ('a.xlsx', '2026-11-05') "
            "RETURNING status, linhas_lidas, linhas_erro"
        )
        assert cursor.fetchone() == ("PENDENTE", 0, 0)


@pytest.mark.parametrize("status", ["PENDENTE", "OK", "PARCIAL", "ERRO"])
def test_e2_status_do_schema_sao_aceitos(db, status):
    assert _importacao(status=status).status == status


def test_e2_status_fora_dos_quatro_e_recusado(db):
    _falha_no_banco(lambda: _importacao(status="CONCLUIDO"))


def test_e2_importacao_sem_nome_do_arquivo_e_recusada(db):
    _falha_no_banco(lambda: _importacao(arquivo_nome=None))


def test_e2_importacao_sem_data_de_referencia_e_recusada(db):
    _falha_no_banco(lambda: _importacao(data_referencia=None))


def test_e2_importacao_registra_o_resultado(db):
    processado = datetime(2026, 11, 6, 3, 0, tzinfo=SAO_PAULO)
    importacao = _importacao(status="PARCIAL", linhas_lidas=120, linhas_erro=3, processado_em=processado)
    importacao.refresh_from_db()
    assert (importacao.status, importacao.linhas_lidas, importacao.linhas_erro) == ("PARCIAL", 120, 3)
    assert importacao.processado_em == processado

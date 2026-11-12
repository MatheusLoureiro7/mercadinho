"""
Tarefa G3 — tabela de previsão e gravação do resultado. Operação 03, passos 4 e 5 (RN08, RF11).

Para cada produto, a rodada grava em previsao_produto:
- consumo_medio_diario e consumo_por_dia_semana — da G2 (RN06, RN07);
- dias_ate_acabar — o saldo de hoje gasto dia a dia com o consumo de cada dia (RN07: na quinta,
  o sábado da cerveja já conta 26), com a fração do último dia; sem consumo, nulo (não acaba);
- ponto_pedido (RN08) = média × prazo do fornecedor × (1 + estoque_seguranca_pct ÷ 100);
- sugestao_compra (RF11, decisão do grupo sobre a L15 em 12/11/2026) = o que o produto vai vender
  no prazo de entrega + 7 dias, contados de hoje, menos o saldo; nunca negativa; sem pedido mínimo;
- calculado_em — a hora da rodada (o "ainda aprendendo" da RN09 é a G4).

Produto sem fornecedor padrão não tem prazo de entrega: ponto de pedido e sugestão ficam nulos.

Hoje: quinta, 12/11/2026. Janela da média: 13/10 a 11/11 (4 sábados).

Losangos, pelo "sim" e pelo "não":
    tem fornecedor padrão?    sim → *_rn08_*, *_l15_*        não → *_sem_fornecedor_*
    vende alguma coisa?       sim → *_acaba_em_*             não → *_sem_venda_*
    tem saldo?                sim → *_acaba_em_*             não → *_sem_saldo_*
    saldo cobre a sugestão?   sim → *_sugestao_zero_*        não → *_l15_*
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from io import StringIO
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.core.management import call_command

from cadastro.models import Categoria, Fornecedor, Produto
from comum.models import Parametro
from estoque.models import Movimentacao
from previsao.agregacao import dia_da_semana
from previsao.models import ConsumoDiario, PrevisaoProduto
from previsao.projecao import DIAS_ALEM_DO_PRAZO, calcular_previsao
from tests.conftest import divergencias_do_schema

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
AGORA = datetime(2026, 11, 12, 3, 0, tzinfo=SAO_PAULO)
INICIO = date(2026, 10, 13)
DIAS = [INICIO + timedelta(days=n) for n in range(30)]
SABADO = 6


@pytest.fixture(autouse=True)
def madrugada_de_12_11():
    with patch("django.utils.timezone.now", return_value=AGORA):
        yield


def _produto(nome, prazo=3):
    categoria, _ = Categoria.objects.get_or_create(nome="Secos e molhados")
    fornecedor = (
        Fornecedor.objects.create(nome=f"Fornecedor de {nome}", prazo_entrega_dias=prazo) if prazo else None
    )
    return Produto.objects.create(
        categoria=categoria, nome=nome, unidade_medida="KG", fornecedor_padrao=fornecedor
    )


def _vende_todo_dia(produto, quantidade, sabado=None):
    for dia in DIAS:
        vendido = sabado if sabado is not None and dia_da_semana(dia) == SABADO else quantidade
        ConsumoDiario.objects.create(
            produto=produto, data=dia, quantidade_vendida=Decimal(vendido), dia_semana=dia_da_semana(dia)
        )


def _saldo(produto, quantidade):
    Movimentacao.objects.create(produto=produto, tipo="ENTRADA", quantidade=Decimal(quantidade))


def _previsao(produto):
    return PrevisaoProduto.objects.get(produto=produto)


@pytest.fixture
def arroz(db):
    produto = _produto("Arroz 5 kg", prazo=3)
    _vende_todo_dia(produto, "5")
    return produto


@pytest.fixture
def cerveja(db):
    # O exemplo da RN07: 4 sábados × 26 = 104; 26 outros dias × 5 = 130; +6 numa sexta = 240 → 8/dia.
    produto = _produto("Cerveja lata 350 ml", prazo=2)
    _vende_todo_dia(produto, "5", sabado="26")
    sexta = next(dia for dia in DIAS if dia_da_semana(dia) == 5)
    ConsumoDiario.objects.filter(produto=produto, data=sexta).update(quantidade_vendida=Decimal("11"))
    return produto


# --- Tabela ---------------------------------------------------------------------------------------


@pytest.mark.django_db
def test_g3_tabela_previsao_produto_igual_ao_schema():
    assert divergencias_do_schema("previsao_produto") == []


# --- Média, dias até acabar -----------------------------------------------------------------------


def test_rn06_arroz_5_por_dia_com_20_em_estoque_acaba_em_4_dias(arroz):
    _saldo(arroz, "20")
    calcular_previsao()
    previsao = _previsao(arroz)
    assert previsao.consumo_medio_diario == Decimal("5.000")
    assert previsao.dias_ate_acabar == Decimal("4.0")


def test_g3_acaba_em_dias_com_fracao_do_ultimo_dia(arroz):
    _saldo(arroz, "21")
    calcular_previsao()
    assert _previsao(arroz).dias_ate_acabar == Decimal("4.2")


def test_rn07_cerveja_na_quinta_os_dias_ate_acabar_contam_o_sabado(cerveja):
    # Saldo 46: quinta 8 (38), sexta 8 (30), sábado 26 (4), domingo 4 de 8 → 3,5 dias.
    # Só com a média seriam 46 ÷ 8 = 5,8 dias — e o sábado acabaria com a cerveja.
    _saldo(cerveja, "46")
    calcular_previsao()
    assert _previsao(cerveja).consumo_medio_diario == Decimal("8.000")
    assert _previsao(cerveja).dias_ate_acabar == Decimal("3.5")


def test_g3_estoque_de_muitas_semanas_tambem_e_contado(cerveja):
    # Semana da cerveja: 6 × 8 + 26 = 74. Saldo 740 = 10 semanas exatas → 70 dias.
    _saldo(cerveja, "740")
    calcular_previsao()
    assert _previsao(cerveja).dias_ate_acabar == Decimal("70.0")


def test_g3_sem_saldo_acaba_em_zero_dias(arroz):
    calcular_previsao()
    assert _previsao(arroz).dias_ate_acabar == Decimal("0.0")


def test_g3_saldo_negativo_acaba_em_zero_dias(arroz):
    Movimentacao.objects.create(produto=arroz, tipo="VENDA", quantidade=Decimal("2"))
    calcular_previsao()
    assert _previsao(arroz).dias_ate_acabar == Decimal("0.0")


def test_g3_sem_venda_nao_tem_dias_ate_acabar(db):
    fosforo = _produto("Fósforo")
    _saldo(fosforo, "10")
    calcular_previsao()
    previsao = _previsao(fosforo)
    assert previsao.consumo_medio_diario == Decimal("0.000")
    assert previsao.dias_ate_acabar is None
    assert (previsao.ponto_pedido, previsao.sugestao_compra) == (Decimal("0.000"), Decimal("0.000"))


def test_rn07_consumo_por_dia_semana_gravado_de_domingo_a_sabado(cerveja):
    calcular_previsao()
    por_dia = _previsao(cerveja).consumo_por_dia_semana
    assert list(por_dia) == ["0", "1", "2", "3", "4", "5", "6"]
    assert por_dia["6"] == "26.000" and por_dia["0"] == "5.000"


# --- Ponto de pedido (RN08) -----------------------------------------------------------------------


def test_rn08_carne_8_por_dia_prazo_3_e_20_por_cento_da_28_8(db):
    # O exemplo da apostila: 8 × 3 = 24, segurança 24 × 0,20 = 4,8 → 28,8 ≈ 29 kg.
    carne = _produto("Carne moída", prazo=3)
    _vende_todo_dia(carne, "8")
    calcular_previsao()
    assert _previsao(carne).ponto_pedido == Decimal("28.800")


def test_rn08_estoque_de_seguranca_vem_da_tabela_de_parametros(arroz):
    Parametro.objects.filter(chave="estoque_seguranca_pct").update(valor="50")
    calcular_previsao()
    assert _previsao(arroz).ponto_pedido == Decimal("22.500")  # 5 × 3 × 1,5


# --- Sugestão de compra (RF11, L15) ---------------------------------------------------------------


def test_l15_sugestao_e_o_consumo_do_prazo_mais_7_dias_menos_o_saldo(arroz):
    _saldo(arroz, "20")
    calcular_previsao()
    assert _previsao(arroz).sugestao_compra == Decimal("30.000")  # (3 + 7) × 5 − 20


def test_l15_sugestao_conta_o_sabado_da_cerveja(cerveja):
    # Prazo 2 + 7 = 9 dias, de quinta 12/11 a sexta 20/11: um sábado (26) e 8 dias × 8 = 90; − 46.
    _saldo(cerveja, "46")
    calcular_previsao()
    assert _previsao(cerveja).sugestao_compra == Decimal("44.000")


def test_l15_sugestao_zero_quando_o_saldo_ja_cobre(arroz):
    _saldo(arroz, "100")
    calcular_previsao()
    assert _previsao(arroz).sugestao_compra == Decimal("0.000")


def test_l15_sete_dias_alem_do_prazo_decididos_pelo_grupo():
    assert DIAS_ALEM_DO_PRAZO == 7


def test_g3_sem_fornecedor_padrao_nao_tem_ponto_de_pedido_nem_sugestao(db):
    sal = _produto("Sal 1 kg", prazo=None)
    _vende_todo_dia(sal, "1")
    _saldo(sal, "5")
    calcular_previsao()
    previsao = _previsao(sal)
    assert (previsao.ponto_pedido, previsao.sugestao_compra) == (None, None)
    assert (previsao.consumo_medio_diario, previsao.dias_ate_acabar) == (Decimal("1.000"), Decimal("5.0"))


# --- Gravação -------------------------------------------------------------------------------------


def test_g3_grava_a_hora_da_rodada_e_rodar_de_novo_atualiza_sem_duplicar(arroz):
    _saldo(arroz, "20")
    assert calcular_previsao() == 1
    _saldo(arroz, "5")
    depois = AGORA + timedelta(hours=1)  # mesmo dia: a janela da média não anda
    with patch("django.utils.timezone.now", return_value=depois):
        calcular_previsao()
    previsao = _previsao(arroz)
    assert PrevisaoProduto.objects.count() == 1
    assert previsao.calculado_em == depois
    assert previsao.dias_ate_acabar == Decimal("5.0")


def test_g3_numero_de_consultas_nao_cresce_com_os_produtos(db, django_assert_num_queries):
    for n in range(3):
        _vende_todo_dia(_produto(f"Produto {n}"), "1")
    calcular_previsao()  # aquece o cache de tipos do banco
    with django_assert_num_queries(8):
        calcular_previsao()
    for n in range(3, 10):
        _vende_todo_dia(_produto(f"Produto {n}"), "1")
    with django_assert_num_queries(8):
        calcular_previsao()


def test_g3_comando_calcula_e_diz_quantos_produtos(arroz):
    saida = StringIO()
    call_command("calcular_previsao", stdout=saida)
    assert "1 produto" in saida.getvalue()
    assert PrevisaoProduto.objects.filter(produto=arroz).exists()

"""
Tarefa G4 — histórico mínimo antes de projetar (RN09). Operação 03, passo 4.

> Com menos de 14 dias de histórico de vendas, o sistema não apresenta número de previsão. Em vez
> disso, informa que ainda está aprendendo aquele produto.

Em código (docs/REGRAS-NEGOCIO.md): COUNT(DISTINCT data) FROM consumo_diario WHERE produto_id = :p
menor que `historico_minimo_dias` → não grava número e deixa `calculado_em` nulo. O histórico é o
inteiro, não só os 30 dias da média; e consumo_diario só tem dia com venda (G1), então são dias
COM VENDA. O produto aprendendo continua com a linha em previsao_produto, toda nula — é assim que
a tela sabe dizer "ainda aprendendo".

Losango: dias de histórico ≥ historico_minimo_dias?   sim → *_14_dias_projeta*   não → *_13_dias_*
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from cadastro.models import Categoria, Fornecedor, Produto
from comum.models import Parametro
from estoque.models import Movimentacao
from previsao.agregacao import dia_da_semana
from previsao.models import ConsumoDiario, PrevisaoProduto
from previsao.projecao import calcular_previsao

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
AGORA = datetime(2026, 11, 12, 3, 0, tzinfo=SAO_PAULO)
ONTEM = date(2026, 11, 11)
CAMPOS_DE_NUMERO = [
    "consumo_medio_diario",
    "consumo_por_dia_semana",
    "dias_ate_acabar",
    "ponto_pedido",
    "sugestao_compra",
]


@pytest.fixture(autouse=True)
def madrugada_de_12_11():
    with patch("django.utils.timezone.now", return_value=AGORA):
        yield


@pytest.fixture
def frango(db):
    acougue = Categoria.objects.create(nome="Açougue", perecivel_padrao=True)
    fornecedor = Fornecedor.objects.create(nome="Granja Boa Vista", prazo_entrega_dias=2)
    frango = Produto.objects.create(
        categoria=acougue,
        nome="Frango resfriado 1 kg",
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=4,
        fornecedor_padrao=fornecedor,
    )
    Movimentacao.objects.create(produto=frango, tipo="ENTRADA", quantidade=Decimal("10"))
    return frango


def _vendeu_nos_dias(produto, dias, quantidade="5"):
    for dia in dias:
        ConsumoDiario.objects.create(
            produto=produto, data=dia, quantidade_vendida=Decimal(quantidade), dia_semana=dia_da_semana(dia)
        )


def _ultimos(n):
    return [ONTEM - timedelta(days=k) for k in range(n)]


def _aprendendo(produto):
    previsao = PrevisaoProduto.objects.get(produto=produto)
    return previsao.calculado_em is None and all(
        getattr(previsao, campo) is None for campo in CAMPOS_DE_NUMERO
    )


def test_rn09_produto_cadastrado_ha_6_dias_ainda_aprendendo(frango):
    # O teste da apostila: mostra "ainda aprendendo", não "acaba em 2 dias".
    _vendeu_nos_dias(frango, _ultimos(6))
    calcular_previsao()
    assert _aprendendo(frango)


def test_rn09_13_dias_de_historico_ainda_aprendendo(frango):
    _vendeu_nos_dias(frango, _ultimos(13))
    calcular_previsao()
    assert _aprendendo(frango)


def test_rn09_14_dias_projeta(frango):
    _vendeu_nos_dias(frango, _ultimos(14))
    calcular_previsao()
    previsao = PrevisaoProduto.objects.get(produto=frango)
    assert previsao.calculado_em == AGORA
    assert previsao.consumo_medio_diario == Decimal("2.333")  # 14 × 5 ÷ 30 (RN06)
    assert previsao.dias_ate_acabar is not None and previsao.ponto_pedido is not None


def test_rn09_sem_venda_nenhuma_ainda_aprendendo(frango):
    calcular_previsao()
    assert _aprendendo(frango)


def test_rn09_conta_o_historico_inteiro_e_nao_so_os_30_dias(frango):
    _vendeu_nos_dias(frango, [date(2026, 8, 1) + timedelta(days=k) for k in range(10)])
    _vendeu_nos_dias(frango, _ultimos(4))
    calcular_previsao()
    assert not _aprendendo(frango)


def test_rn09_conta_dias_e_nao_quantidade(frango):
    # Vender muito em poucos dias não encurta o aprendizado.
    _vendeu_nos_dias(frango, _ultimos(3), quantidade="500")
    calcular_previsao()
    assert _aprendendo(frango)


def test_rn09_minimo_vem_da_tabela_de_parametros(frango):
    Parametro.objects.filter(chave="historico_minimo_dias").update(valor="20")
    _vendeu_nos_dias(frango, _ultimos(14))
    calcular_previsao()
    assert _aprendendo(frango)


def test_rn09_produto_que_aprendeu_ganha_numero_na_rodada_seguinte(frango):
    _vendeu_nos_dias(frango, _ultimos(13))
    calcular_previsao()
    assert _aprendendo(frango)
    _vendeu_nos_dias(frango, [ONTEM - timedelta(days=13)])
    calcular_previsao()
    assert not _aprendendo(frango)

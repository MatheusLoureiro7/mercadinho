"""
Tarefa G2 — consumo médio (RN06) e por dia da semana (RN07). Operação 03, passo 4.

RN06: total vendido nos últimos 30 dias ÷ 30 — sempre 30, nunca o número de dias com venda.
RN07: média separada por dia da semana; a projeção usa a maior das duas quando a diferença for
relevante. Decisão do grupo (12/11/2026, lacuna L02): relevante = média do dia da semana
≥ 1,5 × média geral.

- Os últimos 30 dias são os mesmos da rodada da G1: até ONTEM (as vendas de hoje ainda não
  entraram). Lê de consumo_diario, que só tem VENDA (RN11, G1).
- A média de um dia da semana divide pelas vezes que aquele dia aparece nos 30 dias (4 ou 5),
  contando os dias sem venda como zero — o mesmo critério da RN06.
- Dia da semana (L27): 0 = domingo … 6 = sábado.

Hoje: quinta, 12/11/2026. Janela: terça 13/10 a quarta 11/11 — terça e quarta aparecem 5 vezes,
os demais dias 4.

Losangos, pelo "sim" e pelo "não":
    dia dentro dos 30 dias?        sim → entra na média                    não → *_fora_da_janela_*
    dia da semana ≥ 1,5 × média?   sim → *_cerveja_*, *_exatamente_1_5_*   não → *_1_4_*, *_mais_fraco_*
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from cadastro.models import Categoria, Produto
from estoque.models import Movimentacao
from previsao.agregacao import agregar_consumo_recente, dia_da_semana
from previsao.calculo import FATOR_DIA_RELEVANTE, consumo_de_todos, consumo_do_produto
from previsao.models import ConsumoDiario

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
HOJE = date(2026, 11, 12)  # quinta
ONTEM = date(2026, 11, 11)
INICIO = date(2026, 10, 13)  # 30 dias até ontem
DIAS = [INICIO + timedelta(days=n) for n in range(30)]
DOMINGO, SEGUNDA, TERCA, QUARTA, QUINTA, SEXTA, SABADO = range(7)
PROXIMO_SABADO = date(2026, 11, 14)
PROXIMA_QUINTA = date(2026, 11, 19)


@pytest.fixture(autouse=True)
def madrugada_de_12_11():
    with patch("django.utils.timezone.now", return_value=datetime(2026, 11, 12, 3, 0, tzinfo=SAO_PAULO)):
        yield


def _produto(nome):
    categoria, _ = Categoria.objects.get_or_create(nome="Secos e molhados")
    return Produto.objects.create(categoria=categoria, nome=nome, unidade_medida="UN")


@pytest.fixture
def arroz(db):
    return _produto("Arroz 5 kg")


@pytest.fixture
def cerveja(db):
    return _produto("Cerveja lata 350 ml")


def _vendeu(produto, dia, quantidade):
    ConsumoDiario.objects.create(
        produto=produto, data=dia, quantidade_vendida=Decimal(quantidade), dia_semana=dia_da_semana(dia)
    )


def _todo_dia(produto, quantidade, exceto=()):
    for dia in DIAS:
        if dia_da_semana(dia) not in exceto:
            _vendeu(produto, dia, quantidade)


# --- RN06 -----------------------------------------------------------------------------------------


def test_rn06_arroz_150_em_30_dias_da_5_por_dia(arroz):
    _todo_dia(arroz, "5")
    assert consumo_do_produto(arroz).medio_diario == Decimal("5.000")


def test_rn06_divide_por_30_mesmo_vendendo_so_em_5_dias(arroz):
    for dia in DIAS[:5]:
        _vendeu(arroz, dia, "6")
    assert consumo_do_produto(arroz).medio_diario == Decimal("1.000")


def test_rn06_venda_fora_da_janela_nao_entra(arroz):
    _vendeu(arroz, INICIO - timedelta(days=1), "300")  # 31 dias atrás
    _vendeu(arroz, HOJE, "300")  # hoje ainda não fechou
    _vendeu(arroz, ONTEM, "30")
    assert consumo_do_produto(arroz).medio_diario == Decimal("1.000")


def test_rn06_media_com_tres_casas(arroz):
    _vendeu(arroz, ONTEM, "10")
    assert consumo_do_produto(arroz).medio_diario == Decimal("0.333")


def test_rn06_sem_venda_nenhuma_media_zero(arroz):
    consumo = consumo_do_produto(arroz)
    assert consumo.medio_diario == Decimal("0.000")
    assert consumo.do_dia(PROXIMO_SABADO) == Decimal("0.000")


def test_rn11_perda_nao_aumenta_a_media(arroz):
    # Do começo ao fim: venda e perda na movimentação → G1 → G2.
    for tipo, quantidade in (("VENDA", "30"), ("PERDA", "300")):
        Movimentacao.objects.create(
            produto=arroz,
            tipo=tipo,
            quantidade=Decimal(quantidade),
            data_hora=datetime(2026, 11, 11, 10, 0, tzinfo=SAO_PAULO),
            motivo="Estragou" if tipo == "PERDA" else None,
        )
    agregar_consumo_recente()
    assert consumo_do_produto(arroz).medio_diario == Decimal("1.000")


# --- RN07 -----------------------------------------------------------------------------------------


def test_rn07_media_do_dia_divide_pelas_vezes_que_o_dia_aparece(arroz):
    _todo_dia(arroz, "2")  # terça aparece 5 vezes (10 ÷ 5), sábado 4 (8 ÷ 4)
    consumo = consumo_do_produto(arroz)
    assert consumo.por_dia_semana[TERCA] == Decimal("2.000")
    assert consumo.por_dia_semana[SABADO] == Decimal("2.000")


def test_rn07_dia_sem_venda_conta_como_zero_na_media_do_dia(arroz):
    sabados = [dia for dia in DIAS if dia_da_semana(dia) == SABADO]
    _vendeu(arroz, sabados[0], "12")  # vendeu num dos 4 sábados
    assert consumo_do_produto(arroz).por_dia_semana[SABADO] == Decimal("3.000")


def test_rn07_sete_dias_sempre_presentes(arroz):
    _vendeu(arroz, ONTEM, "7")
    por_dia = consumo_do_produto(arroz).por_dia_semana
    assert sorted(por_dia) == list(range(7))
    assert por_dia[QUARTA] == Decimal("1.400") and por_dia[DOMINGO] == Decimal("0.000")


def test_rn07_cerveja_8_por_dia_26_no_sabado_a_projecao_do_sabado_usa_26(cerveja):
    # O exemplo da RN07. 4 sábados × 26 = 104; 26 outros dias × 5 = 130; +6 numa sexta = 240 → 8/dia.
    _todo_dia(cerveja, "26", exceto=[d for d in range(7) if d != SABADO])
    _todo_dia(cerveja, "5", exceto=[SABADO])
    sexta = next(dia for dia in DIAS if dia_da_semana(dia) == SEXTA)
    ConsumoDiario.objects.filter(produto=cerveja, data=sexta).update(quantidade_vendida=Decimal("11"))

    consumo = consumo_do_produto(cerveja)
    assert consumo.medio_diario == Decimal("8.000")
    assert consumo.por_dia_semana[SABADO] == Decimal("26.000")
    # Na quinta, a projeção dos próximos dias usa o número do sábado, não a média.
    assert consumo.do_dia(PROXIMO_SABADO) == Decimal("26.000")
    assert consumo.do_dia(PROXIMA_QUINTA) == Decimal("8.000")


def test_rn07_dia_exatamente_1_5_vez_a_media_e_relevante(arroz):
    # 4 sábados × 3 = 12; 26 outros dias: 48 → total 60 → média 2; sábado 3 = 1,5 × 2.
    _todo_dia(arroz, "3", exceto=[d for d in range(7) if d != SABADO])
    outros = [dia for dia in DIAS if dia_da_semana(dia) != SABADO]
    for dia in outros[:24]:
        _vendeu(arroz, dia, "2")
    consumo = consumo_do_produto(arroz)
    assert (consumo.medio_diario, consumo.por_dia_semana[SABADO]) == (Decimal("2.000"), Decimal("3.000"))
    assert consumo.do_dia(PROXIMO_SABADO) == Decimal("3.000")


def test_rn07_dia_1_4_vez_a_media_nao_e_relevante_usa_a_media(arroz):
    # Sábado 2,8 (4 × 2,8 = 11,2); 26 outros dias × 1,8 = 46,8, +2 num deles → total 60, média 2.
    _todo_dia(arroz, "2.8", exceto=[d for d in range(7) if d != SABADO])
    _todo_dia(arroz, "1.8", exceto=[SABADO])
    outro = next(dia for dia in DIAS if dia_da_semana(dia) != SABADO)
    ConsumoDiario.objects.filter(produto=arroz, data=outro).update(quantidade_vendida=Decimal("3.8"))
    consumo = consumo_do_produto(arroz)
    assert (consumo.medio_diario, consumo.por_dia_semana[SABADO]) == (Decimal("2.000"), Decimal("2.800"))
    assert consumo.do_dia(PROXIMO_SABADO) == Decimal("2.000")


def test_rn07_dia_mais_fraco_que_a_media_usa_a_media(arroz):
    # Usa a MAIOR das duas: domingo sem venda nenhuma não derruba a projeção.
    _todo_dia(arroz, "3", exceto=[DOMINGO])
    consumo = consumo_do_produto(arroz)
    assert consumo.por_dia_semana[DOMINGO] == Decimal("0.000")
    assert consumo.do_dia(date(2026, 11, 15)) == consumo.medio_diario


def test_l02_fator_decidido_pelo_grupo_e_1_5():
    assert Decimal("1.5") == FATOR_DIA_RELEVANTE


# --- Todos os produtos de uma vez (rodada diária) -------------------------------------------------


def test_g2_consumo_de_todos_numa_consulta_igual_ao_de_cada_um(arroz, cerveja, django_assert_num_queries):
    _todo_dia(arroz, "5")
    _vendeu(cerveja, ONTEM, "30")
    sem_venda = _produto("Fósforo")
    with django_assert_num_queries(2):  # produtos + consumo_diario
        todos = consumo_de_todos()
    assert todos[arroz.pk] == consumo_do_produto(arroz)
    assert todos[cerveja.pk] == consumo_do_produto(cerveja)
    assert todos[sem_venda.pk].medio_diario == Decimal("0.000")

"""
Tarefa H3 — gerador do aviso de ruptura (RN08) e de fim de semana (RN10). Operação 03, passos 6 a 8.

RN08: saldo <= ponto_pedido → alerta RUPTURA ("o frango acaba em 2 dias", RNF10).
RN10: na quinta, produto crítico de fim de semana → compara o saldo com
      ponto_pedido × (1 + folga_fim_semana_pct ÷ 100) → alerta FIM_SEMANA.
L03 (decidida pelo grupo em 12/11/2026): sem calendário de feriados nesta versão — só sábado e
domingo, avaliados na quinta. Véspera de feriado fica fora do escopo, declarado.

Decisões da H3 (as mesmas da H2 onde cabem):
- produto "ainda aprendendo" (RN09) ou sem fornecedor (sem ponto de pedido, G3) não avisa;
- todo dia, enquanto a condição valer; rodar duas vezes no mesmo dia não duplica; o aviso de um
  dia anterior que não saiu dá lugar ao de hoje;
- urgência (L11): ALTA quando acabou ou acaba antes de a entrega chegar (dias até acabar menor
  que o prazo do fornecedor); MEDIA nos outros casos; fim de semana, MEDIA;
- produto crítico já abaixo do ponto de pedido na quinta: só o aviso de "vai acabar" (que tem o
  botão "Sim, pedir", H7) — não dois avisos do mesmo produto.

Losangos, pelo "sim" e pelo "não":
    tem previsão com ponto de pedido?    sim → segue           não → *_rn09_*, *_sem_fornecedor_*
    saldo <= ponto de pedido?            sim → *_rn08_avisa_*  não → *_rn08_acima_*
    hoje é quinta?                       sim → *_rn10_quinta_* não → *_rn10_quarta_*
    produto crítico?                     sim → *_rn10_quinta_* não → *_rn10_nao_critico_*
    saldo <= ponto × (1 + folga)?        sim → *_rn10_quinta_* não → *_rn10_acima_da_folga_*
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from alertas.models import Alerta
from alertas.ruptura import gerar_avisos_de_ruptura
from cadastro.models import Categoria, Fornecedor, Produto, Usuario
from comum.models import Parametro
from estoque.models import Movimentacao
from previsao.models import PrevisaoProduto

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
QUINTA = datetime(2026, 11, 12, 3, 0, tzinfo=SAO_PAULO)
QUARTA = QUINTA - timedelta(days=1)


@pytest.fixture(autouse=True)
def madrugada_de_quarta():
    with patch("django.utils.timezone.now", return_value=QUARTA):
        yield


@pytest.fixture
def dono(db):
    return Usuario.objects.create_user(login="joao", senha="Mercado#2026", nome="Sr. João", papel="DONO")


def _produto(nome, prazo=2, critico=False, unidade="KG"):
    categoria, _ = Categoria.objects.get_or_create(nome="Açougue")
    fornecedor = (
        Fornecedor.objects.create(nome="Granja Boa Vista", prazo_entrega_dias=prazo)
        if prazo is not None
        else None
    )
    return Produto.objects.create(
        categoria=categoria,
        nome=nome,
        unidade_medida=unidade,
        fornecedor_padrao=fornecedor,
        critico_fim_semana=critico,
    )


def _previsao(produto, *, ponto="10", dias="2.5", sugestao="30", aprendendo=False):
    return PrevisaoProduto.objects.create(
        produto=produto,
        consumo_medio_diario=None if aprendendo else Decimal("4"),
        dias_ate_acabar=None if aprendendo else (Decimal(dias) if dias is not None else None),
        ponto_pedido=None if aprendendo or ponto is None else Decimal(ponto),
        sugestao_compra=None if aprendendo or sugestao is None else Decimal(sugestao),
        calculado_em=None if aprendendo else QUARTA,
    )


def _saldo(produto, quantidade):
    if Decimal(quantidade) > 0:
        Movimentacao.objects.create(produto=produto, tipo="ENTRADA", quantidade=Decimal(quantidade))
    elif Decimal(quantidade) < 0:
        Movimentacao.objects.create(produto=produto, tipo="VENDA", quantidade=-Decimal(quantidade))


@pytest.fixture
def frango(db):
    return _produto("Frango resfriado 1 kg")


def _avisos(produto, **filtro):
    return list(Alerta.objects.filter(produto=produto, **filtro).order_by("id"))


# --- RN08 -----------------------------------------------------------------------------------------


def test_rn08_avisa_quando_o_saldo_cai_abaixo_do_ponto_de_pedido(frango, dono):
    _previsao(frango, ponto="10", dias="2.5", sugestao="30")
    _saldo(frango, "6")
    criados = gerar_avisos_de_ruptura()
    assert len(criados) == 1
    aviso = criados[0]
    assert (aviso.tipo, aviso.status, aviso.destinatario) == ("RUPTURA", "PENDENTE", dono)
    assert aviso.mensagem == (
        "Frango resfriado 1 kg acaba em 2 dias — sobram 6 KG. "
        "Pedir 30 KG — Granja Boa Vista entrega em 2 dias."
    )


def test_rn08_avisa_com_o_saldo_igual_ao_ponto_de_pedido(frango, dono):
    _previsao(frango, ponto="10")
    _saldo(frango, "10")
    assert len(gerar_avisos_de_ruptura()) == 1


def test_rn08_acima_do_ponto_de_pedido_nao_avisa(frango, dono):
    _previsao(frango, ponto="10")
    _saldo(frango, "10.001")
    assert gerar_avisos_de_ruptura() == []


def test_rn09_produto_ainda_aprendendo_nao_avisa_nem_sem_estoque(frango, dono):
    _previsao(frango, aprendendo=True)
    assert gerar_avisos_de_ruptura() == []


def test_rn09_previsao_sem_hora_de_calculo_e_ainda_aprendendo_mesmo_com_numero(frango, dono):
    # A G4 grava a linha toda nula; se um número sobrar, quem manda é o calculado_em nulo (RN09).
    _previsao(frango, ponto="10")
    PrevisaoProduto.objects.filter(produto=frango).update(calculado_em=None)
    assert gerar_avisos_de_ruptura() == []


def test_rn08_produto_sem_previsao_nao_avisa(frango, dono):
    assert gerar_avisos_de_ruptura() == []


def test_rn08_sem_fornecedor_nao_tem_ponto_de_pedido_e_nao_avisa(dono):
    sal = _produto("Sal 1 kg", prazo=None)
    _previsao(sal, ponto=None, sugestao=None)
    assert gerar_avisos_de_ruptura() == []


def test_rn08_produto_que_acabou_avisa_com_urgencia_alta(frango, dono):
    _previsao(frango, ponto="10", dias="0", sugestao="40")
    _saldo(frango, "-1.5")
    aviso = gerar_avisos_de_ruptura()[0]
    assert aviso.severidade == "ALTA"
    assert aviso.mensagem == (
        "Frango resfriado 1 kg acabou — não tem mais no estoque. "
        "Pedir 40 KG — Granja Boa Vista entrega em 2 dias."
    )


def test_rn08_acaba_antes_da_entrega_chegar_e_urgencia_alta(frango, dono):
    _previsao(frango, dias="1.9")  # entrega em 2 dias
    _saldo(frango, "6")
    assert gerar_avisos_de_ruptura()[0].severidade == "ALTA"


def test_rn08_acaba_depois_da_entrega_e_urgencia_media(frango, dono):
    _previsao(frango, dias="2.0")
    _saldo(frango, "6")
    assert gerar_avisos_de_ruptura()[0].severidade == "MEDIA"


@pytest.mark.parametrize(
    "dias, quando",
    [("0.4", "acaba hoje"), ("1.7", "acaba amanhã"), ("3.9", "acaba em 3 dias")],
)
def test_rnf10_dias_contados_por_inteiro_no_vocabulario_da_loja(frango, dono, dias, quando):
    _previsao(frango, dias=dias)
    _saldo(frango, "6")
    mensagem = gerar_avisos_de_ruptura()[0].mensagem
    assert mensagem.startswith(f"Frango resfriado 1 kg {quando} — ")
    assert "ponto" not in mensagem.lower() and "ruptura" not in mensagem.lower()


def test_rnf10_prazo_de_um_dia_no_singular(dono):
    pao = _produto("Pão francês", prazo=1)
    _previsao(pao, dias="3")
    _saldo(pao, "6")
    assert gerar_avisos_de_ruptura()[0].mensagem.endswith("Granja Boa Vista entrega em 1 dia.")


def test_rn08_sem_sugestao_de_compra_nao_diz_quanto_pedir(frango, dono):
    _previsao(frango, sugestao="0")
    _saldo(frango, "6")
    assert gerar_avisos_de_ruptura()[0].mensagem == "Frango resfriado 1 kg acaba em 2 dias — sobram 6 KG."


def test_rn08_sem_dono_o_aviso_e_gravado_sem_destinatario(frango):
    _previsao(frango)
    _saldo(frango, "6")
    assert gerar_avisos_de_ruptura()[0].destinatario is None


# --- Repetição ------------------------------------------------------------------------------------


def test_rn08_rodar_duas_vezes_no_mesmo_dia_nao_duplica(frango, dono):
    _previsao(frango)
    _saldo(frango, "6")
    gerar_avisos_de_ruptura()
    assert gerar_avisos_de_ruptura() == []
    assert len(_avisos(frango)) == 1


def test_rn08_aviso_de_ontem_que_nao_saiu_da_lugar_ao_de_hoje(frango, dono):
    _previsao(frango)
    _saldo(frango, "6")
    with patch("django.utils.timezone.now", return_value=QUARTA - timedelta(days=1)):
        gerar_avisos_de_ruptura()
    gerar_avisos_de_ruptura()
    ontem, hoje = _avisos(frango)
    assert (ontem.status, hoje.status) == ("CANCELADO", "PENDENTE")


def test_rn08_aviso_de_ontem_ja_enviado_continua_enviado_e_hoje_avisa_de_novo(frango, dono):
    _previsao(frango)
    _saldo(frango, "6")
    with patch("django.utils.timezone.now", return_value=QUARTA - timedelta(days=1)):
        gerar_avisos_de_ruptura()
    Alerta.objects.update(status="ENVIADO", enviado_em=QUARTA - timedelta(hours=20))
    gerar_avisos_de_ruptura()
    assert [aviso.status for aviso in _avisos(frango)] == ["ENVIADO", "PENDENTE"]


# --- Depois do "Sim, pedir" ----------------------------------------------------------------------
# Decisão do grupo (12/11/2026): depois que o Sr. João responde "Sim, pedir", o produto não é
# avisado de novo até chegar um lote novo dele — o pedido está a caminho.


def _respondeu_sim(produto, quando):
    with patch("django.utils.timezone.now", return_value=quando):
        aviso = gerar_avisos_de_ruptura()[0]
    Alerta.objects.filter(pk=aviso.pk).update(
        status="ENVIADO", enviado_em=quando, resposta_usuario="Sim, pedir"
    )


def _lote_chegou(produto, dia, quantidade="1"):
    from estoque.models import Lote

    Lote.objects.create(
        produto=produto,
        quantidade_inicial=Decimal(quantidade),
        quantidade_atual=Decimal(quantidade),
        data_entrada=dia,
    )


def test_h3_depois_do_sim_pedir_nao_avisa_de_novo_ate_chegar_mercadoria(frango, dono):
    _previsao(frango)
    _saldo(frango, "6")
    _respondeu_sim(frango, QUARTA - timedelta(days=1))
    assert gerar_avisos_de_ruptura() == []


def test_h3_depois_do_sim_pedir_nem_o_aviso_de_fim_de_semana(carvao, dono):
    _previsao(carvao, ponto="10")
    _saldo(carvao, "8")
    _respondeu_sim(carvao, QUARTA)
    PrevisaoProduto.objects.filter(produto=carvao).update(ponto_pedido=Decimal("9"))  # 8 ≤ 9 × 1,4
    with patch("django.utils.timezone.now", return_value=QUINTA):
        assert gerar_avisos_de_ruptura() == []


def test_h3_chegou_lote_depois_do_sim_e_continua_baixo_avisa_de_novo(frango, dono):
    _previsao(frango)
    _saldo(frango, "6")
    _respondeu_sim(frango, QUARTA - timedelta(days=2))
    _lote_chegou(frango, date(2026, 11, 10))
    assert len(gerar_avisos_de_ruptura()) == 1


def test_h3_lote_que_chegou_no_mesmo_dia_do_sim_conta_como_chegado(frango, dono):
    # O aviso nasce às 03h00; a entrega das 10h00 do mesmo dia já é a mercadoria pedida.
    _previsao(frango)
    _saldo(frango, "6")
    _respondeu_sim(frango, QUARTA - timedelta(days=1))
    _lote_chegou(frango, date(2026, 11, 10))
    assert len(gerar_avisos_de_ruptura()) == 1


def test_h3_lote_antigo_nao_conta_como_chegada_do_pedido(frango, dono):
    _previsao(frango)
    _saldo(frango, "6")
    _lote_chegou(frango, date(2026, 11, 1))
    _respondeu_sim(frango, QUARTA - timedelta(days=1))
    assert gerar_avisos_de_ruptura() == []


@pytest.fixture
def carvao(db):
    return _produto("Carvão 5 kg", critico=True, unidade="UN")


# --- RN10 -----------------------------------------------------------------------------------------


def test_rn10_quinta_critico_dentro_da_folga_avisa_para_o_fim_de_semana(carvao, dono):
    _previsao(carvao, ponto="10", dias="4.2", sugestao="20")
    _saldo(carvao, "14")  # 10 × 1,4 = 14
    with patch("django.utils.timezone.now", return_value=QUINTA):
        criados = gerar_avisos_de_ruptura()
    assert [(aviso.tipo, aviso.severidade) for aviso in criados] == [("FIM_SEMANA", "MEDIA")]
    assert criados[0].mensagem == (
        "Para o fim de semana: Carvão 5 kg acaba em 4 dias — sobram 14 UN. "
        "Pedir 20 UN — Granja Boa Vista entrega em 2 dias."
    )


def test_rn10_quinta_acima_da_folga_nao_avisa(carvao, dono):
    _previsao(carvao, ponto="10")
    _saldo(carvao, "14.001")
    with patch("django.utils.timezone.now", return_value=QUINTA):
        assert gerar_avisos_de_ruptura() == []


def test_rn10_quarta_nao_avalia_o_fim_de_semana(carvao, dono):
    _previsao(carvao, ponto="10")
    _saldo(carvao, "12")
    assert gerar_avisos_de_ruptura() == []


def test_rn10_quinta_produto_nao_critico_nao_avisa_pelo_fim_de_semana(frango, dono):
    _previsao(frango, ponto="10")
    _saldo(frango, "12")
    with patch("django.utils.timezone.now", return_value=QUINTA):
        assert gerar_avisos_de_ruptura() == []


def test_rn10_quinta_critico_abaixo_do_ponto_recebe_so_o_aviso_de_vai_acabar(carvao, dono):
    _previsao(carvao, ponto="10")
    _saldo(carvao, "8")
    with patch("django.utils.timezone.now", return_value=QUINTA):
        criados = gerar_avisos_de_ruptura()
    assert [aviso.tipo for aviso in criados] == ["RUPTURA"]


def test_rn10_folga_vem_da_tabela_de_parametros(carvao, dono):
    Parametro.objects.filter(chave="folga_fim_semana_pct").update(valor="10")
    _previsao(carvao, ponto="10")
    _saldo(carvao, "12")  # acima de 10 × 1,1
    with patch("django.utils.timezone.now", return_value=QUINTA):
        assert gerar_avisos_de_ruptura() == []


def test_l03_sexta_nao_e_avaliada_sem_calendario_de_feriados(carvao, dono):
    _previsao(carvao, ponto="10")
    _saldo(carvao, "12")
    with patch("django.utils.timezone.now", return_value=QUINTA + timedelta(days=1)):
        assert gerar_avisos_de_ruptura() == []


def test_rn10_quinta_rodar_duas_vezes_nao_duplica(carvao, dono):
    _previsao(carvao, ponto="10")
    _saldo(carvao, "12")
    with patch("django.utils.timezone.now", return_value=QUINTA):
        gerar_avisos_de_ruptura()
        assert gerar_avisos_de_ruptura() == []


# --- Na rodada ------------------------------------------------------------------------------------


def test_h3_entrada_de_mercadoria_cancela_o_aviso_que_ainda_nao_saiu(frango, dono):
    from estoque.entrada import registrar_entrada

    _previsao(frango)
    _saldo(frango, "6")
    gerar_avisos_de_ruptura()
    registrar_entrada(usuario=None, produto=frango, quantidade=Decimal("30"))
    assert [aviso.status for aviso in _avisos(frango)] == ["CANCELADO"]


def test_h3_usa_a_data_da_loja(frango, dono):
    # 22h30 de quarta em São Paulo já é quinta em UTC: ainda não é dia de avaliar o fim de semana.
    carvao = _produto("Carvão 5 kg", critico=True, unidade="UN")
    _previsao(carvao, ponto="10")
    _saldo(carvao, "12")
    with patch("django.utils.timezone.now", return_value=datetime(2026, 11, 11, 22, 30, tzinfo=SAO_PAULO)):
        assert gerar_avisos_de_ruptura() == []
    assert date(2026, 11, 12).isoweekday() == 4

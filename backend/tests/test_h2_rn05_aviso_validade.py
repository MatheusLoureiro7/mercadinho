"""
Tarefa H2 — gerador do aviso de validade (RN05).

> Gera um aviso quando um lote de produto perecível está a N dias ou menos do vencimento.
  Condição: lote.data_validade − hoje ≤ dias_aviso_validade AND quantidade_atual > 0.

Decisões da H2 (docs/ACOMPANHAMENTO.md, 08/10/2026):
- todo dia, enquanto o lote estiver no prazo e com mercadoria (a RN13 junta os do dia numa
  mensagem só); rodar duas vezes no mesmo dia não duplica;
- lote vencido também avisa (a condição o inclui), com frase própria: sai só como perda (RN16);
- o aviso de ontem que não chegou a sair é substituído pelo de hoje (contagem de dias atual);
- urgência (L11): ALTA para vencido e para o que vence hoje, MEDIA para o que ainda tem dias;
- destinatário: o usuário DONO ativo (o celular dele é ligado na H6).
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.utils import timezone

from alertas.estados import enviar
from alertas.models import Alerta
from alertas.validade import gerar_avisos_de_validade
from cadastro.models import Categoria, Produto, Usuario
from comum.models import Parametro
from estoque.models import Lote

DIA_21 = date(2026, 9, 21)  # o exemplo da Apostila I
SAO_PAULO = ZoneInfo("America/Sao_Paulo")


@pytest.fixture
def frios(db):
    return Categoria.objects.create(nome="Frios", perecivel_padrao=True)


@pytest.fixture
def presunto(frios):
    return Produto.objects.create(
        nome="Presunto", categoria=frios, unidade_medida="KG", perecivel=True, durabilidade_dias=7
    )


@pytest.fixture
def iogurte(frios):
    return Produto.objects.create(
        nome="Iogurte natural", categoria=frios, unidade_medida="UN", perecivel=True, durabilidade_dias=15
    )


@pytest.fixture
def dono(db):
    return Usuario.objects.create_user(login="joao", senha="Mercado#2026", nome="Sr. João", papel="DONO")


def _lote(produto, validade, quantidade="2.5"):
    return Lote.objects.create(
        produto=produto,
        quantidade_inicial=Decimal(quantidade),
        quantidade_atual=Decimal(quantidade),
        data_entrada=DIA_21 - timedelta(days=5),
        data_validade=validade,
    )


def _rodada(hoje=DIA_21):
    """A rodada roda às 03h00 do dia da loja; o aviso nasce com essa hora (gerado_em)."""
    madrugada = datetime(hoje.year, hoje.month, hoje.day, 3, 0, tzinfo=SAO_PAULO)
    with patch("django.utils.timezone.now", return_value=madrugada):
        return gerar_avisos_de_validade(hoje=hoje)


# ------------------------------------------------------------------------------------------------
# A condição da RN05
# ------------------------------------------------------------------------------------------------


def test_rn05_lote_que_vence_dentro_do_prazo_gera_aviso(presunto, dono):
    # Apostila I: lote vence 24/09, parâmetro em 3 dias → aviso gerado em 21/09.
    lote = _lote(presunto, date(2026, 9, 24))

    [aviso] = _rodada()

    assert aviso.tipo == "VALIDADE"
    assert aviso.status == "PENDENTE"
    assert aviso.lote == lote and aviso.produto == presunto
    assert aviso.mensagem == "Presunto vence em 3 dias — 2,5 KG na prateleira."
    assert aviso.severidade == "MEDIA"
    assert aviso.destinatario == dono


def test_rn05_lote_fora_do_prazo_nao_gera_aviso(presunto):
    _lote(presunto, date(2026, 9, 30))

    assert _rodada() == []
    assert not Alerta.objects.exists()


def test_rn05_um_dia_alem_do_prazo_nao_gera_aviso(presunto):
    _lote(presunto, date(2026, 9, 25))  # 4 dias, parâmetro 3

    assert _rodada() == []


def test_rn05_lote_zerado_nao_gera_aviso(presunto):
    _lote(presunto, date(2026, 9, 23), quantidade="0")

    assert _rodada() == []


def test_rn05_produto_nao_perecivel_nao_gera_aviso(db):
    secos = Categoria.objects.create(nome="Secos e molhados")
    arroz = Produto.objects.create(nome="Arroz 5 kg", categoria=secos, unidade_medida="PCT")
    _lote(arroz, date(2026, 9, 22))  # validade anotada, mas o produto não é perecível

    assert _rodada() == []


def test_rn05_lote_sem_validade_nao_gera_aviso(presunto):
    _lote(presunto, None)

    assert _rodada() == []


def test_rn05_n_vem_do_parametro_e_nao_do_codigo(presunto):
    Parametro.objects.filter(chave="dias_aviso_validade").update(valor="5")
    _lote(presunto, date(2026, 9, 26))  # 5 dias

    assert len(_rodada()) == 1


def test_rn05_l01_o_prazo_e_lido_por_produto(presunto, iogurte):
    # L01: o prazo é global hoje, mas é lido produto a produto — quando o grupo decidir "por
    # categoria", muda um lugar só (comum.parametros.dias_aviso_validade).
    _lote(presunto, date(2026, 9, 25))
    _lote(iogurte, date(2026, 9, 25))

    def prazo(produto=None):
        return 4 if produto == presunto else 3

    with patch("alertas.validade.dias_aviso_validade", side_effect=prazo):
        avisos = _rodada()

    assert [a.produto for a in avisos] == [presunto]


def test_x1_prazo_e_lido_uma_vez_por_produto_e_nao_uma_vez_por_lote(presunto, iogurte):
    """X1, item 21: com centenas de lotes, eram centenas de leituras iguais (RNF06)."""
    for dia in range(20, 30):
        _lote(presunto, date(2026, 9, dia))
    _lote(iogurte, date(2026, 9, 22))

    with patch("alertas.validade.dias_aviso_validade", return_value=3) as prazo:
        _rodada()

    assert sorted(chamada.args[0].nome for chamada in prazo.call_args_list) == ["Iogurte natural", "Presunto"]


# ------------------------------------------------------------------------------------------------
# A frase e a urgência (RNF10, L11)
# ------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("validade", "mensagem", "severidade"),
    [
        (date(2026, 9, 23), "Presunto vence em 2 dias — 2,5 KG na prateleira.", "MEDIA"),
        (date(2026, 9, 22), "Presunto vence amanhã — 2,5 KG na prateleira.", "MEDIA"),
        (date(2026, 9, 21), "Presunto vence hoje — 2,5 KG na prateleira.", "ALTA"),
    ],
)
def test_rn05_frase_e_urgencia_de_quem_ainda_vai_vencer(presunto, validade, mensagem, severidade):
    _lote(presunto, validade)

    [aviso] = _rodada()

    assert (aviso.mensagem, aviso.severidade) == (mensagem, severidade)


@pytest.mark.parametrize(
    ("validade", "quando"),
    [(date(2026, 9, 20), "venceu ontem"), (date(2026, 9, 18), "venceu há 3 dias")],
)
def test_rn05_rn16_lote_vencido_avisa_que_so_sai_como_perda(iogurte, validade, quando):
    _lote(iogurte, validade, quantidade="3")

    [aviso] = _rodada()

    assert aviso.mensagem == (
        f"Iogurte natural {quando} — 3 UN na prateleira. Tire e registre a perda em Avarias e quebras."
    )
    assert aviso.severidade == "ALTA"


def test_rn05_cada_lote_no_prazo_tem_o_seu_aviso(presunto):
    vence_amanha = _lote(presunto, date(2026, 9, 22), quantidade="1")
    vence_em_3 = _lote(presunto, date(2026, 9, 24))

    avisos = _rodada()

    assert {a.lote for a in avisos} == {vence_amanha, vence_em_3}


# ------------------------------------------------------------------------------------------------
# Todo dia, sem duplicar no mesmo dia
# ------------------------------------------------------------------------------------------------


def test_rn05_avisa_de_novo_no_dia_seguinte_enquanto_vale(presunto):
    lote = _lote(presunto, date(2026, 9, 24))
    enviar(_rodada(DIA_21), quando=timezone.now())  # o de 21/09 saiu

    [de_hoje] = _rodada(DIA_21 + timedelta(days=1))

    assert de_hoje.mensagem == "Presunto vence em 2 dias — 2,5 KG na prateleira."
    assert Alerta.objects.filter(lote=lote).count() == 2


def test_rn05_rodar_duas_vezes_no_mesmo_dia_nao_duplica(presunto):
    _lote(presunto, date(2026, 9, 24))

    _rodada()
    segunda = _rodada()

    assert segunda == []
    assert Alerta.objects.count() == 1


def test_rn05_aviso_de_ontem_que_nao_saiu_e_trocado_pelo_de_hoje(presunto):
    lote = _lote(presunto, date(2026, 9, 24))
    [de_ontem] = _rodada(DIA_21)  # ficou PENDENTE (o Telegram não mandou)

    [de_hoje] = _rodada(DIA_21 + timedelta(days=1))

    de_ontem.refresh_from_db()
    assert de_ontem.status == "CANCELADO"
    assert list(Alerta.objects.a_enviar().filter(lote=lote)) == [de_hoje]


def test_rn05_aviso_de_ontem_ja_enviado_fica_como_esta(presunto):
    _lote(presunto, date(2026, 9, 24))
    [de_ontem] = _rodada(DIA_21)
    enviar([de_ontem], quando=timezone.now())

    _rodada(DIA_21 + timedelta(days=1))

    de_ontem.refresh_from_db()
    assert de_ontem.status == "ENVIADO"


def test_rn05_lote_que_saiu_do_prazo_ou_zerou_para_de_avisar(presunto):
    lote = _lote(presunto, date(2026, 9, 24))
    _rodada(DIA_21)
    Lote.objects.filter(pk=lote.pk).update(quantidade_atual=0)  # vendido ou perdido

    assert _rodada(DIA_21 + timedelta(days=1)) == []


# ------------------------------------------------------------------------------------------------
# Para quem
# ------------------------------------------------------------------------------------------------


def test_rn05_sem_dono_cadastrado_o_aviso_fica_sem_destinatario(presunto):
    _lote(presunto, date(2026, 9, 24))

    [aviso] = _rodada()

    assert aviso.destinatario is None  # a H5 decide o que fazer; o aviso não se perde


def test_rn05_dono_desativado_nao_recebe(presunto, dono):
    Usuario.objects.filter(pk=dono.pk).update(ativo=False)
    _lote(presunto, date(2026, 9, 24))

    [aviso] = _rodada()

    assert aviso.destinatario is None


def test_rn05_esposa_e_sobrinho_nao_sao_destinatarios(presunto):
    Usuario.objects.create_user(login="esposa", senha="Mercado#2026", nome="Esposa", papel="GESTAO")
    Usuario.objects.create_user(login="sobrinho", senha="Mercado#2026", nome="Sobrinho", papel="OPERACAO")
    _lote(presunto, date(2026, 9, 24))

    [aviso] = _rodada()

    assert aviso.destinatario is None

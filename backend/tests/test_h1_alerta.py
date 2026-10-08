"""
Tarefa H1 — tabela de aviso e controle de estado.

- A tabela `alerta` igual ao schema.sql (Apostila IV): colunas, padrões, restrições e índice.
- Severidade (L11, decidida na H1): ALTA, MEDIA, BAIXA, validadas no código — o banco continua
  igual ao schema.sql, como a unidade de medida (L17). Ordem de urgência da RN13: severidade,
  depois gerado_em.
- Estados (operação 03; RN12, RN13; operação 02, passo 10):

      PENDENTE ──segurar──▶ SEGURADO            (janela de silêncio, RN12)
      PENDENTE/SEGURADO ──enviar──▶ ENVIADO     (todos com o mesmo enviado_em, RN13)
      PENDENTE/SEGURADO ──cancelar──▶ CANCELADO (chegou mercadoria, operação 02 passo 10)
      ENVIADO e CANCELADO não mudam mais.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from alertas.estados import TransicaoDeAvisoInvalida, cancelar, enviar, segurar
from alertas.models import Alerta
from alertas.servicos import cancelar_aviso_de_ruptura_pendente, criar_aviso
from cadastro.models import Categoria, Produto, Usuario
from estoque.entrada import registrar_entrada
from tests.conftest import divergencias_do_schema, indices, restricoes

SAO_PAULO = ZoneInfo("America/Sao_Paulo")


@pytest.fixture
def presunto(db):
    frios = Categoria.objects.create(nome="Frios", perecivel_padrao=True)
    return Produto.objects.create(
        nome="Presunto", categoria=frios, unidade_medida="KG", perecivel=True, durabilidade_dias=7
    )


@pytest.fixture
def frango(db):
    acougue = Categoria.objects.create(nome="Açougue", perecivel_padrao=True)
    return Produto.objects.create(
        nome="Frango resfriado 1 kg",
        categoria=acougue,
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=4,
    )


@pytest.fixture
def dono(db):
    return Usuario.objects.create_user(login="joao", senha="Mercado#2026", nome="Sr. João", papel="DONO")


def _aviso(produto, tipo="VALIDADE", severidade="MEDIA", **campos):
    return criar_aviso(
        produto=produto, tipo=tipo, severidade=severidade, mensagem=f"Aviso de {produto.nome}", **campos
    )


# ------------------------------------------------------------------------------------------------
# A tabela, igual à Apostila IV
# ------------------------------------------------------------------------------------------------


def test_h1_tabela_igual_ao_schema(db):
    assert divergencias_do_schema("alerta") == []


def test_h1_restricoes_do_schema_existem(db):
    assert {"ck_alerta_tipo", "ck_alerta_status"} <= restricoes("alerta")


def test_h1_l11_banco_nao_ganhou_restricao_de_severidade(db):
    # L11: a lista de severidades é validada no código; o banco fica igual ao schema.sql.
    checks = {nome for nome in restricoes("alerta") if nome.startswith("ck_")}
    assert checks == {"ck_alerta_tipo", "ck_alerta_status"}


def test_h1_indice_dos_pendentes_do_schema_existe(db):
    assert "(status, gerado_em)" in indices("alerta")["ix_alerta_pendente"]


def test_h1_padroes_do_schema(presunto):
    aviso = _aviso(presunto)
    aviso.refresh_from_db()

    assert aviso.status == "PENDENTE"
    assert aviso.canal == "TELEGRAM"
    assert aviso.gerado_em is not None
    assert aviso.enviado_em is None


@pytest.mark.parametrize("tipo", ["VALIDADE", "RUPTURA", "FIM_SEMANA"])
def test_h1_tipos_do_schema_sao_aceitos(presunto, tipo):
    assert _aviso(presunto, tipo=tipo).tipo == tipo


def test_h1_banco_recusa_tipo_fora_do_schema(presunto):
    with pytest.raises(IntegrityError), transaction.atomic():
        Alerta.objects.create(produto=presunto, tipo="PROMOCAO", severidade="MEDIA", mensagem="x")


def test_h1_banco_recusa_status_fora_do_schema(presunto):
    with pytest.raises(IntegrityError), transaction.atomic():
        Alerta.objects.create(
            produto=presunto, tipo="VALIDADE", severidade="MEDIA", mensagem="x", status="LIDO"
        )


def test_h1_aviso_de_validade_aponta_o_lote_e_o_de_ruptura_nao(presunto, dono):
    lote = registrar_entrada(produto=presunto, quantidade=Decimal("2.5"), usuario=None)

    validade = _aviso(presunto, lote=lote, destinatario=dono)
    ruptura = _aviso(presunto, tipo="RUPTURA")

    assert validade.lote == lote and validade.destinatario == dono
    assert ruptura.lote is None  # schema.sql: "nulo em aviso de ruptura"


# ------------------------------------------------------------------------------------------------
# Severidade (L11) e ordem de urgência (RN13)
# ------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("severidade", ["ALTA", "MEDIA", "BAIXA"])
def test_h1_l11_severidades_aceitas(presunto, severidade):
    assert _aviso(presunto, severidade=severidade).severidade == severidade


@pytest.mark.parametrize("severidade", ["URGENTE", "alta", "", None])
def test_h1_l11_severidade_fora_da_lista_e_recusada(presunto, severidade):
    with pytest.raises(ValueError, match="severidade"):
        _aviso(presunto, severidade=severidade)
    assert not Alerta.objects.exists()


def test_h1_l11_tipo_fora_da_lista_e_recusado_antes_do_banco(presunto):
    with pytest.raises(ValueError, match="tipo"):
        _aviso(presunto, tipo="PROMOCAO")


def test_h1_mensagem_vazia_e_recusada(presunto):
    # RNF10: a mensagem é o que o Sr. João lê no celular; aviso sem texto não serve.
    with pytest.raises(ValueError, match="mensagem"):
        criar_aviso(produto=presunto, tipo="VALIDADE", severidade="ALTA", mensagem="  ")


def test_h1_rn13_ordem_de_urgencia_severidade_depois_gerado_em(presunto):
    agora = timezone.now()
    baixa = _aviso(presunto, severidade="BAIXA")
    alta_nova = _aviso(presunto, severidade="ALTA")
    media = _aviso(presunto, severidade="MEDIA")
    alta_velha = _aviso(presunto, severidade="ALTA")
    Alerta.objects.filter(pk=alta_velha.pk).update(gerado_em=agora - timedelta(hours=5))

    ordem = list(Alerta.objects.por_urgencia().values_list("pk", flat=True))

    assert ordem == [alta_velha.pk, alta_nova.pk, media.pk, baixa.pk]


def test_h1_a_enviar_sao_os_pendentes_e_os_segurados(presunto):
    pendente = _aviso(presunto)
    segurado = _aviso(presunto)
    segurar([segurado])
    enviado = _aviso(presunto)
    enviar([enviado], quando=timezone.now())
    cancelado = _aviso(presunto)
    cancelar([cancelado])

    assert set(Alerta.objects.a_enviar().values_list("pk", flat=True)) == {pendente.pk, segurado.pk}


# ------------------------------------------------------------------------------------------------
# Controle de estado
# ------------------------------------------------------------------------------------------------


def test_h1_rn12_pendente_pode_ser_segurado(presunto):
    aviso = _aviso(presunto)

    assert segurar([aviso]) == 1
    aviso.refresh_from_db()
    assert aviso.status == "SEGURADO"
    assert aviso.enviado_em is None


@pytest.mark.parametrize("origem", ["PENDENTE", "SEGURADO"])
def test_h1_rn13_enviar_marca_todos_com_o_mesmo_enviado_em(presunto, origem):
    avisos = [_aviso(presunto) for _ in range(3)]
    if origem == "SEGURADO":
        segurar(avisos)
    quando = datetime(2026, 9, 21, 13, 5, tzinfo=SAO_PAULO)

    assert enviar(avisos, quando=quando) == 3

    enviados = Alerta.objects.filter(pk__in=[a.pk for a in avisos])
    assert set(enviados.values_list("status", flat=True)) == {"ENVIADO"}
    assert set(enviados.values_list("enviado_em", flat=True)) == {quando}


@pytest.mark.parametrize("origem", ["PENDENTE", "SEGURADO"])
def test_h1_pendente_ou_segurado_pode_ser_cancelado(presunto, origem):
    aviso = _aviso(presunto)
    if origem == "SEGURADO":
        segurar([aviso])

    assert cancelar([aviso]) == 1
    aviso.refresh_from_db()
    assert aviso.status == "CANCELADO"


@pytest.mark.parametrize(
    ("final", "transicao"),
    [
        ("ENVIADO", segurar),
        ("ENVIADO", cancelar),
        ("ENVIADO", lambda avisos: enviar(avisos, quando=timezone.now())),
        ("CANCELADO", segurar),
        ("CANCELADO", lambda avisos: enviar(avisos, quando=timezone.now())),
        ("CANCELADO", cancelar),
    ],
)
def test_h1_enviado_e_cancelado_nao_mudam_mais(presunto, final, transicao):
    aviso = _aviso(presunto)
    if final == "ENVIADO":
        enviar([aviso], quando=timezone.now())
    else:
        cancelar([aviso])
    antes = Alerta.objects.values().get(pk=aviso.pk)

    with pytest.raises(TransicaoDeAvisoInvalida):
        transicao([aviso])

    assert Alerta.objects.values().get(pk=aviso.pk) == antes


def test_h1_segurado_nao_volta_a_ser_segurado(presunto):
    aviso = _aviso(presunto)
    segurar([aviso])

    with pytest.raises(TransicaoDeAvisoInvalida):
        segurar([aviso])


def test_h1_transicao_e_tudo_ou_nada(presunto):
    # Um aviso já enviado no meio do lote: nenhum dos outros muda (nada pela metade).
    pendente_1, ja_enviado, pendente_2 = _aviso(presunto), _aviso(presunto), _aviso(presunto)
    enviar([ja_enviado], quando=timezone.now())

    with pytest.raises(TransicaoDeAvisoInvalida):
        enviar([pendente_1, ja_enviado, pendente_2], quando=timezone.now())

    assert Alerta.objects.get(pk=pendente_1.pk).status == "PENDENTE"
    assert Alerta.objects.get(pk=pendente_2.pk).status == "PENDENTE"


def test_h1_transicao_le_o_estado_do_banco_e_nao_o_da_memoria(presunto):
    # A rodada das 03h00 e uma entrada de mercadoria podem mexer no mesmo aviso: vale o banco.
    aviso = _aviso(presunto)
    copia_velha = Alerta.objects.get(pk=aviso.pk)  # ainda PENDENTE na memória
    cancelar([aviso])

    with pytest.raises(TransicaoDeAvisoInvalida):
        enviar([copia_velha], quando=timezone.now())
    assert Alerta.objects.get(pk=aviso.pk).status == "CANCELADO"


def test_h1_enviar_exige_o_momento_do_envio(presunto):
    with pytest.raises(TypeError):
        enviar([_aviso(presunto)])  # RN13: o mesmo enviado_em para todos, decidido por quem envia


def test_h1_lista_vazia_nao_faz_nada(db):
    assert segurar([]) == enviar([], quando=timezone.now()) == cancelar([]) == 0


# ------------------------------------------------------------------------------------------------
# Operação 02, passo 10: chegou mercadoria → cancela o aviso de "vai acabar"
# ------------------------------------------------------------------------------------------------


def test_h1_entrada_cancela_o_aviso_de_ruptura_pendente_do_produto(frango):
    pendente = _aviso(frango, tipo="RUPTURA")
    segurado = _aviso(frango, tipo="RUPTURA")
    segurar([segurado])

    assert cancelar_aviso_de_ruptura_pendente(frango) == 2
    assert set(Alerta.objects.values_list("status", flat=True)) == {"CANCELADO"}
    assert pendente.pk and segurado.pk


def test_h1_entrada_nao_cancela_aviso_de_validade_nem_de_outro_produto(frango, presunto):
    validade = _aviso(frango, tipo="VALIDADE")
    fim_semana = _aviso(frango, tipo="FIM_SEMANA")
    de_outro = _aviso(presunto, tipo="RUPTURA")

    assert cancelar_aviso_de_ruptura_pendente(frango) == 0
    for aviso in (validade, fim_semana, de_outro):
        aviso.refresh_from_db()
        assert aviso.status == "PENDENTE"


def test_h1_entrada_nao_mexe_em_aviso_de_ruptura_ja_enviado(frango):
    enviado = _aviso(frango, tipo="RUPTURA")
    enviar([enviado], quando=timezone.now())

    assert cancelar_aviso_de_ruptura_pendente(frango) == 0
    enviado.refresh_from_db()
    assert enviado.status == "ENVIADO"


def test_h1_registrar_entrada_cancela_de_verdade_o_aviso_de_ruptura(frango):
    # De ponta a ponta: a C2 já chamava o passo 10; com a tabela, ele age.
    aviso = _aviso(frango, tipo="RUPTURA")

    registrar_entrada(produto=frango, quantidade=Decimal("40"), usuario=None)

    aviso.refresh_from_db()
    assert aviso.status == "CANCELADO"


def test_h1_entrada_que_falha_nao_cancela_o_aviso(frango):
    aviso = _aviso(frango, tipo="RUPTURA")

    with patch("estoque.entrada.Movimentacao.objects.create", side_effect=IntegrityError("falhou")):
        with pytest.raises(IntegrityError):
            registrar_entrada(produto=frango, quantidade=Decimal("40"), usuario=None)

    aviso.refresh_from_db()
    assert aviso.status == "PENDENTE"

"""
Tarefa C3 — RN04: lote de perecível precisa de data de validade.

> Ao registrar a entrada de um lote de produto perecível, a data de validade é obrigatória. Se não
> for informada, o sistema calcula automaticamente somando a durabilidade do produto à data de
> entrada. Validade anterior à data de hoje é recusada.

Ordem (docs/REGRAS-NEGOCIO.md):
1. não perecível → validade opcional, segue;
2. perecível com validade → usa ela;
3. perecível sem validade → data_entrada + durabilidade_dias;
4. validade (informada ou calculada) anterior a hoje → recusa.

Fluxograma 02: seis situações a testar — as cinco de validade estão aqui; a sexta (a transação
de lote + movimentação) está em test_c2_entrada_lote.py.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest import mock

import pytest
from django.utils import timezone

from cadastro.models import Categoria, Produto, Usuario
from comum.autenticacao import gerar_token
from comum.erros import ErroDeRegraDeNegocio
from estoque.entrada import registrar_entrada
from estoque.models import Lote, Movimentacao
from estoque.regras import MENSAGEM_RN04, validade_do_lote

URL = "/api/lotes/"
HOJE = date(2026, 9, 21)  # o exemplo da Apostila I


@pytest.fixture
def no_dia_21_09():
    meio_dia = timezone.make_aware(datetime(2026, 9, 21, 12, 0))
    with mock.patch("django.utils.timezone.now", return_value=meio_dia):
        yield


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
def arroz(db):
    secos = Categoria.objects.create(nome="Secos e molhados")
    return Produto.objects.create(categoria=secos, nome="Arroz 5 kg", unidade_medida="PCT")


@pytest.fixture
def sobrinho(client, db):
    usuario = Usuario.objects.create_user(
        login="sobrinho", senha="Mercado#2026", nome="Sobrinho", papel="OPERACAO"
    )
    cabecalho = {"HTTP_AUTHORIZATION": f"Bearer {gerar_token(usuario)}"}

    class ClienteLogado:
        def post(self, dados):
            return client.post(URL, dados, content_type="application/json", **cabecalho)

    return ClienteLogado()


def _recusa_rn04(resposta):
    assert resposta.status_code == 400
    erro = resposta.json()["erro"]
    assert (erro["codigo"], erro["regra"], erro["mensagem"]) == ("regra_de_negocio", "RN04", MENSAGEM_RN04)
    assert list(erro["campos"]) == ["data_validade"]  # aponta só o campo da validade


# --- A regra, no módulo de serviço ---------------------------------------------------------------


def test_rn04_passo1_nao_perecivel_sem_validade_segue_sem_validade(arroz):
    assert validade_do_lote(arroz, data_entrada=HOJE, data_validade=None, hoje=HOJE) is None


def test_rn04_passo1_nao_perecivel_com_validade_usa_a_informada(arroz):
    validade = HOJE + timedelta(days=180)
    assert validade_do_lote(arroz, data_entrada=HOJE, data_validade=validade, hoje=HOJE) == validade


def test_rn04_passo2_perecivel_com_validade_usa_a_informada(frango):
    validade = HOJE + timedelta(days=2)  # a embalagem manda, mesmo diferente da durabilidade
    assert validade_do_lote(frango, data_entrada=HOJE, data_validade=validade, hoje=HOJE) == validade


def test_rn04_passo3_perecivel_sem_validade_calcula_entrada_mais_durabilidade(frango):
    # Apostila I: "entrada de frango em 21/09 sem validade, durabilidade 4 dias → sistema grava 25/09".
    assert validade_do_lote(frango, data_entrada=HOJE, data_validade=None, hoje=HOJE) == date(2026, 9, 25)


@pytest.mark.parametrize("produto", ["frango", "arroz"])
def test_rn04_passo4_validade_anterior_a_hoje_e_recusada(request, produto):
    with pytest.raises(ErroDeRegraDeNegocio) as recusa:
        validade_do_lote(
            request.getfixturevalue(produto), data_entrada=HOJE, data_validade=date(2026, 9, 20), hoje=HOJE
        )
    assert (recusa.value.regra, recusa.value.campo) == ("RN04", "data_validade")


def test_rn04_passo4_validade_hoje_e_aceita(frango):
    # "anterior à data de hoje": hoje ainda não é anterior.
    assert validade_do_lote(frango, data_entrada=HOJE, data_validade=HOJE, hoje=HOJE) == HOJE


# --- Na API: as situações do fluxograma 02 -------------------------------------------------------


def test_rn04_api_perecivel_sem_validade_grava_a_validade_calculada(sobrinho, frango, no_dia_21_09):
    resposta = sobrinho.post({"produto": frango.pk, "quantidade": "40"})
    assert resposta.status_code == 201
    assert resposta.json()["data_validade"] == "2026-09-25"
    assert Lote.objects.get().data_validade == date(2026, 9, 25)


def test_rn04_api_perecivel_com_validade_grava_a_informada(sobrinho, frango, no_dia_21_09):
    resposta = sobrinho.post({"produto": frango.pk, "quantidade": "40", "data_validade": "2026-09-23"})
    assert resposta.status_code == 201
    assert Lote.objects.get().data_validade == date(2026, 9, 23)


def test_rn04_api_validade_no_passado_e_recusada_e_nada_e_gravado(sobrinho, frango, no_dia_21_09):
    _recusa_rn04(sobrinho.post({"produto": frango.pk, "quantidade": "40", "data_validade": "2026-09-20"}))
    assert not Lote.objects.exists()
    assert not Movimentacao.objects.exists()


def test_rn04_api_nao_perecivel_sem_validade_e_aceito(sobrinho, arroz, no_dia_21_09):
    resposta = sobrinho.post({"produto": arroz.pk, "quantidade": "20"})
    assert resposta.status_code == 201
    assert Lote.objects.get().data_validade is None


def test_rn04_api_nao_perecivel_com_validade_vencida_tambem_e_recusado(sobrinho, arroz, no_dia_21_09):
    # Passo 1 "segue" para o passo 4: validade informada e já vencida é recusada para qualquer lote.
    _recusa_rn04(sobrinho.post({"produto": arroz.pk, "quantidade": "20", "data_validade": "2026-09-01"}))
    assert not Lote.objects.exists()


def test_rn04_vale_tambem_para_quem_chama_o_servico_sem_a_api(frango, no_dia_21_09):
    # A regra mora no serviço: qualquer caminho que registre entrada (ex.: carga inicial J2) passa
    # por ela, não só a tela.
    with pytest.raises(ErroDeRegraDeNegocio):
        registrar_entrada(
            produto=frango, quantidade=Decimal("1"), usuario=None, data_validade=date(2026, 9, 1)
        )
    lote = registrar_entrada(produto=frango, quantidade=Decimal("1"), usuario=None)
    assert lote.data_validade == date(2026, 9, 25)


def test_rn04_hoje_e_o_dia_da_loja_mesmo_a_noite(frango):
    # 22h30 de 21/09 em São Paulo já é 22/09 em UTC. Validade 21/09 informada às 22h30 é "hoje".
    noite = timezone.make_aware(datetime(2026, 9, 21, 22, 30))
    with mock.patch("django.utils.timezone.now", return_value=noite):
        lote = registrar_entrada(produto=frango, quantidade=Decimal("1"), usuario=None, data_validade=HOJE)
    assert lote.data_validade == HOJE

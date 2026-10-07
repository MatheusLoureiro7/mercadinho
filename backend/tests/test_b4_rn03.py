"""
Tarefa B4 — RN03: produto perecível exige prazo de durabilidade.

> Um produto marcado como perecível só pode ser salvo com o campo de durabilidade em dias
> preenchido e maior que zero.

Onde: API de cadastro de produto, ANTES de gravar. Fluxograma 01: devolve só o campo que falta,
para a tela manter o que já foi digitado. Nada é gravado.
Cada losango do fluxograma vira pelo menos dois testes (caminho "sim" e caminho "não").
"""

import pytest

from cadastro.models import Categoria, Produto, Usuario
from cadastro.regras import MENSAGEM_RN03, verificar_rn03
from comum.autenticacao import gerar_token
from comum.erros import ErroDeRegraDeNegocio

URL = "/api/produtos/"


@pytest.fixture
def sobrinho(client, db):
    usuario = Usuario.objects.create_user(
        login="sobrinho", senha="Mercado#2026", nome="Sobrinho", papel="OPERACAO"
    )
    cabecalho = {"HTTP_AUTHORIZATION": f"Bearer {gerar_token(usuario)}"}

    class ClienteLogado:
        def post(self, dados):
            return client.post(URL, dados, content_type="application/json", **cabecalho)

        def patch(self, produto_id, dados):
            return client.patch(f"{URL}{produto_id}/", dados, content_type="application/json", **cabecalho)

    return ClienteLogado()


@pytest.fixture
def acougue(db):
    return Categoria.objects.create(nome="Açougue", perecivel_padrao=True)


@pytest.fixture
def secos(db):
    return Categoria.objects.create(nome="Secos e molhados")


def _frango(categoria, **extras):
    return {"nome": "Frango resfriado 1 kg", "categoria": categoria.pk, "unidade_medida": "KG", **extras}


def _recusa_rn03(resposta):
    assert resposta.status_code == 400
    erro = resposta.json()["erro"]
    assert erro["codigo"] == "regra_de_negocio"
    assert erro["regra"] == "RN03"
    assert erro["mensagem"] == MENSAGEM_RN03
    # Fluxograma 01: aponta só o campo que falta — a tela mantém o resto do que foi digitado.
    assert list(erro["campos"]) == ["durabilidade_dias"]


# --- A regra, no módulo de serviço ---------------------------------------------------------------


@pytest.mark.parametrize("durabilidade", [None, 0, -3])
def test_rn03_regra_recusa_perecivel_sem_durabilidade_valida(durabilidade):
    with pytest.raises(ErroDeRegraDeNegocio) as recusa:
        verificar_rn03(perecivel=True, durabilidade_dias=durabilidade)
    assert recusa.value.regra == "RN03"
    assert recusa.value.campo == "durabilidade_dias"


@pytest.mark.parametrize(("perecivel", "durabilidade"), [(True, 4), (True, 1), (False, None), (False, 0)])
def test_rn03_regra_aceita(perecivel, durabilidade):
    verificar_rn03(perecivel=perecivel, durabilidade_dias=durabilidade)  # não levanta nada


# --- Losango "perecível marcado e durabilidade vazia?" — na API ------------------------------------


def test_rn03_perecivel_sem_durabilidade_e_recusado(sobrinho, acougue):
    # Exemplo da Apostila I: "Frango resfriado 1 kg" perecível sem durabilidade → recusado.
    _recusa_rn03(sobrinho.post(_frango(acougue, perecivel=True)))
    assert not Produto.objects.exists()  # nada é gravado


def test_rn03_perecivel_com_durabilidade_e_salvo(sobrinho, acougue):
    # ... com 4 dias → salvo.
    resposta = sobrinho.post(_frango(acougue, perecivel=True, durabilidade_dias=4))
    assert resposta.status_code == 201
    assert Produto.objects.get().durabilidade_dias == 4


def test_rn03_perecivel_com_durabilidade_vazia_explicita_e_recusado(sobrinho, acougue):
    _recusa_rn03(sobrinho.post(_frango(acougue, perecivel=True, durabilidade_dias=None)))


@pytest.mark.parametrize("durabilidade", [0, -1])
def test_rn03_perecivel_com_durabilidade_zero_ou_negativa_e_recusado(sobrinho, acougue, durabilidade):
    # "preenchido e maior que zero"
    _recusa_rn03(sobrinho.post(_frango(acougue, perecivel=True, durabilidade_dias=durabilidade)))
    assert not Produto.objects.exists()


def test_rn03_nao_perecivel_sem_durabilidade_e_salvo(sobrinho, secos):
    resposta = sobrinho.post({"nome": "Arroz 5 kg", "categoria": secos.pk, "unidade_medida": "PCT"})
    assert resposta.status_code == 201


def test_rn03_vale_para_quem_herdou_perecivel_da_categoria(sobrinho, acougue):
    # L19: no Açougue o produto já nasce perecível — então a RN03 vale para ele também.
    _recusa_rn03(sobrinho.post(_frango(acougue)))
    assert not Produto.objects.exists()


def test_rn03_nunca_vira_erro_interno(sobrinho, acougue):
    # Antes da B4, só o banco barrava e a API respondia 500. Agora a recusa é explicada.
    resposta = sobrinho.post(_frango(acougue, perecivel=True))
    assert resposta.status_code != 500


# --- RN03 também na edição ----------------------------------------------------------------------


@pytest.fixture
def arroz(sobrinho, secos):
    return sobrinho.post({"nome": "Arroz 5 kg", "categoria": secos.pk, "unidade_medida": "PCT"}).json()["id"]


@pytest.fixture
def frango(sobrinho, acougue):
    return sobrinho.post(_frango(acougue, perecivel=True, durabilidade_dias=4)).json()["id"]


def test_rn03_marcar_como_perecivel_sem_durabilidade_e_recusado(sobrinho, arroz):
    _recusa_rn03(sobrinho.patch(arroz, {"perecivel": True}))
    assert Produto.objects.get(pk=arroz).perecivel is False  # nada mudou


def test_rn03_marcar_como_perecivel_junto_com_a_durabilidade_e_aceito(sobrinho, arroz):
    resposta = sobrinho.patch(arroz, {"perecivel": True, "durabilidade_dias": 180})
    assert resposta.status_code == 200
    assert Produto.objects.get(pk=arroz).perecivel is True


def test_rn03_apagar_a_durabilidade_de_um_perecivel_e_recusado(sobrinho, frango):
    _recusa_rn03(sobrinho.patch(frango, {"durabilidade_dias": None}))
    assert Produto.objects.get(pk=frango).durabilidade_dias == 4


def test_rn03_zerar_a_durabilidade_de_um_perecivel_e_recusado(sobrinho, frango):
    _recusa_rn03(sobrinho.patch(frango, {"durabilidade_dias": 0}))


def test_rn03_mudar_a_durabilidade_de_um_perecivel_para_outro_valor_e_aceito(sobrinho, frango):
    assert sobrinho.patch(frango, {"durabilidade_dias": 5}).status_code == 200
    assert Produto.objects.get(pk=frango).durabilidade_dias == 5


def test_rn03_deixar_de_ser_perecivel_libera_a_durabilidade(sobrinho, frango):
    resposta = sobrinho.patch(frango, {"perecivel": False, "durabilidade_dias": None})
    assert resposta.status_code == 200


def test_rn03_editar_outro_campo_de_um_perecivel_valido_e_aceito(sobrinho, frango):
    assert sobrinho.patch(frango, {"preco_venda": "15.90"}).status_code == 200

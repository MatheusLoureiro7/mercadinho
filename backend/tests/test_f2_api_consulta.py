"""
Tarefa F2 — API de consulta de estoque com filtros (RF07, RN14, RN16).

/api/estoque/        posição por produto  — ?categoria= ?busca= ?abaixo_do_minimo=1 ?validade_proxima=1
/api/estoque/lotes/  posição por lote     — ?categoria= ?produto= ?busca= ?situacao=VENCIDO,VENCENDO

Tela Consulta de estoque: os três perfis (RN14). Só leitura.
"""

from datetime import date, datetime
from decimal import Decimal
from unittest import mock

import pytest
from django.utils import timezone

from cadastro.models import Categoria, Produto, Usuario
from comum.autenticacao import gerar_token
from estoque.models import Lote, Movimentacao

URL_PRODUTOS = "/api/estoque/"
URL_LOTES = "/api/estoque/lotes/"


@pytest.fixture(autouse=True)
def no_dia_21_09():
    meio_dia = timezone.make_aware(datetime(2026, 9, 21, 12, 0))
    with mock.patch("django.utils.timezone.now", return_value=meio_dia):
        yield


@pytest.fixture
def usuarios(db):
    return {
        papel: Usuario.objects.create_user(login=papel.lower(), senha="Mercado#2026", nome=papel, papel=papel)
        for papel in ("DONO", "GESTAO", "OPERACAO")
    }


@pytest.fixture
def api(client, usuarios):
    def _cliente(papel="GESTAO"):
        cabecalho = {"HTTP_AUTHORIZATION": f"Bearer {gerar_token(usuarios[papel])}"}

        class ClienteLogado:
            def get(self, url):
                return client.get(url, **cabecalho)

            def post(self, url, dados):
                return client.post(url, dados, content_type="application/json", **cabecalho)

        return ClienteLogado()

    return _cliente


@pytest.fixture
def loja(db):
    """Um pedaço da loja: frios com lote vencido e vencendo, açougue abaixo do mínimo, secos ok."""
    frios = Categoria.objects.create(nome="Frios", perecivel_padrao=True)
    acougue = Categoria.objects.create(nome="Açougue", perecivel_padrao=True)
    secos = Categoria.objects.create(nome="Secos e molhados")
    iogurte = Produto.objects.create(
        categoria=frios, nome="Iogurte natural", unidade_medida="UN", perecivel=True, durabilidade_dias=15
    )
    presunto = Produto.objects.create(
        categoria=frios, nome="Presunto", unidade_medida="KG", perecivel=True, durabilidade_dias=7
    )
    alcatra = Produto.objects.create(
        categoria=acougue,
        nome="Alcatra",
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=3,
        estoque_minimo=Decimal("5"),
    )
    arroz = Produto.objects.create(
        categoria=secos, nome="Arroz 5 kg", unidade_medida="PCT", estoque_minimo=Decimal("10")
    )
    lotes = {
        "iogurte_vencido": _lote(iogurte, "6", date(2026, 9, 20)),  # RN16
        "iogurte_bom": _lote(iogurte, "10", date(2026, 10, 1)),
        "presunto_vencendo": _lote(presunto, "2.5", date(2026, 9, 24)),  # RN05, N = 3
        "alcatra": _lote(alcatra, "2", date(2026, 9, 23)),  # abaixo do mínimo (5) e vencendo
        "arroz": _lote(arroz, "20", None),
    }
    return {
        "categorias": {"frios": frios, "acougue": acougue, "secos": secos},
        "produtos": {"iogurte": iogurte, "presunto": presunto, "alcatra": alcatra, "arroz": arroz},
        "lotes": lotes,
    }


def _lote(produto, quantidade, validade):
    lote = Lote.objects.create(
        produto=produto,
        quantidade_inicial=Decimal(quantidade),
        quantidade_atual=Decimal(quantidade),
        data_entrada=date(2026, 9, 15),
        data_validade=validade,
    )
    Movimentacao.objects.create(produto=produto, lote=lote, tipo="ENTRADA", quantidade=Decimal(quantidade))
    return lote


def _nomes(resposta, campo="nome"):
    return [item[campo] for item in resposta.json()]


# =================================================================================================
# RN14: os três perfis consultam; ninguém escreve
# =================================================================================================


@pytest.mark.parametrize("papel", ["DONO", "GESTAO", "OPERACAO"])
@pytest.mark.parametrize("url", [URL_PRODUTOS, URL_LOTES])
def test_rn14_os_tres_perfis_consultam_o_estoque(api, loja, papel, url):
    assert api(papel).get(url).status_code == 200


@pytest.mark.parametrize("url", [URL_PRODUTOS, URL_LOTES])
def test_rn14_consulta_sem_login_e_recusada(client, loja, url):
    assert client.get(url).status_code == 401


@pytest.mark.parametrize("url", [URL_PRODUTOS, URL_LOTES])
def test_rn01_consulta_nao_escreve_nada(api, loja, url):
    # RN01: ninguém grava saldo. A consulta é só leitura.
    assert api("OPERACAO").post(url, {"saldo": "999"}).status_code == 405


# =================================================================================================
# Por produto
# =================================================================================================


def test_f2_posicao_por_produto(api, loja):
    corpo = {item["nome"]: item for item in api().get(URL_PRODUTOS).json()}
    assert corpo["Alcatra"] == {
        "produto_id": loja["produtos"]["alcatra"].pk,
        "nome": "Alcatra",
        "categoria_id": loja["categorias"]["acougue"].pk,
        "categoria_nome": "Açougue",
        "unidade_medida": "KG",
        "perecivel": True,
        "critico_fim_semana": False,
        "estoque_minimo": "5.000",
        "saldo": "2.000",  # texto, nunca float
        "abaixo_do_minimo": True,
        "lotes_vencidos": 0,
        "lotes_vencendo": 1,
        "proxima_validade": "2026-09-23",
    }


def test_rf07_agrupado_por_categoria(api, loja):
    # Ordem de categoria e, dentro dela, de nome — a tela agrupa por categoria (RF07).
    assert _nomes(api().get(URL_PRODUTOS)) == ["Alcatra", "Iogurte natural", "Presunto", "Arroz 5 kg"]


def test_rf07_filtra_por_categoria(api, loja):
    frios = loja["categorias"]["frios"].pk
    assert _nomes(api().get(f"{URL_PRODUTOS}?categoria={frios}")) == ["Iogurte natural", "Presunto"]


def test_f2_busca_pelo_nome(api, loja):
    assert _nomes(api().get(f"{URL_PRODUTOS}?busca=iog")) == ["Iogurte natural"]


@pytest.mark.parametrize("valor", ["1", "true", "sim"])
def test_rf07_so_o_que_esta_abaixo_do_minimo(api, loja, valor):
    assert _nomes(api().get(f"{URL_PRODUTOS}?abaixo_do_minimo={valor}")) == ["Alcatra"]


def test_rf07_so_o_que_tem_lote_vencendo_ou_vencido(api, loja):
    nomes = _nomes(api().get(f"{URL_PRODUTOS}?validade_proxima=1"))
    assert nomes == ["Alcatra", "Iogurte natural", "Presunto"]


def test_f2_filtros_combinados(api, loja):
    frios = loja["categorias"]["frios"].pk
    assert _nomes(api().get(f"{URL_PRODUTOS}?categoria={frios}&abaixo_do_minimo=1")) == []


def test_f2_filtro_desligado_mostra_tudo(api, loja):
    assert len(api().get(f"{URL_PRODUTOS}?abaixo_do_minimo=0").json()) == 4


# =================================================================================================
# Por lote
# =================================================================================================


def test_f2_posicao_por_lote(api, loja):
    lote = loja["lotes"]["presunto_vencendo"]
    corpo = {item["id"]: item for item in api().get(URL_LOTES).json()}
    assert corpo[lote.pk] == {
        "id": lote.pk,
        "produto_id": loja["produtos"]["presunto"].pk,
        "produto_nome": "Presunto",
        "categoria_nome": "Frios",
        "unidade_medida": "KG",
        "fornecedor_nome": None,
        "quantidade_atual": "2.500",
        "data_entrada": "2026-09-15",
        "data_validade": "2026-09-24",
        "dias_para_vencer": 3,
        "situacao": "VENCENDO",
    }


def test_rn16_lote_vencido_aparece_destacado(api, loja):
    # "lote de iogurte vencido em 20/09 aparece destacado em 21/09".
    vencido = loja["lotes"]["iogurte_vencido"].pk
    corpo = {item["id"]: item for item in api("DONO").get(URL_LOTES).json()}
    assert (corpo[vencido]["situacao"], corpo[vencido]["dias_para_vencer"]) == ("VENCIDO", -1)


def test_f2_lotes_em_ordem_de_validade(api, loja):
    ordem = [item["id"] for item in api().get(URL_LOTES).json()]
    lotes = loja["lotes"]
    assert ordem == [
        lotes["iogurte_vencido"].pk,
        lotes["alcatra"].pk,
        lotes["presunto_vencendo"].pk,
        lotes["iogurte_bom"].pk,
        lotes["arroz"].pk,
    ]


def test_rf07_lotes_por_situacao(api, loja):
    lotes = loja["lotes"]
    vencidos = [item["id"] for item in api().get(f"{URL_LOTES}?situacao=VENCIDO").json()]
    assert vencidos == [lotes["iogurte_vencido"].pk]
    atencao = [item["id"] for item in api().get(f"{URL_LOTES}?situacao=VENCIDO,VENCENDO").json()]
    assert atencao == [lotes["iogurte_vencido"].pk, lotes["alcatra"].pk, lotes["presunto_vencendo"].pk]


def test_f2_situacao_em_minusculas_e_aceita(api, loja):
    assert len(api().get(f"{URL_LOTES}?situacao=vencido").json()) == 1


def test_f2_lotes_por_produto_e_por_categoria(api, loja):
    iogurte = loja["produtos"]["iogurte"].pk
    assert len(api().get(f"{URL_LOTES}?produto={iogurte}").json()) == 2
    secos = loja["categorias"]["secos"].pk
    assert _nomes(api().get(f"{URL_LOTES}?categoria={secos}"), "produto_nome") == ["Arroz 5 kg"]


def test_f2_lotes_busca_pelo_nome_do_produto(api, loja):
    assert _nomes(api().get(f"{URL_LOTES}?busca=presu"), "produto_nome") == ["Presunto"]


# =================================================================================================
# Filtros inválidos
# =================================================================================================


@pytest.mark.parametrize(
    ("url", "campo"),
    [
        (f"{URL_PRODUTOS}?categoria=abc", "categoria"),
        (f"{URL_PRODUTOS}?abaixo_do_minimo=talvez", "abaixo_do_minimo"),
        (f"{URL_LOTES}?situacao=ESTRAGADO", "situacao"),
        (f"{URL_LOTES}?produto=x", "produto"),
    ],
)
def test_f2_filtro_invalido_aponta_o_campo(api, loja, url, campo):
    resposta = api().get(url)
    assert resposta.status_code == 400
    assert campo in resposta.json()["erro"]["campos"]


# =================================================================================================
# Desempenho: computador antigo (RNF06, R04) e até 2.000 produtos
# =================================================================================================


@pytest.mark.parametrize("url", [URL_PRODUTOS, URL_LOTES])
def test_rnf06_consulta_nao_faz_uma_consulta_por_produto(api, loja, url, django_assert_max_num_queries):
    frios = loja["categorias"]["frios"]
    for numero in range(50):
        produto = Produto.objects.create(
            categoria=frios,
            nome=f"Queijo {numero}",
            unidade_medida="KG",
            perecivel=True,
            durabilidade_dias=10,
        )
        _lote(produto, "1", date(2026, 9, 25))
    cliente = api()
    # Login (usuário) + parâmetro de dias + a consulta: o número não cresce com os 50 produtos.
    with django_assert_max_num_queries(4):
        resposta = cliente.get(url)
    assert len(resposta.json()) >= 50

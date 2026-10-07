"""
Tarefa B2 — API de categoria e fornecedor.

- Fornecedor (RF02): nome, contato e, principalmente, o prazo de entrega — o número que faz o
  ponto de pedido funcionar no bloco G (RN08). Tela "Fornecedores": só OPERACAO (RN14).
- Categoria: não tem tela própria (L18). Ler é da Consulta de estoque (os três perfis, RF07 pede
  saldo "por categoria"); criar e editar é da tela de Produtos (OPERACAO).
- Nada é apagado: categoria e fornecedor são tabelas de origem (Apostila IV, seção 5).
"""

import pytest

from cadastro.models import Categoria, Fornecedor, Usuario
from comum.autenticacao import gerar_token

SENHA = "Mercado#2026"


@pytest.fixture
def usuarios(db):
    return {
        papel: Usuario.objects.create_user(login=papel.lower(), senha=SENHA, nome=papel, papel=papel)
        for papel in ("DONO", "GESTAO", "OPERACAO")
    }


@pytest.fixture
def api(client, usuarios):
    """Cliente já logado: api("OPERACAO").post(...)."""

    class ClienteLogado:
        def __init__(self, papel):
            self.cabecalho = {"HTTP_AUTHORIZATION": f"Bearer {gerar_token(usuarios[papel])}"}

        def get(self, url):
            return client.get(url, **self.cabecalho)

        def post(self, url, dados):
            return client.post(url, dados, content_type="application/json", **self.cabecalho)

        def patch(self, url, dados):
            return client.patch(url, dados, content_type="application/json", **self.cabecalho)

        def put(self, url, dados):
            return client.put(url, dados, content_type="application/json", **self.cabecalho)

        def delete(self, url):
            return client.delete(url, **self.cabecalho)

    return ClienteLogado


@pytest.fixture
def frios(db):
    return Categoria.objects.create(nome="Frios", perecivel_padrao=True)


@pytest.fixture
def boi_bom(db):
    return Fornecedor.objects.create(
        nome="Frigorífico Boi Bom", prazo_entrega_dias=3, contato="(11) 99999-0000"
    )


# =================================================================================================
# Categoria
# =================================================================================================


def test_b2_operacao_cadastra_categoria(api):
    resposta = api("OPERACAO").post("/api/categorias/", {"nome": "Secos e molhados"})
    assert resposta.status_code == 201
    assert resposta.json() == {
        "id": resposta.json()["id"],
        "nome": "Secos e molhados",
        "perecivel_padrao": False,
    }
    assert Categoria.objects.filter(nome="Secos e molhados").exists()


def test_b2_categoria_perecivel_por_padrao(api):
    resposta = api("OPERACAO").post("/api/categorias/", {"nome": "Açougue", "perecivel_padrao": True})
    assert resposta.status_code == 201
    assert Categoria.objects.get(nome="Açougue").perecivel_padrao is True


def test_b2_categoria_com_nome_repetido_e_recusada(api, frios):
    resposta = api("OPERACAO").post("/api/categorias/", {"nome": "Frios"})
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"] == {"nome": ["Já existe uma categoria com esse nome."]}
    assert Categoria.objects.count() == 1


def test_b2_categoria_sem_nome_e_recusada(api):
    resposta = api("OPERACAO").post("/api/categorias/", {"nome": "   "})
    assert resposta.status_code == 400
    assert "nome" in resposta.json()["erro"]["campos"]


def test_b2_nome_da_categoria_e_gravado_sem_espacos_nas_pontas(api):
    api("OPERACAO").post("/api/categorias/", {"nome": "  Bebidas  "})
    assert Categoria.objects.filter(nome="Bebidas").exists()


def test_b2_operacao_edita_categoria(api, frios):
    resposta = api("OPERACAO").patch(f"/api/categorias/{frios.pk}/", {"nome": "Frios e laticínios"})
    assert resposta.status_code == 200
    frios.refresh_from_db()
    assert frios.nome == "Frios e laticínios"


@pytest.mark.parametrize("papel", ["DONO", "GESTAO", "OPERACAO"])
def test_l18_os_tres_perfis_leem_as_categorias(api, frios, papel):
    # Consulta de estoque mostra o saldo "por categoria" (RF07) e é dos três perfis (RN14).
    resposta = api(papel).get("/api/categorias/")
    assert resposta.status_code == 200
    assert [c["nome"] for c in resposta.json()] == ["Frios"]


@pytest.mark.parametrize("papel", ["DONO", "GESTAO"])
def test_l18_dono_e_gestao_nao_criam_categoria(api, papel):
    resposta = api(papel).post("/api/categorias/", {"nome": "Bebidas"})
    assert resposta.status_code == 403
    assert not Categoria.objects.exists()


@pytest.mark.parametrize("papel", ["DONO", "GESTAO"])
def test_l18_dono_e_gestao_nao_editam_categoria(api, frios, papel):
    resposta = api(papel).patch(f"/api/categorias/{frios.pk}/", {"nome": "Outro nome"})
    assert resposta.status_code == 403
    frios.refresh_from_db()
    assert frios.nome == "Frios"


def test_b2_categoria_nunca_e_apagada(api, frios):
    # Tabela de origem: nunca é apagada (Apostila IV, seção 5).
    resposta = api("OPERACAO").delete(f"/api/categorias/{frios.pk}/")
    assert resposta.status_code == 405
    assert Categoria.objects.filter(pk=frios.pk).exists()


def test_b2_categorias_sem_login_responde_401(client, db):
    assert client.get("/api/categorias/").status_code == 401


def test_b2_categoria_inexistente_responde_404(api):
    resposta = api("OPERACAO").get("/api/categorias/9999/")
    assert resposta.status_code == 404
    assert resposta.json()["erro"]["codigo"] == "nao_encontrado"


def test_b2_categorias_vem_em_ordem_alfabetica(api):
    for nome in ["Secos e molhados", "Açougue", "Frios"]:
        Categoria.objects.create(nome=nome)
    nomes = [c["nome"] for c in api("GESTAO").get("/api/categorias/").json()]
    assert nomes == ["Açougue", "Frios", "Secos e molhados"]


# =================================================================================================
# Fornecedor
# =================================================================================================


def test_b2_operacao_cadastra_fornecedor(api):
    resposta = api("OPERACAO").post(
        "/api/fornecedores/",
        {
            "nome": "Distribuidora Sol",
            "prazo_entrega_dias": 2,
            "pedido_minimo": "150.00",
            "contato": "Carlos",
        },
    )
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["prazo_entrega_dias"] == 2
    assert corpo["pedido_minimo"] == "150.00"  # dinheiro sai como texto, nunca float
    assert corpo["contato"] == "Carlos"


def test_b2_fornecedor_sem_prazo_de_entrega_e_recusado(api):
    # RF02: "principalmente, em quantos dias o fornecedor entrega depois do pedido".
    resposta = api("OPERACAO").post("/api/fornecedores/", {"nome": "Distribuidora Sol"})
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"] == {
        "prazo_entrega_dias": ["Informe em quantos dias o fornecedor entrega depois do pedido."]
    }
    assert not Fornecedor.objects.exists()


def test_b2_fornecedor_com_prazo_negativo_e_recusado(api):
    resposta = api("OPERACAO").post(
        "/api/fornecedores/", {"nome": "Distribuidora Sol", "prazo_entrega_dias": -1}
    )
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"] == {
        "prazo_entrega_dias": ["O prazo de entrega não pode ser negativo."]
    }


def test_b2_fornecedor_com_prazo_que_nao_e_numero_e_recusado(api):
    resposta = api("OPERACAO").post(
        "/api/fornecedores/", {"nome": "Distribuidora Sol", "prazo_entrega_dias": "três"}
    )
    assert resposta.status_code == 400
    assert "prazo_entrega_dias" in resposta.json()["erro"]["campos"]


def test_b2_fornecedor_entrega_no_mesmo_dia(api):
    resposta = api("OPERACAO").post(
        "/api/fornecedores/", {"nome": "Padaria da esquina", "prazo_entrega_dias": 0}
    )
    assert resposta.status_code == 201


def test_b2_fornecedor_sem_nome_e_recusado(api):
    resposta = api("OPERACAO").post("/api/fornecedores/", {"nome": "", "prazo_entrega_dias": 2})
    assert resposta.status_code == 400
    assert "nome" in resposta.json()["erro"]["campos"]


def test_b2_pedido_minimo_negativo_e_recusado(api):
    resposta = api("OPERACAO").post(
        "/api/fornecedores/",
        {"nome": "Distribuidora Sol", "prazo_entrega_dias": 2, "pedido_minimo": "-10.00"},
    )
    assert resposta.status_code == 400
    assert "pedido_minimo" in resposta.json()["erro"]["campos"]


def test_b2_contato_e_pedido_minimo_sao_opcionais(api):
    # RNF05: formulário curto, nada de campo opcional obrigatório.
    resposta = api("OPERACAO").post(
        "/api/fornecedores/", {"nome": "Distribuidora Sol", "prazo_entrega_dias": 2, "contato": ""}
    )
    assert resposta.status_code == 201
    fornecedor = Fornecedor.objects.get()
    assert fornecedor.contato is None  # vazio vira nulo, como no schema.sql
    assert fornecedor.pedido_minimo is None


def test_b2_operacao_corrige_o_prazo_do_fornecedor(api, boi_bom):
    resposta = api("OPERACAO").patch(f"/api/fornecedores/{boi_bom.pk}/", {"prazo_entrega_dias": 4})
    assert resposta.status_code == 200
    boi_bom.refresh_from_db()
    assert boi_bom.prazo_entrega_dias == 4
    assert boi_bom.contato == "(11) 99999-0000"  # o resto não mudou


def test_b2_edicao_completa_tambem_exige_o_prazo(api, boi_bom):
    resposta = api("OPERACAO").put(f"/api/fornecedores/{boi_bom.pk}/", {"nome": "Frigorífico Boi Bom"})
    assert resposta.status_code == 400
    boi_bom.refresh_from_db()
    assert boi_bom.prazo_entrega_dias == 3


@pytest.mark.parametrize("papel", ["DONO", "GESTAO"])
def test_rn14_dono_e_gestao_nao_acessam_fornecedores(api, boi_bom, papel):
    assert api(papel).get("/api/fornecedores/").status_code == 403
    resposta = api(papel).post("/api/fornecedores/", {"nome": "Outro", "prazo_entrega_dias": 1})
    assert resposta.status_code == 403
    assert Fornecedor.objects.count() == 1


def test_b2_fornecedor_nunca_e_apagado(api, boi_bom):
    resposta = api("OPERACAO").delete(f"/api/fornecedores/{boi_bom.pk}/")
    assert resposta.status_code == 405
    assert Fornecedor.objects.filter(pk=boi_bom.pk).exists()


def test_b2_fornecedores_vem_em_ordem_alfabetica(api):
    for nome in ["Distribuidora Sol", "Atacadão Central", "Frigorífico Boi Bom"]:
        Fornecedor.objects.create(nome=nome, prazo_entrega_dias=1)
    nomes = [f["nome"] for f in api("OPERACAO").get("/api/fornecedores/").json()]
    assert nomes == ["Atacadão Central", "Distribuidora Sol", "Frigorífico Boi Bom"]


def test_b2_consulta_um_fornecedor(api, boi_bom):
    resposta = api("OPERACAO").get(f"/api/fornecedores/{boi_bom.pk}/")
    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Frigorífico Boi Bom"

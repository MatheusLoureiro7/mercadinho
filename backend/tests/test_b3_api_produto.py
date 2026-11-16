"""
Tarefa B3 — API de produto, com validações.

RF01: nome, categoria, unidade de medida, se é perecível e por quantos dias dura, preço de custo,
preço de venda e estoque mínimo. RF15: marcar os críticos de fim de semana.
Fluxograma/operação 01: valida tipo e obrigatoriedade (passo 5) e nome único na categoria
(passo 6). A RN03 (perecível exige durabilidade) é a tarefa B4.
"""

from decimal import Decimal

import pytest

from cadastro.models import Categoria, Fornecedor, Produto, Usuario
from comum.autenticacao import gerar_token

URL = "/api/produtos/"


@pytest.fixture
def usuarios(db):
    return {
        papel: Usuario.objects.create_user(login=papel.lower(), senha="Mercado#2026", nome=papel, papel=papel)
        for papel in ("DONO", "GESTAO", "OPERACAO")
    }


@pytest.fixture
def api(client, usuarios):
    class ClienteLogado:
        def __init__(self, papel):
            self.cabecalho = {"HTTP_AUTHORIZATION": f"Bearer {gerar_token(usuarios[papel])}"}

        def get(self, url):
            return client.get(url, **self.cabecalho)

        def post(self, url, dados):
            return client.post(url, dados, content_type="application/json", **self.cabecalho)

        def patch(self, url, dados):
            return client.patch(url, dados, content_type="application/json", **self.cabecalho)

        def delete(self, url):
            return client.delete(url, **self.cabecalho)

    return ClienteLogado


@pytest.fixture
def secos(db):
    return Categoria.objects.create(nome="Secos e molhados")


@pytest.fixture
def acougue(db):
    return Categoria.objects.create(nome="Açougue", perecivel_padrao=True)


@pytest.fixture
def boi_bom(db):
    return Fornecedor.objects.create(nome="Frigorífico Boi Bom", prazo_entrega_dias=3)


def _arroz(categoria, **extras):
    return {"nome": "Arroz 5 kg", "categoria": categoria.pk, "unidade_medida": "PCT", **extras}


# --- Cadastro ------------------------------------------------------------------------------------


def test_b3_operacao_cadastra_produto_completo(api, acougue, boi_bom):
    resposta = api("OPERACAO").post(
        URL,
        {
            "nome": "Alcatra",
            "categoria": acougue.pk,
            "fornecedor_padrao": boi_bom.pk,
            "unidade_medida": "KG",
            "perecivel": True,
            "durabilidade_dias": 3,
            "preco_custo": "39.90",
            "preco_venda": "54.90",
            "estoque_minimo": "2.500",
            "critico_fim_semana": True,
        },
    )
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["categoria_nome"] == "Açougue"
    assert corpo["fornecedor_padrao_nome"] == "Frigorífico Boi Bom"
    assert corpo["preco_venda"] == "54.90"  # dinheiro como texto, nunca float
    assert corpo["estoque_minimo"] == "2.500"  # carne em quilo fracionado
    alcatra = Produto.objects.get(nome="Alcatra")
    assert alcatra.preco_custo == Decimal("39.90")
    assert alcatra.critico_fim_semana is True  # RF15


def test_rn01_produto_nao_tem_saldo_na_api(api, secos):
    # RN01: saldo é derivado das movimentações; nunca é um campo do produto.
    corpo = api("OPERACAO").post(URL, _arroz(secos)).json()
    assert "saldo" not in corpo
    resposta = api("OPERACAO").post(URL, {**_arroz(secos, nome="Feijão 1 kg"), "saldo": "50"})
    assert resposta.status_code == 201
    assert "saldo" not in resposta.json()


def test_b3_campos_obrigatorios_faltando_sao_apontados(api):
    # Operação 01, passo 5: devolve o campo que falta; nada é gravado.
    resposta = api("OPERACAO").post(URL, {})
    assert resposta.status_code == 400
    assert set(resposta.json()["erro"]["campos"]) == {"nome", "categoria", "unidade_medida"}
    assert not Produto.objects.exists()


def test_b3_so_os_campos_obrigatorios_bastam(api, secos):
    # RNF05: formulário curto — o resto é opcional.
    resposta = api("OPERACAO").post(URL, _arroz(secos))
    assert resposta.status_code == 201
    arroz = Produto.objects.get()
    assert arroz.preco_venda is None
    assert arroz.critico_fim_semana is False


def test_b3_categoria_inexistente_e_recusada(api, db):
    resposta = api("OPERACAO").post(URL, {"nome": "Arroz", "categoria": 9999, "unidade_medida": "PCT"})
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"] == {"categoria": ["Essa categoria não existe."]}


def test_b3_fornecedor_inexistente_e_recusado(api, secos):
    resposta = api("OPERACAO").post(URL, _arroz(secos, fornecedor_padrao=9999))
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"] == {"fornecedor_padrao": ["Esse fornecedor não existe."]}


# --- L17: unidade de medida ----------------------------------------------------------------------


@pytest.mark.parametrize("unidade", ["KG", "UN", "L", "PCT"])
def test_l17_unidades_aceitas(api, secos, unidade):
    assert api("OPERACAO").post(URL, _arroz(secos, unidade_medida=unidade)).status_code == 201


def test_l17_unidade_fora_da_lista_e_recusada(api, secos):
    resposta = api("OPERACAO").post(URL, _arroz(secos, unidade_medida="quilo"))
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"] == {"unidade_medida": ["Escolha a unidade: KG, UN, L ou PCT."]}


def test_l17_unidade_em_minusculas_e_gravada_em_maiusculas(api, secos):
    api("OPERACAO").post(URL, _arroz(secos, unidade_medida=" kg "))
    assert Produto.objects.get().unidade_medida == "KG"


# --- Números -------------------------------------------------------------------------------------


@pytest.mark.parametrize("campo", ["preco_custo", "preco_venda", "estoque_minimo"])
def test_b3_valores_negativos_sao_recusados(api, secos, campo):
    resposta = api("OPERACAO").post(URL, _arroz(secos, **{campo: "-1"}))
    assert resposta.status_code == 400
    assert campo in resposta.json()["erro"]["campos"]


def test_b3_preco_com_mais_de_dois_centavos_e_recusado(api, secos):
    resposta = api("OPERACAO").post(URL, _arroz(secos, preco_venda="10.999"))
    assert resposta.status_code == 400
    assert "preco_venda" in resposta.json()["erro"]["campos"]


def test_b3_preco_que_nao_e_numero_e_recusado(api, secos):
    resposta = api("OPERACAO").post(URL, _arroz(secos, preco_venda="dez reais"))
    assert resposta.status_code == 400
    assert "preco_venda" in resposta.json()["erro"]["campos"]


def test_x1_durabilidade_acima_de_10_anos_e_recusada(api, acougue):
    """X1, item 14 (decisão do grupo, 16/11/2026): 2 bilhões de dias quebravam a entrada de mercadoria."""
    dados = {"nome": "Frango", "categoria": acougue.pk, "unidade_medida": "KG", "perecivel": True}
    resposta = api("OPERACAO").post(URL, {**dados, "durabilidade_dias": 2_000_000_000})
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"]["durabilidade_dias"] == [
        "A durabilidade vai até 3650 dias (10 anos)."
    ]
    assert api("OPERACAO").post(URL, {**dados, "durabilidade_dias": 3650}).status_code == 201


def test_b3_durabilidade_que_nao_e_numero_e_recusada(api, acougue):
    resposta = api("OPERACAO").post(
        URL,
        {"nome": "Frango", "categoria": acougue.pk, "unidade_medida": "KG", "durabilidade_dias": "quatro"},
    )
    assert resposta.status_code == 400
    assert "durabilidade_dias" in resposta.json()["erro"]["campos"]


# --- Fluxograma 01, passo 6: nome único na categoria -----------------------------------------------


def test_b3_nome_repetido_na_mesma_categoria_e_recusado(api, secos):
    api("OPERACAO").post(URL, _arroz(secos))
    resposta = api("OPERACAO").post(URL, _arroz(secos))
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"] == {
        "nome": ["Já existe um produto com esse nome nesta categoria."]
    }
    assert Produto.objects.count() == 1


@pytest.mark.parametrize("parecido", ["arroz 5 KG", "  Arroz   5 kg ", "ÁRROZ 5 KG"])
def test_x1_nome_que_so_muda_maiuscula_acento_ou_espaco_e_repetido(api, secos, parecido):
    """X1, item 12: a importação compara assim (L05); dois nomes "iguais" deixariam a venda pendente."""
    api("OPERACAO").post(URL, _arroz(secos))
    resposta = api("OPERACAO").post(URL, _arroz(secos, nome=parecido))
    assert resposta.status_code == 400
    assert resposta.json()["erro"]["campos"] == {
        "nome": ["Já existe um produto com esse nome nesta categoria."]
    }
    assert Produto.objects.count() == 1


def test_x1_editar_para_um_nome_parecido_com_outro_e_recusado(api, secos):
    api("OPERACAO").post(URL, _arroz(secos))
    feijao_id = api("OPERACAO").post(URL, _arroz(secos, nome="Feijão 1 kg")).json()["id"]
    resposta = api("OPERACAO").patch(f"{URL}{feijao_id}/", {"nome": "arroz 5 KG"})
    assert resposta.status_code == 400


def test_x1_corrigir_a_maiuscula_do_proprio_nome_e_aceito(api, secos):
    produto_id = api("OPERACAO").post(URL, _arroz(secos, nome="arroz 5 kg")).json()["id"]
    assert api("OPERACAO").patch(f"{URL}{produto_id}/", {"nome": "Arroz 5 kg"}).status_code == 200


def test_b3_mesmo_nome_em_outra_categoria_e_aceito(api, secos):
    outra = Categoria.objects.create(nome="Promoções")
    api("OPERACAO").post(URL, _arroz(secos))
    assert api("OPERACAO").post(URL, _arroz(outra)).status_code == 201


def test_b3_editar_o_proprio_produto_sem_mudar_o_nome_e_aceito(api, secos):
    produto_id = api("OPERACAO").post(URL, _arroz(secos)).json()["id"]
    resposta = api("OPERACAO").patch(f"{URL}{produto_id}/", {"nome": "Arroz 5 kg", "preco_venda": "27.90"})
    assert resposta.status_code == 200
    assert Produto.objects.get().preco_venda == Decimal("27.90")


def test_b3_editar_para_um_nome_que_ja_existe_na_categoria_e_recusado(api, secos):
    api("OPERACAO").post(URL, _arroz(secos))
    feijao_id = api("OPERACAO").post(URL, _arroz(secos, nome="Feijão 1 kg")).json()["id"]
    resposta = api("OPERACAO").patch(f"{URL}{feijao_id}/", {"nome": "Arroz 5 kg"})
    assert resposta.status_code == 400
    assert "nome" in resposta.json()["erro"]["campos"]


def test_b3_mudar_de_categoria_para_uma_onde_o_nome_ja_existe_e_recusado(api, secos):
    outra = Categoria.objects.create(nome="Promoções")
    api("OPERACAO").post(URL, _arroz(secos))
    na_outra = api("OPERACAO").post(URL, _arroz(outra)).json()["id"]
    resposta = api("OPERACAO").patch(f"{URL}{na_outra}/", {"categoria": secos.pk})
    assert resposta.status_code == 400
    assert "nome" in resposta.json()["erro"]["campos"]


# --- L19: perecível herda o padrão da categoria ---------------------------------------------------


def test_l19_produto_sem_dizer_se_e_perecivel_herda_da_categoria(api, acougue):
    resposta = api("OPERACAO").post(
        URL,
        {
            "nome": "Frango resfriado 1 kg",
            "categoria": acougue.pk,
            "unidade_medida": "KG",
            "durabilidade_dias": 4,
        },
    )
    assert resposta.status_code == 201
    assert resposta.json()["perecivel"] is True


def test_l19_categoria_nao_perecivel_da_produto_nao_perecivel(api, secos):
    assert api("OPERACAO").post(URL, _arroz(secos)).json()["perecivel"] is False


def test_l19_quem_diz_explicitamente_prevalece_sobre_a_categoria(api, acougue):
    resposta = api("OPERACAO").post(
        URL, {"nome": "Carvão 3 kg", "categoria": acougue.pk, "unidade_medida": "PCT", "perecivel": False}
    )
    assert resposta.status_code == 201
    assert resposta.json()["perecivel"] is False


# --- Lista e filtros -----------------------------------------------------------------------------


def test_b3_lista_em_ordem_alfabetica(api, secos):
    for nome in ["Óleo 900 ml", "Arroz 5 kg", "Feijão 1 kg"]:
        Produto.objects.create(categoria=secos, nome=nome, unidade_medida="UN")
    assert [p["nome"] for p in api("OPERACAO").get(URL).json()] == [
        "Arroz 5 kg",
        "Feijão 1 kg",
        "Óleo 900 ml",
    ]


def test_b3_busca_pelo_nome(api, secos):
    for nome in ["Arroz 5 kg", "Arroz integral 1 kg", "Feijão 1 kg"]:
        Produto.objects.create(categoria=secos, nome=nome, unidade_medida="UN")
    nomes = [p["nome"] for p in api("OPERACAO").get(f"{URL}?busca=arroz").json()]
    assert nomes == ["Arroz 5 kg", "Arroz integral 1 kg"]


def test_b3_filtra_pela_categoria(api, secos, acougue):
    Produto.objects.create(categoria=secos, nome="Arroz 5 kg", unidade_medida="PCT")
    Produto.objects.create(
        categoria=acougue, nome="Alcatra", unidade_medida="KG", perecivel=True, durabilidade_dias=3
    )
    nomes = [p["nome"] for p in api("OPERACAO").get(f"{URL}?categoria={acougue.pk}").json()]
    assert nomes == ["Alcatra"]


def test_b3_filtro_de_categoria_invalido_e_recusado(api, secos):
    resposta = api("OPERACAO").get(f"{URL}?categoria=abc")
    assert resposta.status_code == 400
    assert "categoria" in resposta.json()["erro"]["campos"]


# --- RN14 e nada apagado -------------------------------------------------------------------------


@pytest.mark.parametrize("papel", ["DONO", "GESTAO"])
def test_rn14_dono_e_gestao_nao_cadastram_produto(api, secos, papel):
    # Operação 01, passo 3: recusa antes de tocar no banco.
    assert api(papel).post(URL, _arroz(secos)).status_code == 403
    assert api(papel).get(URL).status_code == 403
    assert not Produto.objects.exists()


def test_b3_produto_nunca_e_apagado(api, secos):
    produto_id = api("OPERACAO").post(URL, _arroz(secos)).json()["id"]
    assert api("OPERACAO").delete(f"{URL}{produto_id}/").status_code == 405
    assert Produto.objects.filter(pk=produto_id).exists()

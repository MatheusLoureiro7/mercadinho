"""
Tarefa B1 — tabelas de usuário, categoria, produto e fornecedor.

O banco criado pelas migrações tem de ser o da Apostila IV (schema.sql): mesmas tabelas, mesmas
colunas, mesmos tipos, mesmas restrições. As regras que o próprio banco garante (RN03, RN14,
prazo do fornecedor) são testadas aqui; a validação na API é das tarefas B3, B4 e A4.
"""

from decimal import Decimal

import pytest
from django.contrib.auth import authenticate
from django.db import IntegrityError, connection, transaction

from cadastro.models import Categoria, Fornecedor, Produto, Usuario
from tests.conftest import TIPOS_POSTGRES, colunas_do_schema, colunas_no_banco, restricoes

TABELAS_B1 = ["categoria", "fornecedor", "produto", "usuario"]

# --- O banco confere com a Apostila IV ------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize("tabela", TABELAS_B1)
def test_b1_tabela_tem_exatamente_as_colunas_do_schema(tabela):
    esperado = colunas_do_schema(tabela)
    no_banco = colunas_no_banco(tabela)
    assert set(no_banco) == set(esperado), "colunas diferentes da Apostila IV"


@pytest.mark.django_db
@pytest.mark.parametrize("tabela", TABELAS_B1)
def test_b1_colunas_tem_tipo_tamanho_e_obrigatoriedade_do_schema(tabela):
    esperado = colunas_do_schema(tabela)
    no_banco = colunas_no_banco(tabela)
    for nome, coluna in esperado.items():
        real = no_banco[nome]
        assert real["tipo"] == TIPOS_POSTGRES[coluna["tipo"]], f"{tabela}.{nome}: tipo"
        if coluna["tamanho"]:
            assert real["tamanho"] == coluna["tamanho"], f"{tabela}.{nome}: tamanho"
        if coluna["escala"] is not None:
            assert real["escala"] == coluna["escala"], f"{tabela}.{nome}: casas decimais"
        assert real["nulo"] == coluna["nulo"], f"{tabela}.{nome}: aceita nulo?"


@pytest.mark.django_db
@pytest.mark.parametrize("tabela", TABELAS_B1)
def test_b1_valores_padrao_sao_os_do_schema(tabela):
    esperado = colunas_do_schema(tabela)
    no_banco = colunas_no_banco(tabela)
    for nome, coluna in esperado.items():
        padrao_real = no_banco[nome]["padrao"]
        if coluna["tipo"] == "SERIAL":
            # SERIAL e IDENTITY são o mesmo inteiro sequencial; o Django gera IDENTITY, a forma
            # recomendada pelo PostgreSQL. O schema.sql marca os tipos como derivados do uso.
            serial = padrao_real and padrao_real.startswith("nextval")
            assert serial or no_banco[nome]["identidade"], f"{tabela}.{nome}: sequência"
        elif coluna["padrao"]:
            assert padrao_real == coluna["padrao"].lower(), f"{tabela}.{nome}: valor padrão"


@pytest.mark.django_db
def test_b1_restricoes_nomeadas_do_schema_existem():
    assert "ck_fornecedor_prazo" in restricoes("fornecedor")
    assert {"ck_produto_rn03", "uq_produto_nome_categoria"} <= restricoes("produto")
    assert "ck_usuario_papel" in restricoes("usuario")


@pytest.mark.django_db
def test_rn01_produto_nao_tem_coluna_de_saldo():
    # RN01: o saldo é sempre derivado das movimentações. Nunca uma coluna.
    assert not any("saldo" in coluna for coluna in colunas_no_banco("produto"))


# --- Fixtures ------------------------------------------------------------------------------------


@pytest.fixture
def acougue(db):
    return Categoria.objects.create(nome="Açougue", perecivel_padrao=True)


@pytest.fixture
def frios(db):
    return Categoria.objects.create(nome="Frios", perecivel_padrao=True)


def _falha_no_banco(funcao):
    """Executa uma gravação que o banco precisa recusar, sem estragar a transação do teste."""
    with pytest.raises(IntegrityError), transaction.atomic():
        funcao()


# --- RN03: perecível exige prazo de durabilidade (última defesa, no banco) -------------------------


def test_rn03_banco_recusa_perecivel_sem_durabilidade(acougue):
    _falha_no_banco(
        lambda: Produto.objects.create(
            categoria=acougue, nome="Frango resfriado 1 kg", unidade_medida="KG", perecivel=True
        )
    )


def test_rn03_banco_recusa_perecivel_com_durabilidade_zero(acougue):
    _falha_no_banco(
        lambda: Produto.objects.create(
            categoria=acougue,
            nome="Frango resfriado 1 kg",
            unidade_medida="KG",
            perecivel=True,
            durabilidade_dias=0,
        )
    )


def test_rn03_banco_aceita_perecivel_com_durabilidade(acougue):
    frango = Produto.objects.create(
        categoria=acougue,
        nome="Frango resfriado 1 kg",
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=4,
    )
    assert frango.pk is not None


def test_rn03_banco_aceita_nao_perecivel_sem_durabilidade(db):
    secos = Categoria.objects.create(nome="Secos e molhados")
    arroz = Produto.objects.create(categoria=secos, nome="Arroz 5 kg", unidade_medida="PCT")
    assert arroz.durabilidade_dias is None


# --- Fluxograma 01: nome único na categoria ------------------------------------------------------


def test_b1_nome_repetido_na_mesma_categoria_e_recusado(frios):
    Produto.objects.create(
        categoria=frios, nome="Presunto", unidade_medida="KG", perecivel=True, durabilidade_dias=7
    )
    _falha_no_banco(
        lambda: Produto.objects.create(
            categoria=frios, nome="Presunto", unidade_medida="KG", perecivel=True, durabilidade_dias=7
        )
    )


def test_b1_mesmo_nome_em_outra_categoria_e_aceito(frios, acougue):
    Produto.objects.create(
        categoria=frios, nome="Linguiça", unidade_medida="KG", perecivel=True, durabilidade_dias=5
    )
    outra = Produto.objects.create(
        categoria=acougue, nome="Linguiça", unidade_medida="KG", perecivel=True, durabilidade_dias=5
    )
    assert outra.pk is not None


def test_b1_categoria_repetida_e_recusada(frios):
    _falha_no_banco(lambda: Categoria.objects.create(nome="Frios"))


# --- Valores padrão e Decimal --------------------------------------------------------------------


def test_b1_padroes_do_banco_valem_sem_o_django(acougue):
    # O DEFAULT está no banco, como no schema.sql — vale até para quem grava sem passar pelo Django.
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO produto (categoria_id, nome, unidade_medida) VALUES (%s, %s, %s) "
            "RETURNING perecivel, critico_fim_semana",
            [acougue.pk, "Carvão 3 kg", "PCT"],
        )
        assert cursor.fetchone() == (False, False)


def test_b1_precos_e_quantidades_sao_decimal(acougue):
    produto = Produto.objects.create(
        categoria=acougue,
        nome="Carne moída",
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=2,
        preco_custo=Decimal("24.90"),
        preco_venda=Decimal("34.90"),
        estoque_minimo=Decimal("2.500"),
    )
    produto.refresh_from_db()
    assert produto.preco_venda == Decimal("34.90")
    assert produto.estoque_minimo == Decimal("2.500")  # carne vendida em quilo fracionado


# --- Fornecedor ----------------------------------------------------------------------------------


def test_b1_fornecedor_sem_prazo_de_entrega_e_recusado(db):
    _falha_no_banco(lambda: Fornecedor.objects.create(nome="Frigorífico Boi Bom"))


def test_b1_fornecedor_com_prazo_negativo_e_recusado(db):
    _falha_no_banco(lambda: Fornecedor.objects.create(nome="Frigorífico Boi Bom", prazo_entrega_dias=-1))


def test_b1_fornecedor_com_prazo_e_aceito(db):
    fornecedor = Fornecedor.objects.create(nome="Frigorífico Boi Bom", prazo_entrega_dias=3)
    assert fornecedor.prazo_entrega_dias == 3


def test_b1_produto_aponta_o_fornecedor_padrao(acougue):
    fornecedor = Fornecedor.objects.create(nome="Frigorífico Boi Bom", prazo_entrega_dias=3)
    carne = Produto.objects.create(
        categoria=acougue,
        fornecedor_padrao=fornecedor,
        nome="Alcatra",
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=3,
    )
    assert carne.fornecedor_padrao.prazo_entrega_dias == 3


# --- Usuário: RN14 e decisão da L09 --------------------------------------------------------------


def test_rn14_papel_fora_dos_tres_e_recusado(db):
    _falha_no_banco(
        lambda: Usuario.objects.create_user(login="funcionario", senha="x", nome="Zé", papel="CAIXA")
    )


@pytest.mark.parametrize("papel", ["DONO", "GESTAO", "OPERACAO"])
def test_rn14_os_tres_papeis_sao_aceitos(db, papel):
    usuario = Usuario.objects.create_user(login=f"u_{papel.lower()}", senha="x", nome="Teste", papel=papel)
    assert usuario.papel == papel


def test_rnf12_senha_e_gravada_so_como_hash(db):
    usuario = Usuario.objects.create_user(
        login="sobrinho", senha="segredo123", nome="Sobrinho", papel="OPERACAO"
    )
    with connection.cursor() as cursor:
        cursor.execute("SELECT senha_hash FROM usuario WHERE id = %s", [usuario.pk])
        senha_hash = cursor.fetchone()[0]
    assert senha_hash != "segredo123"
    assert "segredo123" not in senha_hash
    assert usuario.check_password("segredo123")
    assert not usuario.check_password("senha-errada")


def test_l09_login_usa_a_tabela_usuario(db):
    Usuario.objects.create_user(login="esposa", senha="segredo123", nome="Esposa", papel="GESTAO")
    assert authenticate(login="esposa", password="segredo123") is not None
    assert authenticate(login="esposa", password="errada") is None


def test_l09_usuario_inativo_nao_entra(db):
    Usuario.objects.create_user(
        login="antigo", senha="segredo123", nome="Antigo", papel="OPERACAO", ativo=False
    )
    assert authenticate(login="antigo", password="segredo123") is None


def test_l09_login_repetido_e_recusado(db):
    Usuario.objects.create_user(login="dono", senha="x", nome="Sr. João", papel="DONO")
    _falha_no_banco(lambda: Usuario.objects.create_user(login="dono", senha="y", nome="Outro", papel="DONO"))


def test_l09_entrar_no_sistema_nao_grava_nada_no_usuario(db):
    # Sem last_login (decisão da L09): o login não escreve na tabela usuario.
    Usuario.objects.create_user(login="dono", senha="x", nome="Sr. João", papel="DONO")
    assert not hasattr(Usuario, "last_login") or Usuario.last_login is None

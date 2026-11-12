"""
Tarefa J2 — carga inicial dos produtos, junto com o cliente.

O mercado é fictício (decisão de 30/10/2026): não há lista real; a carga é de uma lista de exemplo
feita pelo grupo. Para a loja de verdade, o caminho seria o mesmo: a esposa preenche a planilha e o
comando carrega.

    python backend/manage.py carregar_produtos planilha.xlsx

Formato: docs/FORMATO-PLANILHA-PRODUTOS.md — três abas, na ordem do cadastro: Categorias,
Fornecedores e Produtos. Cada linha passa pelas MESMAS conferências da API (B2, B3, RN03, unidade
L17, nome único na categoria — operação 01). Se uma linha estiver errada, **nada é gravado** e o
comando aponta todas, com a aba e o número da linha. O que já está cadastrado (mesmo nome, sem
diferenciar maiúscula nem acento) é mantido como está: rodar de novo não duplica nem altera.

Losangos, pelo "sim" e pelo "não":
    a planilha abre e tem a aba Produtos?   sim → carrega              não → *_planilha_ilegivel_*
    a linha passa nas regras do cadastro?   sim → grava                não → *_linha_errada_*, *_rn03_*
    já está cadastrado?                     sim → *_ja_cadastrado_*    não → grava
"""

from decimal import Decimal
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from openpyxl import Workbook

from cadastro.carga import PlanilhaIlegivel, carregar_planilha
from cadastro.models import Categoria, Fornecedor, Produto

EXEMPLO = Path(__file__).resolve().parents[2] / "docs" / "exemplos" / "produtos-iniciais.xlsx"

CAB_CATEGORIAS = ["Categoria", "Perecível"]
CAB_FORNECEDORES = ["Fornecedor", "Prazo de entrega (dias)", "Pedido mínimo (R$)", "Contato"]
CAB_PRODUTOS = [
    "Produto",
    "Categoria",
    "Unidade",
    "Perecível",
    "Dura quantos dias",
    "Preço de custo",
    "Preço de venda",
    "Estoque mínimo",
    "Fornecedor",
    "Não pode faltar no fim de semana",
]


def _planilha(
    pasta, *, categorias=(), fornecedores=(), produtos=(), abas=("Categorias", "Fornecedores", "Produtos")
):
    livro = Workbook()
    livro.remove(livro.active)
    conteudo = {
        "Categorias": (CAB_CATEGORIAS, categorias),
        "Fornecedores": (CAB_FORNECEDORES, fornecedores),
        "Produtos": (CAB_PRODUTOS, produtos),
    }
    for aba in abas:
        cabecalho, linhas = conteudo[aba]
        folha = livro.create_sheet(aba)
        folha.append(cabecalho)
        for linha in linhas:
            folha.append(list(linha))
    caminho = pasta / "produtos.xlsx"
    livro.save(caminho)
    return caminho


CATEGORIAS = [("Açougue", "sim"), ("Secos e molhados", "não")]
FORNECEDORES = [("Frigorífico Boi Bom", 3, 800, "(11) 3333-4444"), ("Atacadão Central", 2, None, None)]
FRANGO = ("Frango resfriado 1 kg", "Açougue", "KG", None, 4, 12.4, "18,90", 8, "Frigorífico Boi Bom", "sim")
ARROZ = ("Arroz 5 kg", "Secos e molhados", "pct", None, None, 21.5, 27.9, 10, "Atacadão Central", None)


# --- Carga ----------------------------------------------------------------------------------------


@pytest.mark.django_db
def test_j2_carrega_categorias_fornecedores_e_produtos(tmp_path):
    caminho = _planilha(tmp_path, categorias=CATEGORIAS, fornecedores=FORNECEDORES, produtos=[FRANGO, ARROZ])
    resultado = carregar_planilha(caminho)
    assert resultado.erros == []
    assert (
        resultado.criados["categorias"],
        resultado.criados["fornecedores"],
        resultado.criados["produtos"],
    ) == (2, 2, 2)

    frango = Produto.objects.get(nome="Frango resfriado 1 kg")
    assert frango.categoria.nome == "Açougue" and frango.fornecedor_padrao.nome == "Frigorífico Boi Bom"
    assert (frango.unidade_medida, frango.perecivel, frango.durabilidade_dias) == ("KG", True, 4)
    assert (frango.preco_custo, frango.preco_venda, frango.estoque_minimo) == (
        Decimal("12.40"),
        Decimal("18.90"),
        Decimal("8.000"),
    )
    assert frango.critico_fim_semana is True
    arroz = Produto.objects.get(nome="Arroz 5 kg")
    assert (arroz.unidade_medida, arroz.perecivel, arroz.critico_fim_semana) == ("PCT", False, False)
    boi_bom = Fornecedor.objects.get(nome="Frigorífico Boi Bom")
    assert (boi_bom.prazo_entrega_dias, boi_bom.pedido_minimo, boi_bom.contato) == (
        3,
        Decimal("800.00"),
        "(11) 3333-4444",
    )
    assert Categoria.objects.get(nome="Açougue").perecivel_padrao is True


@pytest.mark.django_db
def test_j2_perecivel_em_branco_segue_a_categoria_l19(tmp_path):
    caminho = _planilha(tmp_path, categorias=CATEGORIAS, fornecedores=FORNECEDORES, produtos=[FRANGO])
    carregar_planilha(caminho)
    assert Produto.objects.get(nome="Frango resfriado 1 kg").perecivel is True


@pytest.mark.django_db
def test_j2_categoria_e_fornecedor_escritos_sem_acento_casam(tmp_path):
    produto = ("Alcatra", "acougue", "KG", "sim", 3, 38, 52.9, 5, "frigorifico boi bom", "sim")
    caminho = _planilha(tmp_path, categorias=CATEGORIAS, fornecedores=FORNECEDORES, produtos=[produto])
    assert carregar_planilha(caminho).erros == []
    assert Produto.objects.get(nome="Alcatra").categoria.nome == "Açougue"


@pytest.mark.django_db
def test_j2_abas_de_categorias_e_fornecedores_sao_opcionais_se_ja_cadastrados(tmp_path):
    Categoria.objects.create(nome="Secos e molhados")
    Fornecedor.objects.create(nome="Atacadão Central", prazo_entrega_dias=2)
    caminho = _planilha(tmp_path, produtos=[ARROZ], abas=("Produtos",))
    assert carregar_planilha(caminho).erros == []
    assert Produto.objects.filter(nome="Arroz 5 kg").exists()


# --- Recusa: nada é gravado -----------------------------------------------------------------------


@pytest.mark.django_db
def test_rn03_perecivel_sem_durabilidade_na_planilha_e_recusado_e_nada_e_gravado(tmp_path):
    sem_prazo = ("Linguiça toscana", "Açougue", "KG", "sim", None, 18, 26.9, 4, None, "sim")
    caminho = _planilha(
        tmp_path, categorias=CATEGORIAS, fornecedores=FORNECEDORES, produtos=[FRANGO, sem_prazo]
    )
    resultado = carregar_planilha(caminho)
    assert [(erro.aba, erro.linha, erro.coluna) for erro in resultado.erros] == [
        ("Produtos", 3, "Dura quantos dias")
    ]
    assert "durabilidade" in resultado.erros[0].mensagem.lower() or "dias" in resultado.erros[0].mensagem
    assert Produto.objects.count() == 0 and Categoria.objects.count() == 0 and Fornecedor.objects.count() == 0


@pytest.mark.django_db
def test_j2_linha_errada_aponta_aba_linha_e_coluna_de_todas(tmp_path):
    produtos = [
        ("Feijão carioca 1 kg", "Secos e molhados", "saco", None, None, 6, 8.9, 10, None, None),
        ("Fósforo", "Bazar", "UN", None, None, 2, 3.5, 5, None, None),
        ("Óleo de soja 900 ml", "Secos e molhados", "UN", None, None, 6, "oito", 10, None, None),
        ("Sal 1 kg", "Secos e molhados", "PCT", None, None, 2, 3.5, 5, "Distribuidora que não existe", None),
    ]
    fornecedores = [("Distribuidora Sol", None, None, None)]
    caminho = _planilha(tmp_path, categorias=CATEGORIAS, fornecedores=fornecedores, produtos=produtos)
    erros = [(erro.aba, erro.linha, erro.coluna) for erro in carregar_planilha(caminho).erros]
    assert erros == [
        ("Fornecedores", 2, "Prazo de entrega (dias)"),
        ("Produtos", 2, "Unidade"),
        ("Produtos", 3, "Categoria"),
        ("Produtos", 4, "Preço de venda"),
        ("Produtos", 5, "Fornecedor"),
    ]
    assert Produto.objects.count() == 0


@pytest.mark.django_db
def test_j2_produto_repetido_na_mesma_planilha_e_recusado(tmp_path):
    caminho = _planilha(tmp_path, categorias=CATEGORIAS, fornecedores=FORNECEDORES, produtos=[ARROZ, ARROZ])
    erros = carregar_planilha(caminho).erros
    assert [(erro.linha, erro.coluna) for erro in erros] == [(3, "Produto")]


@pytest.mark.django_db
def test_j2_sim_ou_nao_escrito_de_outro_jeito_e_recusado(tmp_path):
    produto = ("Carvão 3 kg", "Secos e molhados", "PCT", None, None, 12, 19.9, 6, None, "talvez")
    caminho = _planilha(tmp_path, categorias=CATEGORIAS, fornecedores=FORNECEDORES, produtos=[produto])
    erros = carregar_planilha(caminho).erros
    assert [(erro.coluna, erro.mensagem) for erro in erros] == [
        ("Não pode faltar no fim de semana", "Escreva sim ou não (ou deixe em branco)."),
    ]


@pytest.mark.django_db
def test_j2_planilha_ilegivel_sem_a_aba_produtos(tmp_path):
    caminho = _planilha(tmp_path, categorias=CATEGORIAS, abas=("Categorias",))
    with pytest.raises(PlanilhaIlegivel, match="Produtos"):
        carregar_planilha(caminho)


@pytest.mark.django_db
def test_j2_arquivo_que_nao_e_excel_e_ilegivel(tmp_path):
    caminho = tmp_path / "produtos.xlsx"
    caminho.write_text("não é planilha")
    with pytest.raises(PlanilhaIlegivel, match=".xlsx"):
        carregar_planilha(caminho)


@pytest.mark.django_db
def test_j2_falta_coluna_obrigatoria_e_ilegivel(tmp_path):
    livro = Workbook()
    livro.active.title = "Produtos"
    livro.active.append(["Produto", "Unidade"])
    caminho = tmp_path / "produtos.xlsx"
    livro.save(caminho)
    with pytest.raises(PlanilhaIlegivel, match="Categoria"):
        carregar_planilha(caminho)


# --- Rodar de novo --------------------------------------------------------------------------------


@pytest.mark.django_db
def test_j2_ja_cadastrado_e_mantido_e_rodar_de_novo_nao_duplica(tmp_path):
    Categoria.objects.create(nome="Açougue", perecivel_padrao=True)
    caminho = _planilha(tmp_path, categorias=CATEGORIAS, fornecedores=FORNECEDORES, produtos=[FRANGO, ARROZ])
    primeira = carregar_planilha(caminho)
    assert (primeira.criados["categorias"], primeira.mantidos["categorias"]) == (1, 1)
    segunda = carregar_planilha(caminho)
    assert segunda.erros == []
    assert segunda.criados == {"categorias": 0, "fornecedores": 0, "produtos": 0}
    assert segunda.mantidos == {"categorias": 2, "fornecedores": 2, "produtos": 2}
    assert Produto.objects.count() == 2


@pytest.mark.django_db
def test_j2_produto_ja_cadastrado_nao_e_alterado_pela_planilha(tmp_path):
    secos = Categoria.objects.create(nome="Secos e molhados")
    Produto.objects.create(
        nome="Arroz 5 kg", categoria=secos, unidade_medida="PCT", preco_venda=Decimal("25.00")
    )
    Fornecedor.objects.create(nome="Atacadão Central", prazo_entrega_dias=2)
    caminho = _planilha(tmp_path, produtos=[ARROZ], abas=("Produtos",))
    assert carregar_planilha(caminho).mantidos["produtos"] == 1
    assert Produto.objects.get(nome="Arroz 5 kg").preco_venda == Decimal("25.00")


# --- Comando e planilha de exemplo ----------------------------------------------------------------


@pytest.mark.django_db
def test_j2_comando_carrega_e_resume(tmp_path):
    caminho = _planilha(tmp_path, categorias=CATEGORIAS, fornecedores=FORNECEDORES, produtos=[FRANGO, ARROZ])
    saida = StringIO()
    call_command("carregar_produtos", str(caminho), stdout=saida)
    assert "2 produto(s) novo(s)" in saida.getvalue()


@pytest.mark.django_db
def test_j2_comando_com_erro_lista_as_linhas_e_termina_com_erro(tmp_path):
    sem_prazo = ("Linguiça toscana", "Açougue", "KG", "sim", None, 18, 26.9, 4, None, "sim")
    caminho = _planilha(tmp_path, categorias=CATEGORIAS, produtos=[sem_prazo])
    saida = StringIO()
    with pytest.raises(CommandError, match="Nada foi gravado"):
        call_command("carregar_produtos", str(caminho), stdout=saida)
    assert "Produtos, linha 2, Dura quantos dias" in saida.getvalue()


@pytest.mark.django_db
def test_j2_planilha_de_exemplo_do_grupo_carrega_inteira():
    resultado = carregar_planilha(EXEMPLO)
    assert resultado.erros == []
    assert resultado.criados["produtos"] >= 40
    criticos = set(Produto.objects.filter(critico_fim_semana=True).values_list("nome", flat=True))
    # RN10: os itens que o cliente nomeou um a um estão marcados como críticos de fim de semana.
    for palavra in ("Carne", "Carvão", "Cerveja", "Linguiça", "Asinha"):
        assert any(palavra.lower() in nome.lower() for nome in criticos), palavra
    assert all(p.durabilidade_dias for p in Produto.objects.filter(perecivel=True))  # RN03

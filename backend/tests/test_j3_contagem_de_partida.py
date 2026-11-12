"""
Tarefa J3 — inventário de partida: a contagem física que dá o saldo inicial de cada produto.

Decisão do grupo (12/11/2026): a contagem entra **como entrada de mercadoria** (operação 02),
pelo mesmo serviço da tela de Entrada — cada linha contada vira um lote com a sua movimentação
ENTRADA (RN01: saldo só nasce de movimentação), marcada com `origem = 'INVENTARIO'`. Assim o
perecível contado já tem validade (RN04: a da embalagem ou, sem ela, entrada + durabilidade), entra
no aviso de validade (RN05) e sai pelo lote que vence primeiro (RN02).

    python backend/manage.py carregar_contagem planilha.xlsx

Formato: docs/FORMATO-PLANILHA-CONTAGEM.md — aba Contagem: Produto, Categoria (só para nome
repetido em duas categorias), Quantidade contada, Validade, Custo unitário. O mesmo produto pode
vir em várias linhas, uma por validade. Quantidade zero é ignorada (não há o que lançar).

Tudo ou nada, como na J2. A contagem é **de partida**: produto que já tinha estoque registrado antes
desta carga é mantido como está — rodar de novo não lança a contagem duas vezes.

Losangos, pelo "sim" e pelo "não":
    o produto existe (e só um com esse nome)?   sim → lança      não → *_produto_desconhecido_*,
                                                                         *_nome_repetido_*
    o produto é perecível?                       sim → *_rn04_*   não → *_nao_perecivel_*
    a validade já passou?                        sim → *_rn04_validade_passada_*   não → lança
    o produto já tinha estoque?                  sim → *_ja_tinha_estoque_*        não → lança
"""

from datetime import date, datetime
from decimal import Decimal
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from openpyxl import Workbook

from alertas.validade import gerar_avisos_de_validade
from cadastro.carga import carregar_planilha
from cadastro.models import Categoria, Produto, Usuario
from estoque.inventario import PlanilhaIlegivel, carregar_contagem
from estoque.models import Lote, Movimentacao
from estoque.saldo import saldo_do_produto

RAIZ = Path(__file__).resolve().parents[2]
EXEMPLO = RAIZ / "docs" / "exemplos" / "contagem-de-partida.xlsx"
EXEMPLO_PRODUTOS = RAIZ / "docs" / "exemplos" / "produtos-iniciais.xlsx"
SAO_PAULO = ZoneInfo("America/Sao_Paulo")
HOJE = date(2026, 11, 17)
CABECALHO = ["Produto", "Categoria", "Quantidade contada", "Validade", "Custo unitário"]


@pytest.fixture(autouse=True)
def segunda_17_11():
    with patch("django.utils.timezone.now", return_value=datetime(2026, 11, 17, 7, 0, tzinfo=SAO_PAULO)):
        yield


@pytest.fixture
def loja(db):
    acougue = Categoria.objects.create(nome="Açougue", perecivel_padrao=True)
    secos = Categoria.objects.create(nome="Secos e molhados")
    return {
        "frango": Produto.objects.create(
            categoria=acougue,
            nome="Frango resfriado 1 kg",
            unidade_medida="KG",
            perecivel=True,
            durabilidade_dias=4,
        ),
        "arroz": Produto.objects.create(
            categoria=secos, nome="Arroz 5 kg", unidade_medida="PCT", preco_custo=Decimal("21.50")
        ),
    }


def _planilha(pasta, linhas, cabecalho=CABECALHO, aba="Contagem"):
    livro = Workbook()
    livro.active.title = aba
    livro.active.append(cabecalho)
    for linha in linhas:
        livro.active.append(list(linha))
    caminho = pasta / "contagem.xlsx"
    livro.save(caminho)
    return caminho


# --- Lança como entrada ---------------------------------------------------------------------------


def test_j3_cada_linha_vira_lote_com_entrada_marcada_como_inventario(tmp_path, loja):
    caminho = _planilha(tmp_path, [("Arroz 5 kg", None, 12, None, "21,50")])
    resultado = carregar_contagem(caminho)
    assert resultado.erros == [] and resultado.lotes == 1
    lote = Lote.objects.get(produto=loja["arroz"])
    assert (lote.quantidade_inicial, lote.quantidade_atual, lote.data_entrada) == (
        Decimal("12"),
        Decimal("12"),
        HOJE,
    )
    assert lote.custo_unitario == Decimal("21.50")
    entrada = Movimentacao.objects.get(produto=loja["arroz"])
    assert (entrada.tipo, entrada.origem, entrada.lote) == ("ENTRADA", "INVENTARIO", lote)
    assert saldo_do_produto(loja["arroz"]) == Decimal("12")  # RN01


def test_j3_mesmo_produto_em_varias_validades_vira_um_lote_por_linha(tmp_path, loja):
    caminho = _planilha(
        tmp_path,
        [
            ("Frango resfriado 1 kg", None, "3,5", "19/11/2026", None),
            ("Frango resfriado 1 kg", None, 2, date(2026, 11, 20), None),
        ],
    )
    assert carregar_contagem(caminho).lotes == 2
    validades = sorted(Lote.objects.filter(produto=loja["frango"]).values_list("data_validade", flat=True))
    assert validades == [date(2026, 11, 19), date(2026, 11, 20)]
    assert saldo_do_produto(loja["frango"]) == Decimal("5.5")


def test_rn04_perecivel_sem_validade_na_contagem_ganha_entrada_mais_durabilidade(tmp_path, loja):
    carregar_contagem(_planilha(tmp_path, [("Frango resfriado 1 kg", None, 4, None, None)]))
    assert Lote.objects.get(produto=loja["frango"]).data_validade == date(2026, 11, 21)


def test_rn04_validade_passada_na_contagem_e_recusada_e_nada_e_gravado(tmp_path, loja):
    caminho = _planilha(
        tmp_path,
        [("Arroz 5 kg", None, 12, None, None), ("Frango resfriado 1 kg", None, 4, "16/11/2026", None)],
    )
    erros = carregar_contagem(caminho).erros
    assert [(erro.linha, erro.coluna) for erro in erros] == [(3, "Validade")]
    assert "já passou" in erros[0].mensagem
    assert Lote.objects.count() == 0 and Movimentacao.objects.count() == 0


def test_j3_nao_perecivel_sem_validade_fica_sem_validade(tmp_path, loja):
    carregar_contagem(_planilha(tmp_path, [("Arroz 5 kg", None, 12, None, None)]))
    assert Lote.objects.get(produto=loja["arroz"]).data_validade is None


def test_j3_quantidade_zero_e_ignorada(tmp_path, loja):
    resultado = carregar_contagem(_planilha(tmp_path, [("Arroz 5 kg", None, 0, None, None)]))
    assert (resultado.erros, resultado.lotes, resultado.zerados) == ([], 0, 1)
    assert Lote.objects.count() == 0


def test_j3_nome_sem_acento_e_maiuscula_casa_com_o_cadastro(tmp_path, loja):
    carregar_contagem(_planilha(tmp_path, [("ARROZ 5 KG", None, 3, None, None)]))
    assert saldo_do_produto(loja["arroz"]) == Decimal("3")


# --- Recusas --------------------------------------------------------------------------------------


def test_j3_produto_desconhecido_quantidade_e_data_invalidas_apontam_a_linha(tmp_path, loja):
    caminho = _planilha(
        tmp_path,
        [
            ("Picanha", None, 2, None, None),
            ("Arroz 5 kg", None, -1, None, None),
            ("Arroz 5 kg", None, "doze", None, None),
            ("Frango resfriado 1 kg", None, 2, "amanhã", None),
            ("Arroz 5 kg", None, 1, None, "vinte"),
            ("Arroz 5 kg", None, "1,2345", None, None),
        ],
    )
    erros = [(erro.linha, erro.coluna) for erro in carregar_contagem(caminho).erros]
    assert erros == [
        (2, "Produto"),
        (3, "Quantidade contada"),
        (4, "Quantidade contada"),
        (5, "Validade"),
        (6, "Custo unitário"),
        (7, "Quantidade contada"),
    ]
    assert Lote.objects.count() == 0


def test_j3_nome_repetido_em_duas_categorias_pede_a_categoria(tmp_path, loja):
    frios = Categoria.objects.create(nome="Frios", perecivel_padrao=True)
    Produto.objects.create(
        categoria=frios,
        nome="Frango resfriado 1 kg",
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=3,
    )
    erros = carregar_contagem(_planilha(tmp_path, [("Frango resfriado 1 kg", None, 2, None, None)])).erros
    assert [(erro.coluna, "Categoria" in erro.mensagem) for erro in erros] == [("Produto", True)]

    carregar_contagem(_planilha(tmp_path, [("Frango resfriado 1 kg", "frios", 2, None, None)]))
    assert Lote.objects.get().produto.categoria == frios


def test_j3_planilha_sem_a_aba_contagem_ou_sem_coluna_e_ilegivel(tmp_path, loja):
    with pytest.raises(PlanilhaIlegivel, match="Contagem"):
        carregar_contagem(_planilha(tmp_path, [], aba="Outra"))
    with pytest.raises(PlanilhaIlegivel, match="Quantidade contada"):
        carregar_contagem(_planilha(tmp_path, [], cabecalho=["Produto", "Validade"]))


# --- De partida -----------------------------------------------------------------------------------


def test_j3_produto_que_ja_tinha_estoque_e_mantido(tmp_path, loja):
    Movimentacao.objects.create(produto=loja["arroz"], tipo="ENTRADA", quantidade=Decimal("5"))
    resultado = carregar_contagem(_planilha(tmp_path, [("Arroz 5 kg", None, 12, None, None)]))
    assert (resultado.lotes, resultado.mantidos) == (0, 1)
    assert saldo_do_produto(loja["arroz"]) == Decimal("5")


def test_j3_rodar_de_novo_nao_lanca_a_contagem_duas_vezes(tmp_path, loja):
    caminho = _planilha(
        tmp_path,
        [
            ("Frango resfriado 1 kg", None, 2, None, None),
            ("Frango resfriado 1 kg", None, 1, "20/11/2026", None),
        ],
    )
    assert carregar_contagem(caminho).lotes == 2
    segunda = carregar_contagem(caminho)
    assert (segunda.lotes, segunda.mantidos) == (0, 2)
    assert saldo_do_produto(loja["frango"]) == Decimal("3")


def test_rn05_perecivel_contado_perto_de_vencer_ja_entra_no_aviso_de_validade(tmp_path, loja):
    Usuario.objects.create_user(login="joao", senha="Mercado#2026", nome="Sr. João", papel="DONO")
    carregar_contagem(_planilha(tmp_path, [("Frango resfriado 1 kg", None, 2, "18/11/2026", None)]))
    avisos = gerar_avisos_de_validade()
    assert [aviso.produto for aviso in avisos] == [loja["frango"]]


# --- Comando e exemplo ----------------------------------------------------------------------------


def test_j3_comando_lanca_e_resume(tmp_path, loja):
    saida = StringIO()
    call_command(
        "carregar_contagem", str(_planilha(tmp_path, [("Arroz 5 kg", None, 12, None, None)])), stdout=saida
    )
    assert "1 lote(s) lançado(s)" in saida.getvalue()


def test_j3_comando_com_erro_lista_as_linhas_e_nada_e_gravado(tmp_path, loja):
    saida = StringIO()
    with pytest.raises(CommandError, match="Nada foi gravado"):
        call_command(
            "carregar_contagem", str(_planilha(tmp_path, [("Picanha", None, 2, None, None)])), stdout=saida
        )
    assert "Contagem, linha 2, Produto" in saida.getvalue()


@pytest.mark.django_db
def test_j3_contagem_de_exemplo_casa_com_os_produtos_de_exemplo():
    assert carregar_planilha(EXEMPLO_PRODUTOS).erros == []
    resultado = carregar_contagem(EXEMPLO)
    assert resultado.erros == []
    assert resultado.lotes >= 40
    sem_estoque = Produto.objects.exclude(movimentacoes__isnull=False)
    assert sem_estoque.count() <= resultado.zerados

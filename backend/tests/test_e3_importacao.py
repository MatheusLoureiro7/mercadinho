"""
Tarefa E3 — serviço que lê a planilha do caixa e gera venda e movimentação. Operação 04.

Formato: docs/FORMATO-PLANILHA-CAIXA.md (E1). Decisões do grupo em 05/11/2026:
- venda maior que o estoque registrado: grava a venda inteira; o que não coube nos lotes vira
  movimentação VENDA sem lote, e o saldo fica negativo — a contagem é que está errada;
- a planilha é lida de uma pasta fixa, pelo comando `importar_vendas` (rodada das 03h00, G5).

Losangos da operação 04, pelo "sim" e pelo "não":
    arquivo legível?            sim → *_tudo_certo_fica_ok            não → *_arquivo_ilegivel_*
    linha válida?               sim → grava                            não → *_linha_invalida_*
    produto casou?              sim → *_rn01_*, *_rn02_*               não → *_produto_que_nao_casou_*
    estoque cobre a venda?      sim → baixa só dos lotes               não → *_venda_maior_que_o_estoque_*
    lote vencido na data?       sim → *_rn16_*_nao_sai_na_venda        não → *_rn16_*_ainda_valia_*
"""

import os
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from io import StringIO
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from openpyxl import Workbook

from cadastro.models import Categoria, Produto
from caixa.fechamento import apurado_do_fechamento
from comum.erros import ErroDeRegraDeNegocio
from estoque.entrada import registrar_entrada
from estoque.models import Lote, Movimentacao
from estoque.perda import registrar_perda
from estoque.saldo import saldo_do_produto
from previsao.consumo import vendido_no_periodo
from vendas.importacao import ArquivoJaImportado, importar_planilha
from vendas.leitor import ArquivoIlegivel, LeitorDePlanilhaExcel
from vendas.models import ImportacaoPdv, ItemVenda, Venda

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
DIA = date(2026, 11, 5)
CABECALHO = ["Cupom", "Data", "Hora", "Produto", "Quantidade", "Preço unitário", "Pagamento"]


def _planilha(pasta, linhas, nome="vendas-2026-11-05.xlsx", cabecalho=CABECALHO):
    livro = Workbook()
    livro.active.append(cabecalho)
    for linha in linhas:
        livro.active.append(list(linha))
    caminho = pasta / nome
    livro.save(caminho)
    return caminho


def _linha(cupom, produto, quantidade, preco, hora=time(8, 14), dia=DIA, pagamento="PIX"):
    return (cupom, dia, hora, produto, quantidade, preco, pagamento)


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
def feijao(db):
    secos = Categoria.objects.create(nome="Secos e molhados")
    return Produto.objects.create(categoria=secos, nome="Feijão carioca 1 kg", unidade_medida="PCT")


def _lote(produto, quantidade, validade, entrada=DIA - timedelta(days=2)):
    lote = Lote.objects.create(
        produto=produto,
        quantidade_inicial=Decimal(quantidade),
        quantidade_atual=Decimal(quantidade),
        data_entrada=entrada,
        data_validade=validade,
    )
    Movimentacao.objects.create(produto=produto, lote=lote, tipo="ENTRADA", quantidade=Decimal(quantidade))
    return lote


# --- Leitura da planilha --------------------------------------------------------------------------


def test_e3_le_a_planilha_de_exemplo_do_grupo():
    from tests.test_e1_formato_planilha import EXEMPLO

    leitura = LeitorDePlanilhaExcel().ler(EXEMPLO)
    assert len(leitura.linhas) == 10 and leitura.erros == []
    primeira = leitura.linhas[0]
    assert primeira.cupom == "1021"
    assert primeira.data_hora == datetime(2026, 11, 5, 8, 14, tzinfo=SAO_PAULO)
    assert (primeira.produto, primeira.quantidade, primeira.preco) == (
        "Arroz 5 kg",
        Decimal("2"),
        Decimal("27.90"),
    )
    assert primeira.pagamento == "PIX"


def test_e3_cabecalho_sem_acento_e_em_outra_ordem_e_aceito(tmp_path):
    cabecalho = ["produto", "CUPOM", "data", "hora", "quantidade", "preco unitario"]
    caminho = _planilha(tmp_path, [("Arroz 5 kg", 7, DIA, time(9, 0), 1, 27.9)], cabecalho=cabecalho)
    leitura = LeitorDePlanilhaExcel().ler(caminho)
    assert leitura.linhas[0].produto == "Arroz 5 kg" and leitura.linhas[0].pagamento is None


def test_e3_numero_escrito_como_texto_com_virgula_e_aceito(tmp_path):
    caminho = _planilha(tmp_path, [_linha(1, "Frango", "1,275", "21,90")])
    linha = LeitorDePlanilhaExcel().ler(caminho).linhas[0]
    assert (linha.quantidade, linha.preco) == (Decimal("1.275"), Decimal("21.90"))


def test_e3_linha_em_branco_e_ignorada(tmp_path):
    caminho = _planilha(tmp_path, [_linha(1, "Arroz 5 kg", 1, 27.9), (None,) * 7])
    leitura = LeitorDePlanilhaExcel().ler(caminho)
    assert len(leitura.linhas) == 1 and leitura.erros == []


@pytest.mark.parametrize(
    "linha, campo",
    [
        (_linha(1, "Arroz 5 kg", 0, 27.9), "Quantidade"),
        (_linha(1, "Arroz 5 kg", "dois", 27.9), "Quantidade"),
        (_linha(1, "Arroz 5 kg", "1.2345", 27.9), "Quantidade"),
        (_linha(1, "Arroz 5 kg", 1, -1), "Preço unitário"),
        (_linha(1, "", 1, 27.9), "Produto"),
        (_linha(None, "Arroz 5 kg", 1, 27.9), "Cupom"),
        (_linha(1, "Arroz 5 kg", 1, 27.9, hora="manhã"), "Hora"),
        (_linha(1, "Arroz 5 kg", 1, 27.9, dia="ontem"), "Data"),
    ],
)
def test_e3_linha_invalida_vira_erro_com_o_numero_da_linha(tmp_path, linha, campo):
    caminho = _planilha(tmp_path, [_linha(1, "Arroz 5 kg", 1, 27.9), linha])
    leitura = LeitorDePlanilhaExcel().ler(caminho)
    assert len(leitura.linhas) == 1
    assert [(erro.numero_linha, erro.campo) for erro in leitura.erros] == [(3, campo)]


def test_e3_arquivo_que_nao_e_planilha_e_ilegivel(tmp_path):
    caminho = tmp_path / "vendas.xlsx"
    caminho.write_text("isto não é uma planilha")
    with pytest.raises(ArquivoIlegivel):
        LeitorDePlanilhaExcel().ler(caminho)


def test_e3_planilha_sem_coluna_obrigatoria_e_ilegivel_e_diz_qual(tmp_path):
    caminho = _planilha(tmp_path, [], cabecalho=["Cupom", "Data", "Hora", "Produto", "Quantidade"])
    with pytest.raises(ArquivoIlegivel, match="Preço unitário"):
        LeitorDePlanilhaExcel().ler(caminho)


# --- Venda e item ---------------------------------------------------------------------------------


def test_e3_cupom_com_dois_itens_vira_uma_venda_com_a_soma(tmp_path, frango, feijao):
    _lote(frango, "10", DIA + timedelta(days=3))
    _lote(feijao, "10", None)
    caminho = _planilha(
        tmp_path,
        [_linha(1021, "Feijão carioca 1 kg", 2, 8.99), _linha(1021, "Frango resfriado 1 kg", 1.275, 21.9)],
    )

    importar_planilha(caminho)

    venda = Venda.objects.get()
    assert venda.valor_total == Decimal("45.90")  # 2 × 8,99 + 1,275 × 21,90 = 17,98 + 27,9225
    assert venda.data_hora == datetime(2026, 11, 5, 8, 14, tzinfo=SAO_PAULO)
    assert venda.forma_pagamento == "PIX"
    assert venda.itens.count() == 2


def test_x1_total_do_cupom_arredonda_cada_item_como_o_caixa(tmp_path, frango):
    """X1, item 15 (decisão do grupo, 16/11/2026): 0,333 × 19,99 = 6,66 por item; o cupom dá 13,32."""
    linhas = [
        _linha(1, "Frango resfriado 1 kg", 0.333, 19.99),
        _linha(1, "Frango resfriado 1 kg", 0.333, 19.99),
    ]
    importar_planilha(_planilha(tmp_path, linhas))
    assert Venda.objects.get().valor_total == Decimal("13.32")


def test_e3_cada_cupom_vira_uma_venda(tmp_path, feijao):
    _lote(feijao, "10", None)
    caminho = _planilha(
        tmp_path, [_linha(1, "Feijão carioca 1 kg", 1, 8.99), _linha(2, "Feijão carioca 1 kg", 1, 8.99)]
    )
    importar_planilha(caminho)
    assert Venda.objects.count() == 2


# --- Baixa no estoque (RN01, RN02, RN16) ----------------------------------------------------------


def test_e3_rn01_linha_que_casou_gera_movimentacao_venda_e_baixa_o_saldo(tmp_path, frango):
    _lote(frango, "10", DIA + timedelta(days=3))
    importar_planilha(_planilha(tmp_path, [_linha(1, "Frango resfriado 1 kg", 2.5, 21.9)]))

    venda = Movimentacao.objects.get(tipo="VENDA")
    assert (venda.quantidade, venda.preco_unitario, venda.origem) == (
        Decimal("2.5"),
        Decimal("21.90"),
        "IMPORTACAO_PDV",
    )
    assert venda.data_hora == datetime(
        2026, 11, 5, 8, 14, tzinfo=SAO_PAULO
    )  # a hora da venda, não a da importação
    assert saldo_do_produto(frango) == Decimal("7.5")


def test_e3_rn02_sai_do_lote_que_vence_primeiro(tmp_path, frango):
    vence_depois = _lote(frango, "5", DIA + timedelta(days=4), entrada=DIA - timedelta(days=3))
    vence_antes = _lote(frango, "5", DIA + timedelta(days=1), entrada=DIA - timedelta(days=1))
    importar_planilha(_planilha(tmp_path, [_linha(1, "Frango resfriado 1 kg", 2, 21.9)]))

    vence_antes.refresh_from_db(), vence_depois.refresh_from_db()
    assert (vence_antes.quantidade_atual, vence_depois.quantidade_atual) == (Decimal("3"), Decimal("5"))


def test_e3_rn02_venda_maior_que_um_lote_continua_no_proximo_com_uma_linha_por_lote(tmp_path, frango):
    primeiro = _lote(frango, "2", DIA + timedelta(days=1))
    segundo = _lote(frango, "5", DIA + timedelta(days=3))
    importar_planilha(_planilha(tmp_path, [_linha(1, "Frango resfriado 1 kg", 3, 21.9)]))

    baixas = Movimentacao.objects.filter(tipo="VENDA").order_by("id")
    assert [(b.lote, b.quantidade) for b in baixas] == [(primeiro, Decimal("2")), (segundo, Decimal("1"))]


def test_e3_venda_maior_que_o_estoque_grava_a_venda_inteira_e_o_saldo_fica_negativo(tmp_path, frango):
    lote = _lote(frango, "3", DIA + timedelta(days=2))
    importar_planilha(_planilha(tmp_path, [_linha(1, "Frango resfriado 1 kg", 5, 21.9)]))

    baixas = Movimentacao.objects.filter(tipo="VENDA").order_by("id")
    assert [(b.lote, b.quantidade) for b in baixas] == [(lote, Decimal("3")), (None, Decimal("2"))]
    assert saldo_do_produto(frango) == Decimal("-2")  # mostra que a contagem do estoque está errada


def _soma_dos_lotes(produto):
    return sum(Lote.objects.filter(produto=produto).values_list("quantidade_atual", flat=True), Decimal(0))


def test_e3_venda_a_mais_e_descontada_da_proxima_carga_e_saldo_e_lotes_batem(tmp_path, frango):
    """X1, item 3: 5 no estoque, venda de 8, carga de 10 — o lote novo nasce com 7, não com 10."""
    _lote(frango, "5", DIA + timedelta(days=3))
    importar_planilha(_planilha(tmp_path, [_linha(1, "Frango resfriado 1 kg", 8, 21.9)]))

    lote = registrar_entrada(produto=frango, quantidade=Decimal("10"), usuario=None)

    lote.refresh_from_db()
    assert (lote.quantidade_inicial, lote.quantidade_atual) == (Decimal("10"), Decimal("7"))
    assert saldo_do_produto(frango) == _soma_dos_lotes(frango) == Decimal("7")


def test_e3_depois_da_venda_a_mais_a_perda_maior_que_o_saldo_e_recusada(tmp_path, frango):
    _lote(frango, "5", DIA + timedelta(days=3))
    importar_planilha(_planilha(tmp_path, [_linha(1, "Frango resfriado 1 kg", 8, 21.9)]))
    registrar_entrada(produto=frango, quantidade=Decimal("10"), usuario=None)

    with pytest.raises(ErroDeRegraDeNegocio):
        registrar_perda(produto=frango, quantidade=Decimal("10"), motivo="estragou", usuario=None)
    assert saldo_do_produto(frango) == Decimal("7")


def test_e3_carga_menor_que_a_venda_a_mais_fica_zerada_e_a_seguinte_desconta_o_resto(tmp_path, frango):
    _lote(frango, "5", DIA + timedelta(days=3))
    importar_planilha(_planilha(tmp_path, [_linha(1, "Frango resfriado 1 kg", 8, 21.9)]))

    pequena = registrar_entrada(produto=frango, quantidade=Decimal("2"), usuario=None)
    grande = registrar_entrada(produto=frango, quantidade=Decimal("10"), usuario=None)

    pequena.refresh_from_db()
    grande.refresh_from_db()
    assert (pequena.quantidade_atual, grande.quantidade_atual) == (Decimal("0"), Decimal("9"))
    assert saldo_do_produto(frango) == _soma_dos_lotes(frango) == Decimal("9")


def test_e3_rn16_lote_vencido_na_data_da_venda_nao_sai_na_venda(tmp_path, frango):
    vencido = _lote(frango, "5", DIA - timedelta(days=1))
    bom = _lote(frango, "5", DIA + timedelta(days=2))
    importar_planilha(_planilha(tmp_path, [_linha(1, "Frango resfriado 1 kg", 2, 21.9)]))

    vencido.refresh_from_db(), bom.refresh_from_db()
    assert (vencido.quantidade_atual, bom.quantidade_atual) == (Decimal("5"), Decimal("3"))


def test_e3_rn16_lote_que_ainda_valia_no_dia_da_venda_sai_mesmo_importado_depois(tmp_path, frango):
    """A importação roda às 03h00 do dia seguinte; o lote que venceu no dia da venda ainda valia."""
    vence_no_dia = _lote(frango, "5", DIA)
    caminho = _planilha(tmp_path, [_linha(1, "Frango resfriado 1 kg", 2, 21.9)])
    as_tres_do_dia_seguinte = datetime(2026, 11, 6, 3, 0, tzinfo=SAO_PAULO)
    with patch("django.utils.timezone.now", return_value=as_tres_do_dia_seguinte):
        importar_planilha(caminho)
    vence_no_dia.refresh_from_db()
    assert vence_no_dia.quantidade_atual == Decimal("3")


def test_e3_rn11_venda_importada_entra_no_consumo(tmp_path, frango):
    _lote(frango, "10", DIA + timedelta(days=3))
    importar_planilha(_planilha(tmp_path, [_linha(1, "Frango resfriado 1 kg", 2.5, 21.9, hora=time(22, 30))]))
    assert vendido_no_periodo(frango, DIA, DIA) == Decimal("2.5")  # 22h30 ainda é o dia da loja


# --- Casamento com o cadastro (L05: pelo nome) ----------------------------------------------------


def test_e3_nome_sem_acento_e_com_maiuscula_casa_com_o_cadastro(tmp_path, feijao):
    _lote(feijao, "10", None)
    importar_planilha(_planilha(tmp_path, [_linha(1, "  FEIJAO  carioca 1 KG ", 1, 8.99)]))
    assert ItemVenda.objects.get().produto == feijao


def test_e3_nome_que_existe_em_duas_categorias_fica_pendente(tmp_path, feijao):
    """O cadastro aceita o mesmo nome em categorias diferentes (B1); aí não se chuta qual é."""
    outra = Categoria.objects.create(nome="Hortifruti")
    Produto.objects.create(categoria=outra, nome="Feijão carioca 1 kg", unidade_medida="PCT")
    [importacao] = importar_planilha(_planilha(tmp_path, [_linha(1, "Feijão carioca 1 kg", 1, 8.99)]))
    assert ItemVenda.objects.get().produto is None
    assert not Movimentacao.objects.filter(tipo="VENDA").exists()
    assert importacao.status == "PARCIAL"


def test_e3_produto_que_nao_casou_fica_pendente_e_nao_trava_as_demais(tmp_path, feijao):
    _lote(feijao, "10", None)
    caminho = _planilha(
        tmp_path, [_linha(1, "Leite integral 1 L", 6, 5.49), _linha(1, "Feijão carioca 1 kg", 1, 8.99)]
    )

    [importacao] = importar_planilha(caminho)

    pendente = ItemVenda.objects.get(produto__isnull=True)
    assert (pendente.quantidade, pendente.preco) == (Decimal("6"), Decimal("5.49"))
    assert Movimentacao.objects.filter(tipo="VENDA").count() == 1  # só a do feijão
    assert Venda.objects.get().valor_total == Decimal("41.93")  # a venda é inteira: 32,94 + 8,99
    assert (importacao.status, importacao.linhas_lidas, importacao.linhas_erro) == ("PARCIAL", 2, 1)


# --- Resultado da importação ----------------------------------------------------------------------


def test_e3_tudo_certo_fica_ok_com_a_data_das_vendas(tmp_path, feijao):
    _lote(feijao, "10", None)
    [importacao] = importar_planilha(_planilha(tmp_path, [_linha(1, "Feijão carioca 1 kg", 1, 8.99)]))
    assert (importacao.status, importacao.linhas_lidas, importacao.linhas_erro) == ("OK", 1, 0)
    assert importacao.arquivo_nome == "vendas-2026-11-05.xlsx"
    assert importacao.data_referencia == DIA
    assert importacao.processado_em is not None


def test_e3_linha_invalida_recusa_a_planilha_inteira_e_nada_e_gravado(tmp_path, feijao):
    """X1, item 2 (decisão do grupo, 16/11/2026): linha que não pode ser lida não pode sumir das vendas."""
    _lote(feijao, "10", None)
    caminho = _planilha(
        tmp_path, [_linha(1, "Feijão carioca 1 kg", 1, 8.99), _linha(2, "Feijão carioca 1 kg", 0, 8.99)]
    )
    [importacao] = importar_planilha(caminho)
    assert (importacao.status, importacao.linhas_lidas, importacao.linhas_erro) == ("ERRO", 2, 1)
    assert not Venda.objects.exists() and not ItemVenda.objects.exists()
    assert saldo_do_produto(feijao) == Decimal("10")


def test_e3_planilha_recusada_por_linha_invalida_entra_depois_de_corrigida(tmp_path, feijao):
    _lote(feijao, "10", None)
    estragada = [
        _linha(1, "Feijão carioca 1 kg", 1, 8.99),
        _linha(2, "Feijão carioca 1 kg", 2, 8.99, hora="9h30"),
    ]
    importar_planilha(_planilha(tmp_path, estragada))
    corrigida = [
        _linha(1, "Feijão carioca 1 kg", 1, 8.99),
        _linha(2, "Feijão carioca 1 kg", 2, 8.99, hora=time(9, 30)),
    ]
    [importacao] = importar_planilha(_planilha(tmp_path, corrigida))
    assert (importacao.status, importacao.linhas_lidas) == ("OK", 2)
    assert saldo_do_produto(feijao) == Decimal("7")


def test_e3_linha_invalida_nao_deixa_o_caixa_fechar_com_o_apurado_errado(tmp_path, feijao):
    """X1, item 2: o cupom de R$ 200,00 com a hora "9h30" virava uma sobra falsa de R$ 200,00."""
    _lote(feijao, "10", None)
    linhas = [
        _linha(1, "Feijão carioca 1 kg", 1, 20, pagamento="Dinheiro"),
        _linha(2, "Feijão carioca 1 kg", 1, 200, hora="9h30", pagamento="Dinheiro"),
    ]
    importar_planilha(_planilha(tmp_path, linhas))
    with (
        patch("django.utils.timezone.now", return_value=datetime(2026, 11, 6, 9, 0, tzinfo=SAO_PAULO)),
        pytest.raises(ErroDeRegraDeNegocio, match="ainda não entraram"),
    ):
        apurado_do_fechamento()


def test_e3_arquivo_ilegivel_fica_com_erro_e_nada_e_gravado(tmp_path, db):
    caminho = tmp_path / "vendas-2026-11-05.xlsx"
    caminho.write_text("isto não é uma planilha")
    [importacao] = importar_planilha(caminho)
    assert importacao.status == "ERRO"
    assert not Venda.objects.exists() and not ItemVenda.objects.exists()


def test_e3_o_mesmo_arquivo_nao_e_importado_duas_vezes(tmp_path, feijao):
    _lote(feijao, "10", None)
    caminho = _planilha(tmp_path, [_linha(1, "Feijão carioca 1 kg", 1, 8.99)])
    importar_planilha(caminho)
    with pytest.raises(ArquivoJaImportado):
        importar_planilha(caminho)
    assert Venda.objects.count() == 1 and saldo_do_produto(feijao) == Decimal("9")


def test_e3_mesmas_vendas_com_outro_nome_de_arquivo_nao_entram_de_novo(tmp_path, feijao):
    """X1, item 1: o que identifica as vendas é o dia delas, não o nome do arquivo."""
    _lote(feijao, "10", None)
    importar_planilha(_planilha(tmp_path, [_linha(1, "Feijão carioca 1 kg", 1, 8.99)]))
    copia = _planilha(tmp_path, [_linha(1, "Feijão carioca 1 kg", 1, 8.99)], nome="copia.xlsx")
    with pytest.raises(ArquivoJaImportado):
        importar_planilha(copia)
    assert Venda.objects.count() == 1 and saldo_do_produto(feijao) == Decimal("9")
    assert ImportacaoPdv.objects.count() == 1  # a cópia recusada não deixa registro


def test_e3_mesmo_nome_de_arquivo_com_vendas_de_outro_dia_entra(tmp_path, feijao):
    _lote(feijao, "10", None)
    importar_planilha(_planilha(tmp_path, [_linha(1, "Feijão carioca 1 kg", 1, 8.99)], nome="vendas.xlsx"))
    dia_seguinte = _linha(7, "Feijão carioca 1 kg", 2, 8.99, dia=DIA + timedelta(days=1))
    [importacao] = importar_planilha(_planilha(tmp_path, [dia_seguinte], nome="vendas.xlsx"))
    assert importacao.status == "OK" and importacao.data_referencia == DIA + timedelta(days=1)
    assert Venda.objects.count() == 2 and saldo_do_produto(feijao) == Decimal("7")


def test_e3_planilha_com_um_dia_ja_importado_e_um_novo_so_traz_o_dia_novo(tmp_path, feijao):
    _lote(feijao, "10", None)
    importar_planilha(_planilha(tmp_path, [_linha(1, "Feijão carioca 1 kg", 1, 8.99)]))
    caminho = _planilha(
        tmp_path,
        [
            _linha(1, "Feijão carioca 1 kg", 1, 8.99),
            _linha(7, "Feijão carioca 1 kg", 2, 8.99, dia=DIA + timedelta(days=1)),
        ],
        nome="vendas-da-semana.xlsx",
    )
    [importacao] = importar_planilha(caminho)
    assert (importacao.status, importacao.linhas_lidas) == ("OK", 1)
    assert Venda.objects.count() == 2 and saldo_do_produto(feijao) == Decimal("7")


def test_e3_planilha_com_dois_dias_gera_uma_importacao_por_dia(tmp_path, feijao):
    """X1, item 4 (decisão do grupo, 16/11/2026): cada dia da planilha tem o seu registro."""
    _lote(feijao, "10", None)
    amanha = DIA + timedelta(days=1)
    caminho = _planilha(
        tmp_path,
        [
            _linha(1, "Feijão carioca 1 kg", 1, 8.99),
            _linha(1, "Feijão carioca 1 kg", 2, 8.99, dia=amanha),  # o caixa recomeça os cupons
            _linha(2, "Produto que não existe", 1, 5, dia=amanha),
        ],
        nome="vendas-atrasadas.xlsx",
    )
    importacoes = importar_planilha(caminho)
    resumo = [
        (i.arquivo_nome, i.data_referencia, i.status, i.linhas_lidas, i.linhas_erro) for i in importacoes
    ]
    assert resumo == [
        ("vendas-atrasadas.xlsx", DIA, "OK", 1, 0),
        ("vendas-atrasadas.xlsx", amanha, "PARCIAL", 2, 1),
    ]
    assert Venda.objects.count() == 3 and saldo_do_produto(feijao) == Decimal("7")


def test_e3_planilha_com_dois_dias_libera_o_fechamento_do_segundo(tmp_path, feijao):
    _lote(feijao, "10", None)
    amanha = DIA + timedelta(days=1)
    linhas = [
        _linha(1, "Feijão carioca 1 kg", 1, 8.99, pagamento="Dinheiro"),
        _linha(5, "Feijão carioca 1 kg", 2, 10, dia=amanha, pagamento="Dinheiro"),
    ]
    importar_planilha(_planilha(tmp_path, linhas))
    with patch("django.utils.timezone.now", return_value=datetime(2026, 11, 7, 9, 0, tzinfo=SAO_PAULO)):
        assert apurado_do_fechamento() == (amanha, Decimal("20.00"))


def test_e3_segundo_dia_de_uma_planilha_de_dois_dias_nao_entra_de_novo(tmp_path, feijao):
    _lote(feijao, "10", None)
    amanha = DIA + timedelta(days=1)
    linhas = [
        _linha(1, "Feijão carioca 1 kg", 1, 8.99),
        _linha(5, "Feijão carioca 1 kg", 2, 8.99, dia=amanha),
    ]
    importar_planilha(_planilha(tmp_path, linhas))
    copia = _planilha(tmp_path, [_linha(5, "Feijão carioca 1 kg", 2, 8.99, dia=amanha)], nome="copia.xlsx")
    with pytest.raises(ArquivoJaImportado):
        importar_planilha(copia)
    assert saldo_do_produto(feijao) == Decimal("7")


def test_e3_falha_no_meio_desfaz_tudo_e_a_importacao_fica_com_erro(tmp_path, feijao, monkeypatch):
    _lote(feijao, "10", None)
    caminho = _planilha(
        tmp_path, [_linha(1, "Feijão carioca 1 kg", 1, 8.99), _linha(2, "Feijão carioca 1 kg", 1, 8.99)]
    )
    original = Movimentacao.objects.create
    chamadas = []

    def falha_na_segunda(**campos):
        chamadas.append(1)
        if len(chamadas) == 2:
            raise RuntimeError("banco caiu")
        return original(**campos)

    monkeypatch.setattr(Movimentacao.objects, "create", falha_na_segunda)
    with pytest.raises(RuntimeError):
        importar_planilha(caminho)
    assert not Venda.objects.exists() and saldo_do_produto(feijao) == Decimal("10")
    assert ImportacaoPdv.objects.get().status == "ERRO"


def test_e3_planilha_de_exemplo_com_os_dados_de_demonstracao(db):
    from tests.test_e1_formato_planilha import EXEMPLO

    call_command("loaddata", "demonstracao", verbosity=0)
    [importacao] = importar_planilha(EXEMPLO)
    assert Venda.objects.count() == 5 and ItemVenda.objects.count() == 10
    assert list(ItemVenda.objects.filter(produto__isnull=True).values_list("quantidade", flat=True)) == [
        Decimal("6")
    ]
    assert (importacao.status, importacao.linhas_lidas, importacao.linhas_erro) == ("PARCIAL", 10, 1)


# --- Comando da rodada diária ---------------------------------------------------------------------


def test_e3_comando_importa_as_planilhas_novas_da_pasta(tmp_path, feijao, settings):
    _lote(feijao, "10", None)
    settings.PASTA_VENDAS_CAIXA = str(tmp_path)
    _planilha(
        tmp_path,
        [_linha(1, "Feijão carioca 1 kg", 1, 8.99, dia=DIA - timedelta(days=1))],
        nome="vendas-2026-11-04.xlsx",
    )
    _planilha(tmp_path, [_linha(2, "Feijão carioca 1 kg", 2, 8.99)], nome="vendas-2026-11-05.xlsx")
    (tmp_path / "anotacoes.txt").write_text("não é planilha")
    saida = StringIO()

    call_command("importar_vendas", stdout=saida)
    call_command("importar_vendas", stdout=saida)  # de novo: nada novo

    assert list(ImportacaoPdv.objects.order_by("id").values_list("arquivo_nome", flat=True)) == [
        "vendas-2026-11-04.xlsx",
        "vendas-2026-11-05.xlsx",
    ]
    assert Venda.objects.count() == 2
    assert "Nenhuma planilha nova" in saida.getvalue()


def test_e3_comando_importa_a_planilha_regravada_com_o_mesmo_nome(tmp_path, feijao, settings):
    """X1, item 1: o caixa que grava sempre vendas.xlsx por cima do arquivo anterior."""
    _lote(feijao, "10", None)
    settings.PASTA_VENDAS_CAIXA = str(tmp_path)
    _planilha(tmp_path, [_linha(1, "Feijão carioca 1 kg", 1, 8.99)], nome="vendas.xlsx")
    call_command("importar_vendas", stdout=StringIO())

    caminho = _planilha(
        tmp_path, [_linha(7, "Feijão carioca 1 kg", 2, 8.99, dia=DIA + timedelta(days=1))], nome="vendas.xlsx"
    )
    depois = ImportacaoPdv.objects.get().processado_em.timestamp() + 60
    os.utime(caminho, (depois, depois))
    call_command("importar_vendas", stdout=StringIO())

    assert ImportacaoPdv.objects.count() == 2
    assert saldo_do_produto(feijao) == Decimal("7")


def test_e3_comando_avisa_e_segue_quando_a_planilha_repete_vendas_ja_importadas(tmp_path, feijao, settings):
    _lote(feijao, "10", None)
    settings.PASTA_VENDAS_CAIXA = str(tmp_path)
    _planilha(tmp_path, [_linha(1, "Feijão carioca 1 kg", 1, 8.99)], nome="vendas-2026-11-05.xlsx")
    call_command("importar_vendas", stdout=StringIO())
    _planilha(tmp_path, [_linha(1, "Feijão carioca 1 kg", 1, 8.99)], nome="copia.xlsx")
    saida = StringIO()

    call_command("importar_vendas", stdout=saida)

    assert "copia.xlsx: as vendas desta planilha já tinham entrado" in saida.getvalue()
    assert ImportacaoPdv.objects.count() == 1 and saldo_do_produto(feijao) == Decimal("9")


def test_e3_comando_sem_pasta_configurada_avisa(db, settings):
    settings.PASTA_VENDAS_CAIXA = ""
    with pytest.raises(CommandError, match="PASTA_VENDAS_CAIXA"):
        call_command("importar_vendas")


def test_e3_comando_termina_com_erro_se_alguma_planilha_nao_foi_lida(tmp_path, db, settings):
    settings.PASTA_VENDAS_CAIXA = str(tmp_path)
    (tmp_path / "vendas-2026-11-05.xlsx").write_text("quebrada")
    with pytest.raises(CommandError, match="vendas-2026-11-05.xlsx"):
        call_command("importar_vendas", stdout=StringIO())

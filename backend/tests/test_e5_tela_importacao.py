"""
Tarefa E5 — tela de acompanhamento da importação. Tela "Importação de vendas", do sobrinho
(OPERACAO, RN14): "traz as vendas registradas no caixa da loja" (Apostila II).

A planilha não é enviada pela tela: o sobrinho a salva na pasta do caixa e a rodada das 03h00 a
importa (decisão do grupo na E3, 05/11/2026; G5). A tela mostra:
- as **vendas para conferir** — os itens que não casaram com o cadastro (operação 04, passo 6) —,
  com data, hora, quantidade e preço (L26), e deixa ligar cada um a um produto (E4);
- as **planilhas lidas** (importacao_pdv), com a situação de cada uma.

API nova desta tarefa:  GET /api/importacoes/   as últimas 30 leituras, a mais nova primeiro.
"""

import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from playwright.sync_api import expect

from cadastro.models import Categoria, Produto, Usuario
from comum.autenticacao import gerar_token
from estoque.models import Lote, Movimentacao
from estoque.saldo import saldo_do_produto
from tests.conftest import abrir_tela
from vendas.models import ImportacaoPdv, ItemVenda, Venda

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
TELA = "importacao-vendas.html"
SAO_PAULO = ZoneInfo("America/Sao_Paulo")
SENHA = "Mercado#2026"


def _importacao(nome, dia, status="OK", lidas=10, erro=0, processado=None):
    return ImportacaoPdv.objects.create(
        arquivo_nome=nome,
        data_referencia=dia,
        status=status,
        linhas_lidas=lidas,
        linhas_erro=erro,
        processado_em=processado
        or datetime(dia.year, dia.month, dia.day, 3, 0, tzinfo=SAO_PAULO) + timedelta(days=1),
    )


def _pendente(quantidade="1.275", preco="21.90", quando=datetime(2026, 11, 5, 8, 14, tzinfo=SAO_PAULO)):
    venda = Venda.objects.create(data_hora=quando, valor_total=Decimal("27.92"), forma_pagamento="PIX")
    return ItemVenda.objects.create(
        venda=venda, produto=None, quantidade=Decimal(quantidade), preco=Decimal(preco)
    )


def _frango():
    acougue, _ = Categoria.objects.get_or_create(nome="Açougue", defaults={"perecivel_padrao": True})
    frango = Produto.objects.create(
        categoria=acougue,
        nome="Frango resfriado 1 kg",
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=4,
    )
    lote = Lote.objects.create(
        produto=frango,
        quantidade_inicial=Decimal("10"),
        quantidade_atual=Decimal("10"),
        data_entrada=date(2026, 11, 3),
        data_validade=date(2026, 11, 9),
    )
    Movimentacao.objects.create(produto=frango, lote=lote, tipo="ENTRADA", quantidade=Decimal("10"))
    return frango


# ------------------------------------------------------------------------------------------------
# API
# ------------------------------------------------------------------------------------------------


@pytest.fixture
def api(client, db):
    usuarios = {
        papel: Usuario.objects.create_user(login=papel.lower(), senha=SENHA, nome=papel, papel=papel)
        for papel in ("DONO", "GESTAO", "OPERACAO")
    }

    def ler(url="/api/importacoes/", papel="OPERACAO"):
        return client.get(url, HTTP_AUTHORIZATION=f"Bearer {gerar_token(usuarios[papel])}")

    return ler


def test_e5_api_lista_as_planilhas_lidas_da_mais_nova_para_a_mais_antiga(api):
    _importacao("vendas-2026-11-04.xlsx", date(2026, 11, 4))
    _importacao("vendas-2026-11-05.xlsx", date(2026, 11, 5), status="PARCIAL", erro=2)
    resposta = api()
    assert resposta.status_code == 200
    primeira, segunda = resposta.json()
    assert primeira == {
        "id": primeira["id"],
        "arquivo_nome": "vendas-2026-11-05.xlsx",
        "data_referencia": "2026-11-05",
        "linhas_lidas": 10,
        "linhas_erro": 2,
        "status": "PARCIAL",
        "processado_em": "2026-11-06T03:00:00-03:00",
    }
    assert segunda["arquivo_nome"] == "vendas-2026-11-04.xlsx"


def test_e5_api_mostra_so_as_30_ultimas(api):
    for n in range(32):
        _importacao(f"vendas-{n:02d}.xlsx", date(2026, 10, 1) + timedelta(days=n))
    nomes = [linha["arquivo_nome"] for linha in api().json()]
    assert len(nomes) == 30 and nomes[0] == "vendas-31.xlsx" and "vendas-01.xlsx" not in nomes


def test_e5_api_sem_planilha_lista_vazia(api):
    assert api().json() == []


@pytest.mark.parametrize("papel", ["DONO", "GESTAO"])
def test_rn14_so_operacao_ve_as_planilhas_lidas(api, papel):
    assert api(papel=papel).status_code == 403


def test_e5_api_nao_importa_nem_apaga_pela_tela(api):
    _importacao("vendas-2026-11-05.xlsx", date(2026, 11, 5))
    assert api().status_code == 200
    from django.test import Client

    assert Client().post("/api/importacoes/").status_code in (401, 403, 405)


# ------------------------------------------------------------------------------------------------
# Tela, sem navegador
# ------------------------------------------------------------------------------------------------


def test_e5_tela_entra_no_menu_do_sobrinho():
    sessao = (FRONTEND / "js" / "sessao.js").read_text(encoding="utf-8")
    assert 'importacao_vendas: { nome: "Importação de vendas", endereco: "importacao-vendas.html" }' in sessao


def test_e5_tela_exige_login_e_o_perfil_da_importacao():
    html = (FRONTEND / TELA).read_text(encoding="utf-8")
    script = re.search(r'src="js/([\w-]+)\.js"', html).group(1)
    assert 'entrarNaTela("importacao_vendas")' in (FRONTEND / "js" / f"{script}.js").read_text(
        encoding="utf-8"
    )


def test_e5_planilha_nao_e_enviada_pela_tela():
    # A planilha vai para a pasta do caixa; a rodada das 03h00 importa (E3, G5).
    html = (FRONTEND / TELA).read_text(encoding="utf-8")
    assert 'type="file"' not in html
    assert "03h00" in html


def test_e5_tela_so_liga_o_produto_e_nao_apaga_venda():
    script = (FRONTEND / "js" / "importacao-vendas.js").read_text(encoding="utf-8")
    assert "DELETE" not in script and "api.alterar" not in script


# ------------------------------------------------------------------------------------------------
# Na tela
# ------------------------------------------------------------------------------------------------


@pytest.fixture
def sobrinho(painel):
    return Usuario.objects.create_user(login="sobrinho", senha=SENHA, nome="Sobrinho", papel="OPERACAO")


@pytest.mark.tela
def test_e5_mostra_a_venda_para_conferir_com_data_hora_quantidade_e_preco(page, painel, sobrinho):
    _pendente()
    abrir_tela(page, painel, sobrinho, TELA)
    linha = page.locator("#corpo-pendentes tr").first
    expect(linha).to_contain_text("05/11/2026")
    expect(linha).to_contain_text("08:14")
    expect(linha).to_contain_text("1,275")
    expect(linha).to_contain_text("R$ 21,90")
    expect(page.locator("#contagem-pendentes")).to_contain_text("1 venda")


@pytest.mark.tela
def test_e5_liga_a_venda_ao_produto_e_ela_sai_do_estoque(page, painel, sobrinho):
    frango = _frango()
    _pendente(quantidade="2")
    abrir_tela(page, painel, sobrinho, TELA)

    page.locator("#corpo-pendentes button", has_text="Escolher o produto").first.click()
    expect(page.locator("#formulario")).to_be_visible()
    expect(page.locator("#venda-escolhida")).to_contain_text("05/11/2026 às 08:14")
    page.fill("#campo-procurar", "frango")
    expect(page.locator("#campo-produto")).to_have_value(str(frango.pk))
    page.click("#botao-ligar")

    expect(page.locator("#sucesso")).to_contain_text("Frango resfriado 1 kg")
    expect(page.locator("#corpo-pendentes")).to_contain_text("Nenhuma venda para conferir")
    expect(page.locator("#formulario")).to_be_hidden()
    assert saldo_do_produto(frango) == Decimal("8")
    assert ItemVenda.objects.get().produto == frango


@pytest.mark.tela
def test_e5_sem_escolher_o_produto_aponta_o_campo(page, painel, sobrinho):
    _frango()
    _pendente()
    abrir_tela(page, painel, sobrinho, TELA)
    page.locator("#corpo-pendentes button", has_text="Escolher o produto").first.click()
    page.click("#botao-ligar")
    expect(page.locator("#erro-produto")).to_contain_text("Escolha o produto")
    assert ItemVenda.objects.get().produto is None


@pytest.mark.tela
def test_e5_cancelar_fecha_o_formulario_e_volta_para_a_lista(page, painel, sobrinho):
    _frango()
    _pendente()
    abrir_tela(page, painel, sobrinho, TELA)
    page.locator("#corpo-pendentes button", has_text="Escolher o produto").first.click()
    page.click("#botao-cancelar")
    expect(page.locator("#formulario")).to_be_hidden()
    expect(page.locator("#corpo-pendentes button", has_text="Escolher o produto").first).to_be_focused()


@pytest.mark.tela
def test_e5_venda_ja_ligada_por_outra_pessoa_mostra_o_motivo(page, painel, sobrinho):
    frango = _frango()
    item = _pendente()
    abrir_tela(page, painel, sobrinho, TELA)
    page.locator("#corpo-pendentes button", has_text="Escolher o produto").first.click()
    ItemVenda.objects.filter(pk=item.pk).update(produto=frango)  # alguém resolveu antes
    page.fill("#campo-procurar", "frango")
    page.click("#botao-ligar")
    expect(page.locator("#resumo-de-erros")).to_contain_text("já foi ligada")


@pytest.mark.tela
def test_e5_sem_venda_para_conferir_diz_que_esta_tudo_certo(page, painel, sobrinho):
    abrir_tela(page, painel, sobrinho, TELA)
    expect(page.locator("#corpo-pendentes")).to_contain_text("Nenhuma venda para conferir")


@pytest.mark.tela
def test_e5_mostra_as_planilhas_lidas_com_a_situacao_em_palavras(page, painel, sobrinho):
    _importacao("vendas-2026-11-04.xlsx", date(2026, 11, 4), status="ERRO", lidas=0)
    _importacao("vendas-2026-11-05.xlsx", date(2026, 11, 5), status="PARCIAL", erro=2)
    abrir_tela(page, painel, sobrinho, TELA)
    linhas = page.locator("#corpo-planilhas tr")
    expect(linhas).to_have_count(2)
    expect(linhas.nth(0)).to_contain_text("vendas-2026-11-05.xlsx")
    expect(linhas.nth(0)).to_contain_text("Lida, com vendas a conferir")
    expect(linhas.nth(1)).to_contain_text("Não foi lida")


@pytest.mark.tela
def test_e5_sem_planilha_lida_explica_onde_salvar(page, painel, sobrinho):
    abrir_tela(page, painel, sobrinho, TELA)
    expect(page.locator("#corpo-planilhas")).to_contain_text("Nenhuma planilha lida ainda")


@pytest.mark.tela
def test_e5_no_celular_a_venda_e_a_planilha_cabem_na_tela(page, painel, sobrinho):
    from tests.test_telas_no_celular import _ESCONDIDO_A_DIREITA, CELULAR

    _pendente()
    _importacao(
        "vendas-do-caixa-exportadas-em-2026-11-05-loja-centro.xlsx", date(2026, 11, 5), status="PARCIAL"
    )
    page.set_viewport_size(CELULAR)
    abrir_tela(page, painel, sobrinho, TELA)
    page.wait_for_selector("#corpo-planilhas tr th")
    botao = page.locator("#corpo-pendentes button", has_text="Escolher o produto").first
    botao.scroll_into_view_if_needed()
    expect(botao).to_be_in_viewport(ratio=1)
    assert page.evaluate(_ESCONDIDO_A_DIREITA) == []

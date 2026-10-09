"""
Painel no celular — pedido do grupo em 09/10/2026, fora do cronograma (docs/ACOMPANHAMENTO.md).

A análise de 09/10 achou: no celular (360 px), as tabelas ficavam numa caixa que rola para o lado —
na Consulta de estoque só aparecia o nome do produto; o "Editar" de Produtos e Fornecedores e o
"Ver lotes" ficavam escondidos à direita; e o cabeçalho ocupava duas linhas.

Correção: abaixo de 640 px, cada linha de tabela vira um cartão ("rótulo: valor"), com o botão da
linha em largura inteira; o cabeçalho fica numa linha só. No computador da loja (R04) nada muda.
Sem mudar dado, regra ou endereço da API.
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from playwright.sync_api import expect

from cadastro.models import Categoria, Fornecedor, Produto, Usuario
from estoque.entrada import registrar_entrada
from estoque.perda import registrar_perda
from tests.conftest import abrir_tela

CELULAR = {"width": 360, "height": 780}
COMPUTADOR_DA_LOJA = {"width": 1024, "height": 768}
SENHA = "Mercado#2026"

TELAS = [
    ("produtos.html", "#corpo-tabela tr td"),
    ("fornecedores.html", "#corpo-tabela tr td"),
    ("entrada-mercadoria.html", "#corpo-tabela tr td"),
    ("avarias.html", "#corpo-tabela tr td"),
    ("consulta-estoque.html", "#lista-estoque tr td"),
]

# O que sai da largura da tela (ou fica numa caixa que rola de lado) dentro do conteúdo da página.
_ESCONDIDO_A_DIREITA = """() => {
  const largura = document.documentElement.clientWidth;
  const problemas = [];
  for (const e of document.querySelectorAll('main *')) {
    const estilo = getComputedStyle(e);
    if (estilo.display === 'none' || estilo.visibility === 'hidden') continue;
    if (e.closest('.visualmente-oculto, thead')) continue;
    const caixa = e.getBoundingClientRect();
    if (caixa.width === 0 || caixa.height === 0) continue;
    const nome = e.tagName + ' ' + (e.textContent || '').trim().slice(0, 30);
    if (caixa.right > largura + 1) problemas.push(nome);
    if (['auto', 'scroll'].includes(estilo.overflowX) && e.scrollWidth > e.clientWidth + 1)
      problemas.push('rola de lado: ' + e.className);
  }
  return problemas.slice(0, 10);
}"""


@pytest.fixture
def loja(painel):
    acougue = Categoria.objects.create(nome="Açougue", perecivel_padrao=True)
    secos = Categoria.objects.create(nome="Secos e molhados")
    atacadao = Fornecedor.objects.create(
        nome="Atacadão Central", prazo_entrega_dias=2, pedido_minimo=Decimal("500"), contato="(11) 4000-0000"
    )
    sobrinho = Usuario.objects.create_user(login="sobrinho", senha=SENHA, nome="Sobrinho", papel="OPERACAO")
    frango = Produto.objects.create(
        nome="Frango resfriado 1 kg",
        categoria=acougue,
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=5,
        estoque_minimo=Decimal("8"),
        preco_venda=Decimal("18.90"),
        critico_fim_semana=True,
        fornecedor_padrao=atacadao,
    )
    arroz = Produto.objects.create(
        nome="Arroz 5 kg",
        categoria=secos,
        unidade_medida="PCT",
        estoque_minimo=Decimal("10"),
        preco_venda=Decimal("27.50"),
    )
    hoje = timezone.localdate()
    registrar_entrada(
        produto=frango,
        quantidade=Decimal("5.5"),
        usuario=sobrinho,
        fornecedor=atacadao,
        custo_unitario=Decimal("12.40"),
        data_validade=hoje + timedelta(days=2),
    )
    registrar_entrada(produto=arroz, quantidade=Decimal("5"), usuario=sobrinho, fornecedor=atacadao)
    registrar_perda(produto=arroz, quantidade=Decimal("2"), motivo="Rasgou o pacote", usuario=sobrinho)
    return sobrinho


def _abrir(page, painel, sobrinho, tela, espera, tamanho=CELULAR):
    page.set_viewport_size(tamanho)
    abrir_tela(page, painel, sobrinho, tela)
    page.wait_for_selector(espera)


def _ver_inteiro(elemento):
    """Rola a página até o elemento (ele pode estar abaixo do formulário) e confere que aparece
    inteiro — com a tabela antiga, a coluna ficava fora da tela mesmo depois de rolar."""
    elemento.scroll_into_view_if_needed()
    expect(elemento).to_be_in_viewport(ratio=1)


# ------------------------------------------------------------------------------------------------
# Nada escondido à direita
# ------------------------------------------------------------------------------------------------


@pytest.mark.tela
@pytest.mark.parametrize(("tela", "espera"), TELAS)
def test_celular_nada_fica_escondido_a_direita(page, painel, loja, tela, espera):
    _abrir(page, painel, loja, tela, espera)

    assert page.evaluate(_ESCONDIDO_A_DIREITA) == []


@pytest.mark.tela
def test_celular_consulta_mostra_quantidade_minimo_validade_e_ver_lotes(page, painel, loja):
    _abrir(page, painel, loja, "consulta-estoque.html", "#lista-estoque tr td")
    cartao = page.locator("#lista-estoque tr", has=page.get_by_text("Frango resfriado 1 kg")).first

    for rotulo, valor in [("Em estoque", "5,5 KG"), ("Mínimo", "8 KG"), ("Validade", "Perto de vencer")]:
        celula = cartao.locator(f'td[data-rotulo="{rotulo}"]')
        expect(celula).to_contain_text(valor)
        _ver_inteiro(celula)
    _ver_inteiro(cartao.get_by_role("button", name="Ver lotes de Frango resfriado 1 kg"))


@pytest.mark.tela
def test_celular_lotes_abertos_ficam_dentro_da_tela(page, painel, loja):
    _abrir(page, painel, loja, "consulta-estoque.html", "#lista-estoque tr td")

    page.get_by_role("button", name="Ver lotes de Frango resfriado 1 kg").click()
    lotes = page.get_by_role("list", name="Lotes de Frango resfriado 1 kg, do que vence primeiro ao último")
    expect(lotes).to_contain_text("Atacadão Central")

    assert page.evaluate(_ESCONDIDO_A_DIREITA) == []


@pytest.mark.tela
@pytest.mark.parametrize(("tela", "botao"), [("produtos.html", "Editar"), ("fornecedores.html", "Editar")])
def test_celular_editar_fica_a_vista(page, painel, loja, tela, botao):
    _abrir(page, painel, loja, tela, "#corpo-tabela tr td")

    _ver_inteiro(page.locator("#corpo-tabela").get_by_role("button", name=botao).first)


@pytest.mark.tela
@pytest.mark.parametrize(
    ("tela", "espera", "seletor"),
    [
        ("produtos.html", "#corpo-tabela tr td", "#corpo-tabela button"),
        ("fornecedores.html", "#corpo-tabela tr td", "#corpo-tabela button"),
        ("consulta-estoque.html", "#lista-estoque tr td", "#lista-estoque button"),
    ],
)
def test_celular_botao_da_linha_tem_44px_para_o_dedo(page, painel, loja, tela, espera, seletor):
    _abrir(page, painel, loja, tela, espera)

    alturas = page.eval_on_selector_all(seletor, "bs => bs.map(b => b.getBoundingClientRect().height)")
    assert alturas and min(alturas) >= 44


@pytest.mark.tela
def test_celular_listas_do_dia_viram_cartoes_com_rotulo(page, painel, loja):
    _abrir(page, painel, loja, "avarias.html", "#corpo-tabela tr td")

    expect(page.locator('#corpo-tabela td[data-rotulo="Motivo"]').first).to_have_text("Rasgou o pacote")
    _ver_inteiro(page.locator('#corpo-tabela td[data-rotulo="Motivo"]').first)


# ------------------------------------------------------------------------------------------------
# Cabeçalho
# ------------------------------------------------------------------------------------------------


@pytest.mark.tela
def test_celular_cabecalho_numa_linha_so_mais_o_menu(page, painel, loja):
    _abrir(page, painel, loja, "produtos.html", "#corpo-tabela tr td")

    marca = page.locator(".cabecalho__marca").bounding_box()
    sair = page.locator("#botao-sair").bounding_box()
    assert abs(marca["y"] + marca["height"] / 2 - (sair["y"] + sair["height"] / 2)) < 8  # mesma linha
    assert page.locator(".cabecalho").bounding_box()["height"] <= 130
    assert page.evaluate(_ESCONDIDO_A_DIREITA) == []


# ------------------------------------------------------------------------------------------------
# Leitor de tela e computador da loja
# ------------------------------------------------------------------------------------------------


@pytest.mark.tela
def test_celular_cartao_continua_sendo_tabela_para_o_leitor_de_tela(page, painel, loja):
    _abrir(page, painel, loja, "consulta-estoque.html", "#lista-estoque tr td")

    tabela = page.get_by_role("table")
    expect(tabela).to_have_count(1)
    expect(tabela.get_by_role("columnheader", name="Em estoque")).to_have_count(1)
    linha = tabela.get_by_role("row", name="Frango resfriado 1 kg")
    expect(linha.get_by_role("cell").first).to_contain_text("5,5 KG")


@pytest.mark.tela
@pytest.mark.parametrize(("tela", "espera"), TELAS)
def test_computador_da_loja_continua_com_tabela(page, painel, loja, tela, espera):
    _abrir(page, painel, loja, tela, espera, tamanho=COMPUTADOR_DA_LOJA)

    exibicao = page.eval_on_selector(".tabela", "t => getComputedStyle(t).display")
    cabecalho_visivel = page.eval_on_selector(".tabela thead", "t => t.getBoundingClientRect().height > 1")
    assert exibicao == "table"
    assert cabecalho_visivel


@pytest.mark.tela
@pytest.mark.parametrize(("tela", "espera"), TELAS)
def test_tablet_nada_fica_escondido_a_direita(page, painel, loja, tela, espera):
    _abrir(page, painel, loja, tela, espera, tamanho={"width": 768, "height": 1024})

    assert page.evaluate(_ESCONDIDO_A_DIREITA) == []

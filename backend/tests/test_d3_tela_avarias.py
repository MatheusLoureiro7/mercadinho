"""
Tarefa D3 — tela de Avarias e quebras (RF04, fluxograma 03).

O caderno de avarias do sobrinho: o que venceu, quebrou ou estragou sai do estoque, sempre com o
motivo. A tela envia para POST /api/perdas/ (D1) e mostra o que a API responde; a regra é da API
(motivo obrigatório, lote do produto, não perder mais do que existe; RN11 e RN16 também).

Aqui: o contrato entre a tela e a API, o acesso (RN14) e o comportamento na tela. O fluxo completo
(as situações do fluxograma 03 e o que fica gravado) é a tarefa D4.
"""

import re
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from django.utils import timezone
from playwright.sync_api import expect

from cadastro.models import Categoria, Produto, Usuario
from estoque.entrada import registrar_entrada
from estoque.models import Lote
from estoque.serializers import MENSAGEM_SEM_MOTIVO, RegistroDePerdaSerializer
from tests.conftest import abrir_tela, guardar_sessao

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
TELA = FRONTEND / "avarias.html"
SCRIPT = FRONTEND / "js" / "avarias.js"
SENHA = "Mercado#2026"


# ------------------------------------------------------------------------------------------------
# Contrato tela × API e acesso
# ------------------------------------------------------------------------------------------------


def _campos_da_tela() -> set[str]:
    bloco = re.search(r"const CAMPOS = \{(.*?)\n\};", SCRIPT.read_text(encoding="utf-8"), flags=re.S)
    assert bloco, "avarias.js sem o mapa CAMPOS"
    return set(re.findall(r"^\s{2}(\w+): \{", bloco.group(1), flags=re.MULTILINE))


def test_d3_tela_envia_exatamente_os_campos_da_api():
    assert _campos_da_tela() == set(RegistroDePerdaSerializer().fields)


def test_d3_tela_tem_lugar_para_o_erro_de_cada_campo():
    html = TELA.read_text(encoding="utf-8")
    for campo in _campos_da_tela():
        assert f'id="erro-{campo}"' in html, campo


def test_d3_tela_entra_no_menu_do_sobrinho():
    sessao = (FRONTEND / "js" / "sessao.js").read_text(encoding="utf-8")

    assert 'avarias: { nome: "Avarias e quebras", endereco: "avarias.html" }' in sessao


def test_d3_tela_exige_login_e_o_perfil_de_avarias():
    assert 'src="js/avarias.js"' in TELA.read_text(encoding="utf-8")
    assert 'entrarNaTela("avarias")' in SCRIPT.read_text(encoding="utf-8")


# ------------------------------------------------------------------------------------------------
# Na tela (navegador → API → banco)
# ------------------------------------------------------------------------------------------------


@pytest.fixture
def loja(painel):
    frios = Categoria.objects.create(nome="Frios", perecivel_padrao=True)
    sobrinho = Usuario.objects.create_user(login="sobrinho", senha=SENHA, nome="Sobrinho", papel="OPERACAO")
    iogurte = Produto.objects.create(
        nome="Iogurte natural", categoria=frios, unidade_medida="UN", perecivel=True, durabilidade_dias=15
    )
    hoje = timezone.localdate()
    # Um lote bom (entra hoje) e um vencido ontem (RN16) — o vencido entrou há 20 dias.
    registrar_entrada(produto=iogurte, quantidade=Decimal("10"), usuario=sobrinho)
    vencido = registrar_entrada(
        produto=iogurte, quantidade=Decimal("3"), usuario=sobrinho, data_validade=hoje + timedelta(days=5)
    )
    Lote.objects.filter(pk=vencido.pk).update(data_validade=hoje - timedelta(days=1))
    return {"sobrinho": sobrinho, "iogurte": iogurte, "vencido": vencido}


@pytest.fixture
def tela(page, painel, loja):
    abrir_tela(page, painel, loja["sobrinho"], "avarias.html")
    page.wait_for_selector("#corpo-tabela tr")
    return page


@pytest.mark.tela
def test_d3_lotes_do_produto_aparecem_na_ordem_de_validade_com_o_vencido_destacado(tela):
    tela.fill("#campo-procurar", "iogurte")

    opcoes = tela.locator("#lista-de-lotes label")
    expect(opcoes).to_have_count(3)  # "pela ordem de validade" + os dois lotes
    expect(opcoes.nth(1)).to_contain_text("Vencido")  # RN16: vence primeiro, aparece primeiro
    expect(opcoes.nth(1)).to_contain_text("3 UN")
    expect(opcoes.nth(2)).to_contain_text("10 UN")


@pytest.mark.tela
def test_d3_sem_escolher_lote_a_perda_sai_pela_ordem_de_validade(tela):
    tela.fill("#campo-procurar", "iogurte")

    expect(tela.locator("#lista-de-lotes input[value='']")).to_be_checked()
    expect(tela.locator("#lista-de-lotes label").first).to_contain_text("ordem de validade")


@pytest.mark.tela
def test_d3_botao_de_motivo_preenche_o_motivo(tela):
    tela.click("button[data-motivo='Venceu']")

    expect(tela.locator("#campo-motivo")).to_have_value("Venceu")


@pytest.mark.tela
def test_d3_sem_motivo_a_api_recusa_e_o_digitado_fica(tela):
    tela.fill("#campo-procurar", "iogurte")
    tela.fill("#campo-quantidade", "2")
    tela.click("#botao-salvar")

    expect(tela.locator("#erro-motivo")).to_have_text(MENSAGEM_SEM_MOTIVO)
    expect(tela.locator("#campo-quantidade")).to_have_value("2")


@pytest.mark.tela
def test_d3_perda_registrada_aparece_no_caderno_de_hoje(tela, loja):
    tela.fill("#campo-procurar", "iogurte")
    tela.check(f"#lista-de-lotes input[value='{loja['vencido'].pk}']")
    tela.fill("#campo-quantidade", "3")
    tela.click("button[data-motivo='Venceu']")
    tela.click("#botao-salvar")

    expect(tela.locator("#sucesso-texto")).to_contain_text("Perda registrada: 3 UN de Iogurte natural")
    expect(tela.locator("#sucesso-texto")).to_contain_text("Agora tem 10 UN em estoque.")
    primeira = tela.locator("#corpo-tabela tr").first
    expect(primeira).to_contain_text("Iogurte natural")
    expect(primeira).to_contain_text("Venceu")
    expect(primeira).to_contain_text("Sobrinho")


@pytest.mark.tela
def test_d3_lote_que_zerou_some_da_lista_de_lotes(tela, loja):
    tela.fill("#campo-procurar", "iogurte")
    tela.check(f"#lista-de-lotes input[value='{loja['vencido'].pk}']")
    tela.fill("#campo-quantidade", "3")
    tela.fill("#campo-motivo", "Venceu")
    tela.click("#botao-salvar")
    expect(tela.locator("#sucesso")).to_be_visible()

    tela.fill("#campo-procurar", "iogurte")

    expect(tela.locator("#lista-de-lotes label")).to_have_count(2)  # ordem de validade + o lote bom


@pytest.mark.tela
def test_d3_rn14_outro_perfil_nao_abre_avarias(page, painel, loja):
    esposa = Usuario.objects.create_user(login="esposa", senha=SENHA, nome="Esposa", papel="GESTAO")
    guardar_sessao(page, painel, esposa)

    page.goto(painel + "/avarias.html")

    expect(page.locator("#recado")).to_have_text("O seu perfil não tem acesso à tela de Avarias e quebras.")


# ------------------------------------------------------------------------------------------------
# A frase da recusa aparece direto na tela: quantidade escrita como na loja (achado na D3)
# ------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("valor", "unidade", "esperado"),
    [
        ("3.000", "UN", "3 UN"),
        ("2.000", "KG", "2 KG"),
        ("2.500", "KG", "2,5 KG"),
        ("0.125", "KG", "0,125 KG"),
    ],
)
def test_d3_quantidade_na_frase_da_api_e_escrita_como_na_loja(valor, unidade, esperado):
    from estoque.perda import _quantidade_na_loja

    assert _quantidade_na_loja(Decimal(valor), Produto(unidade_medida=unidade)) == esperado

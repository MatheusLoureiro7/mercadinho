"""
Tarefa I2 — tela de Fechamento de caixa (RF12, RN15, fluxograma 06). Usada pela esposa (GESTAO, RN14).

"Confere o dinheiro contado contra o apurado no dia" (Apostila II). A diferença é o valor contado
menos o apurado; é calculada (na tela, só para mostrar antes de confirmar; gravada, pelo banco —
coluna gerada), nunca digitada. Correção é um registro novo: o anterior nunca some (RN15).

Decisão do grupo (09/10/2026): a I2 é feita só como tela agora e ligada à API na I1, que espera a
E2 (vendas) e a D01. Contrato proposto para a I1 (registrado no diário):

    GET  /api/fechamentos/apurado/?data=AAAA-MM-DD  → {"data", "valor_sistema"}      (L12)
    GET  /api/fechamentos/?data=AAAA-MM-DD          → registros do dia, o mais novo primeiro
    POST /api/fechamentos/  {"valor_contado"}       → o registro gravado (data e apurado: servidor)

Até a I1, a API responde 404 e a tela diz que o fechamento ainda não está disponível. Nos testes,
o navegador responde por esses três endereços; o resto (login, sessão, menu, RN14) é a API de
verdade.
"""

import json
import re
from decimal import Decimal
from pathlib import Path

import pytest
from playwright.sync_api import expect

from cadastro.models import Usuario
from tests.conftest import abrir_tela

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
TELA = "fechamento-caixa.html"
SENHA = "Mercado#2026"
ENDERECOS_DO_FECHAMENTO = re.compile(r".*/api/fechamentos/.*")


# ------------------------------------------------------------------------------------------------
# Sem navegador
# ------------------------------------------------------------------------------------------------


def test_i2_tela_entra_no_menu_da_esposa():
    sessao = (FRONTEND / "js" / "sessao.js").read_text(encoding="utf-8")

    assert 'fechamento_caixa: { nome: "Fechamento de caixa", endereco: "fechamento-caixa.html" }' in sessao


def test_i2_tela_exige_login_e_o_perfil_do_fechamento():
    html = (FRONTEND / TELA).read_text(encoding="utf-8")
    script = re.search(r'src="js/([\w-]+)\.js"', html).group(1)

    assert 'entrarNaTela("fechamento_caixa")' in (FRONTEND / "js" / f"{script}.js").read_text(
        encoding="utf-8"
    )


def test_i2_rn15_so_o_dinheiro_contado_e_o_dia_do_caixa_sao_digitados():
    """
    Nem a diferença nem o apurado têm campo: um é calculado, o outro vem do sistema (RN15). O dia do
    caixa é escolhido desde a revisão X1, item 6 (decisão do grupo, 16/11/2026).
    """
    html = (FRONTEND / TELA).read_text(encoding="utf-8")

    campos = set(re.findall(r'<(?:input|select|textarea)[^>]*\bname="([\w]+)"', html))
    assert campos == {"valor_contado", "data"}


def test_i2_rn15_tela_nao_altera_nem_apaga_fechamento():
    script = (FRONTEND / "js" / "fechamento-caixa.js").read_text(encoding="utf-8")

    assert "api.alterar" not in script
    assert "DELETE" not in script


# ------------------------------------------------------------------------------------------------
# Na tela
# ------------------------------------------------------------------------------------------------


class FechamentoDeMentira:
    """Responde pelos endereços que a I1 vai criar, do jeito proposto no contrato."""

    def __init__(self, page):
        self.disponivel = True
        self.apurado = "3240.00"
        self.registros = []
        self.recebidos = []
        self.resposta_do_post = None  # (status, corpo) para forçar recusa
        page.route(ENDERECOS_DO_FECHAMENTO, self._responder)

    def _json(self, rota, status, corpo):
        rota.fulfill(status=status, content_type="application/json", body=json.dumps(corpo))

    def _responder(self, rota):
        pedido = rota.request
        if not self.disponivel:
            return self._json(
                rota, 404, {"erro": {"codigo": "nao_encontrado", "mensagem": "Endereço não encontrado."}}
            )
        if pedido.method == "POST":
            corpo = json.loads(pedido.post_data or "{}")
            self.recebidos.append(corpo)
            if self.resposta_do_post:
                return self._json(rota, *self.resposta_do_post)
            contado = Decimal(corpo["valor_contado"])
            registro = {
                "id": len(self.registros) + 1,
                "data": "2026-10-09",
                "valor_sistema": self.apurado,
                "valor_contado": f"{contado:.2f}",
                "diferenca": f"{contado - Decimal(self.apurado):.2f}",
                "registrado_por_nome": "Esposa",
                "registrado_em": f"2026-10-09T19:0{len(self.registros)}:00-03:00",
            }
            self.registros.insert(0, registro)
            return self._json(rota, 201, registro)
        if "/apurado/" in pedido.url:
            return self._json(rota, 200, {"data": "2026-10-09", "valor_sistema": self.apurado})
        return self._json(rota, 200, self.registros)


@pytest.fixture
def esposa(painel):
    return Usuario.objects.create_user(login="esposa", senha=SENHA, nome="Esposa", papel="GESTAO")


@pytest.fixture
def caixa(page):
    return FechamentoDeMentira(page)


@pytest.fixture
def tela(page, painel, esposa, caixa):
    abrir_tela(page, painel, esposa, TELA)
    expect(page.locator("#valor-apurado")).to_have_text("R$ 3.240,00")
    return page


def _contar(page, valor):
    page.fill("#campo-contado", valor)


def _registrar(page, valor, vezes):
    """Conta, registra e espera a lista mostrar `vezes` registros (a lista vazia também tem 1 linha)."""
    _contar(page, valor)
    page.click("#botao-salvar")
    expect(page.locator("#sucesso")).to_contain_text("Fechamento registrado")
    expect(page.locator("#corpo-tabela tr:not(:has(.vazio))")).to_have_count(vezes)


@pytest.mark.tela
def test_i2_mostra_o_apurado_pelo_sistema(tela):
    expect(tela.locator("#valor-apurado")).to_have_text("R$ 3.240,00")


@pytest.mark.tela
def test_i2_rn15_falta_no_caixa_aparece_antes_de_confirmar(tela, caixa):
    """O exemplo da Apostila I: apurado R$ 3.240,00, contado R$ 3.215,00 → −R$ 25,00."""
    _contar(tela, "3.215,00")

    expect(tela.locator("#diferenca")).to_contain_text("Faltam R$ 25,00")
    assert caixa.recebidos == []  # nada gravado só por digitar


@pytest.mark.tela
def test_i2_rn15_sobra_no_caixa(tela):
    _contar(tela, "3250")

    expect(tela.locator("#diferenca")).to_contain_text("Sobram R$ 10,00")


@pytest.mark.tela
def test_i2_rn15_caixa_bate(tela):
    _contar(tela, "3240,00")

    expect(tela.locator("#diferenca")).to_contain_text("O caixa bateu")


@pytest.mark.tela
def test_i2_rn15_registra_e_mostra_na_lista_do_dia(tela, caixa):
    _contar(tela, "3.215,00")
    tela.click("#botao-salvar")

    # Só o contado e o dia do caixa (X1, item 6): apurado e diferença, nunca.
    assert caixa.recebidos == [{"valor_contado": "3215.00", "data": tela.input_value("#campo-dia")}]
    expect(tela.locator("#sucesso")).to_contain_text("Fechamento registrado")
    linha = tela.locator("#corpo-tabela tr").first
    expect(linha).to_contain_text("19:00")
    expect(linha).to_contain_text("R$ 3.215,00")
    expect(linha).to_contain_text("-R$ 25,00")
    expect(linha).to_contain_text("Esposa")


@pytest.mark.tela
def test_i2_o_que_foi_digitado_durante_o_registro_nao_some(tela, caixa):
    """Achado na I2: limpar o campo depois de gravar apagava a contagem digitada enquanto gravava."""
    _contar(tela, "3.215,00")
    tela.click("#botao-salvar")
    _contar(tela, "3.240,00")  # já digitando a próxima, antes de a primeira terminar

    expect(tela.locator("#sucesso")).to_contain_text("Fechamento registrado")
    expect(tela.locator("#campo-contado")).to_have_value("3.240,00")


@pytest.mark.tela
def test_i2_rn15_contar_de_novo_gera_registro_novo_e_o_anterior_fica(tela, caixa):
    _registrar(tela, "3.215,00", 1)

    _registrar(tela, "3.240,00", 2)

    linhas = tela.locator("#corpo-tabela tr")
    expect(linhas).to_have_count(2)
    expect(linhas.nth(0)).to_contain_text("R$ 3.240,00")  # o mais novo primeiro
    expect(linhas.nth(1)).to_contain_text("R$ 3.215,00")  # o anterior continua lá


@pytest.mark.tela
@pytest.mark.parametrize("digitado", ["", "abc", "-10", "12,345"])
def test_i2_contado_invalido_nao_vai_para_o_sistema(tela, caixa, digitado):
    _contar(tela, digitado)
    tela.click("#botao-salvar")

    expect(tela.locator("#erro-valor_contado")).to_be_visible()
    expect(tela.locator("#campo-contado")).to_have_attribute("aria-invalid", "true")
    assert caixa.recebidos == []


@pytest.mark.tela
def test_i2_recusa_da_api_aparece_embaixo_do_campo(tela, caixa):
    caixa.resposta_do_post = (
        400,
        {
            "erro": {
                "codigo": "validacao",
                "mensagem": "Confira os campos destacados.",
                "campos": {"valor_contado": ["Informe o dinheiro contado na gaveta."]},
            }
        },
    )
    _contar(tela, "3.215,00")
    tela.click("#botao-salvar")

    expect(tela.locator("#erro-valor_contado")).to_have_text("Informe o dinheiro contado na gaveta.")
    expect(tela.locator("#campo-contado")).to_have_value("3.215,00")  # o que foi digitado fica


@pytest.mark.tela
def test_i2_antes_da_i1_a_tela_avisa_que_nao_esta_disponivel(page, painel, esposa, caixa):
    caixa.disponivel = False

    abrir_tela(page, painel, esposa, TELA)

    expect(page.locator("#indisponivel")).to_contain_text("ainda não está disponível")
    expect(page.locator("#botao-salvar")).to_be_disabled()
    expect(page.locator("#campo-contado")).to_be_disabled()


@pytest.mark.tela
def test_i2_rn14_sobrinho_nao_abre_o_fechamento(page, painel, caixa):
    sobrinho = Usuario.objects.create_user(login="sobrinho", senha=SENHA, nome="Sobrinho", papel="OPERACAO")

    abrir_tela(page, painel, sobrinho, TELA)

    expect(page).not_to_have_url(re.compile(r"fechamento-caixa\.html"))
    expect(page.locator("#recado")).to_contain_text("não tem acesso à tela de Fechamento de caixa")


@pytest.mark.tela
def test_i2_no_celular_nada_fica_escondido(page, painel, esposa, caixa):
    from tests.test_telas_no_celular import _ESCONDIDO_A_DIREITA

    page.set_viewport_size({"width": 360, "height": 780})
    abrir_tela(page, painel, esposa, TELA)
    expect(page.locator("#valor-apurado")).to_have_text("R$ 3.240,00")
    _registrar(page, "3.215,00", 1)

    assert page.evaluate(_ESCONDIDO_A_DIREITA) == []

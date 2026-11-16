"""
Tarefa F3 — tela de Consulta de estoque, com destaque para o mínimo e os vencidos (RF07, RN16).

A única tela que os três usam (RN14). Mostra o saldo por produto e por categoria, o que está abaixo
do mínimo, perto de vencer e vencido — tudo calculado pela API da F2 (/api/estoque/ e
/api/estoque/lotes/). A tela só lê (RN01): não grava nada e não decide regra.
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
from estoque.perda import registrar_perda
from previsao.models import PrevisaoProduto
from tests.conftest import abrir_tela, entrar_pelo_login

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
TELA = "consulta-estoque.html"
SENHA = "Mercado#2026"


# ------------------------------------------------------------------------------------------------
# Menu e acesso
# ------------------------------------------------------------------------------------------------


def test_f3_tela_entra_no_menu_dos_tres_perfis():
    sessao = (FRONTEND / "js" / "sessao.js").read_text(encoding="utf-8")

    assert 'consulta_estoque: { nome: "Consulta de estoque", endereco: "consulta-estoque.html" }' in sessao


def test_f3_tela_exige_login_e_o_perfil_da_consulta():
    script = re.search(r'src="js/([\w-]+)\.js"', (FRONTEND / TELA).read_text(encoding="utf-8")).group(1)

    assert 'entrarNaTela("consulta_estoque")' in (FRONTEND / "js" / f"{script}.js").read_text(
        encoding="utf-8"
    )


def test_f3_rn01_tela_nao_tem_formulario_de_gravacao():
    html = (FRONTEND / TELA).read_text(encoding="utf-8")

    assert "<form" not in html
    assert "api.criar" not in (FRONTEND / "js" / "consulta-estoque.js").read_text(encoding="utf-8")
    assert "api.alterar" not in (FRONTEND / "js" / "consulta-estoque.js").read_text(encoding="utf-8")


# ------------------------------------------------------------------------------------------------
# Na tela (navegador → API → banco)
# ------------------------------------------------------------------------------------------------


def _hoje():
    return timezone.localdate()


@pytest.fixture
def loja(painel):
    """
    Frios: iogurte com um lote vencido ontem (RN16) e um bom; presunto que vence em 2 dias.
    Secos e molhados: arroz abaixo do mínimo (3 de 10) e feijão folgado (20 de 10).
    """
    frios = Categoria.objects.create(nome="Frios", perecivel_padrao=True)
    secos = Categoria.objects.create(nome="Secos e molhados")
    sobrinho = Usuario.objects.create_user(login="sobrinho", senha=SENHA, nome="Sobrinho", papel="OPERACAO")

    def produto(nome, categoria, unidade, minimo=None, dias=None, **extra):
        return Produto.objects.create(
            nome=nome,
            categoria=categoria,
            unidade_medida=unidade,
            perecivel=dias is not None,
            durabilidade_dias=dias,
            estoque_minimo=minimo,
            **extra,
        )

    iogurte = produto("Iogurte natural", frios, "UN", dias=15)
    presunto = produto("Presunto", frios, "KG", minimo=Decimal("1"), dias=7)
    arroz = produto("Arroz 5 kg", secos, "PCT", minimo=Decimal("10"), critico_fim_semana=True)
    feijao = produto("Feijão carioca 1 kg", secos, "PCT", minimo=Decimal("10"))

    hoje = _hoje()
    registrar_entrada(produto=iogurte, quantidade=Decimal("10"), usuario=sobrinho)
    vencido = registrar_entrada(
        produto=iogurte, quantidade=Decimal("3"), usuario=sobrinho, data_validade=hoje
    )
    Lote.objects.filter(pk=vencido.pk).update(data_validade=hoje - timedelta(days=1))
    registrar_entrada(
        produto=presunto, quantidade=Decimal("2.5"), usuario=sobrinho, data_validade=hoje + timedelta(days=2)
    )
    registrar_entrada(produto=arroz, quantidade=Decimal("5"), usuario=sobrinho)
    registrar_perda(produto=arroz, quantidade=Decimal("2"), motivo="Rasgou o pacote", usuario=sobrinho)
    registrar_entrada(produto=feijao, quantidade=Decimal("20"), usuario=sobrinho)
    return {"sobrinho": sobrinho, "iogurte": iogurte, "arroz": arroz}


@pytest.fixture
def tela(page, painel, loja):
    abrir_tela(page, painel, loja["sobrinho"], TELA)
    page.wait_for_selector("#lista-estoque tr td")
    return page


def _linha(page, nome):
    return page.locator("#lista-estoque tr", has=page.locator("th, td", has_text=nome)).first


@pytest.mark.tela
def test_f3_rf07_saldo_por_produto_agrupado_por_categoria(tela):
    grupos = tela.locator("#lista-estoque th[scope='rowgroup']")
    expect(grupos).to_have_text(["Frios", "Secos e molhados"])
    expect(_linha(tela, "Iogurte natural")).to_contain_text("13 UN")  # 10 + 3 (o vencido ainda conta)
    expect(_linha(tela, "Presunto")).to_contain_text("2,5 KG")
    expect(_linha(tela, "Arroz 5 kg")).to_contain_text("3 PCT")  # 5 − 2 de perda (RN01)


@pytest.mark.tela
def test_f3_rf07_abaixo_do_minimo_aparece_destacado(tela):
    expect(_linha(tela, "Arroz 5 kg")).to_contain_text("Abaixo do mínimo")
    expect(_linha(tela, "Feijão carioca 1 kg")).not_to_contain_text("Abaixo do mínimo")


@pytest.mark.tela
def test_f3_rn16_lote_vencido_aparece_destacado(tela):
    expect(_linha(tela, "Iogurte natural")).to_contain_text("1 lote vencido")
    expect(_linha(tela, "Presunto")).to_contain_text("Perto de vencer")
    expect(_linha(tela, "Feijão carioca 1 kg")).not_to_contain_text("vencid")


@pytest.mark.tela
def test_x1_rf08_rn09_tela_mostra_quando_acaba_ou_ainda_aprendendo(page, painel, loja):
    """X1, item 10: a previsão da rodada das 03h00 aparece na consulta, no vocabulário da loja."""
    feijao = Produto.objects.get(nome="Feijão carioca 1 kg")
    presunto = Produto.objects.get(nome="Presunto")
    agora = timezone.now()
    PrevisaoProduto.objects.create(
        produto=feijao,
        consumo_medio_diario=Decimal("1.6"),
        dias_ate_acabar=Decimal("12.5"),
        calculado_em=agora,
    )
    PrevisaoProduto.objects.create(
        produto=presunto,
        consumo_medio_diario=Decimal("1.8"),
        dias_ate_acabar=Decimal("1.4"),
        calculado_em=agora,
    )
    PrevisaoProduto.objects.create(produto=loja["arroz"])  # RN09: menos de 14 dias de venda

    abrir_tela(page, painel, loja["sobrinho"], TELA)
    expect(page.locator("#lista-estoque thead")).to_contain_text("Quando acaba")
    expect(_linha(page, "Feijão carioca 1 kg")).to_contain_text("Em 12 dias")
    expect(_linha(page, "Presunto")).to_contain_text("Amanhã")
    expect(_linha(page, "Arroz 5 kg")).to_contain_text("Ainda aprendendo")
    expect(_linha(page, "Iogurte natural")).to_contain_text("Ainda aprendendo")  # sem previsão
    expect(_linha(page, "Arroz 5 kg")).not_to_contain_text("0 dias")


@pytest.mark.tela
def test_f3_resumo_conta_o_que_precisa_de_atencao(tela):
    expect(tela.locator("#contador-vencidos")).to_have_text("1")
    expect(tela.locator("#contador-vencendo")).to_have_text("1")
    expect(tela.locator("#contador-abaixo")).to_have_text("1")


@pytest.mark.tela
def test_f3_resumo_filtra_so_o_que_esta_abaixo_do_minimo(tela):
    tela.click("#filtro-abaixo")

    expect(tela.locator("#filtro-abaixo")).to_have_attribute("aria-pressed", "true")
    expect(tela.locator("#lista-estoque tr:has(td)")).to_have_count(1)
    expect(_linha(tela, "Arroz 5 kg")).to_be_visible()

    tela.click("#filtro-abaixo")  # de novo: volta a mostrar tudo
    expect(tela.locator("#lista-estoque tr:has(td)")).to_have_count(4)


@pytest.mark.tela
def test_f3_resumo_filtra_vencidos(tela):
    tela.click("#filtro-vencidos")

    expect(tela.locator("#lista-estoque tr:has(td)")).to_have_count(1)
    expect(_linha(tela, "Iogurte natural")).to_be_visible()


@pytest.mark.tela
def test_f3_procurar_sem_acento(tela):
    tela.fill("#campo-procurar", "feijao")

    expect(tela.locator("#lista-estoque tr:has(td)")).to_have_count(1)
    expect(_linha(tela, "Feijão carioca 1 kg")).to_be_visible()


@pytest.mark.tela
def test_f3_procurar_sem_resultado_diz_isso(tela):
    tela.fill("#campo-procurar", "picanha")

    expect(tela.locator("#lista-estoque")).to_contain_text("Nenhum produto encontrado")


@pytest.mark.tela
def test_f3_ver_lotes_do_produto_na_ordem_de_validade(tela):
    botao = _linha(tela, "Iogurte natural").locator("button", has_text="Ver lotes")
    botao.click()

    expect(botao).to_have_attribute("aria-expanded", "true")
    lotes = tela.locator(".lotes-do-produto li")
    expect(lotes).to_have_count(2)
    expect(lotes.first).to_contain_text("Vencido há 1 dia")  # vence primeiro, aparece primeiro
    expect(lotes.first).to_contain_text("3 UN")
    expect(lotes.nth(1)).to_contain_text("10 UN")


@pytest.mark.tela
def test_f3_rn01_usar_a_tela_nao_grava_nada(tela):
    gravacoes = []
    tela.on("request", lambda r: r.method in ("POST", "PUT", "PATCH", "DELETE") and gravacoes.append(r.url))

    tela.click("#filtro-vencidos")
    tela.click("#filtro-vencidos")
    tela.fill("#campo-procurar", "iogurte")
    _linha(tela, "Iogurte natural").locator("button", has_text="Ver lotes").click()
    tela.click("#botao-atualizar")
    expect(tela.locator("#lista-estoque tr:has(td)").first).to_be_visible()

    assert gravacoes == []


@pytest.mark.tela
def test_f3_atualizar_traz_o_saldo_novo(tela, loja):
    registrar_entrada(produto=loja["arroz"], quantidade=Decimal("10"), usuario=loja["sobrinho"])

    tela.click("#botao-atualizar")

    expect(_linha(tela, "Arroz 5 kg")).to_contain_text("13 PCT")
    expect(_linha(tela, "Arroz 5 kg")).not_to_contain_text("Abaixo do mínimo")
    expect(tela.locator("#contador-abaixo")).to_have_text("0")


@pytest.mark.tela
@pytest.mark.parametrize(
    ("papel", "login"), [("DONO", "joao"), ("GESTAO", "esposa"), ("OPERACAO", "sobrinho2")]
)
def test_f3_rn14_os_tres_perfis_abrem_a_consulta(page, painel, loja, papel, login):
    Usuario.objects.create_user(login=login, senha=SENHA, nome=login.title(), papel=papel)

    entrar_pelo_login(page, painel, login, SENHA)
    page.click('#menu a[href="consulta-estoque.html"]')

    expect(page.locator('#menu a[aria-current="page"]')).to_have_text("Consulta de estoque")
    expect(page.locator("#lista-estoque")).to_contain_text("Arroz 5 kg")


@pytest.mark.tela
@pytest.mark.parametrize(("papel", "login"), [("DONO", "joao"), ("GESTAO", "esposa")])
def test_f3_dono_e_esposa_caem_na_consulta_ao_entrar(page, painel, loja, papel, login):
    # A consulta é a primeira (e, por enquanto, a única) tela pronta do perfil deles.
    Usuario.objects.create_user(login=login, senha=SENHA, nome=login.title(), papel=papel)

    entrar_pelo_login(page, painel, login, SENHA)

    page.wait_for_url(re.compile(r"consulta-estoque\.html$"))

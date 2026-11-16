"""
Documentação do sistema em dia — "docs as code", critério de aceite dos slides do professor
(13/11/2026). Ver docs/sistema/LEIA-ME.md.

- Os quatro documentos tirados do código (rastreabilidade, dicionário de dados, contratos da API e
  dependências) precisam estar iguais ao que o código gera hoje: endpoint, tabela, regra ou
  dependência nova sem `python docs/sistema/gerar.py` faz este teste falhar.
- Endpoint novo precisa de descrição no gerador.
- O índice tem os 24 documentos dos slides, todo arquivo citado existe e todo documento das quatro
  pastas está no índice; cada documento escrito à mão diz quando foi atualizado.
"""

import importlib.util
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "docs" / "sistema"


@pytest.fixture(scope="module")
def gerador():
    especificacao = importlib.util.spec_from_file_location("gerar_documentacao", PASTA / "gerar.py")
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def _indice():
    texto = (PASTA / "LEIA-ME.md").read_text(encoding="utf-8")
    secao = texto.split("## Os 24 documentos")[1].split("## ")[0]
    return [
        linha for linha in secao.splitlines() if re.match(r"\| (Usar|Manter|Sustentar|Evoluir) \|", linha)
    ]


@pytest.mark.django_db
def test_documentos_gerados_do_codigo_estao_em_dia(gerador):
    assert gerador.desatualizados() == [], "rode: python docs/sistema/gerar.py"


@pytest.mark.django_db
def test_contratos_nao_mudam_depois_que_a_api_ja_foi_chamada(gerador):
    """O DRF põe "head" nas ações da rota na primeira chamada; o documento não pode mudar por isso."""
    from django.urls import resolve

    antes = gerador.contratos_da_api()
    acoes = resolve("/api/produtos/").func.actions
    acoes["head"] = acoes["get"]  # o que o DRF faz quando a tela pede a lista de produtos
    try:
        assert gerador.contratos_da_api() == antes
    finally:
        del acoes["head"]


@pytest.mark.django_db
def test_todo_endpoint_da_api_tem_descricao(gerador):
    assert gerador.SEM_DESCRICAO not in gerador.contratos_da_api()


def test_indice_tem_os_24_documentos_dos_slides_seis_por_pergunta():
    linhas = _indice()
    assert len(linhas) == 24
    for pergunta in ("Usar", "Manter", "Sustentar", "Evoluir"):
        assert sum(linha.startswith(f"| {pergunta} |") for linha in linhas) == 6


def test_todo_arquivo_do_indice_existe_e_todo_documento_esta_no_indice():
    citados = set()
    for linha in _indice():
        for arquivo in re.findall(r"`([^`]+\.md)`", linha):
            caminho = RAIZ / arquivo if "/" in arquivo and arquivo.startswith("docs/") else PASTA / arquivo
            if arquivo in ("README.md", "COMO-RODAR.md"):
                caminho = RAIZ / arquivo
            assert caminho.exists(), arquivo
            citados.add(caminho.resolve())
    for pasta in ("usar", "manter", "sustentar", "evoluir"):
        for documento in (PASTA / pasta).glob("*.md"):
            assert documento.resolve() in citados, f"{documento.name} não está no índice (LEIA-ME.md)"


def test_documento_escrito_a_mao_diz_quando_foi_atualizado(gerador):
    gerados = {PASTA / nome for nome in gerador.GERADOS}
    for documento in PASTA.glob("*/*.md"):
        if documento in gerados:
            continue
        assert re.search(r"\*Atualizado em \d{2}/\d{2}/\d{4}\.\*", documento.read_text(encoding="utf-8")), (
            documento.name
        )


# --- A página navegável (X2, 16/11/2026) ----------------------------------------------------------
# O HTML e o PDF saem dos mesmos .md. A página tem menu com os 24 documentos, e os códigos citados
# no texto (RN05, ADR-013, `usar/faq.md`) levam até onde a coisa está definida.


@pytest.fixture(scope="module")
def pagina(gerador):
    return gerador.montar_html()


def test_x2_pagina_nao_depende_de_caminho_deste_computador(pagina):
    assert "file://" not in pagina and str(RAIZ) not in pagina
    assert "../../frontend/fontes/" in pagina  # as fontes do painel, por caminho relativo


def test_x2_pagina_nao_busca_nada_na_internet(pagina):
    assert not re.search(r"""(?:src|href)=["']https?://""", pagina)


def test_x2_todo_link_interno_aponta_para_algo_que_existe(pagina):
    ids = set(re.findall(r'\bid="([^"]+)"', pagina))
    destinos = set(re.findall(r'href="#([^"]+)"', pagina))
    assert destinos and destinos <= ids, sorted(destinos - ids)[:10]
    assert len(ids) == len(re.findall(r'\bid="([^"]+)"', pagina)), "id repetido na página"


def test_x2_menu_tem_os_24_documentos_com_a_situacao_do_indice(pagina):
    menu = pagina.split('<nav id="menu"')[1].split("</nav>")[0]
    assert len(re.findall(r'class="menu__doc"', menu)) == 24
    mapa = pagina.split('<div class="mapa">')[1].split("</section>")[0]  # depois da legenda
    assert len(re.findall(r'class="mapa__doc', mapa)) == 24
    assert mapa.count("Gerado do código") == 4 and "Parcial" in mapa


def test_x2_codigo_de_regra_adr_e_documento_citados_viram_link(gerador, pagina):
    assert '<tr id="RN11">' in pagina and 'id="ADR-013"' in pagina
    html = gerador.markdown_para_html("A perda não entra (RN11), ver ADR-013 e `usar/faq.md`.")
    assert 'href="#RN11"' in html and 'href="#ADR-013"' in html and 'href="#usar-faq"' in html
    assert 'href="#RNF06"' not in gerador.markdown_para_html("Leve no computador antigo (RNF06).")


def test_x2_regra_nao_aponta_para_si_mesma_na_linha_que_a_define(pagina):
    linha = pagina.split('<tr id="RN11">')[1].split("</tr>")[0]
    assert 'href="#RN11"' not in linha


def test_x2_ficha_da_capa_sai_dos_proprios_documentos(gerador):
    ficha = gerador.ficha()
    assert ficha["Regras de negócio"] == "16" and ficha["Tabelas"] == "14"
    assert ficha["Versão do sistema"] == "0.4.0"
    assert int(ficha["Endereços da API"]) >= 20

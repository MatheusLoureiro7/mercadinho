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

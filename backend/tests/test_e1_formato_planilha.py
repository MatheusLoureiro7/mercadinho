"""
Tarefa E1 — formato da planilha de vendas do caixa (decisão D01 = Excel; grupo, 05/11/2026).

O formato está em docs/FORMATO-PLANILHA-CAIXA.md e o exemplo em docs/exemplos/. Estes testes
garantem que o exemplo segue o formato documentado — é ele que o importador (E3) vai ler nos
testes e na demonstração — e que o exemplo exercita os dois caminhos da operação 04, passo 6:
linha que casa com um produto cadastrado e linha que não casa (fica pendente).
"""

import json
import unicodedata
from datetime import date, datetime, time
from pathlib import Path

import pytest
from openpyxl import load_workbook

RAIZ = Path(__file__).resolve().parents[2]
FORMATO = RAIZ / "docs" / "FORMATO-PLANILHA-CAIXA.md"
EXEMPLO = RAIZ / "docs" / "exemplos" / "vendas-2026-11-05.xlsx"
DEMONSTRACAO = RAIZ / "backend" / "comum" / "fixtures" / "demonstracao.json"

COLUNAS = ["Cupom", "Data", "Hora", "Produto", "Quantidade", "Preço unitário", "Pagamento"]


def _simples(texto: str) -> str:
    """Nome comparado sem maiúscula, acento nem espaço a mais (decisão L05)."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.lower().split())


@pytest.fixture(scope="module")
def linhas():
    aba = load_workbook(EXEMPLO, read_only=True).worksheets[0]
    cabecalho, *resto = aba.iter_rows(values_only=True)
    return list(cabecalho), [dict(zip(cabecalho, linha, strict=True)) for linha in resto]


def test_e1_o_documento_define_as_sete_colunas():
    texto = FORMATO.read_text(encoding="utf-8")
    for coluna in COLUNAS:
        assert f"**{coluna}**" in texto


def test_e1_exemplo_tem_o_cabecalho_do_documento(linhas):
    cabecalho, _ = linhas
    assert cabecalho == COLUNAS


def test_e1_exemplo_e_de_um_dia_so(linhas):
    _, dados = linhas
    assert {
        linha["Data"].date() if isinstance(linha["Data"], datetime) else linha["Data"] for linha in dados
    } == {date(2026, 11, 5)}


def test_e1_exemplo_tem_os_campos_obrigatorios_em_cada_linha(linhas):
    _, dados = linhas
    for linha in dados:
        assert linha["Cupom"] and linha["Produto"]
        assert isinstance(linha["Hora"], time)
        assert linha["Quantidade"] > 0
        assert linha["Preço unitário"] >= 0


def test_e1_exemplo_tem_cupom_com_mais_de_um_item_e_quilo_fracionado(linhas):
    _, dados = linhas
    cupons = [linha["Cupom"] for linha in dados]
    assert any(cupons.count(c) > 1 for c in cupons)
    assert any(linha["Quantidade"] != int(linha["Quantidade"]) for linha in dados)


def test_e1_exemplo_tem_linha_que_casa_e_linha_que_nao_casa_com_o_cadastro(linhas):
    _, dados = linhas
    cadastrados = {
        _simples(o["fields"]["nome"])
        for o in json.loads(DEMONSTRACAO.read_text(encoding="utf-8"))
        if o["model"] == "cadastro.produto"
    }
    casam = [linha["Produto"] for linha in dados if _simples(linha["Produto"]) in cadastrados]
    nao_casam = [linha["Produto"] for linha in dados if _simples(linha["Produto"]) not in cadastrados]
    assert "Feijao carioca 1 kg" in casam  # sem acento na planilha, "Feijão" no cadastro
    assert nao_casam == ["Leite integral 1 L"]  # fica pendente e não trava as demais

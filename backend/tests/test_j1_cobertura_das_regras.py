"""
Tarefa J1 — testes automatizados de todas as regras.

"J1 não é para deixar para o fim. Escreva o teste junto com cada regra; J1 é o fechamento e a
cobertura que faltou, não o começo." (docs/ROTEIRO.md)

1. Guarda: toda regra de docs/REGRAS-NEGOCIO.md tem pelo menos um teste com o código dela no nome
   (CLAUDE.md: "Nomeie o teste pelo código da regra") — menos as que ainda não existem no código,
   listadas em AINDA_SEM_CODIGO com o motivo. Implementar uma delas obriga a tirá-la da lista, e o
   teste passa a cobrar.
2. Exemplos literais da Apostila I que faltavam (o resto está no teste da tarefa de cada regra).
"""

import re
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from cadastro.models import Categoria, Produto
from estoque.fifo import lotes_em_ordem_de_validade
from estoque.models import Lote

RAIZ = Path(__file__).resolve().parents[2]
TESTES = Path(__file__).resolve().parent

# Regras que ainda não têm código: o teste delas nasce com a tarefa que as implementa.
AINDA_SEM_CODIGO = {
    "RN08": "ponto de pedido e aviso de ruptura — G3/H3, espera a D01",
    "RN09": "histórico mínimo para prever — G4, espera a D01",
    "RN10": "produtos que não podem faltar no fim de semana — H3, espera a D01 (e a L03, feriados)",
}


def _regras_da_especificacao() -> list[str]:
    texto = (RAIZ / "docs" / "REGRAS-NEGOCIO.md").read_text(encoding="utf-8")
    return sorted(set(re.findall(r"^\| (RN\d{2}) \|", texto, flags=re.MULTILINE)))


def _testes_por_regra() -> dict[str, set[str]]:
    achados: dict[str, set[str]] = {}
    for arquivo in TESTES.glob("test_*.py"):
        for nome in re.findall(r"^def (test_\w+)", arquivo.read_text(encoding="utf-8"), flags=re.MULTILINE):
            for numero in re.findall(r"rn(\d{2})", nome):
                achados.setdefault(f"RN{numero}", set()).add(f"{arquivo.name}::{nome}")
    return achados


def test_j1_a_especificacao_tem_as_16_regras():
    assert _regras_da_especificacao() == [f"RN{n:02d}" for n in range(1, 17)]


@pytest.mark.parametrize("regra", [f"RN{n:02d}" for n in range(1, 17)])
def test_j1_toda_regra_com_codigo_tem_teste_com_o_nome_dela(regra):
    testes = _testes_por_regra().get(regra, set())
    if regra in AINDA_SEM_CODIGO:
        assert not testes, (
            f"{regra} já tem teste ({sorted(testes)[:3]}): tire-a de AINDA_SEM_CODIGO — "
            f"ela deixou de ser '{AINDA_SEM_CODIGO[regra]}'."
        )
    else:
        assert testes, f"{regra} tem código e nenhum teste com 'rn{regra[2:]}' no nome."


# ------------------------------------------------------------------------------------------------
# RN02 — o exemplo literal da Apostila I
# ------------------------------------------------------------------------------------------------

HOJE = date(2026, 9, 21)


@pytest.fixture
def presunto(db):
    frios = Categoria.objects.create(nome="Frios", perecivel_padrao=True)
    return Produto.objects.create(
        nome="Presunto", categoria=frios, unidade_medida="KG", perecivel=True, durabilidade_dias=7
    )


def _lote(produto, quantidade, validade, entrada):
    return Lote.objects.create(
        produto=produto,
        quantidade_inicial=Decimal(quantidade),
        quantidade_atual=Decimal(quantidade),
        data_entrada=entrada,
        data_validade=validade,
    )


def test_rn02_exemplo_da_apostila_sai_o_de_28_09_mesmo_com_o_de_05_10_mais_a_mao(presunto):
    """
    "Dois lotes de presunto, um vence 28/09 e outro 05/10. Venda de 2 kg baixa do lote de 28/09,
    mesmo que o de 05/10 esteja mais à mão." O de 05/10 entrou ANTES (id menor, entrada mais
    antiga): ordenar por id ou por data de entrada daria o lote errado.
    """
    mais_a_mao = _lote(presunto, "3", date(2026, 10, 5), entrada=HOJE - timedelta(days=5))
    vence_antes = _lote(presunto, "3", date(2026, 9, 28), entrada=HOJE - timedelta(days=1))

    ordem_da_venda = list(lotes_em_ordem_de_validade(presunto, hoje=HOJE, incluir_vencidos=False))

    assert ordem_da_venda == [vence_antes, mais_a_mao]
    assert mais_a_mao.pk < vence_antes.pk and mais_a_mao.data_entrada < vence_antes.data_entrada


# ------------------------------------------------------------------------------------------------
# Falha intermitente dos testes de tela (registrada em 08/10) — causa achada na J1
# ------------------------------------------------------------------------------------------------
# Rastro do navegador numa falha: ao abrir a Consulta, o Chromium pediu seis módulos JS no mesmo
# milissegundo e um voltou "net::ERR_SOCKET_NOT_CONNECTED". Com um módulo faltando, nenhum roda: a
# tela aparece sem menu e não chama a API. Causa: o servidor padrão do Python aceita só 5 conexões
# na fila (request_queue_size = 5); uma rajada maior com a máquina ocupada estoura a fila. Vale
# para o servir.py de verdade (o painel de quem roda o sistema), não só para os testes.

RAJADA = 64


def _rajada(endereco: str, caminho: str) -> list[str]:
    import http.client
    import threading
    import urllib.parse

    partes = urllib.parse.urlsplit(endereco)
    largada = threading.Barrier(RAJADA)
    falhas: list[str] = []

    def pedir():
        try:
            largada.wait()
            conexao = http.client.HTTPConnection(partes.hostname, partes.port, timeout=10)
            conexao.request("GET", caminho)
            resposta = conexao.getresponse()
            resposta.read()
            conexao.close()
            if resposta.status >= 500:
                falhas.append(str(resposta.status))
        except OSError as erro:
            falhas.append(type(erro).__name__)

    pedidos = [threading.Thread(target=pedir) for _ in range(RAJADA)]
    for pedido in pedidos:
        pedido.start()
    for pedido in pedidos:
        pedido.join()
    return falhas


def test_j1_servir_aguenta_a_rajada_de_modulos_de_uma_tela():
    from tests.conftest import _no_fundo, carregar_servir

    servidor = carregar_servir().criar_servidor(porta=0, endereco_api="http://127.0.0.1:9")
    try:
        assert _rajada(_no_fundo(servidor), "/js/situacao.js") == []
    finally:
        servidor.shutdown()
        servidor.server_close()


def test_j1_api_dos_testes_de_tela_aguenta_a_rajada(painel):
    """A API dos testes de tela (conftest.painel) tem o mesmo limite; os pedidos passam pelo painel."""
    assert _rajada(painel, "/api/sessoes/atual/") == []  # 401 sem login: o que importa é conectar

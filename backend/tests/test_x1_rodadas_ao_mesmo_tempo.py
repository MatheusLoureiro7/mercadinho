"""
X1, item 16 — duas rodadas ao mesmo tempo (o cron das 03h00 e alguém rodando o comando à mão).

A importação e os avisos conferem ("o dia já entrou?", "já avisei hoje?") e depois gravam. Sem trava,
as duas conferem juntas, as duas ouvem "não" e as duas gravam. Aqui a primeira é atrasada de
propósito no meio da gravação, e a segunda chega nesse meio-tempo: com a trava do PostgreSQL
(pg_advisory_xact_lock), a segunda espera e encontra o que a primeira gravou.
"""

import threading
import time as relogio
from datetime import date, time
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.db import connection
from openpyxl import Workbook

from alertas import ruptura
from alertas.models import Alerta
from cadastro.models import Categoria, Fornecedor, Produto, Usuario
from estoque.models import Movimentacao
from previsao.models import PrevisaoProduto
from tests.conftest import _regravar_parametros_iniciais
from vendas import importacao
from vendas.models import Venda

DIA = date(2026, 11, 5)


@pytest.fixture(autouse=True)
def parametros(transactional_db):
    """O banco de verdade (sem transação de teste) começa e termina com os parâmetros da L21."""
    _regravar_parametros_iniciais()
    yield
    _regravar_parametros_iniciais()


def _em_paralelo(*tarefas):
    """Roda cada tarefa numa linha de execução (cada uma com a sua conexão) e devolve o que deu."""
    resultados = [None] * len(tarefas)

    def rodar(posicao, tarefa):
        try:
            resultados[posicao] = tarefa()
        except Exception as erro:
            resultados[posicao] = erro
        finally:
            connection.close()

    linhas = []
    for posicao, tarefa in enumerate(tarefas):
        linha = threading.Thread(target=rodar, args=(posicao, tarefa))
        linha.start()
        linhas.append(linha)
        relogio.sleep(0.2)  # a segunda chega com a primeira no meio da gravação
    for linha in linhas:
        linha.join(timeout=30)
    return resultados


def _atrasar_a_primeira(funcao):
    chamadas = []

    def atrasada(*args, **kwargs):
        chamadas.append(1)
        resultado = funcao(*args, **kwargs)
        if len(chamadas) == 1:
            relogio.sleep(0.8)
        return resultado

    return atrasada


def _planilha(pasta, nome):
    livro = Workbook()
    livro.active.append(["Cupom", "Data", "Hora", "Produto", "Quantidade", "Preço unitário", "Pagamento"])
    livro.active.append([1, DIA, time(8, 14), "Feijão carioca 1 kg", 1, 8.99, "PIX"])
    caminho = pasta / nome
    livro.save(caminho)
    return caminho


def test_x1_duas_importacoes_da_mesma_venda_ao_mesmo_tempo_nao_duplicam(transactional_db, tmp_path):
    secos = Categoria.objects.create(nome="Secos e molhados")
    Produto.objects.create(categoria=secos, nome="Feijão carioca 1 kg", unidade_medida="PCT")
    primeira, segunda = _planilha(tmp_path, "vendas.xlsx"), _planilha(tmp_path, "copia.xlsx")

    with patch.object(importacao, "_gravar", _atrasar_a_primeira(importacao._gravar)):
        resultados = _em_paralelo(
            lambda: importacao.importar_planilha(primeira), lambda: importacao.importar_planilha(segunda)
        )

    assert Venda.objects.count() == 1
    assert isinstance(resultados[1], importacao.ArquivoJaImportado), resultados


def test_x1_dois_avisos_de_vai_acabar_ao_mesmo_tempo_nao_duplicam(transactional_db):
    Usuario.objects.create_user(login="joao", senha="Mercado#2026", nome="Sr. João", papel="DONO")
    acougue = Categoria.objects.create(nome="Açougue")
    granja = Fornecedor.objects.create(nome="Granja Boa Vista", prazo_entrega_dias=2)
    frango = Produto.objects.create(
        categoria=acougue, nome="Frango resfriado 1 kg", unidade_medida="KG", fornecedor_padrao=granja
    )
    Movimentacao.objects.create(produto=frango, tipo="ENTRADA", quantidade=Decimal("6"))
    PrevisaoProduto.objects.create(
        produto=frango,
        consumo_medio_diario=Decimal("4"),
        dias_ate_acabar=Decimal("1.5"),
        ponto_pedido=Decimal("10"),
        sugestao_compra=Decimal("30"),
        calculado_em="2026-11-11T03:00:00-03:00",
    )

    with patch.object(ruptura, "criar_aviso", _atrasar_a_primeira(ruptura.criar_aviso)):
        resultados = _em_paralelo(ruptura.gerar_avisos_de_ruptura, ruptura.gerar_avisos_de_ruptura)

    assert Alerta.objects.filter(produto=frango).count() == 1, resultados

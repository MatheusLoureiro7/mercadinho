"""
Importação das vendas do caixa — tarefa E3. Operação 04 da Apostila IV (RN01, RN02, RN16).

    importacao = importar_planilha(caminho)

1. Registra a importação como PENDENTE (passo 2) e lê a planilha (passo 3).
2. Cada cupom vira uma `venda`; cada linha, um `item_venda` (passo 7). O valor total é a soma de
   quantidade × preço unitário dos itens (E1: a planilha não traz total).
3. O produto é procurado pelo nome do cadastro, sem diferença de maiúscula, acento nem espaço a mais
   (decisão L05). Linha que não casa fica com o item sem produto, pendente de revisão, e NÃO trava
   as demais (passo 6). Nome que existe em duas categorias também fica pendente: não se chuta.
4. Linha que casou baixa o estoque (passo 8): movimentação VENDA na hora da venda, saindo do lote
   de validade mais próxima (RN02), sem lote vencido NO DIA DA VENDA (RN16) — a importação roda às
   03h00 do dia seguinte, e o lote que venceu no dia ainda valia na hora em que foi vendido.
5. Venda maior que o estoque registrado (decisão do grupo, 05/11/2026): a venda já aconteceu e é
   gravada inteira; o que não coube nos lotes vira movimentação VENDA sem lote, e o saldo fica
   negativo na consulta — é a contagem do estoque que está errada, e o consumo da previsão é o real.
6. Situação (passo 9): OK, se toda linha foi lida e casou; PARCIAL, se alguma ficou pendente ou com
   erro; ERRO, se a planilha não abriu ou se a gravação falhou — e aí nada fica gravado.

`linhas_erro` conta as linhas que NÃO baixaram o estoque: as com erro de leitura e as pendentes.
"""

import logging
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from django.db import transaction
from django.utils import timezone

from cadastro.models import Produto
from comum.busca import sem_acento
from estoque.fifo import lotes_em_ordem_de_validade
from estoque.models import Movimentacao
from vendas.leitor import ArquivoIlegivel, LeitorDeArquivoDoCaixa, LeitorDePlanilhaExcel, LinhaDeVenda
from vendas.models import ImportacaoPdv, ItemVenda, Venda

logger = logging.getLogger("mercadinho.importacao")

CENTAVO = Decimal("0.01")
ORIGEM = "IMPORTACAO_PDV"


class ArquivoJaImportado(Exception):
    """A mesma planilha já entrou (OK ou PARCIAL): importar de novo duplicaria as vendas."""


def _nome_simples(nome: str) -> str:
    return " ".join(sem_acento(nome).split())


def _produtos_por_nome() -> dict[str, Produto | None]:
    """Nome simplificado → produto; None quando o nome existe em mais de uma categoria."""
    produtos: dict[str, Produto | None] = {}
    for produto in Produto.objects.all():
        chave = _nome_simples(produto.nome)
        produtos[chave] = None if chave in produtos else produto
    return produtos


def _baixar_do_estoque(produto: Produto, linha: LinhaDeVenda) -> None:
    dia_da_venda = timezone.localtime(linha.data_hora).date()
    lotes = lotes_em_ordem_de_validade(produto, hoje=dia_da_venda, incluir_vencidos=False).select_for_update()
    restante = linha.quantidade
    for lote in lotes:
        if restante <= 0:
            break
        baixa = min(restante, lote.quantidade_atual)
        lote.quantidade_atual -= baixa
        lote.save(update_fields=["quantidade_atual"])
        _movimentacao(produto, linha, baixa, lote)
        restante -= baixa
    if restante > 0:
        _movimentacao(produto, linha, restante, None)


def _movimentacao(produto, linha, quantidade, lote):
    Movimentacao.objects.create(
        produto=produto,
        lote=lote,
        tipo=Movimentacao.Tipo.VENDA,
        quantidade=quantidade,
        preco_unitario=linha.preco,
        data_hora=linha.data_hora,
        origem=ORIGEM,
    )


def _gravar(linhas: list[LinhaDeVenda]) -> int:
    """Grava vendas, itens e baixas; devolve quantas linhas ficaram pendentes (sem produto)."""
    produtos = _produtos_por_nome()
    por_cupom: dict[str, list[LinhaDeVenda]] = defaultdict(list)
    for linha in linhas:
        por_cupom[linha.cupom].append(linha)

    pendentes = 0
    for itens in por_cupom.values():
        primeira = itens[0]
        total = sum((item.quantidade * item.preco for item in itens), Decimal(0))
        venda = Venda.objects.create(
            data_hora=primeira.data_hora,
            valor_total=total.quantize(CENTAVO, rounding=ROUND_HALF_UP),
            forma_pagamento=primeira.pagamento,
        )
        for item in itens:
            produto = produtos.get(_nome_simples(item.produto))
            ItemVenda.objects.create(
                venda=venda, produto=produto, quantidade=item.quantidade, preco=item.preco
            )
            if produto is None:
                pendentes += 1
            else:
                _baixar_do_estoque(produto, item)
    return pendentes


def importar_planilha(caminho: Path, leitor: LeitorDeArquivoDoCaixa | None = None) -> ImportacaoPdv:
    caminho = Path(caminho)
    if ImportacaoPdv.objects.filter(
        arquivo_nome=caminho.name, status__in=[ImportacaoPdv.Status.OK, ImportacaoPdv.Status.PARCIAL]
    ).exists():
        raise ArquivoJaImportado(f"A planilha {caminho.name} já foi importada.")

    importacao = ImportacaoPdv.objects.create(arquivo_nome=caminho.name, data_referencia=timezone.localdate())

    try:
        leitura = (leitor or LeitorDePlanilhaExcel()).ler(caminho)
    except ArquivoIlegivel as erro:
        logger.warning("Importação %s com erro: %s", caminho.name, erro)
        return _concluir(importacao, ImportacaoPdv.Status.ERRO)

    lidas = len(leitura.linhas) + len(leitura.erros)
    for erro in leitura.erros:
        logger.warning("%s, linha %s: %s", caminho.name, erro.numero_linha, erro.mensagem)
    if leitura.linhas:
        importacao.data_referencia = timezone.localtime(leitura.linhas[0].data_hora).date()

    try:
        with transaction.atomic():
            pendentes = _gravar(leitura.linhas)
    except Exception:
        logger.exception("Importação %s interrompida; nada foi gravado.", caminho.name)
        _concluir(importacao, ImportacaoPdv.Status.ERRO, lidas=lidas, com_erro=lidas)
        raise

    com_erro = len(leitura.erros) + pendentes
    situacao = ImportacaoPdv.Status.OK if com_erro == 0 else ImportacaoPdv.Status.PARCIAL
    return _concluir(importacao, situacao, lidas=lidas, com_erro=com_erro)


def _concluir(
    importacao: ImportacaoPdv, situacao: str, *, lidas: int = 0, com_erro: int = 0
) -> ImportacaoPdv:
    importacao.status = situacao
    importacao.linhas_lidas = lidas
    importacao.linhas_erro = com_erro
    importacao.processado_em = timezone.now()
    importacao.save()
    return importacao

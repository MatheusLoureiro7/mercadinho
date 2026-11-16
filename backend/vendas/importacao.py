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
7. Importar duas vezes (decisão do grupo, 16/11/2026, revisão X1 item 1): as vendas são reconhecidas
   pelo DIA, não pelo nome do arquivo. Linha de um dia que já entrou (OK ou PARCIAL) é ignorada; se
   todas forem assim, a planilha é recusada sem deixar registro (`ArquivoJaImportado`).

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
    """Os dias de venda da planilha já entraram (OK ou PARCIAL): importar de novo duplicaria as vendas."""


def _dias_ja_importados(dias: set) -> set:
    return set(
        ImportacaoPdv.objects.filter(
            data_referencia__in=dias, status__in=[ImportacaoPdv.Status.OK, ImportacaoPdv.Status.PARCIAL]
        ).values_list("data_referencia", flat=True)
    )


def _dia(linha: LinhaDeVenda):
    return timezone.localtime(linha.data_hora).date()


def _nome_simples(nome: str) -> str:
    return " ".join(sem_acento(nome).split())


def _produtos_por_nome() -> dict[str, Produto | None]:
    """Nome simplificado → produto; None quando o nome existe em mais de uma categoria."""
    produtos: dict[str, Produto | None] = {}
    for produto in Produto.objects.all():
        chave = _nome_simples(produto.nome)
        produtos[chave] = None if chave in produtos else produto
    return produtos


def baixar_venda_do_estoque(produto: Produto, quantidade: Decimal, preco: Decimal | None, data_hora) -> None:
    """Passo 8. Também usada ao casar depois um item pendente (E4, `vendas.conciliacao`)."""
    dia_da_venda = timezone.localtime(data_hora).date()
    lotes = lotes_em_ordem_de_validade(produto, hoje=dia_da_venda, incluir_vencidos=False).select_for_update()
    restante = quantidade
    for lote in lotes:
        if restante <= 0:
            break
        baixa = min(restante, lote.quantidade_atual)
        lote.quantidade_atual -= baixa
        lote.save(update_fields=["quantidade_atual"])
        _movimentacao(produto, baixa, preco, data_hora, lote)
        restante -= baixa
    if restante > 0:
        _movimentacao(produto, restante, preco, data_hora, None)


def _movimentacao(produto, quantidade, preco, data_hora, lote):
    Movimentacao.objects.create(
        produto=produto,
        lote=lote,
        tipo=Movimentacao.Tipo.VENDA,
        quantidade=quantidade,
        preco_unitario=preco,
        data_hora=data_hora,
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
                baixar_venda_do_estoque(produto, item.quantidade, item.preco, item.data_hora)
    return pendentes


def importar_planilha(caminho: Path, leitor: LeitorDeArquivoDoCaixa | None = None) -> ImportacaoPdv:
    caminho = Path(caminho)
    importacao = ImportacaoPdv.objects.create(arquivo_nome=caminho.name, data_referencia=timezone.localdate())

    try:
        leitura = (leitor or LeitorDePlanilhaExcel()).ler(caminho)
    except ArquivoIlegivel as erro:
        logger.warning("Importação %s com erro: %s", caminho.name, erro)
        return _concluir(importacao, ImportacaoPdv.Status.ERRO)

    ja_importados = _dias_ja_importados({_dia(linha) for linha in leitura.linhas})
    linhas = [linha for linha in leitura.linhas if _dia(linha) not in ja_importados]
    if leitura.linhas and not linhas:
        importacao.delete()
        raise ArquivoJaImportado(f"As vendas da planilha {caminho.name} já tinham entrado.")

    lidas = len(linhas) + len(leitura.erros)
    for erro in leitura.erros:
        logger.warning("%s, linha %s: %s", caminho.name, erro.numero_linha, erro.mensagem)
    if linhas:
        importacao.data_referencia = _dia(linhas[0])

    try:
        with transaction.atomic():
            pendentes = _gravar(linhas)
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

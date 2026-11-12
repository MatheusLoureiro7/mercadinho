"""
Inventário de partida — tarefa J3. Formato: docs/FORMATO-PLANILHA-CONTAGEM.md.

    resultado = carregar_contagem(caminho)

Decisão do grupo (12/11/2026): a contagem física entra **como entrada de mercadoria**, pelo mesmo
serviço da tela de Entrada (`registrar_entrada`, operação 02): cada linha contada vira um lote com a
sua movimentação ENTRADA, `origem = 'INVENTARIO'` (RN01). O perecível ganha validade (RN04: a da
embalagem ou entrada + durabilidade; validade que já passou é recusada), e por isso já entra no
aviso de validade (RN05) e na saída pelo lote que vence primeiro (RN02).

Tudo ou nada, como a carga dos produtos (J2): linha recusada não deixa gravar nada, e o resultado
traz todas (linha no Excel e coluna). A contagem é de partida: produto que já tinha estoque
registrado antes desta carga é mantido — rodar de novo não lança duas vezes.
"""

import re
import zipfile
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.db import transaction
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from cadastro.models import Produto
from comum.busca import sem_acento
from comum.erros import ErroDeRegraDeNegocio
from estoque.entrada import registrar_entrada
from estoque.models import Movimentacao

ABA = "Contagem"
ORIGEM = "INVENTARIO"
OBRIGATORIAS = ["Produto", "Quantidade contada"]
OPCIONAIS = ["Categoria", "Validade", "Custo unitário"]


class PlanilhaIlegivel(Exception):
    """A planilha não abre, não tem a aba Contagem ou falta coluna obrigatória: nada é lançado."""


@dataclass(frozen=True)
class ErroNaPlanilha:
    aba: str
    linha: int
    coluna: str
    mensagem: str


@dataclass
class Resultado:
    lotes: int = 0
    zerados: int = 0  # linhas com quantidade zero: não há o que lançar
    mantidos: int = 0  # linhas de produto que já tinha estoque antes da carga
    erros: list[ErroNaPlanilha] = field(default_factory=list)


class _Recusa(Exception):
    def __init__(self, coluna, mensagem):
        super().__init__(mensagem)
        self.coluna, self.mensagem = coluna, mensagem


class _Desfazer(Exception):
    pass


def _simples(texto) -> str:
    return " ".join(sem_acento(str(texto)).split())


def _vazio(valor) -> bool:
    return valor is None or (isinstance(valor, str) and not valor.strip())


def _numero(valor, coluna: str, casas: int) -> Decimal:
    try:
        numero = Decimal(str(valor).strip().replace(",", "."))
    except InvalidOperation:
        raise _Recusa(coluna, "Escreva só o número, por exemplo 2,5.") from None
    if not numero.is_finite() or numero < 0:
        raise _Recusa(coluna, "Escreva um número que não seja negativo, por exemplo 2,5.")
    if -numero.as_tuple().exponent > casas:
        raise _Recusa(coluna, f"Use no máximo {casas} casas depois da vírgula.")
    return numero


def _data(valor) -> date:
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    if isinstance(valor, str) and re.fullmatch(r"\s*\d{2}/\d{2}/\d{4}\s*", valor):
        try:
            return datetime.strptime(valor.strip(), "%d/%m/%Y").date()
        except ValueError:
            pass
    raise _Recusa("Validade", "Escreva a data como na embalagem: dd/mm/aaaa.")


def _linhas(caminho: Path) -> list[tuple[int, dict]]:
    try:
        livro = load_workbook(caminho, read_only=True, data_only=True)
    except (InvalidFileException, zipfile.BadZipFile, KeyError, OSError) as erro:
        raise PlanilhaIlegivel(f"A planilha {Path(caminho).name} não abre no formato .xlsx.") from erro
    try:
        folha = next((f for f in livro.worksheets if _simples(f.title) == _simples(ABA)), None)
        if folha is None:
            raise PlanilhaIlegivel(f"A planilha não tem a aba {ABA}.")
        linhas = folha.iter_rows(values_only=True)
        cabecalho = [_simples(c) if c is not None else "" for c in next(linhas, ())]
        posicao = {
            c: cabecalho.index(_simples(c)) for c in OBRIGATORIAS + OPCIONAIS if _simples(c) in cabecalho
        }
        faltam = [c for c in OBRIGATORIAS if c not in posicao]
        if faltam:
            raise PlanilhaIlegivel(f"Falta na aba {ABA} a coluna: {', '.join(faltam)}.")
        return [
            (numero, {c: linha[i] if i < len(linha) else None for c, i in posicao.items()})
            for numero, linha in enumerate(linhas, start=2)
            if any(not _vazio(valor) for valor in linha)
        ]
    finally:
        livro.close()


def _produto(valores: dict, por_nome: dict[str, list[Produto]]) -> Produto:
    nome = valores.get("Produto")
    if _vazio(nome):
        raise _Recusa("Produto", "Escreva o nome do produto.")
    candidatos = por_nome.get(_simples(nome), [])
    if not _vazio(valores.get("Categoria")):
        candidatos = [p for p in candidatos if _simples(p.categoria.nome) == _simples(valores["Categoria"])]
    if not candidatos:
        raise _Recusa(
            "Produto", f"O produto {str(nome).strip()!r} não está no cadastro. Cadastre antes (J2)."
        )
    if len(candidatos) > 1:
        raise _Recusa(
            "Produto", "Há produto com esse nome em mais de uma categoria: preencha a coluna Categoria."
        )
    return candidatos[0]


def carregar_contagem(caminho: Path) -> Resultado:
    linhas = _linhas(Path(caminho))
    resultado = Resultado()
    por_nome = defaultdict(list)
    for produto in Produto.objects.select_related("categoria"):
        por_nome[_simples(produto.nome)].append(produto)
    ja_tinham_estoque = set(Movimentacao.objects.values_list("produto_id", flat=True).distinct())

    try:
        with transaction.atomic():
            for numero, valores in linhas:
                try:
                    produto = _produto(valores, por_nome)
                    if _vazio(valores.get("Quantidade contada")):
                        raise _Recusa("Quantidade contada", "Escreva quanto foi contado (zero, se não tem).")
                    quantidade = _numero(valores["Quantidade contada"], "Quantidade contada", casas=3)
                    validade = None if _vazio(valores.get("Validade")) else _data(valores["Validade"])
                    custo = (
                        None
                        if _vazio(valores.get("Custo unitário"))
                        else _numero(valores["Custo unitário"], "Custo unitário", casas=2)
                    )
                    if produto.pk in ja_tinham_estoque:
                        resultado.mantidos += 1
                        continue
                    if quantidade == 0:
                        resultado.zerados += 1
                        continue
                    try:
                        registrar_entrada(
                            produto=produto,
                            quantidade=quantidade,
                            usuario=None,
                            custo_unitario=custo,
                            data_validade=validade,
                            origem=ORIGEM,
                        )
                    except ErroDeRegraDeNegocio as recusa:  # RN04: validade que já passou
                        raise _Recusa("Validade", recusa.mensagem) from recusa
                    resultado.lotes += 1
                except _Recusa as recusa:
                    resultado.erros.append(ErroNaPlanilha(ABA, numero, recusa.coluna, recusa.mensagem))
            if resultado.erros:
                raise _Desfazer
    except _Desfazer:
        resultado.lotes = 0
    return resultado

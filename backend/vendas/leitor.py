"""
Leitura da planilha de vendas do caixa — tarefa E3. Operação 04, passo 3.

Formato decidido na E1: docs/FORMATO-PLANILHA-CAIXA.md (planilha .xlsx, uma linha por produto
vendido). O importador conversa com a interface `LeitorDeArquivoDoCaixa` (decisão D01): se um dia o
caixa exportar outro formato, troca-se o leitor, não o importador.

Linha com problema não derruba a planilha: vira um `ErroDeLinha` com o número da linha no Excel e
a coluna, e as outras seguem. Só a planilha que não abre, ou sem coluna obrigatória, é ilegível.
"""

import re
import zipfile
from dataclasses import dataclass, field
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Protocol
from zoneinfo import ZoneInfo

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from comum.busca import sem_acento

FUSO_DA_LOJA = ZoneInfo("America/Sao_Paulo")

OBRIGATORIAS = ["Cupom", "Data", "Hora", "Produto", "Quantidade", "Preço unitário"]
OPCIONAIS = ["Pagamento"]


@dataclass(frozen=True)
class LinhaDeVenda:
    numero_linha: int
    cupom: str
    data_hora: datetime
    produto: str
    quantidade: Decimal
    preco: Decimal
    pagamento: str | None


@dataclass(frozen=True)
class ErroDeLinha:
    numero_linha: int
    campo: str
    mensagem: str


@dataclass
class Leitura:
    linhas: list[LinhaDeVenda] = field(default_factory=list)
    erros: list[ErroDeLinha] = field(default_factory=list)


class ArquivoIlegivel(Exception):
    """A planilha não abre ou não tem as colunas obrigatórias: nada dela é importado."""


class LeitorDeArquivoDoCaixa(Protocol):
    def ler(self, caminho: Path) -> Leitura: ...


class _ValorInvalido(Exception):
    pass


def _simples(texto: str) -> str:
    return " ".join(sem_acento(str(texto)).split())


def _vazio(valor) -> bool:
    return valor is None or (isinstance(valor, str) and not valor.strip())


def _texto(valor, *, maximo: int | None = None) -> str:
    if _vazio(valor):
        raise _ValorInvalido("está em branco")
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    texto = " ".join(str(valor).split())
    if maximo and len(texto) > maximo:
        raise _ValorInvalido(f"passa de {maximo} letras")
    return texto


def _numero(valor, *, casas: int, minimo: Decimal, aceita_minimo: bool) -> Decimal:
    if _vazio(valor) or isinstance(valor, bool):
        raise _ValorInvalido("está em branco")
    try:
        numero = Decimal(str(valor).strip().replace(",", "."))
    except InvalidOperation:
        raise _ValorInvalido("não é um número") from None
    if not numero.is_finite():
        raise _ValorInvalido("não é um número")
    if numero < minimo or (numero == minimo and not aceita_minimo):
        raise _ValorInvalido(
            "tem de ser maior que zero" if minimo == 0 and not aceita_minimo else "não pode ser negativo"
        )
    if -numero.as_tuple().exponent > casas:
        raise _ValorInvalido(f"tem mais de {casas} casas depois da vírgula")
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
    raise _ValorInvalido("não é uma data no formato dd/mm/aaaa")


def _hora(valor) -> time:
    if isinstance(valor, datetime):
        return valor.time()
    if isinstance(valor, time):
        return valor
    if isinstance(valor, str) and re.fullmatch(r"\s*\d{1,2}:\d{2}\s*", valor):
        try:
            return datetime.strptime(valor.strip(), "%H:%M").time()
        except ValueError:
            pass
    raise _ValorInvalido("não é uma hora no formato hh:mm")


class LeitorDePlanilhaExcel:
    """Lê a primeira aba da planilha .xlsx; a linha 1 é o cabeçalho."""

    def ler(self, caminho: Path) -> Leitura:
        try:
            livro = load_workbook(caminho, read_only=True, data_only=True)
        except (InvalidFileException, zipfile.BadZipFile, KeyError, OSError) as erro:
            raise ArquivoIlegivel(f"A planilha {Path(caminho).name} não abre no formato .xlsx.") from erro
        try:
            linhas = livro.worksheets[0].iter_rows(values_only=True)
            cabecalho = next(linhas, ())
            posicao = self._posicoes(cabecalho)
            leitura = Leitura()
            for numero_linha, valores in enumerate(linhas, start=2):
                if all(_vazio(v) for v in valores):
                    continue
                self._ler_linha(numero_linha, valores, posicao, leitura)
            return leitura
        finally:
            livro.close()

    @staticmethod
    def _posicoes(cabecalho) -> dict[str, int]:
        achadas = {_simples(nome): i for i, nome in enumerate(cabecalho) if not _vazio(nome)}
        faltam = [coluna for coluna in OBRIGATORIAS if _simples(coluna) not in achadas]
        if faltam:
            raise ArquivoIlegivel(f"Falta na planilha a coluna: {', '.join(faltam)}.")
        return {
            coluna: achadas[_simples(coluna)]
            for coluna in OBRIGATORIAS + OPCIONAIS
            if _simples(coluna) in achadas
        }

    @staticmethod
    def _ler_linha(numero_linha: int, valores, posicao: dict[str, int], leitura: Leitura) -> None:
        def valor(coluna):
            i = posicao.get(coluna)
            return valores[i] if i is not None and i < len(valores) else None

        conversoes = {
            "Cupom": lambda v: _texto(v, maximo=40),
            "Data": _data,
            "Hora": _hora,
            "Produto": lambda v: _texto(v, maximo=120),
            "Quantidade": lambda v: _numero(v, casas=3, minimo=Decimal(0), aceita_minimo=False),
            "Preço unitário": lambda v: _numero(v, casas=2, minimo=Decimal(0), aceita_minimo=True),
        }
        lidos = {}
        for coluna, converter in conversoes.items():
            try:
                lidos[coluna] = converter(valor(coluna))
            except _ValorInvalido as problema:
                leitura.erros.append(ErroDeLinha(numero_linha, coluna, f"{coluna} {problema}."))
                return
        pagamento = valor("Pagamento")
        try:
            pagamento = None if _vazio(pagamento) else _texto(pagamento, maximo=30)
        except _ValorInvalido as problema:
            leitura.erros.append(ErroDeLinha(numero_linha, "Pagamento", f"Pagamento {problema}."))
            return
        leitura.linhas.append(
            LinhaDeVenda(
                numero_linha=numero_linha,
                cupom=lidos["Cupom"],
                data_hora=datetime.combine(lidos["Data"], lidos["Hora"], tzinfo=FUSO_DA_LOJA),
                produto=lidos["Produto"],
                quantidade=lidos["Quantidade"],
                preco=lidos["Preço unitário"],
                pagamento=pagamento,
            )
        )

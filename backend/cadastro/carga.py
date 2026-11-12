"""
Carga inicial dos produtos por planilha — tarefa J2. Formato: docs/FORMATO-PLANILHA-PRODUTOS.md.

    resultado = carregar_planilha(caminho)

Três abas, na ordem do cadastro: Categorias, Fornecedores e Produtos (as duas primeiras são
opcionais quando já estão cadastradas). Cada linha passa pelos MESMOS serializers da API (B2, B3):
nome obrigatório, prazo de entrega, unidade KG/UN/L/PCT (L17), nome único na categoria e RN03
(operação 01). Categoria e fornecedor da aba Produtos são procurados pelo nome, sem diferenciar
maiúscula, acento nem espaço a mais.

Tudo ou nada: se alguma linha for recusada, a transação é desfeita e nada fica gravado; o resultado
traz todas as linhas com problema (aba, número da linha no Excel e coluna). O que já está cadastrado
com o mesmo nome é mantido como está — rodar de novo não duplica nem altera.
"""

import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from django.db import transaction
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from cadastro.models import Categoria, Fornecedor, Produto
from cadastro.serializers import CategoriaSerializer, FornecedorSerializer, ProdutoSerializer
from comum.busca import sem_acento
from comum.erros import ErroDeRegraDeNegocio

# Aba → {coluna da planilha: campo da API}. As obrigatórias são as que a aba não pode deixar de ter.
COLUNAS = {
    "Categorias": {"Categoria": "nome", "Perecível": "perecivel_padrao"},
    "Fornecedores": {
        "Fornecedor": "nome",
        "Prazo de entrega (dias)": "prazo_entrega_dias",
        "Pedido mínimo (R$)": "pedido_minimo",
        "Contato": "contato",
    },
    "Produtos": {
        "Produto": "nome",
        "Categoria": "categoria",
        "Unidade": "unidade_medida",
        "Perecível": "perecivel",
        "Dura quantos dias": "durabilidade_dias",
        "Preço de custo": "preco_custo",
        "Preço de venda": "preco_venda",
        "Estoque mínimo": "estoque_minimo",
        "Fornecedor": "fornecedor_padrao",
        "Não pode faltar no fim de semana": "critico_fim_semana",
    },
}
OBRIGATORIAS = {
    "Categorias": ["Categoria"],
    "Fornecedores": ["Fornecedor", "Prazo de entrega (dias)"],
    "Produtos": ["Produto", "Categoria", "Unidade"],
}
SIM_OU_NAO = {"perecivel_padrao", "perecivel", "critico_fim_semana"}
NUMEROS = {
    "prazo_entrega_dias",
    "pedido_minimo",
    "durabilidade_dias",
    "preco_custo",
    "preco_venda",
    "estoque_minimo",
}


class PlanilhaIlegivel(Exception):
    """A planilha não abre, não tem a aba Produtos ou falta coluna obrigatória: nada é carregado."""


@dataclass(frozen=True)
class ErroNaPlanilha:
    aba: str
    linha: int
    coluna: str
    mensagem: str


@dataclass
class Resultado:
    criados: dict = field(default_factory=lambda: {"categorias": 0, "fornecedores": 0, "produtos": 0})
    mantidos: dict = field(default_factory=lambda: {"categorias": 0, "fornecedores": 0, "produtos": 0})
    erros: list[ErroNaPlanilha] = field(default_factory=list)


class _Desfazer(Exception):
    pass


class _Recusa(Exception):
    def __init__(self, coluna, mensagem):
        super().__init__(mensagem)
        self.coluna, self.mensagem = coluna, mensagem


def _simples(texto) -> str:
    return " ".join(sem_acento(str(texto)).split())


def _vazio(valor) -> bool:
    return valor is None or (isinstance(valor, str) and not valor.strip())


# ------------------------------------------------------------------------------------------ Leitura


def _abas(caminho: Path) -> dict[str, list[tuple[int, dict]]]:
    """Aba → [(número da linha no Excel, {coluna da planilha: valor})], sem as linhas em branco."""
    try:
        livro = load_workbook(caminho, read_only=True, data_only=True)
    except (InvalidFileException, zipfile.BadZipFile, KeyError, OSError) as erro:
        raise PlanilhaIlegivel(f"A planilha {Path(caminho).name} não abre no formato .xlsx.") from erro
    try:
        por_nome = {_simples(folha.title): folha for folha in livro.worksheets}
        if _simples("Produtos") not in por_nome:
            raise PlanilhaIlegivel("A planilha não tem a aba Produtos.")
        abas = {}
        for aba, colunas in COLUNAS.items():
            folha = por_nome.get(_simples(aba))
            if folha is None:
                abas[aba] = []
                continue
            linhas = folha.iter_rows(values_only=True)
            cabecalho = [_simples(c) if c is not None else "" for c in next(linhas, ())]
            posicao = {
                coluna: cabecalho.index(_simples(coluna))
                for coluna in colunas
                if _simples(coluna) in cabecalho
            }
            faltam = [coluna for coluna in OBRIGATORIAS[aba] if coluna not in posicao]
            if faltam:
                raise PlanilhaIlegivel(f"Falta na aba {aba} a coluna: {', '.join(faltam)}.")
            abas[aba] = [
                (numero, {coluna: linha[i] if i < len(linha) else None for coluna, i in posicao.items()})
                for numero, linha in enumerate(linhas, start=2)
                if any(not _vazio(valor) for valor in linha)
            ]
        return abas
    finally:
        livro.close()


def _dados(aba: str, valores: dict) -> dict:
    """{coluna da planilha: valor} → {campo da API: valor}, como a tela mandaria."""
    dados = {}
    for coluna, valor in valores.items():
        campo = COLUNAS[aba][coluna]
        if _vazio(valor):
            continue
        if campo in SIM_OU_NAO:
            resposta = _simples(valor)
            if resposta not in ("sim", "nao"):
                raise _Recusa(coluna, "Escreva sim ou não (ou deixe em branco).")
            dados[campo] = resposta == "sim"
        elif campo in NUMEROS:
            if isinstance(valor, float) and valor.is_integer():
                valor = int(valor)
            dados[campo] = str(valor).strip().replace(",", ".")
        else:
            dados[campo] = " ".join(str(valor).split())
    return dados


# ------------------------------------------------------------------------------------------ Gravação


def _coluna_do_campo(aba: str, campo: str) -> str:
    return next((coluna for coluna, nome in COLUNAS[aba].items() if nome == campo), next(iter(COLUNAS[aba])))


def _salvar(aba: str, serializer_class, dados: dict):
    entrada = serializer_class(data=dados)
    try:
        valido = entrada.is_valid()
    except ErroDeRegraDeNegocio as recusa:  # RN03 (B4), levantada de dentro da validação
        raise _Recusa(_coluna_do_campo(aba, recusa.campo or ""), recusa.mensagem) from recusa
    if not valido:
        campo, mensagens = next(iter(entrada.errors.items()))
        raise _Recusa(_coluna_do_campo(aba, campo), " ".join(str(m) for m in mensagens))
    return entrada.save()


def _carregar_aba(aba, linhas, resultado, chave, existentes, gravar):
    """Linha a linha: mantém o que já existe pelo nome, grava o resto; anota as recusas."""
    vistos = {}
    for numero, valores in linhas:
        nome = _simples(valores.get(next(iter(COLUNAS[aba]))) or "")
        try:
            if nome in vistos:
                raise _Recusa(
                    next(iter(COLUNAS[aba])), f"Repetido na planilha: já está na linha {vistos[nome]}."
                )
            vistos[nome] = numero
            dados = _dados(aba, valores)
            if gravar(dados, existentes, nome):
                resultado.criados[chave] += 1
            else:
                resultado.mantidos[chave] += 1
        except _Recusa as recusa:
            resultado.erros.append(ErroNaPlanilha(aba, numero, recusa.coluna, recusa.mensagem))


def carregar_planilha(caminho: Path) -> Resultado:
    abas = _abas(Path(caminho))
    resultado = Resultado()
    categorias = {_simples(c.nome): c for c in Categoria.objects.all()}
    fornecedores = {_simples(f.nome): f for f in Fornecedor.objects.all()}

    def gravar_categoria(dados, existentes, nome):
        if nome in existentes:
            return False
        existentes[nome] = _salvar("Categorias", CategoriaSerializer, dados)
        return True

    def gravar_fornecedor(dados, existentes, nome):
        if nome in existentes:
            return False
        existentes[nome] = _salvar("Fornecedores", FornecedorSerializer, dados)
        return True

    def gravar_produto(dados, _existentes, nome):
        categoria = categorias.get(_simples(dados.get("categoria", "")))
        if categoria is None:
            raise _Recusa(
                "Categoria",
                f"A categoria {dados.get('categoria', '')!r} não está na aba Categorias nem no cadastro.",
            )
        dados["categoria"] = categoria.pk
        if "fornecedor_padrao" in dados:
            fornecedor = fornecedores.get(_simples(dados["fornecedor_padrao"]))
            if fornecedor is None:
                raise _Recusa(
                    "Fornecedor",
                    f"O fornecedor {dados['fornecedor_padrao']!r} não está na aba Fornecedores "
                    "nem no cadastro.",
                )
            dados["fornecedor_padrao"] = fornecedor.pk
        if any(_simples(p.nome) == nome for p in Produto.objects.filter(categoria=categoria)):
            return False
        _salvar("Produtos", ProdutoSerializer, dados)
        return True

    try:
        with transaction.atomic():
            _carregar_aba(
                "Categorias", abas["Categorias"], resultado, "categorias", categorias, gravar_categoria
            )
            _carregar_aba(
                "Fornecedores",
                abas["Fornecedores"],
                resultado,
                "fornecedores",
                fornecedores,
                gravar_fornecedor,
            )
            _carregar_aba("Produtos", abas["Produtos"], resultado, "produtos", None, gravar_produto)
            if resultado.erros:
                raise _Desfazer
    except _Desfazer:
        resultado.criados = {chave: 0 for chave in resultado.criados}
    return resultado

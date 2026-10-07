"""
Cadastro — endpoints de categoria e fornecedor. Tarefa B2.

Sem exclusão: categoria e fornecedor são tabelas de origem e nunca são apagadas (Apostila IV,
seção 5). O pedido de exclusão responde 405.
"""

from rest_framework import mixins, viewsets

from cadastro.models import Categoria, Fornecedor
from cadastro.serializers import CategoriaSerializer, FornecedorSerializer


class CadastroSemExclusao(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Listar, consultar, cadastrar e editar. Nunca apagar."""


class CategoriaViewSet(CadastroSemExclusao):
    """
    /api/categorias/ — a categoria não tem tela própria (decisão da L18):
    criar e editar é da tela de Produtos; ler é da Consulta de estoque, que mostra o saldo por
    categoria (RF07) para os três perfis.
    """

    tela = "produtos"
    tela_leitura = "consulta_estoque"
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class FornecedorViewSet(CadastroSemExclusao):
    """/api/fornecedores/ — tela Fornecedores (RF02), só OPERACAO (RN14)."""

    tela = "fornecedores"
    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer

"""
Cadastro — endpoints de categoria e fornecedor (tarefa B2) e de produto (tarefa B3).

Sem exclusão: categoria, fornecedor e produto são tabelas de origem e nunca são apagadas (Apostila IV,
seção 5). O pedido de exclusão responde 405.
"""

from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError

from cadastro.models import Categoria, Fornecedor, Produto
from cadastro.serializers import CategoriaSerializer, FornecedorSerializer, ProdutoSerializer
from comum.busca import filtrar_por_nome


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


class ProdutoViewSet(CadastroSemExclusao):
    """
    /api/produtos/ — tela Produtos (RF01, RF15), só OPERACAO (RN14).

    Filtros da lista: ?busca=<parte do nome>  ?categoria=<id>
    Não existe saldo aqui: o saldo é derivado das movimentações (RN01) e aparece na Consulta de
    estoque (tarefa F2).
    """

    tela = "produtos"
    serializer_class = ProdutoSerializer

    def get_queryset(self):
        produtos = Produto.objects.select_related("categoria", "fornecedor_padrao")
        produtos = filtrar_por_nome(produtos, "nome", self.request.query_params.get("busca", ""))
        categoria = self.request.query_params.get("categoria")
        if categoria:
            if not categoria.isdigit():
                raise ValidationError({"categoria": ["Filtro de categoria inválido."]})
            produtos = produtos.filter(categoria_id=int(categoria))
        return produtos

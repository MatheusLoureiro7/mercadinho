"""
Estoque — endpoints. Tarefa C2: entrada de mercadoria. Tarefa D1: perdas.

/api/lotes/ — tela Entrada de mercadoria, só OPERACAO (RN14).
    POST                     registra a carga que chegou (operação 02)
    GET ?data_entrada=AAAA-MM-DD&produto=<id>   a lista do dia (passo 11)
    GET /api/lotes/{id}/

Lote não se edita nem se apaga: mudar a quantidade dele desalinharia o saldo (RN01). Correção de
estoque é por perda ou ajuste, que deixam rastro em movimentação.
"""

from datetime import date

from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from estoque.entrada import registrar_entrada
from estoque.models import Lote, Movimentacao
from estoque.perda import registrar_perda
from estoque.saldo import saldo_do_produto
from estoque.serializers import (
    EntradaDeLoteSerializer,
    LoteRegistradoSerializer,
    LoteSerializer,
    PerdaSerializer,
    RegistroDePerdaSerializer,
)


class LoteViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    tela = "entrada_mercadoria"
    serializer_class = LoteSerializer

    def get_queryset(self):
        lotes = Lote.objects.select_related("produto", "fornecedor").order_by("-id")
        parametros = self.request.query_params
        if data_entrada := parametros.get("data_entrada"):
            try:
                lotes = lotes.filter(data_entrada=date.fromisoformat(data_entrada))
            except ValueError as erro:
                raise ValidationError({"data_entrada": ["Use a data no formato AAAA-MM-DD."]}) from erro
        if produto := parametros.get("produto"):
            if not produto.isdigit():
                raise ValidationError({"produto": ["Filtro de produto inválido."]})
            lotes = lotes.filter(produto_id=int(produto))
        return lotes

    def create(self, request):
        entrada = EntradaDeLoteSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        lote = registrar_entrada(usuario=request.user, **entrada.validated_data)
        return Response(LoteRegistradoSerializer(lote).data, status=status.HTTP_201_CREATED)


class PerdaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    /api/perdas/ — tela Avarias e quebras, só OPERACAO (RN14). RF04, fluxograma 03.

    POST                               registra a perda: {"produto", "quantidade", "motivo", "lote"?}
    GET ?data=AAAA-MM-DD&produto=<id>  o caderno de avarias, mais recente primeiro

    Perda registrada não se apaga (RN01: nada é apagado em movimentação).
    """

    tela = "avarias"
    serializer_class = PerdaSerializer

    def get_queryset(self):
        perdas = Movimentacao.objects.filter(tipo=Movimentacao.Tipo.PERDA).select_related(
            "produto", "lote", "usuario"
        )
        parametros = self.request.query_params
        if data := parametros.get("data"):
            try:
                perdas = perdas.filter(data_hora__date=date.fromisoformat(data))  # dia da loja
            except ValueError as erro:
                raise ValidationError({"data": ["Use a data no formato AAAA-MM-DD."]}) from erro
        if produto := parametros.get("produto"):
            if not produto.isdigit():
                raise ValidationError({"produto": ["Filtro de produto inválido."]})
            perdas = perdas.filter(produto_id=int(produto))
        return perdas.order_by("-data_hora", "-id")

    def create(self, request):
        entrada = RegistroDePerdaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        perdas = registrar_perda(usuario=request.user, **entrada.validated_data)
        produto = entrada.validated_data["produto"]
        return Response(
            {
                "perdas": PerdaSerializer(perdas, many=True).data,
                "saldo_produto": f"{saldo_do_produto(produto):.3f}",
            },
            status=status.HTTP_201_CREATED,
        )

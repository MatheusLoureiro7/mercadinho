"""
Vendas — endpoints. Tarefa E4: casar o produto do caixa com o cadastro. Tela Importação de vendas,
só OPERACAO (RN14).

/api/itens-pendentes/
    GET                              os itens que a importação não casou, do mais antigo ao mais novo
    POST {id}/casar/ {"produto"}     liga o item ao produto e baixa a venda do estoque (RN01, RN02)

Venda não se registra pela API: só nasce da planilha do caixa (operação 04).
"""

from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from vendas.conciliacao import casar_item, itens_pendentes
from vendas.models import ItemVenda
from vendas.serializers import CasarItemSerializer, ItemCasadoSerializer, ItemPendenteSerializer


class ItemPendenteViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    tela = "importacao_vendas"
    serializer_class = ItemPendenteSerializer

    def get_queryset(self):
        return itens_pendentes()

    @action(detail=True, methods=["post"])
    def casar(self, request, pk=None):
        item = get_object_or_404(ItemVenda, pk=pk)
        entrada = CasarItemSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        item = casar_item(item.pk, entrada.validated_data["produto"])
        return Response(ItemCasadoSerializer(item).data)

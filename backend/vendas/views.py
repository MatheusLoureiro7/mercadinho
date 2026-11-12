"""
Vendas — endpoints. Tarefas E4 (casar o produto do caixa com o cadastro) e E5 (acompanhamento da
importação). Tela Importação de vendas, só OPERACAO (RN14).

/api/importacoes/
    GET                              as últimas 30 planilhas lidas, a mais nova primeiro (E5)

/api/itens-pendentes/
    GET                              os itens que a importação não casou, do mais antigo ao mais novo
    POST {id}/casar/ {"produto"}     liga o item ao produto e baixa a venda do estoque (RN01, RN02)

Venda não se registra pela API, e a planilha não é enviada pela tela: ela vai para a pasta do
caixa e a rodada das 03h00 importa (operação 04; E3, G5).
"""

from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from vendas.conciliacao import casar_item, itens_pendentes
from vendas.models import ImportacaoPdv, ItemVenda
from vendas.serializers import (
    CasarItemSerializer,
    ImportacaoSerializer,
    ItemCasadoSerializer,
    ItemPendenteSerializer,
)

ULTIMAS_LEITURAS = 30


class ImportacaoViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    tela = "importacao_vendas"
    serializer_class = ImportacaoSerializer

    def get_queryset(self):
        return ImportacaoPdv.objects.order_by("-processado_em", "-id")[:ULTIMAS_LEITURAS]


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

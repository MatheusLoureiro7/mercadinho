"""
Estoque — endpoints. Tarefa C2: entrada de mercadoria.

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
from estoque.models import Lote
from estoque.serializers import EntradaDeLoteSerializer, LoteRegistradoSerializer, LoteSerializer


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

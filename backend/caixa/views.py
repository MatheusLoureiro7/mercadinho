"""
Fechamento de caixa — endpoints. Tarefa I1 (RN15, RF12, fluxograma 06). Tela da esposa (GESTAO, RN14).

/api/fechamentos/
    GET  apurado/            {"data", "valor_sistema"} do dia do fechamento (o dia anterior)
    GET  ?data=AAAA-MM-DD    os registros do dia, o mais novo primeiro
    POST {"valor_contado"}   grava; data, apurado e diferença são do sistema

RN15: não existe alterar nem apagar — correção é um registro novo.
"""

from datetime import date

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from caixa.fechamento import apurado_do_fechamento, dia_do_fechamento, registrar_fechamento
from caixa.models import FechamentoCaixa
from caixa.serializers import DinheiroContadoSerializer, FechamentoSerializer


class FechamentoViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    tela = "fechamento_caixa"
    serializer_class = FechamentoSerializer

    def get_queryset(self):
        texto = self.request.query_params.get("data")
        try:
            dia = date.fromisoformat(texto) if texto else dia_do_fechamento()
        except ValueError as erro:
            raise ValidationError({"data": ["Use a data no formato AAAA-MM-DD."]}) from erro
        return (
            FechamentoCaixa.objects.filter(data=dia)
            .select_related("registrado_por")
            .order_by("-registrado_em", "-id")
        )

    def create(self, request):
        entrada = DinheiroContadoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        fechamento = registrar_fechamento(usuario=request.user, **entrada.validated_data)
        return Response(FechamentoSerializer(fechamento).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def apurado(self, request):
        dia, valor = apurado_do_fechamento()
        return Response({"data": dia.isoformat(), "valor_sistema": f"{valor:.2f}"})

"""
Fechamento de caixa — endpoints. Tarefa I1 (RN15, RF12, fluxograma 06). Tela da esposa (GESTAO, RN14).

/api/fechamentos/
    GET  apurado/?data=      {"data", "valor_sistema"} do dia escolhido (sem ?data=, o dia anterior)
    GET  ?data=AAAA-MM-DD    os registros do dia, o mais novo primeiro
    POST {"valor_contado", "data"?}   grava o dia escolhido (sem "data", ontem); apurado e diferença
                                      são do sistema (X1, item 6)

RN15: não existe alterar nem apagar — correção é um registro novo.

/api/balancos/ — Balanço da semana (I3), também da esposa: ver BalancoView.
"""

from datetime import date

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from caixa.balanco import balanco_da_semana, ontem, semana_de
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
        texto = self.request.query_params.get("data")
        try:
            escolhido = date.fromisoformat(texto) if texto else None
        except ValueError as erro:
            raise ValidationError({"data": ["Use a data no formato AAAA-MM-DD."]}) from erro
        dia, valor = apurado_do_fechamento(escolhido)
        return Response({"data": dia.isoformat(), "valor_sistema": f"{valor:.2f}"})


class BalancoView(APIView):
    """
    Balanço da semana — tarefa I3 (RF13, L16). Tela da esposa (GESTAO, RN14).

    GET /api/balancos/?semana=AAAA-MM-DD   qualquer dia da semana; sem o filtro, a semana de ontem
    """

    tela = "balanco_semana"

    def get(self, request):
        texto = request.query_params.get("semana")
        try:
            dia = date.fromisoformat(texto) if texto else ontem()
        except ValueError as erro:
            raise ValidationError({"semana": ["Use a data no formato AAAA-MM-DD."]}) from erro
        if semana_de(dia)[0] > ontem():
            raise ValidationError(
                {"semana": ["Essa semana ainda não começou: escolha uma semana que já tenha vendas."]}
            )
        balanco = balanco_da_semana(dia)
        return Response(
            {
                "inicio": balanco.inicio.isoformat(),
                "fim": balanco.fim.isoformat(),
                "ate": balanco.ate.isoformat(),
                "vendas_total": f"{balanco.vendas_total:.2f}",
                "cupons": balanco.cupons,
                "vendas_por_dia": [
                    {"data": dia.isoformat(), "total": f"{total:.2f}", "cupons": cupons}
                    for dia, total, cupons in balanco.vendas_por_dia
                ],
                "perdas": [
                    {
                        "produto_nome": item.produto_nome,
                        "unidade_medida": item.unidade_medida,
                        "quantidade": f"{item.quantidade:f}",
                        "valor": None if item.valor is None else f"{item.valor:.2f}",
                        "sem_custo": item.sem_custo,
                    }
                    for item in balanco.perdas
                ],
                "perdas_total": f"{balanco.perdas_total:.2f}",
                "perdas_sem_custo": balanco.perdas_sem_custo,
                "resultado": f"{balanco.resultado:.2f}",
                "dias_sem_vendas": [dia.isoformat() for dia in balanco.dias_sem_vendas],
            }
        )

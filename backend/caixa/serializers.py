"""
Fechamento de caixa — o que a API recebe e devolve. Tarefa I1 (RN15).

A tela manda só o dinheiro contado. Data, apurado e diferença são do sistema: se a tela mandar,
são ignorados (RN15 — a diferença é calculada, nunca digitada).
"""

from rest_framework import serializers

from caixa.models import FechamentoCaixa


class DinheiroContadoSerializer(serializers.Serializer):
    valor_contado = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        error_messages={
            "required": "Informe o dinheiro contado na gaveta (campo obrigatório).",
            "null": "Informe o dinheiro contado na gaveta (campo obrigatório).",
            "min_value": "O dinheiro contado não pode ser negativo.",
            "max_decimal_places": "Use no máximo dois centavos, por exemplo 3215.50.",
            "max_digits": "Valor grande demais para o caixa.",
            "max_whole_digits": "Valor grande demais para o caixa.",
            "invalid": "Escreva o valor só com número, por exemplo 3215.00.",
        },
    )


class FechamentoSerializer(serializers.ModelSerializer):
    diferenca = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    registrado_por_nome = serializers.CharField(source="registrado_por.nome", default=None, read_only=True)

    class Meta:
        model = FechamentoCaixa
        fields = [
            "id",
            "data",
            "valor_sistema",
            "valor_contado",
            "diferenca",
            "registrado_por_nome",
            "registrado_em",
        ]
        read_only_fields = fields

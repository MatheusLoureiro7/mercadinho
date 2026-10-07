"""
Cadastro — validação de entrada da API. Tarefas B2 e B3.

Mensagens no vocabulário da loja (RNF10). Os nomes dos campos são os do schema.sql.
"""

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from cadastro.models import Categoria, Fornecedor


class CategoriaSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(
        max_length=80,
        validators=[
            UniqueValidator(
                queryset=Categoria.objects.all(), message="Já existe uma categoria com esse nome."
            )
        ],
    )
    # Opcional: se não vier, vale o DEFAULT FALSE do banco (schema.sql).
    perecivel_padrao = serializers.BooleanField(required=False)

    class Meta:
        model = Categoria
        fields = ["id", "nome", "perecivel_padrao"]


class FornecedorSerializer(serializers.ModelSerializer):
    prazo_entrega_dias = serializers.IntegerField(
        min_value=0,
        error_messages={
            "required": "Informe em quantos dias o fornecedor entrega depois do pedido.",
            "null": "Informe em quantos dias o fornecedor entrega depois do pedido.",
            "min_value": "O prazo de entrega não pode ser negativo.",
            "invalid": "Informe o prazo de entrega em dias, só com números.",
        },
    )
    pedido_minimo = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        required=False,
        allow_null=True,
        error_messages={"min_value": "O pedido mínimo não pode ser negativo."},
    )
    contato = serializers.CharField(max_length=160, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Fornecedor
        fields = ["id", "nome", "prazo_entrega_dias", "pedido_minimo", "contato"]

    def validate_contato(self, valor):
        return valor or None  # vazio vira nulo, como no schema.sql

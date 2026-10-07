"""
Estoque — validação de entrada e formato de saída da API. Tarefa C2.
"""

from rest_framework import serializers

from cadastro.models import Fornecedor, Produto
from estoque.models import Lote, Movimentacao
from estoque.saldo import saldo_do_produto


class EntradaDeLoteSerializer(serializers.Serializer):
    """Operação 02, passo 1: o que a tela de Entrada de mercadoria envia (RF03)."""

    produto = serializers.PrimaryKeyRelatedField(
        queryset=Produto.objects.all(),
        error_messages={
            "required": "Escolha o produto que chegou.",
            "null": "Escolha o produto que chegou.",
            "does_not_exist": "Esse produto não existe.",
            "incorrect_type": "Esse produto não existe.",
        },
    )
    quantidade = serializers.DecimalField(
        max_digits=12,
        decimal_places=3,  # carne chega em quilo fracionado
        error_messages={
            "required": "Informe a quantidade que chegou.",
            "invalid": "Informe a quantidade só com números, por exemplo 12.5.",
        },
    )
    fornecedor = serializers.PrimaryKeyRelatedField(
        queryset=Fornecedor.objects.all(),
        required=False,
        allow_null=True,
        error_messages={
            "does_not_exist": "Esse fornecedor não existe.",
            "incorrect_type": "Esse fornecedor não existe.",
        },
    )
    custo_unitario = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        required=False,
        allow_null=True,
        error_messages={"min_value": "O custo não pode ser negativo."},
    )
    data_validade = serializers.DateField(required=False, allow_null=True)

    def validate_quantidade(self, valor):
        if valor <= 0:
            raise serializers.ValidationError("A quantidade que chegou tem de ser maior que zero.")
        return valor


class LoteSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source="produto.nome", read_only=True)
    unidade_medida = serializers.CharField(source="produto.unidade_medida", read_only=True)
    fornecedor_nome = serializers.CharField(source="fornecedor.nome", read_only=True, default=None)

    class Meta:
        model = Lote
        fields = [
            "id",
            "produto",
            "produto_nome",
            "unidade_medida",
            "fornecedor",
            "fornecedor_nome",
            "quantidade_inicial",
            "quantidade_atual",
            "custo_unitario",
            "data_entrada",
            "data_validade",
        ]
        read_only_fields = fields


class LoteRegistradoSerializer(LoteSerializer):
    """Resposta do passo 11, com o saldo novo do produto (passo 9: "avisa que o saldo mudou")."""

    saldo_produto = serializers.SerializerMethodField()

    class Meta(LoteSerializer.Meta):
        fields = [*LoteSerializer.Meta.fields, "saldo_produto"]
        read_only_fields = fields

    def get_saldo_produto(self, lote) -> str:
        return f"{saldo_do_produto(lote.produto_id):.3f}"


MENSAGEM_SEM_MOTIVO = "Anote o motivo da perda: venceu, quebrou, estragou…"


class RegistroDePerdaSerializer(serializers.Serializer):
    """O que a tela de Avarias e quebras envia (RF04). Tarefa D1."""

    produto = serializers.PrimaryKeyRelatedField(
        queryset=Produto.objects.all(),
        error_messages={
            "required": "Escolha o produto que se perdeu.",
            "null": "Escolha o produto que se perdeu.",
            "does_not_exist": "Esse produto não existe.",
            "incorrect_type": "Esse produto não existe.",
        },
    )
    lote = serializers.PrimaryKeyRelatedField(
        queryset=Lote.objects.all(),
        required=False,
        allow_null=True,
        error_messages={"does_not_exist": "Esse lote não existe.", "incorrect_type": "Esse lote não existe."},
    )
    quantidade = serializers.DecimalField(
        max_digits=12,
        decimal_places=3,
        error_messages={
            "required": "Informe quanto se perdeu.",
            "invalid": "Informe a quantidade só com números, por exemplo 1.5.",
        },
    )
    motivo = serializers.CharField(
        max_length=200,
        error_messages={
            "required": MENSAGEM_SEM_MOTIVO,
            "blank": MENSAGEM_SEM_MOTIVO,
            "null": MENSAGEM_SEM_MOTIVO,
        },
    )

    def validate_quantidade(self, valor):
        if valor <= 0:
            raise serializers.ValidationError("A quantidade perdida tem de ser maior que zero.")
        return valor


class PerdaSerializer(serializers.ModelSerializer):
    """Uma linha do caderno de avarias: uma movimentação PERDA."""

    produto_nome = serializers.CharField(source="produto.nome", read_only=True)
    unidade_medida = serializers.CharField(source="produto.unidade_medida", read_only=True)
    lote_validade = serializers.DateField(source="lote.data_validade", read_only=True, default=None)
    usuario_nome = serializers.CharField(source="usuario.nome", read_only=True, default=None)

    class Meta:
        model = Movimentacao
        fields = [
            "id",
            "produto",
            "produto_nome",
            "unidade_medida",
            "lote",
            "lote_validade",
            "quantidade",
            "motivo",
            "data_hora",
            "usuario_nome",
        ]
        read_only_fields = fields

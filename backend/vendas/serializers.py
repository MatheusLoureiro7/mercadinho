"""
Vendas — o que a API recebe e devolve. Tarefa E4: itens pendentes da importação.

O item pendente não tem o nome escrito na planilha (o modelo de dados não guarda, lacuna L26): a
tela mostra data, hora, quantidade e preço, que o sobrinho confere na planilha dele.
"""

from rest_framework import serializers

from cadastro.models import Produto
from vendas.models import ItemVenda


class ItemPendenteSerializer(serializers.ModelSerializer):
    data_hora = serializers.DateTimeField(source="venda.data_hora", read_only=True)

    class Meta:
        model = ItemVenda
        fields = ["id", "venda", "data_hora", "quantidade", "preco"]
        read_only_fields = fields


class ItemCasadoSerializer(ItemPendenteSerializer):
    produto_nome = serializers.CharField(source="produto.nome", read_only=True)

    class Meta(ItemPendenteSerializer.Meta):
        fields = [*ItemPendenteSerializer.Meta.fields, "produto", "produto_nome"]
        read_only_fields = fields


class CasarItemSerializer(serializers.Serializer):
    produto = serializers.PrimaryKeyRelatedField(
        queryset=Produto.objects.all(),
        error_messages={
            "required": "Escolha o produto que foi vendido (campo obrigatório).",
            "null": "Escolha o produto que foi vendido (campo obrigatório).",
            "does_not_exist": "Este produto não está no cadastro. Escolha outro da lista.",
            "incorrect_type": "Escolha o produto da lista.",
        },
    )

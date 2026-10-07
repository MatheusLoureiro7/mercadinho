"""
Cadastro — validação de entrada da API. Tarefas B2 e B3.

Mensagens no vocabulário da loja (RNF10). Os nomes dos campos são os do schema.sql.
"""

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from cadastro.models import Categoria, Fornecedor, Produto

# L17 (decidida na B3): lista fechada, a que o schema.sql cita. Validada só na API — o banco não tem
# essa restrição. Para acrescentar uma unidade, basta incluí-la aqui.
UNIDADES_DE_MEDIDA = ("KG", "UN", "L", "PCT")


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


def _dinheiro(rotulo: str) -> serializers.DecimalField:
    return serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        required=False,
        allow_null=True,
        error_messages={
            "min_value": f"O {rotulo} não pode ser negativo.",
            "invalid": f"Informe o {rotulo} só com números, por exemplo 12.90.",
        },
    )


class ProdutoSerializer(serializers.ModelSerializer):
    """
    RF01 e RF15. Operação 01: tipo e obrigatoriedade (passo 5) e nome único na categoria (passo 6).
    A RN03 — perecível exige durabilidade — é a tarefa B4.
    """

    categoria = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(),
        error_messages={
            "required": "Escolha a categoria do produto.",
            "null": "Escolha a categoria do produto.",
            "does_not_exist": "Essa categoria não existe.",
            "incorrect_type": "Essa categoria não existe.",
        },
    )
    categoria_nome = serializers.CharField(source="categoria.nome", read_only=True)
    fornecedor_padrao = serializers.PrimaryKeyRelatedField(
        queryset=Fornecedor.objects.all(),
        required=False,
        allow_null=True,
        error_messages={
            "does_not_exist": "Esse fornecedor não existe.",
            "incorrect_type": "Esse fornecedor não existe.",
        },
    )
    fornecedor_padrao_nome = serializers.CharField(
        source="fornecedor_padrao.nome", read_only=True, default=None
    )
    unidade_medida = serializers.CharField(
        max_length=10, error_messages={"required": "Escolha a unidade: KG, UN, L ou PCT."}
    )
    # Opcionais: se não vierem, valem os padrões (L19 para perecível; DEFAULT FALSE do banco).
    perecivel = serializers.BooleanField(required=False)
    critico_fim_semana = serializers.BooleanField(required=False)
    durabilidade_dias = serializers.IntegerField(
        required=False,
        allow_null=True,
        error_messages={"invalid": "Informe a durabilidade em dias, só com números."},
    )
    preco_custo = _dinheiro("preço de custo")
    preco_venda = _dinheiro("preço de venda")
    estoque_minimo = serializers.DecimalField(
        max_digits=12,
        decimal_places=3,  # carne é vendida em quilo fracionado
        min_value=0,
        required=False,
        allow_null=True,
        error_messages={
            "min_value": "O estoque mínimo não pode ser negativo.",
            "invalid": "Informe o estoque mínimo só com números, por exemplo 2.5.",
        },
    )

    class Meta:
        model = Produto
        fields = [
            "id",
            "nome",
            "categoria",
            "categoria_nome",
            "fornecedor_padrao",
            "fornecedor_padrao_nome",
            "unidade_medida",
            "perecivel",
            "durabilidade_dias",
            "preco_custo",
            "preco_venda",
            "estoque_minimo",
            "critico_fim_semana",
        ]
        # O nome único na categoria é checado em validate(), com a mensagem da loja e apontando o
        # campo `nome` (fluxograma 01). Desliga a validação automática do DRF, de texto técnico.
        validators = []

    def validate_unidade_medida(self, valor):
        unidade = valor.strip().upper()
        if unidade not in UNIDADES_DE_MEDIDA:
            raise serializers.ValidationError("Escolha a unidade: KG, UN, L ou PCT.")
        return unidade

    def validate(self, dados):
        # Operação 01, passo 6: "já existe produto com este nome na categoria?"
        nome = dados.get("nome", getattr(self.instance, "nome", None))
        categoria = dados.get("categoria", getattr(self.instance, "categoria", None))
        repetidos = Produto.objects.filter(nome=nome, categoria=categoria)
        if self.instance is not None:
            repetidos = repetidos.exclude(pk=self.instance.pk)
        if repetidos.exists():
            raise serializers.ValidationError({"nome": "Já existe um produto com esse nome nesta categoria."})
        return dados

    def create(self, dados):
        # L19: quem não diz se o produto é perecível herda o padrão da categoria.
        dados.setdefault("perecivel", dados["categoria"].perecivel_padrao)
        return super().create(dados)

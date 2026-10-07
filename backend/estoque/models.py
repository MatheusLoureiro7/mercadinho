"""
Estoque — lote e movimentação. Tarefa C1.

Tabelas (schema.sql): lote, movimentacao — colunas, tipos, padrões, restrições e índices exatamente
como na Apostila IV, seção 6. O saldo do produto NÃO é coluna: é a view vw_estoque_atual (C4, RN01).
Regras que usam estas tabelas: RN01 e RN02 (C4, E3), RN04 (C3), RN11 (D2, G1), RN16 (D1, E3).

Atenção às datas: o Django conversa com o PostgreSQL em UTC (USE_TZ). O DEFAULT CURRENT_DATE do
banco é, portanto, a data em UTC — depois das 21h de São Paulo já é "amanhã". Quem grava lote
informa sempre `data_entrada = timezone.localdate()`; o DEFAULT do banco fica só como rede de
segurança, como no schema.sql.
"""

from django.conf import settings
from django.db import models
from django.db.models import Func, Q
from django.db.models.functions import Length, Trim
from django.db.models.lookups import GreaterThan

from cadastro.models import Fornecedor, Produto


class DataAtual(Func):
    """CURRENT_DATE do PostgreSQL, para o DEFAULT de lote.data_entrada ficar igual ao schema.sql."""

    template = "CURRENT_DATE"
    output_field = models.DateField()


class Agora(Func):
    """
    NOW() do PostgreSQL, como no schema.sql. (O Now() do Django gera STATEMENT_TIMESTAMP(); o NOW()
    é o horário do início da transação, então lote e movimentação gravados juntos ficam com a
    mesma hora — operação 02, passo 7.)
    """

    template = "NOW()"
    output_field = models.DateTimeField()


class Lote(models.Model):
    """Cada carga que chega vira um lote (RF03)."""

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="lotes")
    fornecedor = models.ForeignKey(
        Fornecedor, on_delete=models.PROTECT, null=True, blank=True, related_name="lotes"
    )
    quantidade_inicial = models.DecimalField(max_digits=12, decimal_places=3)
    # Saldo DO LOTE, usado pelo FIFO (RN02). Não confundir com o saldo do produto, que é derivado
    # das movimentações (RN01).
    quantidade_atual = models.DecimalField(max_digits=12, decimal_places=3)
    custo_unitario = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    data_entrada = models.DateField(db_default=DataAtual())
    # RN04: obrigatória se o produto é perecível; se não vier, data_entrada + durabilidade (C3).
    data_validade = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "lote"
        constraints = [
            models.CheckConstraint(condition=Q(quantidade_atual__gte=0), name="ck_lote_qtd"),
        ]
        indexes = [
            # RN02 (FIFO): a baixa por venda procura o lote de validade mais próxima.
            models.Index(
                fields=["produto", "data_validade"],
                name="ix_lote_fifo",
                condition=Q(quantidade_atual__gt=0),
            ),
        ]

    def __str__(self):
        return f"Lote {self.pk} de {self.produto}"


class Movimentacao(models.Model):
    """
    A ÚNICA coisa que altera o estoque. Toda linha explica uma mudança de saldo (RN01). Nada é
    apagado.

    ENTRADA e AJUSTE somam, VENDA e PERDA subtraem — o sinal vem do tipo, a quantidade é sempre
    positiva. PERDA é excluída da base de consumo (RN11).
    """

    class Tipo(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        VENDA = "VENDA", "Venda"
        PERDA = "PERDA", "Perda"
        AJUSTE = "AJUSTE", "Ajuste"

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="movimentacoes")
    lote = models.ForeignKey(
        Lote, on_delete=models.PROTECT, null=True, blank=True, related_name="movimentacoes"
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="movimentacoes",
    )
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    quantidade = models.DecimalField(max_digits=12, decimal_places=3)
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    data_hora = models.DateTimeField(db_default=Agora())
    motivo = models.CharField(max_length=200, null=True, blank=True)  # noqa: DJ001 — obrigatório só na PERDA (D1)
    origem = models.CharField(max_length=20, null=True, blank=True)  # noqa: DJ001 — 'TELA', 'IMPORTACAO_PDV', 'AJUSTE'

    class Meta:
        db_table = "movimentacao"
        constraints = [
            models.CheckConstraint(
                condition=Q(tipo__in=["ENTRADA", "VENDA", "PERDA", "AJUSTE"]),
                name="ck_mov_tipo",
            ),
            models.CheckConstraint(condition=Q(quantidade__gt=0), name="ck_mov_qtd"),
            # Tarefa D1: "API de registro de perda, com motivo obrigatório" — o banco é a última defesa.
            models.CheckConstraint(
                condition=~Q(tipo="PERDA")
                | Q(Q(motivo__isnull=False), GreaterThan(Length(Trim("motivo")), 0)),
                name="ck_mov_perda_motivo",
            ),
        ]
        indexes = [
            models.Index(fields=["produto", "data_hora"], name="ix_mov_produto_data"),
            models.Index(fields=["tipo", "data_hora"], name="ix_mov_tipo_data"),  # RN11
        ]

    def __str__(self):
        return f"{self.tipo} {self.quantidade} de {self.produto}"

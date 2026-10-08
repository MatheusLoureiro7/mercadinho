"""
Avisos — aviso, motor de regras e notificação. Tarefa H1.

Tabela (schema.sql): alerta — colunas, tipos, padrões, restrições e índice exatamente como na
Apostila IV, seção 6. Regras que a usam: RN05 (H2), RN08 e RN10 (H3), RN12 e RN13 (H4), operação 03.

O estado do aviso só muda pelas funções de alertas/estados.py (nunca com .update() solto), e o aviso
só nasce por alertas.servicos.criar_aviso, que valida tipo, severidade e mensagem.
"""

from django.conf import settings
from django.db import models
from django.db.models import Case, IntegerField, Q, Value, When

from cadastro.models import Produto
from comum.sql import Agora
from estoque.models import Lote


class AlertaQuerySet(models.QuerySet):
    def a_enviar(self):
        """O que a próxima janela de envio junta numa mensagem só (RN13): PENDENTE e SEGURADO."""
        return self.filter(status__in=[Alerta.Status.PENDENTE, Alerta.Status.SEGURADO])

    def por_urgencia(self):
        """RN13: ordena por severidade (ALTA, MEDIA, BAIXA — L11) e depois por gerado_em."""
        ordem = Case(
            *[
                When(severidade=valor, then=Value(posicao))
                for posicao, valor in enumerate(Alerta.Severidade.values)
            ],
            default=Value(len(Alerta.Severidade.values)),
            output_field=IntegerField(),
        )
        return self.order_by(ordem, "gerado_em", "id")


class Alerta(models.Model):
    class Tipo(models.TextChoices):
        VALIDADE = "VALIDADE", "Validade"  # RN05 (H2)
        RUPTURA = "RUPTURA", "Vai acabar"  # RN08 (H3)
        FIM_SEMANA = "FIM_SEMANA", "Fim de semana"  # RN10 (H3)

    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        SEGURADO = "SEGURADO", "Segurado na janela de silêncio"  # RN12
        ENVIADO = "ENVIADO", "Enviado"
        CANCELADO = "CANCELADO", "Cancelado"

    class Severidade(models.TextChoices):
        # L11 (decidida na H1): lista fechada, validada no código — o banco não tem essa restrição,
        # igual ao schema.sql. A ordem aqui é a ordem de urgência da RN13.
        ALTA = "ALTA", "Alta"
        MEDIA = "MEDIA", "Média"
        BAIXA = "BAIXA", "Baixa"

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="alertas")
    lote = models.ForeignKey(  # nulo em aviso de ruptura (schema.sql)
        Lote, on_delete=models.PROTECT, null=True, blank=True, related_name="alertas"
    )
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    severidade = models.CharField(max_length=10, choices=Severidade.choices)
    mensagem = models.TextField()  # RNF10: vocabulário da loja
    gerado_em = models.DateTimeField(db_default=Agora())
    enviado_em = models.DateTimeField(null=True, blank=True)
    canal = models.CharField(max_length=20, db_default="TELEGRAM")
    status = models.CharField(max_length=12, choices=Status.choices, db_default=Status.PENDENTE)
    resposta_usuario = models.CharField(max_length=40, null=True, blank=True)  # noqa: DJ001 — "Sim, pedir" (H7)
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="alertas",
    )

    objects = AlertaQuerySet.as_manager()

    class Meta:
        db_table = "alerta"
        constraints = [
            models.CheckConstraint(
                condition=Q(tipo__in=["VALIDADE", "RUPTURA", "FIM_SEMANA"]), name="ck_alerta_tipo"
            ),
            # RN12: SEGURADO é o aviso retido na janela de silêncio
            models.CheckConstraint(
                condition=Q(status__in=["PENDENTE", "SEGURADO", "ENVIADO", "CANCELADO"]),
                name="ck_alerta_status",
            ),
        ]
        indexes = [models.Index(fields=["status", "gerado_em"], name="ix_alerta_pendente")]  # RN13

    def __str__(self):
        return f"{self.tipo} {self.status}: {self.mensagem}"

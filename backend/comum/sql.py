"""
Funções SQL para os DEFAULT do banco ficarem iguais aos do schema.sql.
"""

from django.db import models
from django.db.models import Func


class DataAtual(Func):
    """CURRENT_DATE do PostgreSQL (atenção: em UTC — o "hoje" da loja é timezone.localdate())."""

    template = "CURRENT_DATE"
    output_field = models.DateField()


class Agora(Func):
    """
    NOW() do PostgreSQL, como no schema.sql. (O Now() do Django gera STATEMENT_TIMESTAMP(); o NOW()
    é o horário do início da transação, então o que é gravado junto fica com a mesma hora.)
    """

    template = "NOW()"
    output_field = models.DateTimeField()

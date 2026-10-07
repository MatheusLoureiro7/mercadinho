"""
Registro de log das requisições — tarefa A3.

Uma linha por requisição: método, endereço, situação, tempo e usuário. Fica no console e no
arquivo configurado em LOGGING (core/settings.py).

O corpo da requisição NUNCA é gravado: pode ter senha (RNF12).
"""

import logging
import time

logger = logging.getLogger("mercadinho.requisicao")


class RegistroDeRequisicao:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        inicio = time.monotonic()
        resposta = self.get_response(request)
        duracao_ms = (time.monotonic() - inicio) * 1000

        situacao = resposta.status_code
        if situacao >= 500:
            nivel = logging.ERROR
        elif situacao >= 400:
            nivel = logging.WARNING
        else:
            nivel = logging.INFO

        usuario = getattr(request, "user", None)
        id_usuario = usuario.pk if getattr(usuario, "is_authenticated", False) else "-"

        logger.log(
            nivel,
            "%s %s %s %.0fms usuario=%s",
            request.method,
            request.path,
            situacao,
            duracao_ms,
            id_usuario,
        )
        return resposta

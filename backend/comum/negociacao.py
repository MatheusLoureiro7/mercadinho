"""
A API responde sempre em JSON, seja qual for o cabeçalho Accept (tarefa A3).

O painel é estático e não existe versão HTML de nenhuma resposta (Apostila IV, seção 3).
"""

from rest_framework.negotiation import DefaultContentNegotiation


class SempreJson(DefaultContentNegotiation):
    def select_renderer(self, request, renderers, format_suffix=None):
        return (renderers[0], renderers[0].media_type)

"""
Rotas usadas só nos testes da A4: uma view de mentira por tela da RN14, para conferir a matriz de
acesso sem depender das APIs de negócio (que chegam nas tarefas seguintes).
"""

from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView

from cadastro.models import Categoria
from comum.permissoes import ACESSO_POR_TELA
from core.urls import handler404, handler500  # noqa: F401
from core.urls import urlpatterns as rotas_do_sistema


def _view_da_tela(nome_da_tela):
    class ViewDaTela(APIView):
        tela = nome_da_tela

        def get(self, request):
            return Response({"tela": self.tela})

        def post(self, request):
            # Grava no banco: se a recusa da RN14 vier depois disto, o teste percebe.
            Categoria.objects.create(nome=f"gravado por {self.tela}")
            return Response({"tela": self.tela}, status=201)

    return ViewDaTela.as_view()


class ViewSemTela(APIView):
    """Endpoint que esqueceu de declarar a tela: tem de ser recusado (falha fechada)."""

    def get(self, request):
        return Response({"ok": True})


urlpatterns = [
    *rotas_do_sistema,
    *[path(f"teste/tela/{tela}/", _view_da_tela(tela)) for tela in ACESSO_POR_TELA],
    path("teste/sem-tela/", ViewSemTela.as_view()),
]

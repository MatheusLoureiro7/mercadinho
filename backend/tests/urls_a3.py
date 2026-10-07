"""
Rotas usadas só nos testes da A3, para provocar cada tipo de erro.
Não fazem parte da API do sistema.
"""

from django.http import Http404
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from comum.erros import ErroDeRegraDeNegocio
from core.urls import handler404, handler500  # noqa: F401
from core.urls import urlpatterns as rotas_do_sistema


@api_view(["GET"])
def tudo_certo(request):
    return Response({"ok": True})


@api_view(["POST"])
def recusa_por_validacao(request):
    request.data  # noqa: B018 — força a leitura do corpo (JSON malformado cai aqui)
    raise ValidationError({"durabilidade_dias": ["Este campo é obrigatório."]})


@api_view(["POST"])
def recusa_por_regra(request):
    raise ErroDeRegraDeNegocio(
        "RN03",
        "Produto perecível precisa do prazo de durabilidade em dias. "
        "Sem ele o sistema não consegue avisar quando o produto vai vencer.",
        campo="durabilidade_dias",
    )


@api_view(["GET"])
def quebra(request):
    raise RuntimeError("falha simulada no teste")


@api_view(["GET"])
def nao_acha(request):
    raise Http404


urlpatterns = [
    *rotas_do_sistema,
    path("teste/ok/", tudo_certo),
    path("teste/validacao/", recusa_por_validacao),
    path("teste/regra/", recusa_por_regra),
    path("teste/quebra/", quebra),
    path("teste/nao-acha/", nao_acha),
]

"""
Rotas da API — porta única de entrada do sistema (Apostila IV, seção 3).

Todos os endpoints ficam sob /api/, no plural (CLAUDE.md), registrados no roteador abaixo pelas
tarefas que os criam. Exemplo, quando a B3 chegar:

    roteador.register("produtos", ProdutoViewSet, basename="produto")
"""

from django.urls import include, path
from rest_framework.routers import APIRootView, DefaultRouter

from cadastro.views import CategoriaViewSet, FornecedorViewSet
from comum.views import SessaoAtualView, SessaoView


class RaizDaApi(APIRootView):
    qualquer_perfil = True  # lista os endpoints para quem já entrou no sistema


class Roteador(DefaultRouter):
    APIRootView = RaizDaApi


roteador = Roteador()
roteador.register("categorias", CategoriaViewSet, basename="categoria")  # B2
roteador.register("fornecedores", FornecedorViewSet, basename="fornecedor")  # B2

urlpatterns = [
    path("api/sessoes/", SessaoView.as_view(), name="sessao"),
    path("api/sessoes/atual/", SessaoAtualView.as_view(), name="sessao-atual"),
    path("api/", include(roteador.urls)),
]

# Fora da API também se responde em JSON: não há páginas HTML no sistema.
handler404 = "comum.erros.pagina_nao_encontrada"
handler500 = "comum.erros.erro_interno"

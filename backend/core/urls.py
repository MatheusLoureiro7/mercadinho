"""
Rotas da API — porta única de entrada do sistema (Apostila IV, seção 3).

Todos os endpoints ficam sob /api/, no plural (CLAUDE.md), registrados no roteador abaixo pelas
tarefas que os criam. Exemplo, quando a B3 chegar:

    roteador.register("produtos", ProdutoViewSet, basename="produto")
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

roteador = DefaultRouter()

urlpatterns = [
    path("api/", include(roteador.urls)),
]

# Fora da API também se responde em JSON: não há páginas HTML no sistema.
handler404 = "comum.erros.pagina_nao_encontrada"
handler500 = "comum.erros.erro_interno"

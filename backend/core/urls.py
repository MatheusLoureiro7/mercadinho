"""
Rotas da API — porta única de entrada do sistema (Apostila IV, seção 3).

Todos os endpoints ficam sob /api/, no plural (CLAUDE.md), registrados no roteador abaixo pelas
tarefas que os criam. Exemplo, quando a B3 chegar:

    roteador.register("produtos", ProdutoViewSet, basename="produto")
"""

from django.urls import include, path
from rest_framework.routers import APIRootView, DefaultRouter

from alertas.views import TelegramWebhookView
from cadastro.views import CategoriaViewSet, FornecedorViewSet, ProdutoViewSet
from caixa.views import BalancoView, FechamentoViewSet
from comum.views import SessaoAtualView, SessaoView
from estoque.views import EstoquePorLoteView, EstoquePorProdutoView, LoteViewSet, PerdaViewSet
from vendas.views import ImportacaoViewSet, ItemPendenteViewSet


class RaizDaApi(APIRootView):
    qualquer_perfil = True  # lista os endpoints para quem já entrou no sistema


class Roteador(DefaultRouter):
    APIRootView = RaizDaApi


roteador = Roteador()
roteador.register("categorias", CategoriaViewSet, basename="categoria")  # B2
roteador.register("fornecedores", FornecedorViewSet, basename="fornecedor")  # B2
roteador.register("produtos", ProdutoViewSet, basename="produto")  # B3
roteador.register("lotes", LoteViewSet, basename="lote")  # C2
roteador.register("perdas", PerdaViewSet, basename="perda")  # D1
roteador.register("fechamentos", FechamentoViewSet, basename="fechamento")  # I1
roteador.register("importacoes", ImportacaoViewSet, basename="importacao")  # E5
roteador.register("itens-pendentes", ItemPendenteViewSet, basename="item-pendente")  # E4

urlpatterns = [
    path("api/sessoes/", SessaoView.as_view(), name="sessao"),
    path("api/sessoes/atual/", SessaoAtualView.as_view(), name="sessao-atual"),
    path("api/estoque/", EstoquePorProdutoView.as_view(), name="estoque-produtos"),  # F2
    path("api/estoque/lotes/", EstoquePorLoteView.as_view(), name="estoque-lotes"),  # F2
    path("api/telegram/", TelegramWebhookView.as_view(), name="telegram-webhook"),  # H7
    path("api/balancos/", BalancoView.as_view(), name="balanco"),  # I3
    path("api/", include(roteador.urls)),
]

# Fora da API também se responde em JSON: não há páginas HTML no sistema.
handler404 = "comum.erros.pagina_nao_encontrada"
handler500 = "comum.erros.erro_interno"

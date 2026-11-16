"""
RN14 — três perfis de acesso (requisito RF14: controlar o acesso por perfil). Tarefa A4.

A verificação acontece na camada de autenticação da API, ANTES de qualquer operação e antes de
tocar no banco (Apostila IV, operação 01, passo 3) — nunca dentro da regra de negócio.

Cada endpoint declara a tela a que pertence:

    class ProdutoViewSet(ModelViewSet):
        tela = "produtos"

Endpoint que serve a duas telas pode declarar uma tela só para leitura (GET):

    class CategoriaViewSet(...):
        tela = "produtos"                 # criar e editar: OPERACAO
        tela_leitura = "consulta_estoque" # ler: os três perfis (decisão da L18)

Endpoint que não declara a tela é recusado para todos (falha fechada): esquecer a declaração
nunca abre o acesso.

Únicas exceções: o login (SessaoView, AllowAny) e o webhook do Telegram (SoOTelegram, H7).
"""

import hmac

from django.conf import settings
from rest_framework.permissions import SAFE_METHODS, BasePermission

DONO, GESTAO, OPERACAO = "DONO", "GESTAO", "OPERACAO"

# Tabela da RN14 (docs/REGRAS-NEGOCIO.md), montada a partir do mapa de navegação da Apostila II.
# O Telegram do DONO não é tela: o recebimento das respostas dele é tratado na tarefa H7.
ACESSO_POR_TELA: dict[str, frozenset[str]] = {
    "produtos": frozenset({OPERACAO}),
    "fornecedores": frozenset({OPERACAO}),
    "entrada_mercadoria": frozenset({OPERACAO}),
    "avarias": frozenset({OPERACAO}),
    "importacao_vendas": frozenset({OPERACAO}),
    "consulta_estoque": frozenset({DONO, GESTAO, OPERACAO}),
    "fechamento_caixa": frozenset({GESTAO}),
    "balanco_semana": frozenset({GESTAO}),
}


def telas_do_papel(papel: str) -> list[str]:
    """As telas que entram no menu de quem tem este papel (tela de Login, Apostila II)."""
    return [tela for tela, papeis in ACESSO_POR_TELA.items() if papel in papeis]


class SoOTelegram(BasePermission):
    """
    H7 — o webhook do Telegram (POST /api/telegram/), operação 03, passo 13. Exceção à regra do `tela`
    decidida pelo grupo em 09/10/2026: quem chama é o Telegram, não uma pessoa logada (RN14: "Telegram,
    sem tela, só DONO"). Passa só quem traz o segredo combinado no setWebhook (cabeçalho
    X-Telegram-Bot-Api-Secret-Token), comparado em tempo constante. Sem segredo configurado, ninguém
    passa. Que o clique é do DONO quem confere é alertas.respostas.
    """

    message = "Este endereço é só do Telegram."

    def has_permission(self, request, view):
        segredo = settings.TELEGRAM_WEBHOOK_SEGREDO
        recebido = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        return bool(segredo) and hmac.compare_digest(recebido.encode(), segredo.encode())


class PermissaoPorTela(BasePermission):
    """
    Permissão padrão de toda a API (REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"]).

    - Sem login → 401.
    - `qualquer_perfil = True` na view → qualquer um dos três papéis (ex.: "quem sou eu").
    - `tela = "..."` na view → só os papéis da tabela da RN14.
    - `tela_leitura = "..."` → vale no lugar de `tela` para GET, HEAD e OPTIONS.
    - Nenhum dos dois → recusado.
    """

    message = "O seu perfil não tem acesso a esta parte do sistema."

    def has_permission(self, request, view):
        usuario = request.user
        if not (usuario and usuario.is_authenticated):
            return False
        if getattr(view, "qualquer_perfil", False):
            return True
        tela = getattr(view, "tela", None)
        if request.method in SAFE_METHODS:
            tela = getattr(view, "tela_leitura", tela)
        if tela is None:
            return False
        return usuario.papel in ACESSO_POR_TELA[tela]

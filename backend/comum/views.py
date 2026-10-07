"""
Sessão — o que a tela de Login usa (Apostila II). Tarefa A4.

    POST /api/sessoes/         entra no sistema: {"login", "senha"} → token + usuário + menu
    GET  /api/sessoes/atual/   quem está usando o sistema agora, e o menu do papel

Sair do sistema é o painel descartar o token; não há nada para apagar no servidor (L09).
"""

from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from comum.autenticacao import gerar_token
from comum.permissoes import telas_do_papel


class EntradaSerializer(serializers.Serializer):
    login = serializers.CharField(max_length=60)
    senha = serializers.CharField(max_length=128, trim_whitespace=False)


def _dados_do_usuario(usuario) -> dict:
    return {
        "id": usuario.pk,
        "nome": usuario.nome,
        "login": usuario.login,
        "papel": usuario.papel,
        "telas": telas_do_papel(usuario.papel),
    }


class SessaoView(APIView):
    permission_classes = [AllowAny]
    # RNF12: limite de tentativas de login por endereço, contra adivinhação de senha.
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        entrada = EntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        usuario = authenticate(
            request._request,
            login=entrada.validated_data["login"],
            password=entrada.validated_data["senha"],
        )
        if usuario is None:  # login inexistente, senha errada ou usuário desativado: mesma resposta
            raise AuthenticationFailed("Login ou senha incorretos.")
        return Response(
            {
                "token": gerar_token(usuario),
                "validade_horas": settings.SESSAO_VALIDADE_HORAS,
                "usuario": _dados_do_usuario(usuario),
            },
            status=status.HTTP_201_CREATED,
        )


class SessaoAtualView(APIView):
    qualquer_perfil = True

    def get(self, request):
        return Response(_dados_do_usuario(request.user))

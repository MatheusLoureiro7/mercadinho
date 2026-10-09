"""
Webhook do Telegram — tarefa H7. Operação 03, passo 13: "Webhook recebe a resposta 'Sim, pedir'".

    POST /api/telegram/      quem chama é o Telegram, não uma pessoa logada

Sem login de usuário: a porta é o segredo do Telegram (comum.permissoes.SoOTelegram), decisão do
grupo em 09/10/2026. A regra (é do dono? o aviso vale?) mora em alertas.respostas, não aqui.
Responde sempre 200 a quem passou pela porta — senão o Telegram reenvia o mesmo clique sem parar.
"""

from rest_framework.response import Response
from rest_framework.views import APIView

from alertas.respostas import receber_atualizacao
from alertas.telegram import CanalTelegram
from comum.permissoes import SoOTelegram


class TelegramWebhookView(APIView):
    authentication_classes = []  # nenhum login de usuário vale aqui: só o segredo do Telegram
    permission_classes = [SoOTelegram]

    def post(self, request):
        receber_atualizacao(request.data, CanalTelegram.configurado())
        return Response({"ok": True})

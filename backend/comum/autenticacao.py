"""
Autenticação da API por token assinado — tarefa A4, decisão da L09 (docs/LACUNAS.md).

O token é gerado no login e enviado pelo painel em toda requisição:

    Authorization: Bearer <token>

Ele é assinado com a SECRET_KEY e não fica gravado em tabela nenhuma (o modelo de dados da
Apostila IV não tem tabela de sessão). Deixa de valer quando:
- passa de SESSAO_VALIDADE_HORAS desde o login;
- a senha do usuário é trocada (o token carrega uma impressão do hash da senha);
- o usuário é desativado (`usuario.ativo = false`).
"""

from django.conf import settings
from django.core import signing
from django.utils.crypto import constant_time_compare, salted_hmac
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from cadastro.models import Usuario

_SAL = "mercadinho.sessao"
_PREFIXO = b"bearer"

MENSAGEM_SESSAO_INVALIDA = "Sessão inválida. Entre no sistema de novo."
MENSAGEM_SESSAO_VENCIDA = "Sua sessão expirou. Entre no sistema de novo."


def _impressao_da_senha(usuario: Usuario) -> str:
    return salted_hmac(_SAL, usuario.password).hexdigest()[:16]


def gerar_token(usuario: Usuario) -> str:
    return signing.dumps({"u": usuario.pk, "s": _impressao_da_senha(usuario)}, salt=_SAL)


def usuario_do_token(token: str) -> Usuario:
    try:
        dados = signing.loads(token, salt=_SAL, max_age=settings.SESSAO_VALIDADE_HORAS * 3600)
    except signing.SignatureExpired as exc:
        raise AuthenticationFailed(MENSAGEM_SESSAO_VENCIDA) from exc
    except signing.BadSignature as exc:
        raise AuthenticationFailed(MENSAGEM_SESSAO_INVALIDA) from exc

    usuario = Usuario.objects.filter(pk=dados.get("u"), ativo=True).first()
    if usuario is None or not constant_time_compare(dados.get("s", ""), _impressao_da_senha(usuario)):
        raise AuthenticationFailed(MENSAGEM_SESSAO_INVALIDA)
    return usuario


class AutenticacaoPorToken(BaseAuthentication):
    def authenticate(self, request):
        partes = get_authorization_header(request).split()
        if not partes or partes[0].lower() != _PREFIXO:
            return None  # sem token: a permissão decide (e responde 401)
        if len(partes) != 2:
            raise AuthenticationFailed(MENSAGEM_SESSAO_INVALIDA)
        token = partes[1].decode("latin-1")
        return (usuario_do_token(token), token)

    def authenticate_header(self, request):
        return 'Bearer realm="api"'

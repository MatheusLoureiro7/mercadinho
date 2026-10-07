"""
Tratamento de erro da API — tarefa A3.

Toda resposta de erro tem o mesmo formato, para o painel mostrar a mensagem sem precisar
interpretar o código HTTP:

    {"erro": {"codigo": "validacao", "mensagem": "Confira os campos destacados.",
              "campos": {"durabilidade_dias": ["Este campo é obrigatório."]}}}

- `codigo`: identificador fixo, para o painel decidir o que fazer.
- `mensagem`: texto para a tela, no vocabulário da loja (RNF10).
- `campos`: só em erro de validação; aponta cada campo com problema, para a tela manter o que já
  foi digitado e marcar só o que falta (fluxograma 01).
- `regra`: só quando quem recusou foi uma regra de negócio (RN01 a RN16).
- `id`: só em erro inesperado; é o mesmo código gravado no log, para a equipe achar o problema.
"""

import logging
import uuid

from django.core.exceptions import PermissionDenied
from django.http import Http404, JsonResponse
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as tratador_padrao_do_drf

logger = logging.getLogger("mercadinho.erros")

MENSAGEM_ERRO_INTERNO = "Algo deu errado do nosso lado. Avise a equipe e informe o código {id}."

# Exceção do DRF → (codigo, mensagem). A ordem importa: subclasses antes das classes-mãe.
# Mensagem None: usa o texto que veio na própria exceção.
_MENSAGENS = [
    (exceptions.ValidationError, "validacao", "Confira os campos destacados."),
    (
        exceptions.ParseError,
        "requisicao_invalida",
        "Os dados enviados estão num formato que o sistema não entende.",
    ),
    (exceptions.NotAuthenticated, "nao_autenticado", "Entre no sistema para continuar."),
    (exceptions.AuthenticationFailed, "nao_autenticado", None),  # a mensagem vem de quem recusou
    (exceptions.PermissionDenied, "sem_permissao", "O seu perfil não tem acesso a esta parte do sistema."),
    (exceptions.NotFound, "nao_encontrado", "Não encontramos o que você procurou."),
    (exceptions.MethodNotAllowed, "metodo_nao_permitido", "Esta operação não existe neste endereço."),
    (
        exceptions.Throttled,
        "muitas_tentativas",
        "Muitas tentativas seguidas. Espere um minuto e tente de novo.",
    ),
]


class ErroDeRegraDeNegocio(Exception):
    """
    Levantada pelos módulos de serviço quando uma regra de negócio recusa a operação.

    A regra mora no serviço, não na view (CLAUDE.md); a API só traduz a recusa em resposta 400.

        raise ErroDeRegraDeNegocio(
            "RN03",
            "Produto perecível precisa do prazo de durabilidade em dias. ...",
            campo="durabilidade_dias",
        )
    """

    def __init__(self, regra: str, mensagem: str, campo: str | None = None):
        super().__init__(mensagem)
        self.regra = regra
        self.mensagem = mensagem
        self.campo = campo


def _corpo(codigo: str, mensagem: str, **extras) -> dict:
    erro = {"codigo": codigo, "mensagem": mensagem}
    erro.update({chave: valor for chave, valor in extras.items() if valor is not None})
    return {"erro": erro}


def _em_texto(detalhe):
    """Converte o detalhe de erro do DRF (ErrorDetail, listas, dicionários) em texto simples."""
    if isinstance(detalhe, dict):
        return {str(chave): _em_texto(valor) for chave, valor in detalhe.items()}
    if isinstance(detalhe, list):
        return [_em_texto(item) for item in detalhe]
    return str(detalhe)


def _codigo_e_mensagem(exc: exceptions.APIException) -> tuple[str, str]:
    for classe, codigo, mensagem in _MENSAGENS:
        if isinstance(exc, classe):
            return codigo, mensagem if mensagem is not None else str(exc.detail)
    return exc.default_code, str(exc.detail)  # qualquer outra exceção do DRF: usa o texto dela


def tratar_excecao(exc, contexto):
    """Tratador de exceção da API (REST_FRAMEWORK["EXCEPTION_HANDLER"])."""
    if isinstance(exc, ErroDeRegraDeNegocio):
        campos = {exc.campo: [exc.mensagem]} if exc.campo else None
        return Response(
            _corpo("regra_de_negocio", exc.mensagem, regra=exc.regra, campos=campos),
            status=status.HTTP_400_BAD_REQUEST,
        )

    resposta = tratador_padrao_do_drf(exc, contexto)

    if resposta is None:
        id_erro = uuid.uuid4().hex[:8]
        logger.error("Erro inesperado [%s]", id_erro, exc_info=exc)
        return Response(
            _corpo("erro_interno", MENSAGEM_ERRO_INTERNO.format(id=id_erro), id=id_erro),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # O tratador do DRF já converteu Http404 e PermissionDenied do Django; aqui só traduzimos.
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    codigo, mensagem = _codigo_e_mensagem(exc)

    campos = None
    if isinstance(exc, exceptions.ValidationError):
        detalhe = _em_texto(exc.detail)
        if isinstance(detalhe, dict):
            campos = detalhe
        else:  # erro que não é de um campo só, por exemplo uma combinação inválida
            mensagem = detalhe[0] if detalhe else mensagem

    resposta.data = _corpo(codigo, mensagem, campos=campos)
    return resposta


# --- Fora da API ---------------------------------------------------------------------------------
# O Django só usa estas duas com DEBUG desligado. Não há páginas HTML no sistema (o painel é
# estático), então até o endereço errado responde em JSON.


def pagina_nao_encontrada(request, exception=None):
    return JsonResponse(
        _corpo("nao_encontrado", "Não encontramos o que você procurou."),
        status=status.HTTP_404_NOT_FOUND,
        json_dumps_params={"ensure_ascii": False},
    )


def erro_interno(request):
    # O detalhe técnico já foi para o log pelo próprio Django (logger django.request).
    return JsonResponse(
        _corpo("erro_interno", "Algo deu errado do nosso lado. Avise a equipe."),
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        json_dumps_params={"ensure_ascii": False},
    )

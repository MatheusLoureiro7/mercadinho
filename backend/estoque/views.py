"""
Estoque — endpoints. Tarefa C2: entrada de mercadoria. Tarefa D1: perdas. Tarefa F2: consulta.

/api/lotes/ — tela Entrada de mercadoria, só OPERACAO (RN14).
    POST                     registra a carga que chegou (operação 02)
    GET ?data_entrada=AAAA-MM-DD&produto=<id>   a lista do dia (passo 11)
    GET /api/lotes/{id}/

Lote não se edita nem se apaga: mudar a quantidade dele desalinharia o saldo (RN01). Correção de
estoque é por entrada ou por perda, que deixam rastro em movimentação. Não há operação de ajuste
(lacuna L10, aberta).
"""

from datetime import date

from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from comum.busca import filtrar_por_nome
from estoque.consulta import Situacao, posicao_por_lote, posicao_por_produto
from estoque.entrada import registrar_entrada
from estoque.models import Lote, Movimentacao
from estoque.perda import registrar_perda
from estoque.saldo import saldo_do_produto
from estoque.serializers import (
    EntradaDeLoteSerializer,
    LoteRegistradoSerializer,
    LoteSerializer,
    PerdaSerializer,
    PosicaoPorLoteSerializer,
    PosicaoPorProdutoSerializer,
    RegistroDePerdaSerializer,
)

_SIM = {"1", "true", "sim"}
_NAO = {"0", "false", "nao", "não", ""}


def _sim_ou_nao(parametros, nome: str) -> bool:
    valor = parametros.get(nome, "").strip().lower()
    if valor in _SIM:
        return True
    if valor in _NAO:
        return False
    raise ValidationError({nome: ["Use 1 para sim ou 0 para não."]})


def _id(parametros, nome: str) -> int | None:
    valor = parametros.get(nome)
    if not valor:
        return None
    if not valor.isdigit():
        raise ValidationError({nome: [f"Filtro de {nome} inválido."]})
    return int(valor)


class LoteViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    tela = "entrada_mercadoria"
    serializer_class = LoteSerializer

    def get_queryset(self):
        lotes = Lote.objects.select_related("produto", "fornecedor").order_by("-id")
        parametros = self.request.query_params
        if data_entrada := parametros.get("data_entrada"):
            try:
                lotes = lotes.filter(data_entrada=date.fromisoformat(data_entrada))
            except ValueError as erro:
                raise ValidationError({"data_entrada": ["Use a data no formato AAAA-MM-DD."]}) from erro
        if produto := parametros.get("produto"):
            if not produto.isdigit():
                raise ValidationError({"produto": ["Filtro de produto inválido."]})
            lotes = lotes.filter(produto_id=int(produto))
        return lotes

    def create(self, request):
        entrada = EntradaDeLoteSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        lote = registrar_entrada(usuario=request.user, **entrada.validated_data)
        return Response(LoteRegistradoSerializer(lote).data, status=status.HTTP_201_CREATED)


class PerdaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    /api/perdas/ — tela Avarias e quebras, só OPERACAO (RN14). RF04, fluxograma 03.

    POST                               registra a perda: {"produto", "quantidade", "motivo", "lote"?}
    GET ?data=AAAA-MM-DD&produto=<id>  o caderno de avarias, mais recente primeiro

    Perda registrada não se apaga (RN01: nada é apagado em movimentação).
    """

    tela = "avarias"
    serializer_class = PerdaSerializer

    def get_queryset(self):
        perdas = Movimentacao.objects.filter(tipo=Movimentacao.Tipo.PERDA).select_related(
            "produto", "lote", "usuario"
        )
        parametros = self.request.query_params
        if data := parametros.get("data"):
            try:
                perdas = perdas.filter(data_hora__date=date.fromisoformat(data))  # dia da loja
            except ValueError as erro:
                raise ValidationError({"data": ["Use a data no formato AAAA-MM-DD."]}) from erro
        if produto := parametros.get("produto"):
            if not produto.isdigit():
                raise ValidationError({"produto": ["Filtro de produto inválido."]})
            perdas = perdas.filter(produto_id=int(produto))
        return perdas.order_by("-data_hora", "-id")

    def create(self, request):
        entrada = RegistroDePerdaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        perdas = registrar_perda(usuario=request.user, **entrada.validated_data)
        produto = entrada.validated_data["produto"]
        return Response(
            {
                "perdas": PerdaSerializer(perdas, many=True).data,
                "saldo_produto": f"{saldo_do_produto(produto):.3f}",
            },
            status=status.HTTP_201_CREATED,
        )


class EstoquePorProdutoView(generics.ListAPIView):
    """
    /api/estoque/ — Consulta de estoque por produto (RF07). Os três perfis (RN14). Só leitura.

    ?categoria=<id>  ?busca=<parte do nome>  ?abaixo_do_minimo=1  ?validade_proxima=1
    (validade_proxima: produtos com lote vencido ou vencendo)
    """

    tela = "consulta_estoque"
    serializer_class = PosicaoPorProdutoSerializer

    def get_queryset(self):
        parametros = self.request.query_params
        produtos = posicao_por_produto(hoje=timezone.localdate())
        if (categoria := _id(parametros, "categoria")) is not None:
            produtos = produtos.filter(categoria_id=categoria)
        produtos = filtrar_por_nome(produtos, "nome", parametros.get("busca", ""))
        if _sim_ou_nao(parametros, "abaixo_do_minimo"):
            produtos = produtos.filter(abaixo_do_minimo=True)
        if _sim_ou_nao(parametros, "validade_proxima"):
            produtos = produtos.filter(Q(lotes_vencidos__gt=0) | Q(lotes_vencendo__gt=0))
        return produtos


class EstoquePorLoteView(generics.ListAPIView):
    """
    /api/estoque/lotes/ — Consulta de estoque por lote, com destaque para vencidos (RN16) e
    vencendo (RF07). Os três perfis (RN14). Só leitura.

    ?categoria=<id>  ?produto=<id>  ?busca=<parte do nome>  ?situacao=VENCIDO,VENCENDO,OK,SEM_VALIDADE
    """

    tela = "consulta_estoque"
    serializer_class = PosicaoPorLoteSerializer

    def get_queryset(self):
        parametros = self.request.query_params
        lotes = posicao_por_lote(hoje=timezone.localdate())
        if (categoria := _id(parametros, "categoria")) is not None:
            lotes = lotes.filter(produto__categoria_id=categoria)
        if (produto := _id(parametros, "produto")) is not None:
            lotes = lotes.filter(produto_id=produto)
        lotes = filtrar_por_nome(lotes, "produto__nome", parametros.get("busca", ""))
        if situacao := parametros.get("situacao", "").strip():
            pedidas = {item.strip().upper() for item in situacao.split(",") if item.strip()}
            if not pedidas <= set(Situacao.values):
                raise ValidationError({"situacao": ["Use VENCIDO, VENCENDO, OK ou SEM_VALIDADE."]})
            lotes = lotes.filter(situacao__in=pedidas)
        return lotes

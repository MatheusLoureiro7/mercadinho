"""
Gerador do aviso de ruptura e de fim de semana — tarefa H3 (RN08, RN10). Passos 6 a 8 da operação
03, na rodada diária, logo depois da previsão (G3).

RN08: saldo <= ponto_pedido → aviso RUPTURA, no vocabulário da loja (RNF10):
      "Frango resfriado 1 kg acaba em 2 dias — sobram 6 KG. Pedir 30 KG — Granja Boa Vista entrega
      em 2 dias."
RN10: na quinta, produto crítico de fim de semana com saldo <= ponto_pedido × (1 + folga ÷ 100)
      → aviso FIM_SEMANA. L03 (decisão do grupo, 12/11/2026): sem calendário de feriados nesta
      versão — só sábado e domingo; véspera de feriado fica fora do escopo, declarado.

Decisões da H3 (docs/ACOMPANHAMENTO.md, 12/11/2026), as mesmas da H2 onde cabem:
- sem ponto de pedido não há aviso: produto "ainda aprendendo" (RN09) ou sem fornecedor (G3);
- todo dia, enquanto a condição valer; rodar duas vezes no mesmo dia não duplica; o aviso de um
  dia anterior que ainda não saiu dá lugar ao de hoje;
- urgência (L11): ALTA quando acabou ou acaba antes de a entrega chegar; MEDIA nos outros casos;
  fim de semana, MEDIA;
- produto crítico já abaixo do ponto de pedido na quinta recebe só o aviso de "vai acabar", que
  tem o botão "Sim, pedir" (H7) — não dois avisos do mesmo produto;
- depois que o Sr. João responde "Sim, pedir" (decisão do grupo, 12/11/2026), o produto não é
  avisado de novo até chegar um lote novo dele: o pedido está a caminho. Lote que entra no mesmo
  dia do aviso respondido conta como chegado (o aviso nasce às 03h00, a entrega vem depois);
- esse silêncio dura o prazo de entrega do fornecedor padrão (decisão do grupo, 16/11/2026,
  revisão X1 item 5): "Sim, pedir" no dia 9, entrega em 2 dias, espera até o dia 11; sem lote
  novo, no dia 12 o aviso volta com "O pedido ainda não chegou: " na frente.

O saldo vem de `estoque.saldo` (RN01) e a previsão de previsao_produto; este módulo não lê
movimentação (guarda da RN11, tarefa D2).
"""

from datetime import date, timedelta
from decimal import ROUND_FLOOR, Decimal

from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from alertas.estados import cancelar_os_abertos
from alertas.models import Alerta
from alertas.respostas import RESPOSTA_PEDIR
from alertas.servicos import criar_aviso
from cadastro.models import Usuario
from comum.formatos import quantidade_na_loja
from comum.parametros import parametro_inteiro
from estoque.models import Lote
from estoque.saldo import saldos_de_todos
from previsao.models import PrevisaoProduto

QUINTA = 4  # isoweekday: a RN10 avalia o fim de semana na quinta-feira


def _quando(previsao: PrevisaoProduto) -> str:
    dias = int(previsao.dias_ate_acabar.to_integral_value(rounding=ROUND_FLOOR))
    return {0: "acaba hoje", 1: "acaba amanhã"}.get(dias, f"acaba em {dias} dias")


def _mensagem(previsao: PrevisaoProduto, saldo: Decimal) -> str:
    produto = previsao.produto
    if saldo <= 0:
        texto = f"{produto.nome} acabou — não tem mais no estoque."
    else:
        sobram = quantidade_na_loja(saldo, produto.unidade_medida)
        texto = f"{produto.nome} {_quando(previsao)} — sobram {sobram}."
    if previsao.sugestao_compra:
        fornecedor = produto.fornecedor_padrao
        prazo = fornecedor.prazo_entrega_dias
        entrega = "1 dia" if prazo == 1 else f"{prazo} dias"
        pedir = quantidade_na_loja(previsao.sugestao_compra, produto.unidade_medida)
        texto += f" Pedir {pedir} — {fornecedor.nome} entrega em {entrega}."
    return texto


def _acaba_antes_da_entrega(previsao: PrevisaoProduto, saldo: Decimal) -> bool:
    prazo = previsao.produto.fornecedor_padrao.prazo_entrega_dias
    return saldo <= 0 or (previsao.dias_ate_acabar is not None and previsao.dias_ate_acabar < prazo)


def _pedidos_sem_entrega(hoje: date) -> tuple[set[int], set[int]]:
    """
    Produtos com "Sim, pedir" respondido e nenhum lote entrado desde o dia daquele aviso, separados
    em (ainda no prazo de entrega, prazo já passou).
    """
    ultimo_sim = (
        Alerta.objects.filter(tipo=Alerta.Tipo.RUPTURA, resposta_usuario=RESPOSTA_PEDIR)
        .values("produto_id", "produto__fornecedor_padrao__prazo_entrega_dias")
        .annotate(quando=Max("gerado_em"))
        .order_by()
    )
    ultima_entrada = dict(
        Lote.objects.values("produto_id")
        .annotate(dia=Max("data_entrada"))
        .order_by()
        .values_list("produto_id", "dia")
    )
    a_caminho, atrasados = set(), set()
    for linha in ultimo_sim:
        dia_do_sim = timezone.localdate(linha["quando"])
        entrada = ultima_entrada.get(linha["produto_id"])
        if entrada is not None and entrada >= dia_do_sim:
            continue
        prazo = linha["produto__fornecedor_padrao__prazo_entrega_dias"] or 0
        no_prazo = hoje <= dia_do_sim + timedelta(days=prazo)
        (a_caminho if no_prazo else atrasados).add(linha["produto_id"])
    return a_caminho, atrasados


def gerar_avisos_de_ruptura(*, hoje: date | None = None) -> list[Alerta]:
    """Grava os avisos PENDENTES de "vai acabar" (RN08) e, na quinta, de fim de semana (RN10)."""
    hoje = hoje or timezone.localdate()  # o dia da loja, nunca o CURRENT_DATE (UTC) do banco
    e_quinta = hoje.isoweekday() == QUINTA
    folga = Decimal(1) + Decimal(parametro_inteiro("folga_fim_semana_pct")) / 100
    destinatario = Usuario.objects.filter(papel=Usuario.Papel.DONO, ativo=True).order_by("pk").first()
    saldos = saldos_de_todos()
    a_caminho, atrasados = _pedidos_sem_entrega(hoje)
    tipos = [Alerta.Tipo.RUPTURA, Alerta.Tipo.FIM_SEMANA]
    ja_avisados_hoje = set(
        Alerta.objects.filter(tipo__in=tipos, gerado_em__date=hoje).values_list("produto_id", "tipo")
    )
    previsoes = (
        PrevisaoProduto.objects.filter(calculado_em__isnull=False, ponto_pedido__isnull=False)
        .select_related("produto__fornecedor_padrao")
        .order_by("produto__nome", "produto_id")
    )

    criados = []
    with transaction.atomic():
        for previsao in previsoes:
            produto = previsao.produto
            if produto.pk in a_caminho:
                continue
            saldo = saldos.get(produto.pk, Decimal(0))
            if saldo <= previsao.ponto_pedido:
                tipo = Alerta.Tipo.RUPTURA
                prefixo = "O pedido ainda não chegou: " if produto.pk in atrasados else ""
                severidade = (
                    Alerta.Severidade.ALTA
                    if _acaba_antes_da_entrega(previsao, saldo)
                    else Alerta.Severidade.MEDIA
                )
            elif e_quinta and produto.critico_fim_semana and saldo <= previsao.ponto_pedido * folga:
                tipo, prefixo, severidade = (
                    Alerta.Tipo.FIM_SEMANA,
                    "Para o fim de semana: ",
                    Alerta.Severidade.MEDIA,
                )
            else:
                continue
            if (produto.pk, tipo) in ja_avisados_hoje:
                continue
            cancelar_os_abertos(Alerta.objects.filter(tipo=tipo, produto=produto))
            criados.append(
                criar_aviso(
                    produto=produto,
                    tipo=tipo,
                    severidade=severidade,
                    mensagem=prefixo + _mensagem(previsao, saldo),
                    destinatario=destinatario,
                )
            )
    return criados

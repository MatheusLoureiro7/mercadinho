"""
Gerador do aviso de validade — tarefa H2 (RN05). Passos 6 a 8 da operação 03, na rodada diária.

> Gera um aviso quando um lote de produto perecível está a N dias ou menos do vencimento.
  Condição: lote.data_validade − hoje ≤ dias_aviso_validade AND quantidade_atual > 0.

Decisões da H2 (docs/ACOMPANHAMENTO.md, 08/10/2026):
- todo dia, enquanto o lote estiver no prazo e com mercadoria — a RN13 junta os avisos do dia numa
  mensagem só, a "volta pelas gôndolas" do Sr. João; rodar duas vezes no mesmo dia não duplica;
- lote vencido também avisa (a condição o inclui), dizendo que sai só como perda (RN16);
- o aviso de um dia anterior que ainda não saiu é cancelado e substituído pelo de hoje, que tem a
  contagem de dias certa — senão a mensagem levaria o mesmo lote duas vezes;
- urgência (L11): ALTA para vencido e para o que vence hoje; MEDIA para o que ainda tem dias;
- destinatário: o usuário DONO ativo (o celular dele é ligado na H6). Sem dono, o aviso é gravado
  sem destinatário e não se perde.

Este módulo não lê movimentação: o aviso de validade usa só o lote (guarda da RN11, tarefa D2).
"""

from datetime import date

from django.db import transaction
from django.utils import timezone

from alertas.estados import cancelar_os_abertos
from alertas.models import Alerta
from alertas.servicos import criar_aviso
from cadastro.models import Usuario
from comum.formatos import quantidade_na_loja
from comum.parametros import dias_aviso_validade
from comum.trava import travar
from estoque.models import Lote


def gerar_avisos_de_validade(*, hoje: date | None = None) -> list[Alerta]:
    """Grava um aviso PENDENTE para cada lote no prazo da RN05. Devolve os avisos criados."""
    hoje = hoje or timezone.localdate()  # o dia da loja, nunca o CURRENT_DATE (UTC) do banco
    destinatario = Usuario.objects.filter(papel=Usuario.Papel.DONO, ativo=True).order_by("pk").first()
    candidatos = (
        Lote.objects.filter(produto__perecivel=True, quantidade_atual__gt=0, data_validade__isnull=False)
        .select_related("produto")
        .order_by("data_validade", "id")
    )

    criados = []
    prazos: dict[int, int] = {}  # L01: um prazo por produto, lido uma vez por rodada (X1, item 21)
    with transaction.atomic():
        # Confere "já avisei hoje?" sob a trava: duas rodadas juntas não avisam em dobro (X1, item 16).
        travar("avisos_de_validade")
        ja_avisados_hoje = set(
            Alerta.objects.filter(tipo=Alerta.Tipo.VALIDADE, gerado_em__date=hoje).values_list(
                "lote_id", flat=True
            )
        )
        for lote in candidatos:
            dias = (lote.data_validade - hoje).days
            # L01: o prazo é lido por produto — hoje é global; muda num lugar só quando o grupo decidir.
            if lote.produto_id not in prazos:
                prazos[lote.produto_id] = dias_aviso_validade(lote.produto)
            if dias > prazos[lote.produto_id] or lote.pk in ja_avisados_hoje:
                continue
            # O de dias anteriores que não saiu dá lugar ao de hoje (a gravação de hoje vem logo abaixo).
            cancelar_os_abertos(Alerta.objects.filter(tipo=Alerta.Tipo.VALIDADE, lote=lote))
            criados.append(
                criar_aviso(
                    produto=lote.produto,
                    lote=lote,
                    tipo=Alerta.Tipo.VALIDADE,
                    severidade=Alerta.Severidade.ALTA if dias <= 0 else Alerta.Severidade.MEDIA,
                    mensagem=_mensagem(lote, dias),
                    destinatario=destinatario,
                )
            )
    return criados


def _mensagem(lote: Lote, dias: int) -> str:
    """RNF10: "Presunto vence em 3 dias — 2,5 KG na prateleira." (Apostila I; quantidade como na tela)."""
    nome = lote.produto.nome
    tem = quantidade_na_loja(lote.quantidade_atual, lote.produto.unidade_medida) + " na prateleira"
    if dias < 0:
        quando = "venceu ontem" if dias == -1 else f"venceu há {-dias} dias"
        return f"{nome} {quando} — {tem}. Tire e registre a perda em Avarias e quebras."
    quando = {0: "vence hoje", 1: "vence amanhã"}.get(dias, f"vence em {dias} dias")
    return f"{nome} {quando} — {tem}."

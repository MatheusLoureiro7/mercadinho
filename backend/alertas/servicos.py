"""
Avisos — serviços chamados por outras partes do sistema. Tarefa H1.

- criar_aviso: o único jeito de nascer um aviso; valida tipo, severidade (L11) e mensagem antes de
  gravar. Quem decide QUANDO e COM QUE texto avisar são os geradores (H2 validade, H3 ruptura).
- cancelar_aviso_de_ruptura_pendente: operação 02, passo 10, chamado pela entrada de mercadoria.
"""

from django.utils import timezone

from alertas.estados import cancelar_os_abertos
from alertas.models import Alerta
from cadastro.models import Produto, Usuario
from estoque.models import Lote


def criar_aviso(
    *,
    produto: Produto,
    tipo: str,
    severidade: str,
    mensagem: str,
    lote: Lote | None = None,
    destinatario: Usuario | None = None,
) -> Alerta:
    """Grava um aviso PENDENTE (padrão do schema.sql). Recusa com ValueError o que estiver fora da lista."""
    if tipo not in Alerta.Tipo.values:
        raise ValueError(f"tipo de aviso inválido: {tipo!r}. Use {', '.join(Alerta.Tipo.values)}.")
    if severidade not in Alerta.Severidade.values:
        raise ValueError(
            f"severidade inválida: {severidade!r}. Use {', '.join(Alerta.Severidade.values)} (L11)."
        )
    if not (mensagem or "").strip():
        raise ValueError("mensagem do aviso vazia: é o texto que o Sr. João lê no celular (RNF10).")
    return Alerta.objects.create(
        produto=produto,
        lote=lote,
        # A hora do relógio do sistema, o mesmo que dá o "hoje" da loja (timezone.localdate()): o
        # dia em que o aviso nasce é sempre o dia da rodada que o gerou (achado na H2). Na prática é
        # o NOW() do schema.sql; o padrão do banco continua lá para quem gravar por fora.
        gerado_em=timezone.now(),
        tipo=tipo,
        severidade=severidade,
        mensagem=mensagem.strip(),
        destinatario=destinatario,
    )


def cancelar_aviso_de_ruptura_pendente(produto: Produto) -> int:
    """
    Operação 02, passo 10: chegou mercadoria → cancela o aviso de "vai acabar" do produto que ainda
    não saiu (PENDENTE ou SEGURADO). Aviso de validade e de fim de semana não são tocados; aviso já
    enviado também não. Devolve quantos avisos foram cancelados.
    """
    return cancelar_os_abertos(Alerta.objects.filter(produto=produto, tipo=Alerta.Tipo.RUPTURA))

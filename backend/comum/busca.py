"""
Busca por parte do nome, sem diferença de maiúscula, minúscula ou acento — tarefa B7.

Quem digita no computador da loja nem sempre acerta o acento: "feijao" tem de achar "Feijão
carioca 1 kg" e "acucar" tem de achar "Açúcar refinado". A comparação usa a função translate() do
próprio PostgreSQL, sem extensão nova nem coluna a mais no banco (o modelo de dados é o da
Apostila IV).

    produtos = filtrar_por_nome(Produto.objects.all(), "nome", busca)
    lotes = filtrar_por_nome(Lote.objects.all(), "produto__nome", busca)
"""

from django.db.models import F, Func, QuerySet, Value
from django.db.models.functions import Lower

_COM_ACENTO = "áàâãäéèêëíìîïóòôõöúùûüçñ"
_SEM_ACENTO = "aaaaaeeeeiiiiooooouuuucn"


class _SemAcento(Func):
    function = "TRANSLATE"

    def __init__(self, expressao):
        super().__init__(Lower(expressao), Value(_COM_ACENTO), Value(_SEM_ACENTO))


def sem_acento(texto: str) -> str:
    """O mesmo que a função do banco faz, para o texto que a pessoa digitou."""
    return texto.lower().translate(str.maketrans(_COM_ACENTO, _SEM_ACENTO))


def filtrar_por_nome(consulta: QuerySet, campo: str, busca: str) -> QuerySet:
    busca = (busca or "").strip()
    if not busca:
        return consulta
    return consulta.alias(_nome_sem_acento=_SemAcento(F(campo))).filter(
        _nome_sem_acento__contains=sem_acento(busca)
    )

"""
Leitura dos parâmetros das regras (tabela parametro). Nunca escreva estes números no código.
"""

from comum.models import Parametro


def parametro(chave: str) -> str:
    try:
        return Parametro.objects.values_list("valor", flat=True).get(chave=chave)
    except Parametro.DoesNotExist as erro:
        raise LookupError(f"Parâmetro '{chave}' não está cadastrado na tabela parametro.") from erro


def parametro_inteiro(chave: str) -> int:
    return int(parametro(chave))


def dias_aviso_validade(produto=None) -> int:
    """
    RN05: antecedência, em dias, para "vencendo" e para o aviso de validade.

    L01 (aberta): a RN05 diz que o valor "vale por categoria", mas a tabela parametro só tem uma
    chave global. Por isso o valor é lido por produto: quando o grupo decidir, muda só aqui.
    """
    return parametro_inteiro("dias_aviso_validade")

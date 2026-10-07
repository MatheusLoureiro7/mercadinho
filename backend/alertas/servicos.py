"""
Avisos — serviços chamados por outras partes do sistema.

A tabela `alerta` e o motor de avisos chegam no bloco H. Os pontos de chamada já existem para que
as operações que dependem deles não precisem ser reabertas depois.
"""

from cadastro.models import Produto


def cancelar_aviso_de_ruptura_pendente(produto: Produto) -> int:
    """
    Operação 02, passo 10: chegou mercadoria → cancela o aviso de "vai acabar" pendente do produto.

    Ainda não há avisos: a tabela `alerta` é a tarefa H1, que implementa este cancelamento
    (status PENDENTE/SEGURADO → CANCELADO, tipo RUPTURA). Devolve quantos avisos foram cancelados.
    """
    return 0

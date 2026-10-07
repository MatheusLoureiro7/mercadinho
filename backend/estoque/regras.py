"""
Regras de negócio do estoque. Chamadas pelos serviços (estoque/entrada.py e os que vierem) antes de
gravar — a regra não mora na view nem na tela, e vale para qualquer caminho que grave lote.
"""

from datetime import date, timedelta

from cadastro.models import Produto
from comum.erros import ErroDeRegraDeNegocio

MENSAGEM_RN04 = "Essa validade já passou. Confira a data na embalagem."


def validade_do_lote(
    produto: Produto, *, data_entrada: date, data_validade: date | None, hoje: date
) -> date | None:
    """
    RN04 — Lote de perecível precisa de data de validade (tarefa C3). Operação 02, passos 3 a 5.

    > Ao registrar a entrada de um lote de produto perecível, a data de validade é obrigatória. Se
    > não for informada, o sistema calcula automaticamente somando a durabilidade do produto à data
    > de entrada. Validade anterior à data de hoje é recusada.

    Nesta ordem:
    1. não perecível → validade opcional, segue;
    2. perecível com validade informada → usa ela;
    3. perecível sem validade → data_entrada + durabilidade_dias (a RN03 garante a durabilidade);
    4. validade (informada ou calculada) anterior a hoje → recusa.

    `hoje` é o dia da loja (timezone.localdate()), nunca o CURRENT_DATE do banco, que é UTC.
    Devolve a validade que vai para o lote.
    """
    if produto.perecivel and data_validade is None:
        data_validade = data_entrada + timedelta(days=produto.durabilidade_dias)

    if data_validade is not None and data_validade < hoje:
        raise ErroDeRegraDeNegocio("RN04", MENSAGEM_RN04, campo="data_validade")

    return data_validade

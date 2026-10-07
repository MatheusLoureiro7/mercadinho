"""
Regras de negócio do cadastro. Chamadas pela API antes de gravar (e, no futuro, por qualquer outro
caminho que crie produto, como a carga inicial J2) — a regra não mora na view nem na tela.
"""

from comum.erros import ErroDeRegraDeNegocio

MENSAGEM_RN03 = (
    "Produto perecível precisa do prazo de durabilidade em dias. "
    "Sem ele o sistema não consegue avisar quando o produto vai vencer."
)


def verificar_rn03(perecivel: bool, durabilidade_dias: int | None) -> None:
    """
    RN03 — Produto perecível exige prazo de durabilidade (tarefa B4).

    > Um produto marcado como perecível só pode ser salvo com o campo de durabilidade em dias
    > preenchido e maior que zero.

    O banco tem a mesma condição (ck_produto_rn03) como última linha de defesa.
    """
    if perecivel and (durabilidade_dias is None or durabilidade_dias <= 0):
        raise ErroDeRegraDeNegocio("RN03", MENSAGEM_RN03, campo="durabilidade_dias")

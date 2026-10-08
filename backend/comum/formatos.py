"""
Como a loja escreve números nas frases do sistema (RNF10) — as mesmas regras da tela
(frontend/js/formatos.js), para a mensagem da API e a do celular baterem com o que se vê na tela.
"""

from decimal import Decimal


def quantidade_na_loja(valor: Decimal, unidade: str) -> str:
    """ "3 UN", "2 KG", "2,5 KG", "0,125 KG" — vírgula e sem zeros sobrando (achado na D3)."""
    return f"{Decimal(valor).normalize():f}".replace(".", ",") + f" {unidade}"

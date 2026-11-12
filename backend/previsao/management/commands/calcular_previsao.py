"""
Previsão de cada produto — tarefa G3. Operação 03, passos 4 e 5; vem depois de `agregar_consumo`.

    python backend/manage.py calcular_previsao

Regrava previsao_produto: consumo médio e por dia da semana, dias até acabar, ponto de pedido e
sugestão de compra (RN06, RN07, RN08, RF11). A ordem da rodada das 03h00 (G5) é:
importação → previsão → regras → notificação.
"""

from django.core.management.base import BaseCommand

from previsao.projecao import calcular_previsao


class Command(BaseCommand):
    help = "Calcula a previsão de cada produto (previsao_produto, RN06–RN08, RF11)."

    def handle(self, *args, **opcoes):
        produtos = calcular_previsao()
        self.stdout.write(f"Previsão calculada para {produtos} produto(s).")

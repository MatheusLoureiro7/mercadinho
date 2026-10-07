"""
Parâmetros iniciais — o INSERT do schema.sql (Apostila I, seção 7), copiado literalmente.

ATENÇÃO: nenhum destes valores foi confirmado pelo cliente. São propostas da equipe e o primeiro
assunto da próxima conversa com ele.
"""

from django.db import migrations

PARAMETROS_INICIAIS = [
    ("dias_aviso_validade", "3", "Antecedência do aviso de vencimento, em dias (RN05)"),
    ("estoque_seguranca_pct", "20", "Folga percentual somada ao ponto de pedido (RN08)"),
    ("janela_silencio_manha", "10:30-13:00", "Primeiro pico de venda — nada é enviado (RN12)"),
    ("janela_silencio_tarde", "16:30-18:00", "Segundo pico de venda — nada é enviado (RN12)"),
    ("historico_minimo_dias", "14", "Mínimo de histórico para o sistema projetar (RN09)"),
    ("folga_fim_semana_pct", "40", "Acréscimo nos itens críticos de fim de semana (RN10)"),
    ("hora_rodada_diaria", "03:00", "Horário em que os cálculos rodam"),
]


def criar(apps, schema_editor):
    Parametro = apps.get_model("comum", "Parametro")
    for chave, valor, descricao in PARAMETROS_INICIAIS:
        Parametro.objects.get_or_create(chave=chave, defaults={"valor": valor, "descricao": descricao})


def apagar(apps, schema_editor):
    apps.get_model("comum", "Parametro").objects.filter(chave__in=[p[0] for p in PARAMETROS_INICIAIS]).delete()


class Migration(migrations.Migration):
    dependencies = [("comum", "0001_initial")]

    operations = [migrations.RunPython(criar, apagar)]

"""
Tarefa G5 — agendador das rotinas diárias. Apostila IV, comunicação nº 4 ("Agendador · 03h00,
diariamente") e operação 03, passo 1.

Decisão do grupo (12/11/2026): o agendador é o **cron** do computador do Matheus (D05), sem
dependência nova. Um comando só, `rodada_diaria`, roda os passos na ordem da Apostila IV —
importação → previsão → regras → notificação:

    1. importar_vendas            planilhas novas do caixa (operação 04)
    2. agregar_consumo            consumo de cada dia (G1, RN11)
    3. calcular_previsao          média, dias até acabar, ponto de pedido, sugestão (G2–G4)
    4. avisos de validade         lotes perto de vencer (RN05, H2)
    5. avisos de ruptura          vai acabar (RN08) e fim de semana na quinta (RN10, H3)
    6. enviar_avisos              Telegram, com janela de silêncio e agrupamento (RN12, RN13)

Um passo que falha não impede os outros (o aviso de validade não depende da planilha do caixa);
a rodada termina com erro, dizendo quais falharam, e o motivo vai para o log.

`agenda_cron` escreve as linhas do crontab a partir da tabela de parâmetros: a rodada na
`hora_rodada_diaria` e o envio de novo no fim de cada janela de silêncio, para soltar os avisos
segurados (RN12). Nenhum horário fica escrito no programa.

Losangos, pelo "sim" e pelo "não":
    o passo deu certo?   sim → *_roda_os_passos_na_ordem*   não → *_passo_que_falha_*
"""

import sys
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from io import StringIO
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from openpyxl import Workbook

from alertas.models import Alerta
from cadastro.models import Categoria, Fornecedor, Produto, Usuario
from comum import rodada
from comum.models import Parametro
from estoque.entrada import registrar_entrada
from previsao.agregacao import dia_da_semana
from previsao.models import ConsumoDiario, PrevisaoProduto
from vendas.models import ImportacaoPdv

SAO_PAULO = ZoneInfo("America/Sao_Paulo")
MADRUGADA = datetime(2026, 11, 12, 3, 0, tzinfo=SAO_PAULO)


@pytest.fixture(autouse=True)
def madrugada_de_12_11():
    with patch("django.utils.timezone.now", return_value=MADRUGADA):
        yield


# --- Ordem e falhas -------------------------------------------------------------------------------


def test_g5_roda_os_passos_na_ordem_da_apostila(db):
    feitos = []
    passos = [(nome, lambda saida, nome=nome: feitos.append(nome)) for nome, _ in rodada.PASSOS]
    with patch.object(rodada, "PASSOS", passos):
        assert rodada.rodar(StringIO()) == []
    assert feitos == [
        "Importação das vendas do caixa",
        "Consumo de cada dia",
        "Previsão de cada produto",
        "Avisos de validade",
        "Avisos de vai acabar e de fim de semana",
        "Envio dos avisos pelo Telegram",
    ]


def test_g5_passo_que_falha_nao_impede_os_outros(db, caplog):
    feitos = []

    def quebra(saida):
        raise RuntimeError("pasta sumiu")

    passos = [(nome, lambda saida, nome=nome: feitos.append(nome)) for nome, _ in rodada.PASSOS]
    passos[0] = (passos[0][0], quebra)
    with patch.object(rodada, "PASSOS", passos):
        falhas = rodada.rodar(StringIO())
    assert falhas == ["Importação das vendas do caixa"]
    assert feitos == [nome for nome, _ in rodada.PASSOS[1:]]
    assert "pasta sumiu" in caplog.text


def test_g5_comando_termina_com_erro_dizendo_o_que_falhou(db):
    passos = [(nome, lambda saida: None) for nome, _ in rodada.PASSOS]
    passos[5] = (passos[5][0], lambda saida: (_ for _ in ()).throw(RuntimeError("sem internet")))
    saida = StringIO()
    with patch.object(rodada, "PASSOS", passos), pytest.raises(CommandError, match="Envio dos avisos"):
        call_command("rodada_diaria", stdout=saida)
    assert "Consumo de cada dia: ok" in saida.getvalue()


def test_g5_comando_sem_falha_termina_bem(db):
    passos = [(nome, lambda saida: None) for nome, _ in rodada.PASSOS]
    saida = StringIO()
    with patch.object(rodada, "PASSOS", passos):
        call_command("rodada_diaria", stdout=saida)
    assert "Rodada de 12/11/2026 concluída" in saida.getvalue()


# --- A rodada de verdade --------------------------------------------------------------------------


@pytest.fixture
def loja(db, tmp_path, settings, telegram):
    """Uma planilha de ontem na pasta, um produto com histórico e um lote vencendo; o Sr. João ligado."""
    endereco, _ = telegram
    settings.PASTA_VENDAS_CAIXA = str(tmp_path)
    settings.TELEGRAM_BOT_TOKEN = "123:abc"
    settings.TELEGRAM_API_ENDERECO = endereco
    Usuario.objects.create_user(
        login="joao", senha="Mercado#2026", nome="Sr. João", papel="DONO", telegram_chat_id="999"
    )

    acougue = Categoria.objects.create(nome="Açougue", perecivel_padrao=True)
    fornecedor = Fornecedor.objects.create(nome="Granja Boa Vista", prazo_entrega_dias=2)
    frango = Produto.objects.create(
        categoria=acougue,
        nome="Frango resfriado 1 kg",
        unidade_medida="KG",
        perecivel=True,
        durabilidade_dias=4,
        fornecedor_padrao=fornecedor,
    )
    with patch("django.utils.timezone.now", return_value=MADRUGADA - timedelta(days=3)):
        registrar_entrada(
            usuario=None, produto=frango, quantidade=Decimal("20"), data_validade=date(2026, 11, 14)
        )
    # 18 dias de venda antes da janela de 30 dias (RN09) — dentro dela a G1 regrava pelas vendas.
    for k in range(18):
        dia = date(2026, 9, 1) + timedelta(days=k)
        ConsumoDiario.objects.create(
            produto=frango, data=dia, quantidade_vendida=3, dia_semana=dia_da_semana(dia)
        )

    livro = Workbook()
    livro.active.append(["Cupom", "Data", "Hora", "Produto", "Quantidade", "Preço unitário"])
    livro.active.append([1021, date(2026, 11, 11), time(9, 0), "Frango resfriado 1 kg", 2, 21.9])
    livro.save(tmp_path / "vendas-2026-11-11.xlsx")
    return frango


def test_g5_rodada_de_verdade_importa_calcula_avisa_e_envia(loja, telegram):
    _, servidor = telegram
    call_command("rodada_diaria", stdout=StringIO())

    assert ImportacaoPdv.objects.get().status == ImportacaoPdv.Status.OK
    assert ConsumoDiario.objects.get(produto=loja, data=date(2026, 11, 11)).quantidade_vendida == 2
    assert PrevisaoProduto.objects.get(produto=loja).calculado_em == MADRUGADA
    aviso = Alerta.objects.get(produto=loja, tipo="VALIDADE")
    assert aviso.status == "ENVIADO"
    assert len(servidor.recebidas) == 1


def test_g5_sem_a_pasta_do_caixa_o_resto_da_rodada_acontece(loja, settings):
    settings.PASTA_VENDAS_CAIXA = ""
    with pytest.raises(CommandError, match="Importação das vendas do caixa"):
        call_command("rodada_diaria", stdout=StringIO())
    assert PrevisaoProduto.objects.get(produto=loja).calculado_em == MADRUGADA
    assert Alerta.objects.get(produto=loja, tipo="VALIDADE").status == "ENVIADO"


# --- Linhas do crontab ----------------------------------------------------------------------------


def _crontab():
    saida = StringIO()
    call_command("agenda_cron", stdout=saida)
    return [linha for linha in saida.getvalue().splitlines() if linha and not linha.startswith("#")]


@pytest.mark.django_db
def test_g5_crontab_roda_a_rodada_na_hora_do_parametro_e_solta_os_segurados():
    linhas = _crontab()
    assert len(linhas) == 3
    rodada_diaria, fim_da_manha, fim_da_tarde = linhas
    assert rodada_diaria.startswith("0 3 * * * ") and 'manage.py" rodada_diaria' in rodada_diaria
    assert fim_da_manha.startswith("0 13 * * * ") and 'manage.py" enviar_avisos' in fim_da_manha
    assert fim_da_tarde.startswith("0 18 * * * ") and 'manage.py" enviar_avisos' in fim_da_tarde


@pytest.mark.django_db
def test_g5_crontab_segue_a_tabela_de_parametros():
    Parametro.objects.filter(chave="hora_rodada_diaria").update(valor="02:30")
    Parametro.objects.filter(chave="janela_silencio_tarde").update(valor="16:30-18:45")
    linhas = _crontab()
    assert linhas[0].startswith("30 2 * * * ")
    assert linhas[2].startswith("45 18 * * * ")


@pytest.mark.django_db
def test_g5_crontab_usa_caminhos_completos_e_grava_no_log():
    rodada_diaria = _crontab()[0]
    assert sys.executable in rodada_diaria
    assert str(settings.BASE_DIR / "manage.py") in rodada_diaria
    assert ">> " in rodada_diaria and 'rodada.log" 2>&1' in rodada_diaria

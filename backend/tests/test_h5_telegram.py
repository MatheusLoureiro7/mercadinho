"""
Tarefa H5 — integração com o serviço de mensagens (Telegram). Operação 03, passo 11.

O canal implementa CanalDeAviso.enviar(destinatario, mensagem) (D04) chamando o sendMessage da API
de bots do Telegram. Os testes sobem um "Telegram de mentira" na própria máquina: o HTTP é de
verdade, só o endereço muda.

- Falha conhecida (bot sem token, pessoa sem celular vinculado — H6 —, Telegram fora do ar ou
  recusando) vira FalhaNoEnvio: os avisos daquela pessoa ficam abertos para a próxima rodada e a
  falha não impede o envio das outras pessoas.
- O token do bot nunca aparece em mensagem de erro nem no log (RNF12).
- Mensagem acima do limite do Telegram (4096 caracteres) é dividida entre linhas, na ordem.
"""

import json
import logging
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import StringIO
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from alertas.models import Alerta
from alertas.notificacao import FalhaNoEnvio, enviar_avisos
from alertas.servicos import criar_aviso
from alertas.telegram import LIMITE_DA_MENSAGEM, CanalTelegram
from cadastro.models import Categoria, Produto, Usuario

TOKEN = "123456:SEGREDO-do-bot"
SAO_PAULO = ZoneInfo("America/Sao_Paulo")
AS_09H = datetime(2026, 9, 21, 9, 0, tzinfo=SAO_PAULO)


class _TelegramDeMentira(BaseHTTPRequestHandler):
    recebidas: list = []
    respostas: list = []  # (código, corpo) por chamada; vazio = sucesso

    def do_POST(self):
        tamanho = int(self.headers.get("Content-Length") or 0)
        self.recebidas.append(
            {
                "caminho": self.path,
                "tipo": self.headers.get("Content-Type"),
                "corpo": json.loads(self.rfile.read(tamanho) or b"{}"),
            }
        )
        codigo, corpo = self.respostas.pop(0) if self.respostas else (200, {"ok": True, "result": {}})
        dados = json.dumps(corpo).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def log_message(self, *args):
        pass


@pytest.fixture
def telegram():
    _TelegramDeMentira.recebidas = []
    _TelegramDeMentira.respostas = []
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), _TelegramDeMentira)
    threading.Thread(target=servidor.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True).start()
    yield f"http://127.0.0.1:{servidor.server_address[1]}", _TelegramDeMentira
    servidor.shutdown()
    servidor.server_close()


@pytest.fixture
def canal(telegram):
    endereco, _ = telegram
    return CanalTelegram(token=TOKEN, endereco=endereco)


@pytest.fixture
def dono(db):
    usuario = Usuario.objects.create_user(login="joao", senha="Mercado#2026", nome="Sr. João", papel="DONO")
    usuario.telegram_chat_id = "987654321"
    usuario.save()
    return usuario


@pytest.fixture
def presunto(db):
    frios = Categoria.objects.create(nome="Frios", perecivel_padrao=True)
    return Produto.objects.create(
        nome="Presunto", categoria=frios, unidade_medida="KG", perecivel=True, durabilidade_dias=7
    )


def _aviso(produto, destinatario, mensagem="Presunto vence em 3 dias — 2,5 KG na prateleira."):
    return criar_aviso(
        produto=produto,
        tipo=Alerta.Tipo.VALIDADE,
        severidade="MEDIA",
        mensagem=mensagem,
        destinatario=destinatario,
    )


def _token_na_cadeia(erro: BaseException) -> bool:
    """O token aparece em alguma exceção que um traceback mostraria (texto ou endereço guardado)?"""
    while erro is not None:
        guardado = [str(erro), repr(erro), str(getattr(erro, "url", "")), str(getattr(erro, "filename", ""))]
        if any(TOKEN in texto for texto in guardado):
            return True
        erro = erro.__cause__ or (None if erro.__suppress_context__ else erro.__context__)
    return False


def _status(aviso) -> str:
    aviso.refresh_from_db()
    return aviso.status


# ------------------------------------------------------------------------------------------------
# O canal: chamada ao sendMessage
# ------------------------------------------------------------------------------------------------


def test_h5_envia_pelo_sendmessage_para_o_chat_do_destinatario(canal, telegram, dono):
    _, servidor = telegram

    canal.enviar(dono, "Presunto vence em 3 dias.")

    assert len(servidor.recebidas) == 1
    chamada = servidor.recebidas[0]
    assert chamada["caminho"] == f"/bot{TOKEN}/sendMessage"
    assert chamada["tipo"].startswith("application/json")
    assert chamada["corpo"] == {"chat_id": "987654321", "text": "Presunto vence em 3 dias."}


def test_h5_texto_vai_sem_formatacao_para_nao_quebrar_com_simbolo_do_produto(canal, telegram, dono):
    """Sem parse_mode: um "*" ou "_" no nome do produto não faz o Telegram recusar a mensagem."""
    _, servidor = telegram

    canal.enviar(dono, "Leite *integral* vence_hoje.")

    assert "parse_mode" not in servidor.recebidas[0]["corpo"]
    assert servidor.recebidas[0]["corpo"]["text"] == "Leite *integral* vence_hoje."


def test_h5_mensagem_longa_e_dividida_entre_linhas_na_ordem(canal, telegram, dono):
    _, servidor = telegram
    linhas = [f"{n}. Produto {n:03d} vence em 2 dias — " + "x" * 80 for n in range(1, 101)]
    texto = "\n".join(linhas)
    assert len(texto) > LIMITE_DA_MENSAGEM

    canal.enviar(dono, texto)

    partes = [chamada["corpo"]["text"] for chamada in servidor.recebidas]
    assert len(partes) > 1
    assert all(len(parte) <= LIMITE_DA_MENSAGEM for parte in partes)
    assert "\n".join(partes) == texto  # nada perdido, nada fora de ordem, nenhuma linha cortada


def test_h5_mensagem_curta_e_uma_chamada_so(canal, telegram, dono):
    _, servidor = telegram

    canal.enviar(dono, "a\n" * 10)

    assert len(servidor.recebidas) == 1


# ------------------------------------------------------------------------------------------------
# O canal: o que pode dar errado
# ------------------------------------------------------------------------------------------------


def test_h5_bot_sem_token_falha_sem_chamar_o_telegram(telegram, dono):
    endereco, servidor = telegram

    with pytest.raises(FalhaNoEnvio, match="TELEGRAM_BOT_TOKEN"):
        CanalTelegram(token="", endereco=endereco).enviar(dono, "oi")

    assert servidor.recebidas == []


def test_h5_pessoa_sem_celular_vinculado_falha_sem_chamar_o_telegram(canal, telegram, db):
    _, servidor = telegram
    esposa = Usuario.objects.create_user(login="esposa", senha="Mercado#2026", nome="Esposa", papel="GESTAO")

    with pytest.raises(FalhaNoEnvio, match="esposa"):
        canal.enviar(esposa, "oi")

    assert servidor.recebidas == []


def test_h5_telegram_recusa_vira_falha_com_o_motivo(canal, telegram, dono):
    _, servidor = telegram
    servidor.respostas = [
        (403, {"ok": False, "error_code": 403, "description": "Forbidden: bot was blocked by the user"})
    ]

    with pytest.raises(FalhaNoEnvio, match="bot was blocked"):
        canal.enviar(dono, "oi")


def test_h5_telegram_responde_ok_false_vira_falha(canal, telegram, dono):
    _, servidor = telegram
    servidor.respostas = [(200, {"ok": False, "description": "Bad Request: chat not found"})]

    with pytest.raises(FalhaNoEnvio, match="chat not found"):
        canal.enviar(dono, "oi")


def test_h5_telegram_fora_do_ar_vira_falha(dono):
    canal = CanalTelegram(token=TOKEN, endereco="http://127.0.0.1:9")  # porta fechada

    with pytest.raises(FalhaNoEnvio):
        canal.enviar(dono, "oi")


def test_h5_o_token_nunca_aparece_no_erro_nem_no_log(canal, telegram, dono, caplog):
    _, servidor = telegram
    servidor.respostas = [(401, {"ok": False, "description": "Unauthorized"})]

    with caplog.at_level(logging.DEBUG), pytest.raises(FalhaNoEnvio) as erro:
        canal.enviar(dono, "oi")

    assert TOKEN not in str(erro.value)
    assert not _token_na_cadeia(erro.value)
    assert TOKEN not in caplog.text


def test_h5_fora_do_ar_tambem_nao_mostra_o_token(dono, caplog):
    canal = CanalTelegram(token=TOKEN, endereco="http://127.0.0.1:9")

    with caplog.at_level(logging.DEBUG), pytest.raises(FalhaNoEnvio) as erro:
        canal.enviar(dono, "oi")

    assert TOKEN not in str(erro.value)
    assert not _token_na_cadeia(erro.value)
    assert TOKEN not in caplog.text


# ------------------------------------------------------------------------------------------------
# O serviço de notificação (H4) com o Telegram
# ------------------------------------------------------------------------------------------------


def test_h5_aviso_chega_ao_telegram_e_fica_enviado(canal, telegram, dono, presunto):
    _, servidor = telegram
    aviso = _aviso(presunto, dono)

    with patch("django.utils.timezone.now", return_value=AS_09H):
        resultado = enviar_avisos(canal)

    assert resultado.enviados == 1
    assert _status(aviso) == Alerta.Status.ENVIADO
    assert aviso.mensagem in servidor.recebidas[0]["corpo"]["text"]


def test_h5_falha_de_uma_pessoa_nao_impede_a_outra(canal, telegram, dono, presunto):
    _, servidor = telegram
    esposa = Usuario.objects.create_user(login="esposa", senha="Mercado#2026", nome="Esposa", papel="GESTAO")
    sem_celular = _aviso(presunto, esposa, mensagem="Aviso da esposa.")
    do_dono = _aviso(presunto, dono, mensagem="Aviso do dono.")

    with patch("django.utils.timezone.now", return_value=AS_09H):
        resultado = enviar_avisos(canal)

    assert _status(sem_celular) == Alerta.Status.PENDENTE  # espera a H6 ligar o celular dela
    assert _status(do_dono) == Alerta.Status.ENVIADO
    assert resultado.enviados == 1 and resultado.falhas == 1
    assert len(servidor.recebidas) == 1


def test_h5_telegram_recusou_os_avisos_ficam_para_a_proxima_rodada(canal, telegram, dono, presunto):
    _, servidor = telegram
    aviso = _aviso(presunto, dono)
    servidor.respostas = [(500, {"ok": False, "description": "Internal Server Error"})]

    with patch("django.utils.timezone.now", return_value=AS_09H):
        resultado = enviar_avisos(canal)
        assert _status(aviso) == Alerta.Status.PENDENTE
        assert resultado.falhas == 1

        enviar_avisos(canal)
    assert _status(aviso) == Alerta.Status.ENVIADO


def test_h5_erro_que_nao_e_de_envio_nao_e_engolido(dono, presunto):
    """Defeito no código não pode virar 'tenta de novo amanhã' em silêncio."""

    class CanalComDefeito:
        def enviar(self, destinatario, mensagem):
            raise ZeroDivisionError

    _aviso(presunto, dono)

    with patch("django.utils.timezone.now", return_value=AS_09H), pytest.raises(ZeroDivisionError):
        enviar_avisos(CanalComDefeito())


# ------------------------------------------------------------------------------------------------
# O comando que o agendador chama (G5): manage.py enviar_avisos
# ------------------------------------------------------------------------------------------------


def test_h5_comando_envia_pelo_telegram_configurado(telegram, dono, presunto, settings):
    endereco, servidor = telegram
    settings.TELEGRAM_BOT_TOKEN = TOKEN
    settings.TELEGRAM_API_ENDERECO = endereco
    aviso = _aviso(presunto, dono)
    saida = StringIO()

    with patch("django.utils.timezone.now", return_value=AS_09H):
        call_command("enviar_avisos", stdout=saida)

    assert _status(aviso) == Alerta.Status.ENVIADO
    assert len(servidor.recebidas) == 1
    assert "1 aviso" in saida.getvalue()


def test_h5_comando_na_janela_de_silencio_so_segura(telegram, dono, presunto, settings):
    endereco, servidor = telegram
    settings.TELEGRAM_BOT_TOKEN = TOKEN
    settings.TELEGRAM_API_ENDERECO = endereco
    aviso = _aviso(presunto, dono)
    saida = StringIO()

    with patch("django.utils.timezone.now", return_value=AS_09H.replace(hour=11, minute=15)):
        call_command("enviar_avisos", stdout=saida)

    assert _status(aviso) == Alerta.Status.SEGURADO
    assert servidor.recebidas == []
    assert "segurado" in saida.getvalue()


def test_h5_comando_com_falha_termina_com_erro_e_nao_mostra_o_token(dono, presunto, settings):
    settings.TELEGRAM_BOT_TOKEN = TOKEN
    settings.TELEGRAM_API_ENDERECO = "http://127.0.0.1:9"
    aviso = _aviso(presunto, dono)

    with patch("django.utils.timezone.now", return_value=AS_09H), pytest.raises(CommandError) as erro:
        call_command("enviar_avisos", stdout=StringIO())

    assert TOKEN not in str(erro.value)
    assert _status(aviso) == Alerta.Status.PENDENTE


def test_h5_endereco_da_api_so_aceita_http():
    """O endereço vem do .env: file:// ou outro esquema não pode virar leitura de arquivo local."""
    with pytest.raises(ValueError, match="inválido"):
        CanalTelegram(token=TOKEN, endereco="file:///etc/passwd")

"""
Tarefa H6 — vincular o celular do dono ao usuário (usuario.telegram_chat_id).

Decisão do grupo (08/10/2026): comando de instalação, como o criar_usuario —

    python backend/manage.py vincular_telegram --login joao

mostra um código de uso único (vale alguns minutos) e o link do bot; o Sr. João manda o código ao
bot; o sistema lê a mensagem (getUpdates — funciona sem o sistema estar publicado, D05), grava o
chat dele e manda uma confirmação. Sem tela nova e sem endereço novo na API.

- Só o DONO recebe aviso (schema.sql: "só o DONO recebe aviso"; RN14: Telegram ✔ só para DONO).
- Mensagem com outro código, ou vinda de grupo, é ignorada.
- Se a confirmação não sair, nada é gravado.
"""

from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from alertas.notificacao import FalhaNoEnvio
from alertas.telegram import CanalTelegram
from alertas.vinculo import esperar_o_codigo, gerar_codigo, vincular
from cadastro.models import Usuario

TOKEN = "123456:SEGREDO-do-bot"


@pytest.fixture
def canal(telegram):
    endereco, _ = telegram
    return CanalTelegram(token=TOKEN, endereco=endereco)


@pytest.fixture
def dono(db):
    return Usuario.objects.create_user(login="joao", senha="Mercado#2026", nome="Sr. João", papel="DONO")


def _mensagem(update_id, texto, chat_id=555111, tipo="private"):
    return {
        "update_id": update_id,
        "message": {"message_id": update_id, "chat": {"id": chat_id, "type": tipo}, "text": texto},
    }


def _chamadas(servidor, metodo):
    return [c for c in servidor.recebidas if c["caminho"].endswith(f"/{metodo}")]


# ------------------------------------------------------------------------------------------------
# O código
# ------------------------------------------------------------------------------------------------


def test_h6_codigo_tem_seis_digitos_e_muda_a_cada_vez():
    codigos = {gerar_codigo() for _ in range(50)}

    assert all(len(c) == 6 and c.isdigit() for c in codigos)
    assert len(codigos) > 40


# ------------------------------------------------------------------------------------------------
# Esperar o código chegar ao bot
# ------------------------------------------------------------------------------------------------


def test_h6_acha_o_chat_de_quem_mandou_start_com_o_codigo(canal, telegram):
    _, servidor = telegram
    servidor.atualizacoes = [_mensagem(10, "/start 482913", chat_id=555111)]

    assert esperar_o_codigo(canal, "482913", prazo_segundos=1) == "555111"


def test_h6_aceita_o_codigo_digitado_sozinho(canal, telegram):
    _, servidor = telegram
    servidor.atualizacoes = [_mensagem(10, " 482913 ", chat_id=555111)]

    assert esperar_o_codigo(canal, "482913", prazo_segundos=1) == "555111"


def test_h6_codigo_errado_e_ignorado(canal, telegram):
    _, servidor = telegram
    servidor.atualizacoes = [_mensagem(10, "/start 111111", chat_id=999), _mensagem(11, "oi", chat_id=999)]

    assert esperar_o_codigo(canal, "482913", prazo_segundos=0.3) is None


@pytest.mark.parametrize("texto", ["/start 1482913", "/start 4829130", "meu código é 482913"])
def test_h6_so_vale_o_codigo_exato(canal, telegram, texto):
    _, servidor = telegram
    servidor.atualizacoes = [_mensagem(10, texto, chat_id=999)]

    assert esperar_o_codigo(canal, "482913", prazo_segundos=0.3) is None


def test_h6_codigo_mandado_num_grupo_e_ignorado(canal, telegram):
    _, servidor = telegram
    servidor.atualizacoes = [_mensagem(10, "/start 482913", chat_id=-100, tipo="group")]

    assert esperar_o_codigo(canal, "482913", prazo_segundos=0.3) is None


def test_h6_acha_o_codigo_depois_de_outras_mensagens(canal, telegram):
    _, servidor = telegram
    servidor.atualizacoes = [
        _mensagem(10, "bom dia", chat_id=999),
        {"update_id": 11, "edited_message": {"chat": {"id": 1, "type": "private"}, "text": "x"}},
        _mensagem(12, "/start 482913", chat_id=555111),
    ]

    assert esperar_o_codigo(canal, "482913", prazo_segundos=1) == "555111"


def test_h6_pede_so_as_mensagens_novas_a_cada_volta(canal, telegram):
    """offset = último update_id + 1: o Telegram não devolve de novo o que já foi lido."""
    _, servidor = telegram
    servidor.atualizacoes = [_mensagem(10, "oi", chat_id=999)]

    esperar_o_codigo(canal, "482913", prazo_segundos=0.3)

    offsets = [c["corpo"].get("offset") for c in _chamadas(servidor, "getUpdates")]
    assert len(offsets) >= 2
    assert offsets[1:] == [11] * (len(offsets) - 1)


def test_h6_telegram_fora_do_ar_vira_falha(dono):
    canal = CanalTelegram(token=TOKEN, endereco="http://127.0.0.1:9")

    with pytest.raises(FalhaNoEnvio):
        esperar_o_codigo(canal, "482913", prazo_segundos=1)


# ------------------------------------------------------------------------------------------------
# Gravar o vínculo
# ------------------------------------------------------------------------------------------------


def test_h6_grava_o_chat_e_manda_a_confirmacao(canal, telegram, dono):
    _, servidor = telegram

    vincular(dono, "555111", canal)

    dono.refresh_from_db()
    assert dono.telegram_chat_id == "555111"
    confirmacao = _chamadas(servidor, "sendMessage")
    assert len(confirmacao) == 1
    assert confirmacao[0]["corpo"]["chat_id"] == "555111"
    assert "avisos" in confirmacao[0]["corpo"]["text"]


def test_h6_trocar_de_celular_e_vincular_de_novo(canal, dono):
    vincular(dono, "555111", canal)

    vincular(dono, "777222", canal)

    dono.refresh_from_db()
    assert dono.telegram_chat_id == "777222"


@pytest.mark.parametrize("papel", ["GESTAO", "OPERACAO"])
def test_h6_so_o_dono_recebe_aviso(canal, telegram, db, papel):
    _, servidor = telegram
    outro = Usuario.objects.create_user(login="outro", senha="Mercado#2026", nome="Outro", papel=papel)

    with pytest.raises(ValueError, match="dono"):
        vincular(outro, "555111", canal)

    outro.refresh_from_db()
    assert outro.telegram_chat_id is None
    assert servidor.recebidas == []


def test_h6_usuario_desativado_nao_e_vinculado(canal, dono):
    dono.ativo = False
    dono.save()

    with pytest.raises(ValueError, match="desativado"):
        vincular(dono, "555111", canal)


def test_h6_se_a_confirmacao_nao_sai_nada_e_gravado(canal, telegram, dono):
    _, servidor = telegram
    servidor.respostas = [(403, {"ok": False, "description": "Forbidden: bot was blocked by the user"})]

    with pytest.raises(FalhaNoEnvio):
        vincular(dono, "555111", canal)

    dono.refresh_from_db()
    assert dono.telegram_chat_id is None


# ------------------------------------------------------------------------------------------------
# O comando
# ------------------------------------------------------------------------------------------------


@pytest.fixture
def bot_configurado(telegram, settings):
    endereco, servidor = telegram
    settings.TELEGRAM_BOT_TOKEN = TOKEN
    settings.TELEGRAM_API_ENDERECO = endereco
    return servidor


def test_h6_comando_mostra_o_codigo_e_liga_o_celular(bot_configurado, dono, monkeypatch):
    monkeypatch.setattr("alertas.vinculo.gerar_codigo", lambda: "482913")
    bot_configurado.atualizacoes = [_mensagem(10, "/start 482913", chat_id=555111)]
    saida = StringIO()

    call_command("vincular_telegram", "--login", "joao", "--minutos", "1", stdout=saida)

    texto = saida.getvalue()
    assert "482913" in texto
    assert "https://t.me/MercadoSrJoaoBot?start=482913" in texto
    assert "Pronto" in texto
    dono.refresh_from_db()
    assert dono.telegram_chat_id == "555111"


def test_h6_comando_sem_resposta_no_prazo_nao_grava(bot_configurado, dono, monkeypatch):
    monkeypatch.setattr("alertas.vinculo.gerar_codigo", lambda: "482913")
    monkeypatch.setattr("alertas.management.commands.vincular_telegram.SEGUNDOS_POR_MINUTO", 0.3)

    with pytest.raises(CommandError, match="não chegou"):
        call_command("vincular_telegram", "--login", "joao", "--minutos", "1", stdout=StringIO())

    dono.refresh_from_db()
    assert dono.telegram_chat_id is None


def test_h6_comando_recusa_quem_nao_e_dono_antes_de_falar_com_o_telegram(bot_configurado, db):
    Usuario.objects.create_user(login="sobrinho", senha="Mercado#2026", nome="Sobrinho", papel="OPERACAO")

    with pytest.raises(CommandError, match="dono"):
        call_command("vincular_telegram", "--login", "sobrinho", stdout=StringIO())

    assert bot_configurado.recebidas == []


def test_h6_comando_login_inexistente(bot_configurado, db):
    with pytest.raises(CommandError, match="ninguem"):
        call_command("vincular_telegram", "--login", "ninguem", stdout=StringIO())


def test_h6_comando_sem_token_avisa_e_nao_mostra_codigo(dono, settings):
    settings.TELEGRAM_BOT_TOKEN = ""
    saida = StringIO()

    with pytest.raises(CommandError, match="TELEGRAM_BOT_TOKEN"):
        call_command("vincular_telegram", "--login", "joao", stdout=saida)

    assert "start" not in saida.getvalue()


def test_h6_comando_nao_mostra_o_token(bot_configurado, dono, monkeypatch):
    monkeypatch.setattr("alertas.vinculo.gerar_codigo", lambda: "482913")
    bot_configurado.atualizacoes = [_mensagem(10, "/start 482913")]
    saida = StringIO()

    call_command("vincular_telegram", "--login", "joao", "--minutos", "1", stdout=saida)

    assert TOKEN not in saida.getvalue()


def test_h6_depois_de_vincular_o_aviso_chega_ao_celular(bot_configurado, dono, monkeypatch):
    """Ponta a ponta: o comando da H6 liga o celular, o da H5 entrega o aviso nele."""
    from datetime import datetime
    from unittest.mock import patch
    from zoneinfo import ZoneInfo

    from alertas.models import Alerta
    from alertas.servicos import criar_aviso
    from cadastro.models import Categoria, Produto

    monkeypatch.setattr("alertas.vinculo.gerar_codigo", lambda: "482913")
    bot_configurado.atualizacoes = [_mensagem(10, "/start 482913", chat_id=555111)]
    call_command("vincular_telegram", "--login", "joao", "--minutos", "1", stdout=StringIO())
    frios = Categoria.objects.create(nome="Frios", perecivel_padrao=True)
    presunto = Produto.objects.create(
        nome="Presunto", categoria=frios, unidade_medida="KG", perecivel=True, durabilidade_dias=7
    )
    criar_aviso(
        produto=presunto,
        tipo=Alerta.Tipo.VALIDADE,
        severidade="MEDIA",
        mensagem="Presunto vence em 3 dias.",
        destinatario=Usuario.objects.get(login="joao"),
    )

    as_9h = datetime(2026, 9, 21, 9, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))
    with patch("django.utils.timezone.now", return_value=as_9h):
        call_command("enviar_avisos", stdout=StringIO())

    aviso = _chamadas(bot_configurado, "sendMessage")[-1]["corpo"]
    assert aviso["chat_id"] == "555111"
    assert "Presunto vence em 3 dias." in aviso["text"]

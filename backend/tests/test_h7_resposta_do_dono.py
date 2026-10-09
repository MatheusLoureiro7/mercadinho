"""
Tarefa H7 — receber e registrar a resposta do dono. Operação 03, passos 13 e 14.

    13. Webhook recebe a resposta "Sim, pedir"
    14. UPDATE alerta.resposta_usuario

Decisões do grupo (09/10/2026):
- recebimento por webhook, como na Apostila IV: POST /api/telegram/, chamado pelo Telegram, sem login
  de usuário; protegido pelo token secreto do Telegram (cabeçalho X-Telegram-Bot-Api-Secret-Token)
  e aceitando só o chat do DONO — exceção explícita à regra do `tela` (RN14: "Telegram, sem tela,
  só DONO");
- só o aviso de "vai acabar" (RUPTURA) ganha botão, e só "Sim, pedir" — o que a especificação cita.

Como a RN13 junta vários avisos numa mensagem, cada aviso de ruptura vira um botão próprio, que
leva o número do aviso.
"""

from datetime import datetime
from io import StringIO
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from rest_framework.test import APIClient

from alertas.estados import cancelar, enviar
from alertas.models import Alerta
from alertas.notificacao import enviar_avisos
from alertas.respostas import RESPOSTA_PEDIR, botoes_da_mensagem, registrar_resposta
from alertas.servicos import criar_aviso
from alertas.telegram import CanalTelegram
from cadastro.models import Categoria, Produto, Usuario

TOKEN = "123456:SEGREDO-do-bot"
SEGREDO = "segredo-do-webhook-123"
CHAT_DO_DONO = "555111"
AS_09H = datetime(2026, 9, 21, 9, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))
ENDERECO = "/api/telegram/"


@pytest.fixture
def dono(db):
    usuario = Usuario.objects.create_user(login="joao", senha="Mercado#2026", nome="Sr. João", papel="DONO")
    usuario.telegram_chat_id = CHAT_DO_DONO
    usuario.save()
    return usuario


@pytest.fixture
def acougue(db):
    return Categoria.objects.create(nome="Açougue", perecivel_padrao=True)


def _produto(categoria, nome):
    return Produto.objects.create(
        nome=nome, categoria=categoria, unidade_medida="KG", perecivel=True, durabilidade_dias=5
    )


def _ruptura(produto, dono, *, enviado=True):
    aviso = criar_aviso(
        produto=produto,
        tipo=Alerta.Tipo.RUPTURA,
        severidade="ALTA",
        mensagem=f"{produto.nome} acaba em 2 dias.",
        destinatario=dono,
    )
    if enviado:
        enviar([aviso], quando=AS_09H)
    return aviso


def _validade(produto, dono):
    aviso = criar_aviso(
        produto=produto,
        tipo=Alerta.Tipo.VALIDADE,
        severidade="MEDIA",
        mensagem=f"{produto.nome} vence em 3 dias.",
        destinatario=dono,
    )
    enviar([aviso], quando=AS_09H)
    return aviso


def _clique(aviso_ou_dado, chat_id=CHAT_DO_DONO, id_do_clique="cq-1"):
    dado = aviso_ou_dado if isinstance(aviso_ou_dado, str) else f"pedir:{aviso_ou_dado.pk}"
    return {
        "update_id": 900,
        "callback_query": {
            "id": id_do_clique,
            "from": {"id": int(chat_id), "is_bot": False, "first_name": "João"},
            "message": {"message_id": 7, "chat": {"id": int(chat_id), "type": "private"}, "text": "..."},
            "data": dado,
        },
    }


def _resposta(aviso) -> str | None:
    aviso.refresh_from_db()
    return aviso.resposta_usuario


@pytest.fixture
def webhook(telegram, settings):
    """O endereço do webhook com o bot e o segredo configurados; devolve (cliente, servidor)."""
    endereco, servidor = telegram
    settings.TELEGRAM_BOT_TOKEN = TOKEN
    settings.TELEGRAM_API_ENDERECO = endereco
    settings.TELEGRAM_WEBHOOK_SEGREDO = SEGREDO
    return APIClient(), servidor


def _postar(cliente, corpo, segredo=SEGREDO):
    cabecalhos = {"HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN": segredo} if segredo is not None else {}
    return cliente.post(ENDERECO, corpo, format="json", **cabecalhos)


def _chamadas(servidor, metodo):
    return [c for c in servidor.recebidas if c["caminho"].endswith(f"/{metodo}")]


# ------------------------------------------------------------------------------------------------
# Os botões na mensagem (operação 03, passo 11)
# ------------------------------------------------------------------------------------------------


def test_h7_aviso_de_ruptura_ganha_botao_sim_pedir(acougue, dono):
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono, enviado=False)

    assert botoes_da_mensagem([frango]) == [("Sim, pedir: Frango resfriado", f"pedir:{frango.pk}")]


def test_h7_aviso_de_validade_nao_ganha_botao(acougue, dono):
    alcatra = criar_aviso(
        produto=_produto(acougue, "Alcatra"),
        tipo=Alerta.Tipo.VALIDADE,
        severidade="MEDIA",
        mensagem="Alcatra vence em 3 dias.",
        destinatario=dono,
    )

    assert botoes_da_mensagem([alcatra]) == []


def test_h7_mensagem_agrupada_leva_um_botao_por_aviso_de_ruptura(acougue, dono, telegram):
    endereco, servidor = telegram
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono, enviado=False)
    linguica = _ruptura(_produto(acougue, "Linguiça toscana"), dono, enviado=False)
    criar_aviso(
        produto=_produto(acougue, "Alcatra"),
        tipo=Alerta.Tipo.VALIDADE,
        severidade="MEDIA",
        mensagem="Alcatra vence em 3 dias.",
        destinatario=dono,
    )

    with patch("django.utils.timezone.now", return_value=AS_09H):
        enviar_avisos(CanalTelegram(token=TOKEN, endereco=endereco))

    chamada = _chamadas(servidor, "sendMessage")
    assert len(chamada) == 1  # RN13: continua uma mensagem só
    teclado = chamada[0]["corpo"]["reply_markup"]["inline_keyboard"]
    assert teclado == [
        [{"text": "Sim, pedir: Frango resfriado", "callback_data": f"pedir:{frango.pk}"}],
        [{"text": "Sim, pedir: Linguiça toscana", "callback_data": f"pedir:{linguica.pk}"}],
    ]


def test_h7_mensagem_sem_ruptura_vai_sem_teclado(acougue, dono, telegram):
    endereco, servidor = telegram
    criar_aviso(
        produto=_produto(acougue, "Alcatra"),
        tipo=Alerta.Tipo.VALIDADE,
        severidade="MEDIA",
        mensagem="Alcatra vence em 3 dias.",
        destinatario=dono,
    )

    with patch("django.utils.timezone.now", return_value=AS_09H):
        enviar_avisos(CanalTelegram(token=TOKEN, endereco=endereco))

    assert "reply_markup" not in _chamadas(servidor, "sendMessage")[0]["corpo"]


def test_h7_mensagem_dividida_leva_os_botoes_na_ultima_parte(dono, telegram):
    endereco, servidor = telegram
    canal = CanalTelegram(token=TOKEN, endereco=endereco)
    texto = "\n".join("x" * 100 for _ in range(60))  # passa de 4096 caracteres

    canal.enviar(dono, texto, botoes=[("Sim, pedir: Frango", "pedir:1")])

    partes = _chamadas(servidor, "sendMessage")
    assert len(partes) > 1
    assert all("reply_markup" not in p["corpo"] for p in partes[:-1])
    assert "reply_markup" in partes[-1]["corpo"]


# ------------------------------------------------------------------------------------------------
# Registrar a resposta (operação 03, passo 14)
# ------------------------------------------------------------------------------------------------


def test_h7_sim_pedir_fica_gravado_no_aviso(acougue, dono):
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono)

    texto = registrar_resposta(CHAT_DO_DONO, f"pedir:{frango.pk}")

    assert _resposta(frango) == RESPOSTA_PEDIR == "Sim, pedir"
    assert "Frango resfriado" in texto


def test_h7_clicar_duas_vezes_nao_muda_nada(acougue, dono):
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono)
    registrar_resposta(CHAT_DO_DONO, f"pedir:{frango.pk}")

    texto = registrar_resposta(CHAT_DO_DONO, f"pedir:{frango.pk}")

    assert _resposta(frango) == "Sim, pedir"
    assert "já" in texto.lower()


def test_h7_resposta_de_outro_chat_nao_e_gravada(acougue, dono):
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono)

    registrar_resposta("999999", f"pedir:{frango.pk}")

    assert _resposta(frango) is None


def test_h7_dono_desativado_nao_responde(acougue, dono):
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono)
    dono.ativo = False
    dono.save()

    registrar_resposta(CHAT_DO_DONO, f"pedir:{frango.pk}")

    assert _resposta(frango) is None


def test_h7_aviso_que_nao_e_do_dono_nao_e_gravado(acougue, dono):
    """O aviso foi para outra pessoa: o dono não responde por ela."""
    esposa = Usuario.objects.create_user(login="esposa", senha="Mercado#2026", nome="Esposa", papel="GESTAO")
    frango = _ruptura(_produto(acougue, "Frango resfriado"), esposa)

    registrar_resposta(CHAT_DO_DONO, f"pedir:{frango.pk}")

    assert _resposta(frango) is None


def test_h7_aviso_de_validade_nao_aceita_sim_pedir(acougue, dono):
    alcatra = _validade(_produto(acougue, "Alcatra"), dono)

    registrar_resposta(CHAT_DO_DONO, f"pedir:{alcatra.pk}")

    assert _resposta(alcatra) is None


@pytest.mark.parametrize("situacao", ["pendente", "cancelado"])
def test_h7_aviso_que_nao_foi_enviado_nao_aceita_resposta(acougue, dono, situacao):
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono, enviado=False)
    if situacao == "cancelado":
        cancelar([frango])  # chegou a mercadoria (operação 02, passo 10)

    texto = registrar_resposta(CHAT_DO_DONO, f"pedir:{frango.pk}")

    assert _resposta(frango) is None
    assert "não vale mais" in texto


@pytest.mark.parametrize("dado", ["", "pedir:", "pedir:abc", "pedir:99999", "apagar:1", "pedir:1:2"])
def test_h7_botao_desconhecido_e_ignorado(acougue, dono, dado):
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono)

    registrar_resposta(CHAT_DO_DONO, dado)

    assert _resposta(frango) is None


# ------------------------------------------------------------------------------------------------
# O endereço do webhook (operação 03, passo 13)
# ------------------------------------------------------------------------------------------------


def test_h7_webhook_grava_a_resposta_e_confirma_para_o_dono(webhook, acougue, dono):
    cliente, servidor = webhook
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono)

    resposta = _postar(cliente, _clique(frango, id_do_clique="cq-42"))

    assert resposta.status_code == 200
    assert _resposta(frango) == "Sim, pedir"
    confirmacao = _chamadas(servidor, "answerCallbackQuery")
    assert len(confirmacao) == 1
    assert confirmacao[0]["corpo"]["callback_query_id"] == "cq-42"
    assert "Frango resfriado" in confirmacao[0]["corpo"]["text"]


@pytest.mark.parametrize("segredo", [None, "", "segredo-errado"])
def test_h7_webhook_sem_o_segredo_certo_e_recusado(webhook, acougue, dono, segredo):
    cliente, servidor = webhook
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono)

    resposta = _postar(cliente, _clique(frango), segredo=segredo)

    assert resposta.status_code == 403
    assert _resposta(frango) is None
    assert servidor.recebidas == []


def test_h7_webhook_sem_segredo_configurado_recusa_tudo(webhook, acougue, dono, settings):
    """Segredo vazio no .env não pode virar 'qualquer um entra'."""
    cliente, _ = webhook
    settings.TELEGRAM_WEBHOOK_SEGREDO = ""
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono)

    resposta = _postar(cliente, _clique(frango), segredo="")

    assert resposta.status_code == 403
    assert _resposta(frango) is None


def test_h7_webhook_nao_aceita_login_de_usuario_no_lugar_do_segredo(webhook, acougue, dono):
    """Nem o dono logado no painel grava resposta por este endereço: ele é só do Telegram."""
    from comum.autenticacao import gerar_token

    cliente, _ = webhook
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono)
    cliente.credentials(HTTP_AUTHORIZATION=f"Bearer {gerar_token(dono)}")

    resposta = _postar(cliente, _clique(frango), segredo=None)

    assert resposta.status_code == 403
    assert _resposta(frango) is None


def test_h7_webhook_ignora_o_que_nao_e_clique_em_botao(webhook, dono):
    """Mensagem de texto, foto etc.: responde 200 (senão o Telegram reenvia sem parar) e não faz nada."""
    cliente, servidor = webhook

    resposta = _postar(
        cliente, {"update_id": 1, "message": {"chat": {"id": 1, "type": "private"}, "text": "oi"}}
    )

    assert resposta.status_code == 200
    assert servidor.recebidas == []


def test_h7_webhook_clique_de_estranho_responde_200_e_nao_grava(webhook, acougue, dono):
    cliente, servidor = webhook
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono)

    resposta = _postar(cliente, _clique(frango, chat_id="999999"))

    assert resposta.status_code == 200
    assert _resposta(frango) is None


def test_h7_webhook_grava_mesmo_se_a_confirmacao_falhar(webhook, acougue, dono):
    """A resposta dele é o que importa; a confirmação na tela é cortesia."""
    cliente, servidor = webhook
    servidor.respostas = [(500, {"ok": False, "description": "Internal Server Error"})]
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono)

    resposta = _postar(cliente, _clique(frango))

    assert resposta.status_code == 200
    assert _resposta(frango) == "Sim, pedir"


def test_h7_webhook_corpo_estranho_nao_derruba(webhook):
    cliente, _ = webhook

    for corpo in [{}, {"callback_query": {}}, {"callback_query": {"id": "x", "data": "pedir:1"}}, []]:
        assert _postar(cliente, corpo).status_code == 200


# ------------------------------------------------------------------------------------------------
# Avisar o Telegram do endereço: manage.py configurar_webhook
# ------------------------------------------------------------------------------------------------


def test_h7_configurar_webhook_manda_o_endereco_e_o_segredo(webhook):
    _, servidor = webhook
    saida = StringIO()

    call_command("configurar_webhook", "--url", "https://mercado.exemplo.com.br/api/telegram/", stdout=saida)

    chamada = _chamadas(servidor, "setWebhook")[0]["corpo"]
    assert chamada["url"] == "https://mercado.exemplo.com.br/api/telegram/"
    assert chamada["secret_token"] == SEGREDO
    assert chamada["allowed_updates"] == ["callback_query"]
    assert SEGREDO not in saida.getvalue()
    assert TOKEN not in saida.getvalue()


def test_h7_configurar_webhook_exige_https(webhook):
    _, servidor = webhook

    with pytest.raises(CommandError, match="https"):
        call_command(
            "configurar_webhook", "--url", "http://mercado.exemplo.com.br/api/telegram/", stdout=StringIO()
        )

    assert servidor.recebidas == []


def test_h7_configurar_webhook_exige_segredo(webhook, settings):
    settings.TELEGRAM_WEBHOOK_SEGREDO = ""

    with pytest.raises(CommandError, match="TELEGRAM_WEBHOOK_SEGREDO"):
        call_command(
            "configurar_webhook", "--url", "https://mercado.exemplo.com.br/api/telegram/", stdout=StringIO()
        )


def test_h7_remover_webhook(webhook):
    _, servidor = webhook

    call_command("configurar_webhook", "--remover", stdout=StringIO())

    assert len(_chamadas(servidor, "deleteWebhook")) == 1


def test_h7_vincular_com_webhook_ligado_explica_o_que_fazer(webhook, dono):
    """H6 lê pelo getUpdates, que o Telegram recusa com o webhook ligado (409)."""
    _, servidor = webhook
    servidor.respostas = [
        (200, {"ok": True, "result": {"id": 1, "is_bot": True, "username": "MercadoSrJoaoBot"}}),
        (409, {"ok": False, "description": "Conflict: can't use getUpdates method while webhook is active"}),
    ]

    with pytest.raises(CommandError, match="configurar_webhook --remover"):
        call_command("vincular_telegram", "--login", "joao", "--minutos", "1", stdout=StringIO())


def test_h7_quem_nao_e_dono_nao_responde_mesmo_com_celular_ligado(acougue, dono):
    """Só o DONO recebe aviso (schema.sql); se outra pessoa tiver chat gravado, a resposta não vale."""
    esposa = Usuario.objects.create_user(login="esposa", senha="Mercado#2026", nome="Esposa", papel="GESTAO")
    esposa.telegram_chat_id = "777222"
    esposa.save()
    frango = _ruptura(_produto(acougue, "Frango resfriado"), esposa)

    registrar_resposta("777222", f"pedir:{frango.pk}")

    assert _resposta(frango) is None


@pytest.mark.parametrize("sobra", [":x", "0", " ", ":1"])
def test_h7_botao_com_sobra_no_fim_e_ignorado(acougue, dono, sobra):
    frango = _ruptura(_produto(acougue, "Frango resfriado"), dono)

    registrar_resposta(CHAT_DO_DONO, f"pedir:{frango.pk}{sobra}")

    assert _resposta(frango) is None

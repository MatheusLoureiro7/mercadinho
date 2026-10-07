"""
Tarefa A3 — esqueleto da API: rotas, tratamento de erro e registro de log.

Toda resposta de erro tem o formato {"erro": {"codigo", "mensagem", ...}}, em português e no
vocabulário da loja (RNF10).
"""

import logging

import pytest

pytestmark = pytest.mark.urls("tests.urls_a3")


# --- Rotas ---------------------------------------------------------------------------------------


def test_a3_raiz_da_api_responde_json(client, db):
    # Desde a A4 toda a API exige login: sem token, a raiz responde 401 — em JSON.
    resposta = client.get("/api/")
    assert resposta.status_code == 401
    assert resposta["Content-Type"].startswith("application/json")
    assert resposta.json()["erro"]["codigo"] == "nao_autenticado"


def test_a3_api_so_fala_json_mesmo_quando_o_navegador_pede_html(client):
    # O painel é estático (Apostila IV, seção 3): a API não gera página HTML.
    resposta = client.get("/teste/ok/", HTTP_ACCEPT="text/html")
    assert resposta["Content-Type"].startswith("application/json")
    assert resposta.json() == {"ok": True}


# --- Tratamento de erro --------------------------------------------------------------------------


def test_a3_erro_de_validacao_aponta_o_campo(client):
    # Fluxograma 01: a tela mantém o que foi digitado e aponta só o campo que falta.
    resposta = client.post("/teste/validacao/", {}, content_type="application/json")
    assert resposta.status_code == 400
    erro = resposta.json()["erro"]
    assert erro["codigo"] == "validacao"
    assert erro["mensagem"] == "Confira os campos destacados."
    assert erro["campos"] == {"durabilidade_dias": ["Este campo é obrigatório."]}


def test_a3_erro_de_regra_de_negocio_traz_a_regra_e_a_mensagem(client):
    resposta = client.post("/teste/regra/", {}, content_type="application/json")
    assert resposta.status_code == 400
    erro = resposta.json()["erro"]
    assert erro["codigo"] == "regra_de_negocio"
    assert erro["regra"] == "RN03"
    assert erro["mensagem"].startswith("Produto perecível precisa do prazo de durabilidade")
    assert "durabilidade_dias" in erro["campos"]


def test_a3_json_malformado_e_recusado_em_portugues(client):
    resposta = client.post("/teste/validacao/", "{isso não é json", content_type="application/json")
    assert resposta.status_code == 400
    erro = resposta.json()["erro"]
    assert erro["codigo"] == "requisicao_invalida"
    assert erro["mensagem"] == "Os dados enviados estão num formato que o sistema não entende."


def test_a3_rota_da_api_inexistente_responde_404_em_json(client):
    resposta = client.get("/api/nao-existe/")
    assert resposta.status_code == 404
    assert resposta.json()["erro"]["codigo"] == "nao_encontrado"


def test_a3_registro_nao_encontrado_responde_404_em_json(client):
    resposta = client.get("/teste/nao-acha/")
    assert resposta.status_code == 404
    erro = resposta.json()["erro"]
    assert erro["codigo"] == "nao_encontrado"
    assert erro["mensagem"] == "Não encontramos o que você procurou."


def test_a3_metodo_nao_permitido_responde_405_em_json(client):
    resposta = client.delete("/teste/ok/")
    assert resposta.status_code == 405
    assert resposta.json()["erro"]["codigo"] == "metodo_nao_permitido"


def test_a3_erro_inesperado_nao_mostra_detalhe_tecnico(client):
    resposta = client.get("/teste/quebra/")
    assert resposta.status_code == 500
    erro = resposta.json()["erro"]
    assert erro["codigo"] == "erro_interno"
    assert erro["id"] in erro["mensagem"]
    assert "falha simulada" not in resposta.content.decode()
    assert "Traceback" not in resposta.content.decode()


def test_a3_erro_inesperado_vai_para_o_log_com_o_mesmo_codigo(client, caplog):
    with caplog.at_level(logging.ERROR, logger="mercadinho"):
        resposta = client.get("/teste/quebra/")
    id_erro = resposta.json()["erro"]["id"]
    registros = [r for r in caplog.records if r.name == "mercadinho.erros"]
    assert len(registros) == 1
    assert id_erro in registros[0].getMessage()
    assert registros[0].exc_info is not None  # o detalhe técnico fica no log, não na tela


# --- Registro de log -----------------------------------------------------------------------------


def test_a3_toda_requisicao_vai_para_o_log(client, caplog):
    with caplog.at_level(logging.INFO, logger="mercadinho"):
        client.get("/teste/ok/")
    linhas = [r.getMessage() for r in caplog.records if r.name == "mercadinho.requisicao"]
    assert len(linhas) == 1
    assert "GET /teste/ok/ 200" in linhas[0]


def test_a3_requisicao_recusada_vai_para_o_log_como_aviso(client, caplog):
    with caplog.at_level(logging.INFO, logger="mercadinho"):
        client.post("/teste/validacao/", {}, content_type="application/json")
    registro = next(r for r in caplog.records if r.name == "mercadinho.requisicao")
    assert registro.levelno == logging.WARNING
    assert "POST /teste/validacao/ 400" in registro.getMessage()


def test_a3_log_nao_grava_o_corpo_da_requisicao(client, caplog):
    # RNF12: senha nunca vai para o log.
    with caplog.at_level(logging.DEBUG, logger="mercadinho"):
        client.post("/teste/validacao/", {"senha": "segredo123"}, content_type="application/json")
    assert "segredo123" not in caplog.text


# --- Páginas fora da API -------------------------------------------------------------------------


def test_a3_pagina_inexistente_fora_da_api_responde_json(client):
    resposta = client.get("/qualquer-coisa/")
    assert resposta.status_code == 404
    assert resposta.json()["erro"]["codigo"] == "nao_encontrado"


def test_a3_erro_interno_fora_da_api_responde_json(rf):
    from comum.erros import erro_interno

    resposta = erro_interno(rf.get("/"))
    assert resposta.status_code == 500
    assert b'"erro_interno"' in resposta.content

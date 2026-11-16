"""
Tarefa A4 — autenticação e os três perfis de acesso (RN14, requisito RF14).

- Login pela tela de Login: devolve um token assinado (decisão da L09) e o menu do papel.
- RN14: o papel é verificado na camada de autenticação, ANTES de qualquer operação e antes de
  tocar no banco (Apostila IV, operação 01, passo 3).
"""

from io import StringIO
from unittest import mock

import pytest
from django.core.cache import cache
from django.core.management import CommandError, call_command
from django.test import override_settings

from cadastro.models import Categoria, Usuario
from comum.autenticacao import gerar_token

pytestmark = pytest.mark.urls("tests.urls_a4")

SENHA = "Mercado#2026"

# RN14 — tabela de docs/REGRAS-NEGOCIO.md, transcrita do mapa de navegação da Apostila II.
MATRIZ_RN14 = {
    "produtos": {"OPERACAO"},
    "fornecedores": {"OPERACAO"},
    "entrada_mercadoria": {"OPERACAO"},
    "avarias": {"OPERACAO"},
    "importacao_vendas": {"OPERACAO"},
    "consulta_estoque": {"DONO", "GESTAO", "OPERACAO"},
    "fechamento_caixa": {"GESTAO"},
    "balanco_semana": {"GESTAO"},
}
PAPEIS = ["DONO", "GESTAO", "OPERACAO"]


@pytest.fixture(autouse=True)
def _limpa_limite_de_tentativas():
    cache.clear()  # o limite de tentativas de login fica no cache
    yield
    cache.clear()


@pytest.fixture
def usuarios(db):
    return {
        "DONO": Usuario.objects.create_user(login="joao", senha=SENHA, nome="Sr. João", papel="DONO"),
        "GESTAO": Usuario.objects.create_user(login="esposa", senha=SENHA, nome="Esposa", papel="GESTAO"),
        "OPERACAO": Usuario.objects.create_user(
            login="sobrinho", senha=SENHA, nome="Sobrinho", papel="OPERACAO"
        ),
    }


def _com_token(usuario):
    return {"HTTP_AUTHORIZATION": f"Bearer {gerar_token(usuario)}"}


def _entrar(client, login, senha):
    return client.post("/api/sessoes/", {"login": login, "senha": senha}, content_type="application/json")


# --- Login ---------------------------------------------------------------------------------------


def test_a4_login_correto_devolve_token_e_menu_do_papel(client, usuarios):
    resposta = _entrar(client, "esposa", SENHA)
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["token"]
    assert corpo["usuario"]["nome"] == "Esposa"
    assert corpo["usuario"]["papel"] == "GESTAO"
    # Tela de Login: "identifica a pessoa e monta o menu conforme o papel (RN14)".
    assert set(corpo["usuario"]["telas"]) == {"consulta_estoque", "fechamento_caixa", "balanco_semana"}


def test_a4_login_nunca_devolve_a_senha_nem_o_hash(client, usuarios):
    corpo = _entrar(client, "sobrinho", SENHA).content.decode()
    assert SENHA not in corpo
    assert usuarios["OPERACAO"].password not in corpo


@pytest.mark.parametrize(
    ("login", "senha"),
    [("esposa", "senha-errada"), ("ninguem", SENHA)],
    ids=["senha_errada", "login_inexistente"],
)
def test_a4_login_invalido_e_recusado_sem_dizer_qual_campo_errou(client, usuarios, login, senha):
    resposta = _entrar(client, login, senha)
    assert resposta.status_code == 401
    erro = resposta.json()["erro"]
    assert erro["codigo"] == "nao_autenticado"
    assert erro["mensagem"] == "Login ou senha incorretos."


def test_a4_usuario_desativado_nao_entra(client, usuarios):
    usuarios["GESTAO"].ativo = False
    usuarios["GESTAO"].save()
    assert _entrar(client, "esposa", SENHA).status_code == 401


def test_a4_login_sem_os_campos_aponta_o_que_falta(client, db):
    resposta = client.post("/api/sessoes/", {}, content_type="application/json")
    assert resposta.status_code == 400
    assert set(resposta.json()["erro"]["campos"]) == {"login", "senha"}


def test_a4_muitas_tentativas_seguidas_sao_bloqueadas(client, usuarios):
    # RNF12, segurança básica: impede adivinhar a senha por tentativa e erro.
    for _ in range(10):
        _entrar(client, "esposa", "chute")
    assert _entrar(client, "esposa", SENHA).status_code == 429


def test_rnf12_sistema_usa_o_hash_de_senha_forte_do_django():
    # Os testes trocam o hash por um rápido (conftest.py); o sistema real não pode fazer o mesmo.
    from core import settings as configuracao

    assert not hasattr(configuracao, "PASSWORD_HASHERS")  # padrão do Django: PBKDF2


def test_a4_inventar_o_endereco_de_origem_nao_burla_o_limite(client, usuarios):
    for tentativa in range(10):
        _entrar_de(client, "esposa", "chute", f"10.0.0.{tentativa}")
    assert _entrar_de(client, "esposa", SENHA, "10.0.0.99").status_code == 429


def _entrar_de(client, login, senha, endereco_inventado):
    return client.post(
        "/api/sessoes/",
        {"login": login, "senha": senha},
        content_type="application/json",
        HTTP_X_FORWARDED_FOR=endereco_inventado,
    )


# --- Token ---------------------------------------------------------------------------------------


def test_a4_sessao_atual_mostra_quem_esta_usando(client, usuarios):
    resposta = client.get("/api/sessoes/atual/", **_com_token(usuarios["OPERACAO"]))
    assert resposta.status_code == 200
    assert resposta.json()["papel"] == "OPERACAO"


def test_a4_token_devolvido_no_login_funciona(client, usuarios):
    token = _entrar(client, "joao", SENHA).json()["token"]
    resposta = client.get("/api/sessoes/atual/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert resposta.status_code == 200
    assert resposta.json()["telas"] == ["consulta_estoque"]


def test_a4_sem_token_responde_401(client, db):
    resposta = client.get("/api/sessoes/atual/")
    assert resposta.status_code == 401
    assert resposta.json()["erro"]["codigo"] == "nao_autenticado"
    assert resposta.has_header("WWW-Authenticate")


def test_a4_token_adulterado_e_recusado(client, usuarios):
    token = gerar_token(usuarios["DONO"])
    resposta = client.get("/api/sessoes/atual/", HTTP_AUTHORIZATION=f"Bearer {token[:-2]}xx")
    assert resposta.status_code == 401


def test_a4_token_vencido_e_recusado(client, usuarios):
    token = gerar_token(usuarios["DONO"])
    with override_settings(SESSAO_VALIDADE_HORAS=-1):
        resposta = client.get("/api/sessoes/atual/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert resposta.status_code == 401
    assert resposta.json()["erro"]["mensagem"] == "Sua sessão expirou. Entre no sistema de novo."


def test_a4_token_de_usuario_desativado_deixa_de_valer(client, usuarios):
    token = _com_token(usuarios["OPERACAO"])
    usuarios["OPERACAO"].ativo = False
    usuarios["OPERACAO"].save()
    assert client.get("/api/sessoes/atual/", **token).status_code == 401


def test_a4_trocar_a_senha_derruba_os_tokens_antigos(client, usuarios):
    token = _com_token(usuarios["OPERACAO"])
    usuarios["OPERACAO"].set_password("Outra#Senha2026")
    usuarios["OPERACAO"].save()
    assert client.get("/api/sessoes/atual/", **token).status_code == 401


# --- RN14: matriz de acesso ----------------------------------------------------------------------


def test_rn14_matriz_do_codigo_e_a_da_especificacao():
    from comum.permissoes import ACESSO_POR_TELA

    assert {tela: set(papeis) for tela, papeis in ACESSO_POR_TELA.items()} == MATRIZ_RN14


@pytest.mark.parametrize("tela", list(MATRIZ_RN14))
@pytest.mark.parametrize("papel", PAPEIS)
def test_rn14_cada_papel_acessa_so_as_suas_telas(client, usuarios, tela, papel):
    resposta = client.get(f"/teste/tela/{tela}/", **_com_token(usuarios[papel]))
    if papel in MATRIZ_RN14[tela]:
        assert resposta.status_code == 200
    else:
        assert resposta.status_code == 403
        assert resposta.json()["erro"]["codigo"] == "sem_permissao"


def test_rn14_dono_tenta_cadastrar_produto_e_e_recusado_antes_de_tocar_no_banco(client, usuarios):
    # Apostila IV, operação 01, passo 3.
    resposta = client.post(
        "/teste/tela/produtos/", {}, content_type="application/json", **_com_token(usuarios["DONO"])
    )
    assert resposta.status_code == 403
    assert not Categoria.objects.exists()


def test_rn14_operacao_cadastra_produto(client, usuarios):
    resposta = client.post(
        "/teste/tela/produtos/", {}, content_type="application/json", **_com_token(usuarios["OPERACAO"])
    )
    assert resposta.status_code == 201
    assert Categoria.objects.exists()


def test_rn14_sem_login_e_recusado_antes_de_tocar_no_banco(client, db):
    resposta = client.post("/teste/tela/produtos/", {}, content_type="application/json")
    assert resposta.status_code == 401
    assert not Categoria.objects.exists()


def test_rn14_endpoint_que_nao_declarou_a_tela_e_recusado(client, usuarios):
    # Falha fechada: esquecer de declarar a tela nunca abre o acesso.
    for papel in PAPEIS:
        assert client.get("/teste/sem-tela/", **_com_token(usuarios[papel])).status_code == 403


# --- Comando para criar os três usuários (L14) ---------------------------------------------------


def _criar_usuario(*args, senhas=(SENHA, SENHA)):
    with mock.patch("cadastro.management.commands.criar_usuario.getpass", side_effect=list(senhas)):
        call_command("criar_usuario", *args, stdout=StringIO())


def test_a4_comando_cria_usuario_com_senha_em_hash(db):
    _criar_usuario("--login", "sobrinho", "--nome", "Sobrinho", "--papel", "OPERACAO")
    usuario = Usuario.objects.get(login="sobrinho")
    assert usuario.papel == "OPERACAO"
    assert usuario.check_password(SENHA)


def test_a4_comando_recusa_papel_fora_dos_tres(db):
    with pytest.raises(CommandError):
        _criar_usuario("--login", "caixa", "--nome", "Funcionário", "--papel", "CAIXA")
    assert not Usuario.objects.exists()


def test_a4_comando_recusa_login_repetido(usuarios):
    with pytest.raises(CommandError, match="Já existe"):
        _criar_usuario("--login", "esposa", "--nome", "Outra", "--papel", "GESTAO")


def test_a4_comando_recusa_senhas_diferentes(db):
    with pytest.raises(CommandError, match="não conferem"):
        _criar_usuario("--login", "joao", "--nome", "Sr. João", "--papel", "DONO", senhas=(SENHA, "outra"))
    assert not Usuario.objects.exists()


def test_a4_comando_recusa_senha_fraca(db):
    with pytest.raises(CommandError):
        _criar_usuario("--login", "joao", "--nome", "Sr. João", "--papel", "DONO", senhas=("123", "123"))
    assert not Usuario.objects.exists()

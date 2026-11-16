"""
Tarefa A5 — esteira de publicação em ambiente de teste. Decisão D05 (30/10/2026): o sistema roda no
computador do Matheus. Decisão do grupo (13/11/2026): um script `publicar.py`, sem dependência
nova, com o servidor do próprio Django (o uso previsto é a demonstração; `gunicorn` só com decisão
do grupo).

    python publicar.py                  atualiza, confere, testa e, se tudo passar, publica
    python publicar.py --sem-atualizar  publica o que está na pasta, sem git pull
    python publicar.py --parar          para a API e o painel publicados

A ordem protege o que está no ar: código, dependências, banco, padrão do código e TODOS os testes
vêm antes; só depois a migração do banco de verdade e a troca dos servidores. Passo que falha para
a esteira, e o sistema publicado continua como estava. Cada publicação é registrada no log.

Losangos, pelo "sim" e pelo "não":
    o passo deu certo?                 sim → segue                     não → *_passo_que_falha_*
    a API e o painel responderam?      sim → *_publica_*               não → *_nao_respondeu_*
"""

import importlib.util
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]


@pytest.fixture
def publicar(tmp_path, monkeypatch):
    especificacao = importlib.util.spec_from_file_location("publicar", RAIZ / "publicar.py")
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    monkeypatch.setattr(modulo, "PASTA_ESTADO", tmp_path / ".publicacao")
    monkeypatch.setattr(modulo, "REGISTRO", tmp_path / "logs" / "publicacoes.log")
    monkeypatch.setattr(modulo, "PASTA_LOGS", tmp_path / "logs")
    monkeypatch.setattr(modulo, "ESPERA_SEGUNDOS", 0)
    return modulo


class Maquina:
    """Faz o papel do terminal e dos servidores, anotando tudo o que a esteira pediu."""

    def __init__(self, falha_em=None, responde=True, vivos=()):
        self.comandos, self.iniciados, self.parados, self.ambientes = [], [], [], {}
        self.falha_em, self.responde, self.vivos = falha_em, responde, set(vivos)
        self.proximo_pid = 1000

    def rodar(self, comando):
        self.comandos.append(" ".join(comando))
        return 1 if self.falha_em and self.falha_em in " ".join(comando) else 0

    def iniciar(self, nome, comando, log, ambiente=None):
        self.proximo_pid += 1
        self.iniciados.append(nome)
        self.ambientes[nome] = ambiente or {}
        self.vivos.add(self.proximo_pid)
        return self.proximo_pid

    def parar(self, pid):
        if pid in self.vivos:
            self.vivos.discard(pid)
            self.parados.append(pid)

    def respondeu(self, endereco):
        return self.responde

    def commit(self):
        return "abc1234"


def _rodar(publicar, maquina, *argumentos):
    return publicar.principal(list(argumentos), maquina=maquina)


def test_a5_testes_vem_antes_da_migracao_e_da_troca_dos_servidores(publicar):
    maquina = Maquina()
    assert _rodar(publicar, maquina) == 0
    comandos = maquina.comandos
    ordem = [
        "git pull",
        "pip install",
        "docker compose up",
        "ruff check",
        "ruff format --check",
        "pytest",
        "migrate",
    ]
    posicoes = [next(i for i, c in enumerate(comandos) if trecho in c) for trecho in ordem]
    assert posicoes == sorted(posicoes)
    assert maquina.iniciados == ["api", "painel"]


def test_a5_passo_que_falha_nao_migra_nem_troca_os_servidores(publicar):
    maquina = Maquina(falha_em="pytest")
    assert _rodar(publicar, maquina) == 1
    assert not any("migrate" in c for c in maquina.comandos)
    assert maquina.iniciados == [] and maquina.parados == []
    assert "NÃO publicado" in publicar.REGISTRO.read_text(encoding="utf-8")
    assert "Rodar todos os testes" in publicar.REGISTRO.read_text(encoding="utf-8")


def test_a5_ruff_reprovado_para_antes_dos_testes(publicar):
    maquina = Maquina(falha_em="ruff check")
    assert _rodar(publicar, maquina) == 1
    assert not any("pytest" in c for c in maquina.comandos)


def test_a5_publica_trocando_os_servidores_antigos_pelos_novos(publicar):
    publicar.PASTA_ESTADO.mkdir(parents=True)
    (publicar.PASTA_ESTADO / "api.pid").write_text("501")
    (publicar.PASTA_ESTADO / "painel.pid").write_text("502")
    maquina = Maquina(vivos={501, 502})
    assert _rodar(publicar, maquina) == 0
    assert sorted(maquina.parados) == [501, 502]
    assert (publicar.PASTA_ESTADO / "api.pid").read_text() == "1001"
    assert (publicar.PASTA_ESTADO / "painel.pid").read_text() == "1002"
    registro = publicar.REGISTRO.read_text(encoding="utf-8")
    assert "publicado" in registro and "abc1234" in registro


def test_a5_pid_de_servidor_que_ja_morreu_nao_atrapalha(publicar):
    publicar.PASTA_ESTADO.mkdir(parents=True)
    (publicar.PASTA_ESTADO / "api.pid").write_text("777")
    maquina = Maquina()
    assert _rodar(publicar, maquina) == 0
    assert maquina.parados == []


def test_a5_sem_atualizar_nao_faz_git_pull(publicar):
    maquina = Maquina()
    assert _rodar(publicar, maquina, "--sem-atualizar") == 0
    assert not any("git pull" in c for c in maquina.comandos)


def test_a5_servidor_que_nao_respondeu_termina_com_erro(publicar):
    maquina = Maquina(responde=False)
    assert _rodar(publicar, maquina) == 1
    assert "não respondeu" in publicar.REGISTRO.read_text(encoding="utf-8")


def test_a5_parar_desliga_a_api_e_o_painel(publicar):
    publicar.PASTA_ESTADO.mkdir(parents=True)
    (publicar.PASTA_ESTADO / "api.pid").write_text("501")
    (publicar.PASTA_ESTADO / "painel.pid").write_text("502")
    maquina = Maquina(vivos={501, 502})
    assert _rodar(publicar, maquina, "--parar") == 0
    assert sorted(maquina.parados) == [501, 502] and maquina.comandos == []
    assert not (publicar.PASTA_ESTADO / "api.pid").exists()


def test_a5_usa_o_python_do_ambiente_e_o_servidor_do_django_sem_dependencia_nova(publicar):
    comandos = dict(publicar.SERVIDORES)
    assert comandos["api"][0] == sys.executable and "runserver" in comandos["api"]
    assert "--noreload" in comandos["api"]
    assert comandos["painel"][1].endswith("servir.py")
    requisitos = (RAIZ / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "gunicorn" not in requisitos


def test_a5_estado_da_publicacao_fica_fora_do_git():
    assert ".publicacao/" in (RAIZ / ".gitignore").read_text(encoding="utf-8")


# X1, item 20: com DJANGO_DEBUG=true, endereço errado mostra a página técnica do Django (rotas,
# código, configurações) em vez da resposta em JSON. O sistema publicado nunca sobe assim.


def test_x1_api_publicada_sobe_sem_modo_de_depuracao_qualquer_que_seja_o_env(publicar):
    maquina = Maquina()
    assert _rodar(publicar, maquina) == 0
    assert maquina.ambientes["api"] == {"DJANGO_DEBUG": "false"}


def test_x1_modelo_de_configuracao_vem_sem_modo_de_depuracao():
    linhas = (RAIZ / ".env.example").read_text(encoding="utf-8").splitlines()
    assert "DJANGO_DEBUG=false" in linhas

"""
Tarefa H4 — janela de silêncio (RN12) e avisos agrupados numa mensagem só (RN13).

RN12: nenhum aviso sai entre 10h30 e 13h, nem entre 16h30 e 18h (horário da loja). O que for
gerado nessas faixas fica SEGURADO e sai na primeira janela livre. A verificação é na hora do
ENVIO, não da geração. As faixas vêm da tabela parametro.

RN13: todos os avisos PENDENTE e SEGURADO de uma janela de envio saem numa ÚNICA mensagem,
ordenados por urgência (severidade, depois gerado_em), com UMA chamada ao canal; todos ficam
ENVIADO com o mesmo enviado_em.

O canal de verdade (Telegram) é a H5; aqui o serviço fala com a interface CanalDeAviso (D04).
"""

from datetime import datetime
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from alertas.estados import cancelar, enviar
from alertas.models import Alerta
from alertas.notificacao import FalhaNoEnvio, enviar_avisos, montar_mensagem
from alertas.servicos import criar_aviso
from alertas.telegram import dividir
from cadastro.models import Categoria, Produto, Usuario
from comum.models import Parametro

SAO_PAULO = ZoneInfo("America/Sao_Paulo")


def _as(hora: str, dia: int = 21) -> datetime:
    h, m = (int(parte) for parte in hora.split(":"))
    return datetime(2026, 9, dia, h, m, tzinfo=SAO_PAULO)


class CanalDeMentira:
    """Guarda o que seria enviado, no lugar do Telegram (H5)."""

    def __init__(self, falha: Exception | None = None):
        self.enviadas: list[tuple[Usuario, str]] = []
        self.falha = falha

    def enviar(self, destinatario, mensagem, botoes=()):
        if self.falha:
            raise self.falha
        self.enviadas.append((destinatario, mensagem))


@pytest.fixture
def canal():
    return CanalDeMentira()


@pytest.fixture
def dono(db):
    return Usuario.objects.create_user(login="joao", senha="Mercado#2026", nome="Sr. João", papel="DONO")


@pytest.fixture
def frios(db):
    return Categoria.objects.create(nome="Frios", perecivel_padrao=True)


def _produto(categoria, nome):
    return Produto.objects.create(
        nome=nome, categoria=categoria, unidade_medida="UN", perecivel=True, durabilidade_dias=7
    )


def _aviso(produto, dono, *, mensagem=None, severidade="MEDIA", gerado="03:00"):
    with patch("django.utils.timezone.now", return_value=_as(gerado)):
        return criar_aviso(
            produto=produto,
            tipo=Alerta.Tipo.VALIDADE,
            severidade=severidade,
            mensagem=mensagem or f"{produto.nome} vence em 2 dias.",
            destinatario=dono,
        )


def _rodar(hora: str, canal, dia: int = 21):
    with patch("django.utils.timezone.now", return_value=_as(hora, dia)):
        return enviar_avisos(canal)


def _status(aviso) -> str:
    aviso.refresh_from_db()
    return aviso.status


# ------------------------------------------------------------------------------------------------
# RN12 — dentro da janela de silêncio?
# ------------------------------------------------------------------------------------------------


def test_rn12_aviso_das_11h15_fica_segurado_e_nada_e_enviado(frios, dono, canal):
    aviso = _aviso(_produto(frios, "Presunto"), dono, gerado="11:15")

    _rodar("11:15", canal)

    assert _status(aviso) == Alerta.Status.SEGURADO
    assert canal.enviadas == []


def test_rn12_aviso_segurado_as_11h15_sai_as_13h05(frios, dono, canal):
    """O teste escrito na Apostila I."""
    aviso = _aviso(_produto(frios, "Presunto"), dono, gerado="11:15")
    _rodar("11:15", canal)

    _rodar("13:05", canal)

    aviso.refresh_from_db()
    assert aviso.status == Alerta.Status.ENVIADO
    assert aviso.enviado_em == _as("13:05")
    assert len(canal.enviadas) == 1


def test_rn12_fora_da_janela_o_aviso_sai_na_hora(frios, dono, canal):
    aviso = _aviso(_produto(frios, "Presunto"), dono)

    _rodar("09:00", canal)

    assert _status(aviso) == Alerta.Status.ENVIADO
    assert len(canal.enviadas) == 1


def test_rn12_pico_da_tarde_tambem_segura(frios, dono, canal):
    aviso = _aviso(_produto(frios, "Presunto"), dono)

    _rodar("17:00", canal)

    assert _status(aviso) == Alerta.Status.SEGURADO
    assert canal.enviadas == []


@pytest.mark.parametrize("hora", ["10:30", "12:59", "16:30", "17:59"])
def test_rn12_comeco_da_janela_ja_e_silencio(frios, dono, canal, hora):
    aviso = _aviso(_produto(frios, "Presunto"), dono)

    _rodar(hora, canal)

    assert _status(aviso) == Alerta.Status.SEGURADO


@pytest.mark.parametrize("hora", ["10:29", "13:00", "16:29", "18:00"])
def test_rn12_fim_da_janela_ja_e_livre(frios, dono, canal, hora):
    """'Entre 10h30 e 13h': às 13h00 o pico acabou e o aviso já pode sair."""
    aviso = _aviso(_produto(frios, "Presunto"), dono)

    _rodar(hora, canal)

    assert _status(aviso) == Alerta.Status.ENVIADO


def test_rn12_a_janela_vem_da_tabela_de_parametros(frios, dono, canal):
    Parametro.objects.filter(chave="janela_silencio_manha").update(valor="08:00-09:30")
    aviso = _aviso(_produto(frios, "Presunto"), dono)

    _rodar("09:00", canal)
    assert _status(aviso) == Alerta.Status.SEGURADO

    _rodar("11:00", canal)  # 10h30–13h deixou de ser silêncio
    assert _status(aviso) == Alerta.Status.ENVIADO


def test_rn12_usa_o_horario_da_loja_e_nao_o_utc(frios, dono, canal):
    """11h15 em São Paulo é 14h15 em UTC — fora da janela se o relógio fosse lido em UTC."""
    aviso = _aviso(_produto(frios, "Presunto"), dono)

    with patch("django.utils.timezone.now", return_value=_as("11:15").astimezone(ZoneInfo("UTC"))):
        enviar_avisos(canal)

    assert _status(aviso) == Alerta.Status.SEGURADO


# ------------------------------------------------------------------------------------------------
# RN13 — uma mensagem só, por urgência
# ------------------------------------------------------------------------------------------------


def test_rn13_seis_avisos_pendentes_saem_numa_mensagem_so(frios, dono, canal):
    """O teste escrito na Apostila I: 6 avisos às 13h05 → uma mensagem com 6 itens, não seis."""
    avisos = [_aviso(_produto(frios, f"Produto {n}"), dono) for n in range(6)]

    _rodar("13:05", canal)

    assert len(canal.enviadas) == 1
    destinatario, texto = canal.enviadas[0]
    assert destinatario == dono
    for aviso in avisos:
        assert aviso.mensagem in texto


def test_rn13_comeca_pelo_mais_urgente(frios, dono, canal):
    _aviso(_produto(frios, "Presunto"), dono, mensagem="Presunto vence em 3 dias.", gerado="02:00")
    _aviso(
        _produto(frios, "Iogurte natural"),
        dono,
        mensagem="Iogurte natural vence hoje.",
        severidade="ALTA",
        gerado="03:00",
    )
    _aviso(
        _produto(frios, "Queijo"), dono, mensagem="Queijo: aviso baixo.", severidade="BAIXA", gerado="01:00"
    )

    _rodar("13:05", canal)

    texto = canal.enviadas[0][1]
    assert texto.index("Iogurte natural vence hoje.") < texto.index("Presunto vence em 3 dias.")
    assert texto.index("Presunto vence em 3 dias.") < texto.index("Queijo: aviso baixo.")


def test_rn13_mesma_urgencia_sai_primeiro_o_mais_antigo(frios, dono, canal):
    _aviso(_produto(frios, "Presunto"), dono, mensagem="Presunto vence em 2 dias.", gerado="03:00")
    _aviso(_produto(frios, "Mortadela"), dono, mensagem="Mortadela vence em 2 dias.", gerado="02:00")

    _rodar("13:05", canal)

    texto = canal.enviadas[0][1]
    assert texto.index("Mortadela vence em 2 dias.") < texto.index("Presunto vence em 2 dias.")


def test_rn13_segurado_e_pendente_saem_juntos(frios, dono, canal):
    segurado = _aviso(_produto(frios, "Presunto"), dono, gerado="11:15")
    _rodar("11:15", canal)
    pendente = _aviso(_produto(frios, "Mortadela"), dono, gerado="12:00")

    _rodar("13:05", canal)

    assert len(canal.enviadas) == 1
    assert _status(segurado) == _status(pendente) == Alerta.Status.ENVIADO


def test_rn13_todos_da_mensagem_ficam_com_o_mesmo_enviado_em(frios, dono, canal):
    avisos = [_aviso(_produto(frios, f"Produto {n}"), dono) for n in range(3)]

    _rodar("13:05", canal)

    assert {Alerta.objects.get(pk=a.pk).enviado_em for a in avisos} == {_as("13:05")}


def test_rn13_enviado_e_cancelado_nao_entram_na_mensagem(frios, dono, canal):
    ja_enviado = _aviso(_produto(frios, "Presunto"), dono, mensagem="Presunto já foi avisado.")
    enviar([ja_enviado], quando=_as("09:00"))
    cancelado = _aviso(_produto(frios, "Mortadela"), dono, mensagem="Mortadela foi cancelado.")
    cancelar([cancelado])
    _aviso(_produto(frios, "Queijo"), dono, mensagem="Queijo vence em 2 dias.")

    _rodar("13:05", canal)

    texto = canal.enviadas[0][1]
    assert "Queijo vence em 2 dias." in texto
    assert "já foi avisado" not in texto
    assert "foi cancelado" not in texto
    assert Alerta.objects.get(pk=ja_enviado.pk).enviado_em == _as("09:00")


def test_rn13_sem_aviso_pendente_nada_e_enviado(dono, canal):
    _rodar("13:05", canal)

    assert canal.enviadas == []


def test_rn13_rodar_de_novo_nao_repete_a_mensagem(frios, dono, canal):
    _aviso(_produto(frios, "Presunto"), dono)

    _rodar("13:05", canal)
    _rodar("13:10", canal)

    assert len(canal.enviadas) == 1


def test_rn13_mensagem_numera_os_itens_na_ordem():
    texto = montar_mensagem(["Iogurte natural vence hoje.", "Presunto vence em 3 dias."])

    linhas = texto.splitlines()
    assert "1. Iogurte natural vence hoje." in linhas
    assert "2. Presunto vence em 3 dias." in linhas
    assert linhas.index("1. Iogurte natural vence hoje.") < linhas.index("2. Presunto vence em 3 dias.")


# ------------------------------------------------------------------------------------------------
# O envio falhou ou não tem para quem ir
# ------------------------------------------------------------------------------------------------


def test_h4_se_o_envio_falha_os_avisos_esperam_a_proxima_rodada(frios, dono):
    segurado = _aviso(_produto(frios, "Mortadela"), dono)
    _rodar("11:15", CanalDeMentira())
    pendente = _aviso(_produto(frios, "Presunto"), dono, gerado="12:00")
    sem_internet = CanalDeMentira(falha=FalhaNoEnvio("sem internet"))

    resultado = _rodar("13:05", sem_internet)

    assert resultado.falhas == 1 and resultado.enviados == 0

    assert _status(pendente) == Alerta.Status.PENDENTE
    assert _status(segurado) == Alerta.Status.SEGURADO
    assert Alerta.objects.filter(enviado_em__isnull=False).count() == 0

    canal = CanalDeMentira()
    _rodar("13:10", canal)
    assert len(canal.enviadas) == 1


def test_h4_aviso_sem_destinatario_nao_sai_e_nao_se_perde(frios, canal):
    """Sem DONO cadastrado (H2) o aviso é gravado sem destinatário: fica esperando, não some."""
    aviso = _aviso(_produto(frios, "Presunto"), None)

    _rodar("13:05", canal)

    assert canal.enviadas == []
    assert _status(aviso) == Alerta.Status.PENDENTE


def test_h4_cada_pessoa_recebe_so_os_seus_avisos(frios, dono, canal):
    esposa = Usuario.objects.create_user(login="esposa", senha="Mercado#2026", nome="Esposa", papel="GESTAO")
    _aviso(_produto(frios, "Presunto"), dono, mensagem="Presunto vence em 2 dias.")
    _aviso(_produto(frios, "Mortadela"), esposa, mensagem="Mortadela vence em 2 dias.")

    _rodar("13:05", canal)

    por_pessoa = {destinatario.login: texto for destinatario, texto in canal.enviadas}
    assert set(por_pessoa) == {"joao", "esposa"}
    assert "Mortadela" not in por_pessoa["joao"]
    assert "Presunto" not in por_pessoa["esposa"]


def test_h4_devolve_quantos_sairam_e_quantos_ficaram_segurados(frios, dono, canal):
    _aviso(_produto(frios, "Presunto"), dono)
    _aviso(_produto(frios, "Mortadela"), dono)

    segurou = _rodar("11:15", canal)
    saiu = _rodar("13:05", canal)

    assert segurou.segurados == 2 and segurou.enviados == 0
    assert saiu.enviados == 2 and saiu.mensagens == 1


# --- Mensagem grande dividida (X1, item 17) -------------------------------------------------------
# O Telegram aceita até 4096 caracteres por mensagem. Quando a parte 1 saía e a 2 falhava, nada
# ficava marcado como enviado e a rodada seguinte repetia a parte 1. Agora quem divide é o serviço
# de notificação, sempre entre avisos, e cada parte que sai marca os seus avisos.


class CanalQueCaiNaSegundaParte:
    """Como o Telegram: divide o que passa do limite e manda parte por parte; a 2ª chamada cai."""

    limite_da_mensagem = 300

    def __init__(self, cair=True):
        self.cair = cair
        self.chamadas = 0
        self.entregues: list[str] = []

    def enviar(self, destinatario, mensagem, botoes=()):
        for parte in dividir(mensagem, self.limite_da_mensagem):
            self.chamadas += 1
            if self.cair and self.chamadas == 2:
                raise FalhaNoEnvio("O Telegram não respondeu.")
            self.entregues.append(parte)


def test_x1_parte_que_saiu_nao_e_repetida_quando_a_seguinte_falha(frios, dono):
    produtos = [_produto(frios, f"Produto de nome comprido número {n:02d}") for n in range(12)]
    avisos = [_aviso(produto, dono) for produto in produtos]

    caindo = CanalQueCaiNaSegundaParte()
    resultado = _rodar("14:00", caindo)
    enviados = [aviso for aviso in avisos if _status(aviso) == "ENVIADO"]
    assert resultado.falhas == 1 and 0 < len(enviados) < len(avisos)

    de_volta = CanalQueCaiNaSegundaParte(cair=False)
    _rodar("15:00", de_volta)
    entregue = "\n".join(caindo.entregues + de_volta.entregues)
    for aviso in avisos:
        assert entregue.count(aviso.mensagem) == 1, aviso.mensagem  # cada aviso chega uma vez só
    assert all(_status(aviso) == "ENVIADO" for aviso in avisos)
    assert all(len(parte) <= 300 for parte in caindo.entregues + de_volta.entregues)


def test_x1_mensagem_dividida_continua_com_titulo_e_numeracao_seguida(frios, dono):
    for n in range(12):
        _aviso(_produto(frios, f"Produto de nome comprido número {n:02d}"), dono)
    canal = CanalQueCaiNaSegundaParte(cair=False)
    _rodar("14:00", canal)
    assert len(canal.entregues) > 1
    texto = "\n".join(canal.entregues)
    assert texto.startswith("Avisos do mercado (12):\n1. ")
    assert "\n12. " in texto and texto.count("Avisos do mercado") == 1

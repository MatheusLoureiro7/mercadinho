# ruff: noqa: E501  (textos do documento: quebrar a linha só atrapalha a leitura)
"""
Documentação do sistema — "docs as code" (critério de aceite dos slides do professor, 13/11/2026).

    python docs/sistema/gerar.py            regenera os documentos tirados do código e o PDF
    python docs/sistema/gerar.py --conferir só confere: termina com erro se algum estiver velho

Quatro documentos saem direto do código, para nunca ficarem desatualizados:
    manter/rastreabilidade.md     regra/requisito → onde está no código → teste que prova
    manter/dicionario-de-dados.md as 14 tabelas do schema.sql, coluna por coluna
    manter/contratos-da-api.md    cada endereço da API, método e quem pode usar (RN14)
    evoluir/dependencias.md       bibliotecas, versão instalada, licença e fim de suporte

O teste backend/tests/test_documentacao.py roda a conferência: se alguém criar endpoint, tabela,
regra ou dependência sem regenerar, a suíte falha. Os demais documentos são escritos à mão e o
índice (LEIA-ME.md) diz a situação e a data de cada um.

A página (DOCUMENTACAO-DO-SISTEMA.html) e o PDF juntam tudo, a partir dos mesmos .md: menu com os
24 documentos, procura, tema claro e escuro, e os códigos citados no texto (RN05, ADR-013,
`usar/faq.md`) levando até onde estão definidos. Estilo e script em docs/sistema/modelo/.
"""

import argparse
import html
import importlib.metadata as metadados
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[1]
BACKEND = RAIZ / "backend"
DOCUMENTO = "MDGS-DOC-001"
VERSAO = "1.1"
EMISSAO = "16/11/2026"
PILARES = [
    ("usar", "Usar", "Como faço meu trabalho com o sistema?", "ISO/IEC/IEEE 26514"),
    ("manter", "Manter", "Como o sistema funciona e por que é assim?", "ISO/IEC/IEEE 42010"),
    ("sustentar", "Sustentar", "Como mantenho o sistema no ar e recupero quando cai?", "práticas ITIL"),
    (
        "evoluir",
        "Evoluir",
        "Como atualizo versão, tecnologia ou fornecedor sem quebrar?",
        "ISO/IEC/IEEE 14764",
    ),
]
AVISO_GERADO = "> Gerado automaticamente por `docs/sistema/gerar.py` a partir do código. Não edite à mão: a suíte de testes falha se este arquivo ficar diferente do código."


# ------------------------------------------------------------------------------------------ Django


def _django():
    sys.path.insert(0, str(BACKEND))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    import django

    django.setup()


# ------------------------------------------------------------------------------------------ Rastreabilidade


def _codigo_e_testes():
    codigo, testes = {}, {}
    for arquivo in sorted(BACKEND.rglob("*.py")):
        partes = arquivo.relative_to(BACKEND).parts
        if "migrations" in partes or ".venv" in partes:
            continue
        texto = arquivo.read_text(encoding="utf-8")
        (testes if partes[0] == "tests" else codigo)[arquivo.relative_to(RAIZ).as_posix()] = texto
    return codigo, testes


def rastreabilidade() -> str:
    regras = re.findall(
        r"^\| (RN\d{2}) \| ([^|]+) \|", (RAIZ / "docs/REGRAS-NEGOCIO.md").read_text(encoding="utf-8"), re.M
    )
    requisitos = re.findall(
        r"^\| (RF\d{2}) \| ([^|]+) \|[^|]+\| ([^|]+) \|",
        (RAIZ / "docs/ESPECIFICACAO.md").read_text(encoding="utf-8"),
        re.M,
    )
    codigo, testes = _codigo_e_testes()

    def onde(codigo_regra):
        padrao = re.compile(rf"\b{codigo_regra}\b")
        return [arquivo for arquivo, texto in codigo.items() if padrao.search(texto)]

    def provas(codigo_regra):
        nome = re.compile(rf"^def (test_{codigo_regra.lower()}_\w+)", re.M)
        citado = re.compile(rf"\b{codigo_regra}\b")
        por_nome = sum(len(nome.findall(texto)) for texto in testes.values())
        arquivos = sorted(
            Path(a).name for a, texto in testes.items() if citado.search(texto) or nome.search(texto)
        )
        return por_nome, arquivos

    linhas = [
        "# Rastreabilidade: regra → código → teste",
        "",
        AVISO_GERADO,
        "",
        "Cada regra de negócio (Apostila I) e cada requisito funcional (Apostila III), com os arquivos do",
        "código que a citam e os testes que a provam. Teste com o nome da regra (`test_rn05_...`) é a",
        "prova direta; os arquivos de teste listados citam a regra no texto.",
        "",
        "## Regras de negócio",
        "",
        "| Regra | Nome | Onde está no código | Testes com o nome da regra | Arquivos de teste |",
        "|---|---|---|---|---|",
    ]
    for codigo_regra, nome in regras:
        arquivos = onde(codigo_regra)
        quantos, de_teste = provas(codigo_regra)
        linhas.append(
            f"| {codigo_regra} | {nome.strip()} | {'<br>'.join(f'`{a}`' for a in arquivos) or '—'} | {quantos} | {', '.join(de_teste) or '—'} |"
        )
    linhas += [
        "",
        "## Requisitos funcionais",
        "",
        "| Requisito | Nome | Prioridade | Onde está no código | Arquivos de teste |",
        "|---|---|---|---|---|",
    ]
    for codigo_req, nome, prioridade in requisitos:
        arquivos = onde(codigo_req)
        _, de_teste = provas(codigo_req)
        situacao = "" if arquivos else " (não coberto na primeira versão)"
        linhas.append(
            f"| {codigo_req} | {nome.strip()}{situacao} | {prioridade.strip()} | {'<br>'.join(f'`{a}`' for a in arquivos) or '—'} | {', '.join(de_teste) or '—'} |"
        )
    return "\n".join(linhas) + "\n"


# ------------------------------------------------------------------------------------------ Dicionário de dados


def dicionario_de_dados() -> str:
    _django()
    from django.apps import apps

    sql = (RAIZ / "schema.sql").read_text(encoding="utf-8")
    dono = {m._meta.db_table: f"{m._meta.app_label}.{m.__name__}" for m in apps.get_models()}
    comentarios_tabela = dict(re.findall(r"COMMENT ON TABLE (\w+) IS\s*'((?:[^']|'')*)'", sql))
    comentarios_coluna = {
        (t, c): texto
        for t, c, texto in re.findall(r"COMMENT ON COLUMN (\w+)\.(\w+) IS\s*'((?:[^']|'')*)'", sql)
    }
    linhas = [
        "# Modelo e dicionário de dados",
        "",
        AVISO_GERADO,
        "",
        "Fonte: `schema.sql`, a transcrição da Apostila IV, seção 6 — e conferido contra o banco criado",
        "pelas migrações em `backend/tests/` (cada tabela tem um teste `divergencias_do_schema`).",
        "Saldo de estoque não é coluna: é a view `vw_estoque_atual`, derivada das movimentações (RN01).",
        "",
    ]
    for tabela, corpo in re.findall(r"CREATE TABLE (\w+) \((.*?)\n\);", sql, re.S):
        linhas += [f"## `{tabela}`", ""]
        if tabela in comentarios_tabela:
            linhas += [comentarios_tabela[tabela].replace("''", "'"), ""]
        linhas += [
            f"Model no código: `{dono.get(tabela, '—')}`",
            "",
            "| Coluna | Tipo | Regras | Observação |",
            "|---|---|---|---|",
        ]
        restricoes = []
        for linha in corpo.splitlines():
            texto, _, nota = linha.partition("--")
            texto = texto.strip().rstrip(",")
            if not texto:
                continue
            if texto.startswith(("CONSTRAINT", "PRIMARY KEY", "UNIQUE")):
                restricoes.append(texto)
                continue
            campo = re.match(r"(\w+)\s+([A-Z]+(?:\(\d+(?:,\d+)?\))?)\s*(.*)", texto)
            if not campo:
                continue
            nome, tipo, resto = campo.groups()
            observacao = (
                comentarios_coluna.get((tabela, nome), nota.strip()).replace("''", "'").replace("|", "/")
            )
            linhas.append(f"| `{nome}` | {tipo} | {' '.join(resto.split()) or '—'} | {observacao or '—'} |")
        if restricoes:
            linhas += ["", "Restrições: " + " · ".join(f"`{' '.join(r.split())}`" for r in restricoes)]
        linhas.append("")
    return "\n".join(linhas)


# ------------------------------------------------------------------------------------------ Contratos da API


# O que cada endereço faz, no vocabulário da loja. Endereço novo sem linha aqui sai marcado como
# SEM_DESCRICAO, e o teste da documentação falha até alguém escrever o que ele faz.
SEM_DESCRICAO = "**sem descrição: escreva em DESCRICOES, docs/sistema/gerar.py**"
DESCRICOES = {
    "/api/": "Lista os endereços da API para quem já entrou.",
    "/api/sessoes/": "POST {login, senha}: entra no sistema e recebe o token (A4, L09).",
    "/api/sessoes/atual/": "Quem está usando e as telas do menu daquele perfil (RN14).",
    "/api/categorias/": "GET lista; POST cria categoria, de dentro da tela de Produtos (B2, L18).",
    "/api/categorias/{pk}/": "GET uma categoria; PUT/PATCH altera. Não existe exclusão (tabela de origem).",
    "/api/fornecedores/": "GET lista (filtro por nome); POST cadastra fornecedor (RF02).",
    "/api/fornecedores/{pk}/": "GET um fornecedor; PUT/PATCH altera. Não existe exclusão.",
    "/api/produtos/": "GET lista (filtros por nome e categoria); POST cadastra produto, com a RN03 (RF01, RF15).",
    "/api/produtos/{pk}/": "GET um produto; PUT/PATCH altera, com a RN03. Não existe exclusão.",
    "/api/lotes/": "GET lotes do dia ou do produto; POST registra a mercadoria que chegou, com a RN04 (operação 02).",
    "/api/lotes/{pk}/": "GET um lote. Lote não se edita nem se apaga (RN01).",
    "/api/perdas/": "GET perdas do dia; POST registra perda com motivo, saindo do lote certo (RF04, RN02, RN16).",
    "/api/perdas/{pk}/": "GET uma perda. Perda não se edita nem se apaga (RN01).",
    "/api/estoque/": "Saldo de cada produto, com abaixo do mínimo e vencidos (RF07, RN01, RN16).",
    "/api/estoque/lotes/": "Os lotes de cada produto, do que vence primeiro ao último (RN02, RN16).",
    "/api/importacoes/": "As últimas 30 planilhas do caixa lidas, com a situação de cada uma (E5).",
    "/api/itens-pendentes/": "Vendas da planilha que não casaram com o cadastro, para conferir (E4, L26).",
    "/api/itens-pendentes/{pk}/casar/": "POST {produto}: liga a venda ao produto e baixa o estoque no dia da venda (RN01, RN02).",
    "/api/fechamentos/": "GET fechamentos do dia; POST {valor_contado} registra o fechamento (RF12, RN15).",
    "/api/fechamentos/apurado/": "O valor apurado pelo sistema: vendas em dinheiro do dia do fechamento (L12).",
    "/api/balancos/": "GET ?semana=AAAA-MM-DD: vendas, perdas e resultado da semana (RF13, L16).",
    "/api/telegram/": 'Webhook: recebe o toque do Sr. João em "Sim, pedir" (H7). Só com o segredo do Telegram.',
}


def contratos_da_api() -> str:
    _django()
    from django.urls import URLPattern, URLResolver, get_resolver

    from comum.permissoes import ACESSO_POR_TELA

    def percorrer(padroes, prefixo=""):
        for padrao in padroes:
            if isinstance(padrao, URLResolver):
                yield from percorrer(padrao.url_patterns, prefixo + str(padrao.pattern))
            elif isinstance(padrao, URLPattern):
                yield prefixo + str(padrao.pattern), padrao.callback

    def endereco(rota):
        rota = rota.replace("^", "").replace("$", "").replace("\\.(?P<format>[a-z0-9]+)/?", "")
        rota = re.sub(r"\(\?P<(\w+)>[^)]+\)", r"{\1}", rota)
        rota = re.sub(r"<(?:\w+:)?(\w+)>", r"{\1}", rota)
        return "/" + rota.replace("//", "/")

    vistos, linhas = set(), []
    for rota, callback in percorrer(get_resolver().url_patterns):
        caminho = endereco(rota)
        if not caminho.startswith("/api/") or "format" in rota or caminho in vistos:
            continue
        vistos.add(caminho)
        visao = getattr(callback, "cls", None) or getattr(callback, "view_class", None)
        if visao is None:
            continue
        # o DRF acrescenta "head" em `actions` na primeira chamada da rota: sem o filtro, a lista
        # mudaria conforme o que já rodou antes (o teste falhava só na suíte inteira — J1, 16/11/2026)
        acoes = [m for m in getattr(callback, "actions", None) or {} if m != "head"]
        metodos = (
            sorted(m.upper() for m in acoes)
            if acoes
            else sorted(m.upper() for m in ("get", "post", "put", "patch", "delete") if hasattr(visao, m))
        )
        tela = getattr(visao, "tela", None)
        if tela:
            quem = ", ".join(sorted(ACESSO_POR_TELA.get(tela, [])))
            acesso = f"tela `{tela}` — {quem}"
        elif getattr(visao, "qualquer_perfil", False):
            acesso = "qualquer pessoa com login"
        else:
            nomes = [p.__name__ for p in getattr(visao, "permission_classes", [])]
            acesso = (
                "sem login (entrada no sistema)"
                if "AllowAny" in nomes
                else ("segredo do Telegram (H7)" if "SoOTelegram" in nomes else "qualquer pessoa com login")
            )
        linhas.append((caminho, ", ".join(metodos), acesso, DESCRICOES.get(caminho, SEM_DESCRICAO)))

    saida = [
        "# Contratos da API",
        "",
        AVISO_GERADO,
        "",
        "A API REST é a porta única de entrada (Apostila IV, seção 3). Tudo é JSON. Toda requisição,",
        "fora a entrada no sistema e o webhook do Telegram, leva `Authorization: Bearer <token>`; o",
        "perfil (RN14) é conferido antes de qualquer operação, pela tela que cada endereço declara.",
        "",
        "Formato de erro, igual em toda a API (`backend/comum/erros.py`):",
        "",
        "```",
        '{"erro": {"codigo": "validacao", "mensagem": "Confira os campos destacados.",',
        '          "campos": {"durabilidade_dias": ["..."]}, "regra": "RN03"}}',
        "```",
        "",
        "| Endereço | Métodos | Quem pode usar | O que faz |",
        "|---|---|---|---|",
    ]
    saida += [f"| `{c}` | {m} | {a} | {r} |" for c, m, a, r in sorted(linhas)]
    saida += [
        "",
        "O detalhe de cada campo está no serializer correspondente (`backend/*/serializers.py`) e nos testes da tarefa.",
    ]
    return "\n".join(saida) + "\n"


# ------------------------------------------------------------------------------------------ Dependências


FIM_DE_SUPORTE = {
    "Django": "5.2 é LTS: correções de segurança até abril de 2028",
    "djangorestframework": "acompanha as versões do Django",
    "psycopg": "série 3, ativa",
    "python-dotenv": "ativa",
    "openpyxl": "ativa",
    "pytest": "série 8, ativa",
    "pytest-django": "ativa",
    "pytest-playwright": "ativa",
    "ruff": "ativa",
}


def dependencias() -> str:
    linhas = [
        "# Inventário de dependências (SBOM)",
        "",
        AVISO_GERADO,
        "",
        "Só as bibliotecas que o projeto pede (`requirements.txt` e `requirements-dev.txt`); o resto vem",
        "junto com elas. Dependência nova só entra com decisão do grupo (CLAUDE.md). Nenhuma biblioteca",
        "roda no navegador: o painel é HTML, CSS e JavaScript puros, com fontes servidas pelo próprio",
        "painel (licença OFL, `frontend/fontes/`).",
        "",
        "| Biblioteca | Pedida | Instalada | Licença | Uso | Para quê | Suporte |",
        "|---|---|---|---|---|---|---|",
    ]
    for arquivo, uso in (("requirements.txt", "execução"), ("requirements-dev.txt", "desenvolvimento")):
        for linha in (RAIZ / arquivo).read_text(encoding="utf-8").splitlines():
            texto, _, comentario = linha.partition("#")
            texto = texto.strip()
            if not texto or texto.startswith("-r"):
                continue
            nome = re.split(r"[\[<>=!~ ]", texto, maxsplit=1)[0]
            pedido = texto[len(nome) :].replace("[binary]", " (binary)").strip()
            try:
                distribuicao = metadados.distribution(nome)
                versao = distribuicao.version
                licenca = distribuicao.metadata.get("License-Expression") or next(
                    (
                        c.split("::")[-1].strip()
                        for c in distribuicao.metadata.get_all("Classifier") or []
                        if c.startswith("License ::")
                    ),
                    (distribuicao.metadata.get("License") or "—").splitlines()[0][:30],
                )
            except metadados.PackageNotFoundError:
                versao, licenca = "não instalada", "—"
            linhas.append(
                f"| {nome} | `{pedido}` | {versao} | {licenca} | {uso} | {comentario.strip() or '—'} | {FIM_DE_SUPORTE.get(nome, '—')} |"
            )
    linhas += [
        "",
        "Componentes fora do Python: **PostgreSQL 17** (fixado pela Apostila IV; suporte até novembro de",
        "2029), rodando em contêiner Docker (`docker-compose.yml`), e **Python 3.11 ou mais novo** (3.11",
        "tem suporte até outubro de 2027). A versão de cada um no computador do Matheus está na",
        "matriz de compatibilidade (`evoluir/compatibilidade.md`).",
    ]
    return "\n".join(linhas) + "\n"


GERADOS = {
    "manter/rastreabilidade.md": rastreabilidade,
    "manter/dicionario-de-dados.md": dicionario_de_dados,
    "manter/contratos-da-api.md": contratos_da_api,
    "evoluir/dependencias.md": dependencias,
}


def desatualizados() -> list[str]:
    return [
        nome
        for nome, gerar in GERADOS.items()
        if not (PASTA / nome).exists() or (PASTA / nome).read_text(encoding="utf-8") != gerar()
    ]


# ------------------------------------------------------------------------------------------ Página e PDF
# A página (DOCUMENTACAO-DO-SISTEMA.html) e o PDF saem dos mesmos .md. O estilo e o script ficam em
# docs/sistema/modelo/ e entram inteiros no HTML: é um arquivo só, sem internet e sem biblioteca.

MODELO = PASTA / "modelo"
SITUACOES = {"Pronto": "pronto", "Parcial": "parcial", "Gerado": "gerado"}
_CODIGO_CITADO = re.compile(r"\b(RN\d{2}|RF\d{2}|ADR-\d{3})\b")
_DOCUMENTO_CITADO = re.compile(r"^(?:docs/sistema/)?((?:usar|manter|sustentar|evoluir)/[\w-]+)\.md$")
_destinos_conhecidos: set[str] | None = None


def _ler(nome: str) -> str:
    return (PASTA / nome).read_text(encoding="utf-8")


def _slug(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFD", texto.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", sem_acento).strip("-")


def _destinos() -> set[str]:
    """O que pode ser citado no texto e virar link: regras e requisitos (rastreabilidade), ADRs, documentos."""
    global _destinos_conhecidos
    if _destinos_conhecidos is None:
        _destinos_conhecidos = (
            set(re.findall(r"^\| ((?:RN|RF)\d{2}) \|", _ler("manter/rastreabilidade.md"), re.M))
            | set(re.findall(r"^#+ (ADR-\d{3})\b", _ler("manter/adrs.md"), re.M))
            | {_slug(d.relative_to(PASTA).with_suffix("").as_posix()) for d in PASTA.glob("*/*.md")}
        )
    return _destinos_conhecidos


def _inline(texto: str, refs: bool = True, exceto: str | None = None) -> str:
    """Negrito, itálico e código; com `refs`, o código de regra, o ADR e o documento citados viram link."""
    codigos: list[str] = []

    def guardar(m):
        conteudo = m.group(1)
        # <wbr>: o caminho comprido pode quebrar depois de cada barra (na folha A4 não cabe inteiro).
        marcado = f"<code>{html.escape(conteudo, quote=False).replace('/', '/<wbr>')}</code>"
        documento = _DOCUMENTO_CITADO.match(conteudo)
        if refs and documento and _slug(documento.group(1)) in _destinos():
            marcado = f'<a href="#{_slug(documento.group(1))}">{marcado}</a>'
        codigos.append(marcado)
        return f"\x00{len(codigos) - 1}\x00"

    texto = re.sub(r"`([^`]+)`", guardar, texto)
    texto = html.escape(texto, quote=False).replace("&lt;br&gt;", "<br>")
    texto = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", texto)
    texto = re.sub(r"(?<![\w*])\*([^*]+)\*(?!\w)", r"<i>\1</i>", texto)
    texto = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", texto)
    if refs:
        texto = _CODIGO_CITADO.sub(
            lambda m: (
                f'<a class="ref" href="#{m.group(1)}">{m.group(1)}</a>'
                if m.group(1) in _destinos() and m.group(1) != exceto
                else m.group(1)
            ),
            texto,
        )
    return re.sub(r"\x00(\d+)\x00", lambda m: codigos[int(m.group(1))], texto)


class _Pagina:
    """Guarda o que a página inteira precisa saber: os ids já usados (não podem repetir)."""

    def __init__(self):
        self.ids: set[str] = set()

    def novo_id(self, desejado: str) -> str:
        candidato, n = desejado or "secao", 2
        while candidato in self.ids:
            candidato, n = f"{desejado}-{n}", n + 1
        self.ids.add(candidato)
        return candidato


def markdown_para_html(
    texto: str,
    nivel_base: int = 2,
    prefixo: str = "",
    pagina: _Pagina | None = None,
    define_codigos: bool = False,
    secoes: list | None = None,
) -> str:
    """
    O pedaço do Markdown que estes documentos usam: títulos, parágrafos, listas, tabelas, código,
    citação. Cada título ganha um id (`prefixo`-título) e uma âncora; `secoes` recebe os de primeiro
    nível, para o menu. Com `define_codigos`, a linha de tabela que começa por RN05 vira o destino #RN05.
    """
    pagina = pagina or _Pagina()
    saida, linhas, i = [], texto.splitlines(), 0
    while i < len(linhas):
        linha = linhas[i]
        if linha.startswith("```"):
            bloco = []
            i += 1
            while i < len(linhas) and not linhas[i].startswith("```"):
                bloco.append(html.escape(linhas[i]))
                i += 1
            saida.append("<div class='codigo'><pre>" + "\n".join(bloco) + "</pre></div>")
        elif m := re.match(r"(#+) (.*)", linha):
            nivel = min(6, len(m.group(1)) + nivel_base - 1)
            titulo = m.group(2)
            adr = re.match(r"(ADR-\d{3})\b", titulo)
            sem_marcacao = re.sub(r"[`*]", "", titulo)
            desejado = adr.group(1) if adr else "-".join(filter(None, [prefixo, _slug(sem_marcacao)]))
            ancora = pagina.novo_id(desejado)
            if secoes is not None and len(m.group(1)) == 2:
                secoes.append((ancora, sem_marcacao))
            saida.append(
                f'<h{nivel} id="{ancora}">{_inline(titulo, refs=False)}'
                f'<a class="ancora" href="#{ancora}" aria-label="Link para esta seção">#</a></h{nivel}>'
            )
        elif linha.startswith("|"):
            tabela = []
            while i < len(linhas) and linhas[i].startswith("|"):
                tabela.append([c.strip() for c in linhas[i].strip("|").split("|")])
                i += 1
            i -= 1
            cabecalho, corpo = tabela[0], [t for t in tabela[1:] if not set("".join(t)) <= set("-: ")]
            corpo_html = []
            for celulas in corpo:
                codigo = celulas[0] if define_codigos and re.fullmatch(r"(RN|RF)\d{2}", celulas[0]) else None
                abre = f'<tr id="{pagina.novo_id(codigo)}">' if codigo else "<tr>"
                corpo_html.append(
                    abre + "".join(f"<td>{_inline(c, exceto=codigo)}</td>" for c in celulas) + "</tr>"
                )
            larga = " tabela--larga" if len(cabecalho) >= 5 else ""
            larga += " tabela--rastro" if define_codigos else ""
            saida.append(
                f"<div class='tabela{larga}'><table><thead><tr>"
                + "".join(f"<th scope='col'>{_inline(c, refs=False)}</th>" for c in cabecalho)
                + "</tr></thead><tbody>"
                + "".join(corpo_html)
                + "</tbody></table></div>"
            )
        elif re.match(r"\s*([-*]|\d+\.) ", linha):
            ordenada = bool(re.match(r"\s*\d+\.", linha))
            itens = []
            while i < len(linhas) and (
                re.match(r"\s*([-*]|\d+\.) ", linhas[i]) or (linhas[i].startswith("  ") and linhas[i].strip())
            ):
                if re.match(r"\s*([-*]|\d+\.) ", linhas[i]):
                    itens.append(re.sub(r"\s*([-*]|\d+\.) ", "", linhas[i], count=1))
                else:
                    itens[-1] += " " + linhas[i].strip()
                i += 1
            i -= 1
            marca = "ol" if ordenada else "ul"
            saida.append(
                f"<{marca}>" + "".join(f"<li>{_inline(item)}</li>" for item in itens) + f"</{marca}>"
            )
        elif linha.startswith(">"):
            bloco = []
            while i < len(linhas) and linhas[i].startswith(">"):
                bloco.append(linhas[i].lstrip("> "))
                i += 1
            i -= 1
            citacao = " ".join(bloco)
            if citacao.startswith("Gerado automaticamente"):
                citacao = citacao.removeprefix("Gerado automaticamente ")
                saida.append(
                    f"<blockquote class='do-codigo'>{_inline(citacao[0].upper() + citacao[1:])}</blockquote>"
                )
            else:
                saida.append("<blockquote>" + _inline(citacao) + "</blockquote>")
        elif linha.strip():
            paragrafo = [linha]
            while (
                i + 1 < len(linhas)
                and linhas[i + 1].strip()
                and not re.match(r"(#|\||```|>|\s*([-*]|\d+\.) )", linhas[i + 1])
            ):
                i += 1
                paragrafo.append(linhas[i])
            # Pergunta em negrito numa linha e a resposta na seguinte (FAQ): a resposta desce uma linha.
            if len(paragrafo) > 1 and re.fullmatch(r"\*\*[^*]+\*\*", paragrafo[0].strip()):
                paragrafo[0] = paragrafo[0].strip() + "<br>"
            saida.append("<p>" + _inline(" ".join(paragrafo)) + "</p>")
        i += 1
    return "\n".join(saida)


def documentos_do_indice() -> dict[str, list[dict]]:
    """Pasta → os documentos dela, na ordem do índice (LEIA-ME.md), com nome, situação e data."""
    por_pasta: dict[str, list[dict]] = {pasta: [] for pasta, *_ in PILARES}
    linhas = re.findall(
        r"^\| (?:Usar|Manter|Sustentar|Evoluir) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$",
        _ler("LEIA-ME.md"),
        re.M,
    )
    for nome, arquivos, situacao, data in linhas:
        arquivo = next(a for a in re.findall(r"`([^`]+\.md)`", arquivos) if a.split("/")[0] in por_pasta)
        tipo, _, detalhe = situacao.strip().partition(":")
        por_pasta[arquivo.split("/")[0]].append(
            {
                "nome": nome.strip(),
                "arquivo": arquivo,
                "id": _slug(arquivo.removesuffix(".md")),
                "tipo": SITUACOES[tipo.strip()],
                "situacao": "Gerado do código" if tipo.strip() == "Gerado" else tipo.strip(),
                "detalhe": detalhe.strip(),
                "data": data.strip(),
            }
        )
    return por_pasta


def ficha() -> dict[str, str]:
    """Os números da capa, tirados dos próprios documentos (e do git) na hora de gerar."""

    def contar(padrao: str, nome: str) -> str:
        return str(len(re.findall(padrao, _ler(nome), re.M)))

    versao = re.search(r"^## (\d+\.\d+\.\d+)", _ler("evoluir/changelog.md"), re.M)
    testes = re.search(r"\*\*([\d.]+) testes automáticos", _ler("evoluir/testes-de-regressao.md"))
    try:
        commit = subprocess.run(  # noqa: S603 — comando fixo
            ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607 — o git do PATH
            cwd=RAIZ,
            capture_output=True,
            text=True,
            check=False,
        ).stdout.strip()
    except OSError:
        commit = ""
    return {
        "Documento": DOCUMENTO,
        "Versão do documento": VERSAO,
        "Emitido em": EMISSAO,
        "Versão do sistema": versao.group(1) if versao else "—",
        "Gerado sobre o commit": commit or "—",
        "Testes automáticos": testes.group(1) if testes else "—",
        "Regras de negócio": contar(r"^\| RN\d{2} \|", "manter/rastreabilidade.md"),
        "Requisitos funcionais": contar(r"^\| RF\d{2} \|", "manter/rastreabilidade.md"),
        "Tabelas": contar(r"^## `", "manter/dicionario-de-dados.md"),
        "Endereços da API": contar(r"^\| `/api", "manter/contratos-da-api.md"),
        "Decisões de arquitetura": contar(r"^#+ ADR-\d{3}", "manter/adrs.md"),
        "Documentos": str(sum(len(docs) for docs in documentos_do_indice().values())),
    }


def _marca(tipo: str) -> str:
    return f"<span class='marca marca--{tipo}' aria-hidden='true'></span>"


def montar_html() -> str:
    pagina = _Pagina()
    for fixo in ("inicio", "conteudo", "mapa", "mapa-titulo", "sobre", "menu", "lateral"):
        pagina.novo_id(fixo)
    indice = documentos_do_indice()
    numeros = ficha()
    e = html.escape

    mapa, menu, corpo = [], [], []
    for pasta, titulo, pergunta, referencia in PILARES:
        pagina.novo_id(pasta)
        itens_mapa, itens_menu, artigos = [], [], []
        for doc in indice[pasta]:
            pagina.novo_id(doc["id"])
            texto = _ler(doc["arquivo"])
            titulo_doc = re.match(r"# (.*)", texto).group(1)
            secoes: list[tuple[str, str]] = []
            # O título e a data vão para o cabeçalho do documento; no texto seriam repetição.
            texto = re.sub(r"\*Atualizado em \d{2}/\d{2}/\d{4}\.\*\s*", "", texto, count=1)
            conteudo = markdown_para_html(
                re.sub(r"^# .*\n", "", texto, count=1),
                nivel_base=3,
                prefixo=doc["id"],
                pagina=pagina,
                define_codigos=doc["arquivo"] == "manter/rastreabilidade.md",
                secoes=secoes,
            )
            detalhe = f" — {e(doc['detalhe'])}" if doc["detalhe"] else ""
            selo = f"<span class='selo selo--{doc['tipo']}'>{e(doc['situacao'])}{detalhe}</span>"
            atualizado = "a cada geração" if doc["tipo"] == "gerado" else e(doc["data"])
            artigos.append(
                f'<article class="doc" id="{doc["id"]}"><header class="doc__cabeca">'
                f'<h3 class="doc__titulo">{_inline(titulo_doc, refs=False)}</h3><dl class="doc__meta">'
                f"<div><dt>Arquivo</dt><dd><code>docs/sistema/{e(doc['arquivo'])}</code></dd></div>"
                f"<div><dt>Situação</dt><dd>{selo}</dd></div>"
                f"<div><dt>Atualizado</dt><dd>{atualizado}</dd></div></dl></header>"
                f'<div class="texto">{conteudo}</div></article>'
            )
            itens_mapa.append(
                f'<li><a class="mapa__doc mapa__doc--{doc["tipo"]}" href="#{doc["id"]}">'
                f"<span class='mapa__titulo'>{e(doc['nome'])}</span>"
                f"<span class='mapa__situacao'>{_marca(doc['tipo'])}{e(doc['situacao'])}</span></a></li>"
            )
            sub = "".join(f'<li><a href="#{a}">{e(t)}</a></li>' for a, t in secoes)
            itens_menu.append(
                f'<li data-doc="{doc["id"]}"><a class="menu__doc" href="#{doc["id"]}">{_marca(doc["tipo"])}'
                f"<span>{e(doc['nome'])}<span class='oculto'>, {e(doc['situacao'])}</span></span></a>"
                + (f'<ul class="menu__secoes">{sub}</ul>' if sub else "")
                + "</li>"
            )
        mapa.append(
            f'<div class="mapa__pilar"><h3><a href="#{pasta}">{titulo}</a></h3>'
            f'<p class="mapa__pergunta">{e(pergunta)}</p><ol>{"".join(itens_mapa)}</ol></div>'
        )
        menu.append(
            f'<div class="menu__grupo"><p class="menu__pilar"><a href="#{pasta}">{titulo}</a></p>'
            f'<ul class="menu__lista">{"".join(itens_menu)}</ul></div>'
        )
        corpo.append(
            f'<section class="pilar" id="{pasta}"><h2 class="pilar__titulo">{titulo}</h2>'
            f'<p class="pilar__pergunta">{e(pergunta)} Referência: {e(referencia)}.</p>{"".join(artigos)}</section>'
        )

    # O índice (LEIA-ME.md) sem o título e sem a tabela dos 24: o mapa da capa é essa tabela.
    sobre = re.sub(r"^# .*\n", "", _ler("LEIA-ME.md"), count=1)
    sobre = re.sub(r"## Os 24 documentos\n.*?(?=^## )", "", sobre, flags=re.S | re.M)
    sobre = re.sub(r"\*Atualizado em \d{2}/\d{2}/\d{4}\.\*\s*", "", sobre, count=1)
    sobre_html = markdown_para_html(sobre, nivel_base=3, prefixo="sobre", pagina=pagina)

    legenda = "".join(
        f"<li>{_marca(tipo)}{texto}</li>"
        for tipo, texto in [
            ("pronto", "Pronto: cobre o sistema de hoje"),
            ("parcial", "Parcial: existe, com a lacuna declarada no próprio documento"),
            ("gerado", "Gerado do código: um teste falha se ficar velho"),
        ]
    )
    itens_ficha = "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in numeros.items())
    estilo = (MODELO / "estilo.css").read_text(encoding="utf-8")
    script = (MODELO / "pagina.js").read_text(encoding="utf-8")
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Documentação do Sistema — Mercado do Sr. João</title>
<style>{estilo}</style>
</head>
<body>
<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<button type="button" class="botao abrir-menu" id="abrir-menu" aria-expanded="false" aria-controls="lateral">Menu</button>
<aside class="lateral" id="lateral" aria-label="Navegação da documentação">
<div class="lateral__topo">
<p class="lateral__nome"><a href="#inicio">Documentação do Sistema</a></p>
<p class="lateral__versao">Mercado do Sr. João, versão {e(numeros["Versão do sistema"])}</p>
<div class="busca"><label class="oculto" for="campo-busca">Procurar nos documentos</label>
<input id="campo-busca" type="search" placeholder="Procurar" autocomplete="off" aria-describedby="resultado-busca"><kbd aria-hidden="true">/</kbd></div>
<p class="busca__resultado" id="resultado-busca" aria-live="polite"></p>
</div>
<nav id="menu" aria-label="Documentos">
<div><a class="menu__atalho" href="#mapa">Os 24 documentos</a><a class="menu__atalho" href="#sobre">Como esta documentação é mantida</a></div>
{"".join(menu)}
</nav>
<div class="lateral__pe"><button type="button" class="botao" id="botao-tema">Tema escuro</button></div>
</aside>
<main id="conteudo" tabindex="-1">
<header class="capa" id="inicio">
<p class="capa__grupo">Engenharia de Software, Grupo MDGS</p>
<h1>Documentação do Sistema</h1>
<p class="capa__sistema">Sistema de Gestão de Estoque e Compras do Mercado do Sr. João</p>
<dl class="ficha">{itens_ficha}</dl>
</header>
<section id="mapa" aria-labelledby="mapa-titulo">
<h2 id="mapa-titulo">Os 24 documentos</h2>
<ul class="mapa__legenda">{legenda}</ul>
<div class="mapa">{"".join(mapa)}</div>
</section>
<section class="pilar" id="sobre"><h2 class="pilar__titulo">Como esta documentação é mantida</h2>
<div class="texto">{sobre_html}</div></section>
{"".join(corpo)}
<p class="pe">Gerado por <code>python docs/sistema/gerar.py</code> a partir dos arquivos de <code>docs/sistema/</code>.</p>
</main>
<script>{script}</script>
</body>
</html>
"""


def gerar_pdf() -> Path:
    from playwright.sync_api import sync_playwright

    saida_html = PASTA / "DOCUMENTACAO-DO-SISTEMA.html"
    saida_html.write_text(montar_html(), encoding="utf-8")
    saida_pdf = PASTA / "DOCUMENTACAO-DO-SISTEMA.pdf"
    rodape = (
        "<div style='font:7pt Helvetica,Arial,sans-serif;color:#4a5a52;width:100%;padding:0 15mm;"
        "display:flex;justify-content:space-between'>"
        f"<span>{DOCUMENTO}, versão {VERSAO}, emitido em {EMISSAO}</span>"
        "<span>página <span class='pageNumber'></span> de <span class='totalPages'></span></span></div>"
    )
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        aba = navegador.new_page()
        aba.goto(saida_html.as_uri())
        aba.wait_for_load_state("networkidle")
        aba.evaluate("document.fonts.ready")
        aba.pdf(
            path=str(saida_pdf),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=rodape,
            margin={"top": "16mm", "bottom": "18mm", "left": "15mm", "right": "15mm"},
            outline=True,  # marcadores do PDF a partir dos títulos
            tagged=True,
        )
        navegador.close()
    return saida_pdf


def principal(argumentos=None) -> int:
    leitor = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    leitor.add_argument(
        "--conferir", action="store_true", help="só confere se os documentos gerados estão em dia"
    )
    leitor.add_argument("--sem-pdf", action="store_true", help="regenera os .md sem montar o PDF")
    opcoes = leitor.parse_args(argumentos)
    if opcoes.conferir:
        velhos = desatualizados()
        for nome in velhos:
            print(f"desatualizado: docs/sistema/{nome}")
        return 1 if velhos else 0
    for nome, gerar in GERADOS.items():
        (PASTA / nome).parent.mkdir(parents=True, exist_ok=True)
        (PASTA / nome).write_text(gerar(), encoding="utf-8")
        print(f"gerado: docs/sistema/{nome}")
    if not opcoes.sem_pdf:
        print(f"PDF: {gerar_pdf().relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(principal())

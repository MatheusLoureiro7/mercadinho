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

O PDF (DOCUMENTACAO-DO-SISTEMA.pdf) junta tudo, com cabeçalho oficial, a partir dos mesmos .md.
"""

import argparse
import html
import importlib.metadata as metadados
import os
import re
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[1]
BACKEND = RAIZ / "backend"
DOCUMENTO = "MDGS-DOC-001"
VERSAO = "1.0"
EMISSAO = "13/11/2026"
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
        acoes = getattr(callback, "actions", None)
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


# ------------------------------------------------------------------------------------------ PDF


def _inline(texto: str) -> str:
    texto = html.escape(texto, quote=False).replace("&lt;br&gt;", "<br>")
    texto = re.sub(r"`([^`]+)`", r"<code>\1</code>", texto)
    texto = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", texto)
    texto = re.sub(r"(?<![\w*])\*([^*]+)\*(?!\w)", r"<i>\1</i>", texto)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", texto)


def markdown_para_html(texto: str, nivel_base: int = 2) -> str:
    """O pedaço do Markdown que estes documentos usam: títulos, parágrafos, listas, tabelas, código, citação."""
    saida, linhas, i = [], texto.splitlines(), 0
    while i < len(linhas):
        linha = linhas[i]
        if linha.startswith("```"):
            bloco = []
            i += 1
            while i < len(linhas) and not linhas[i].startswith("```"):
                bloco.append(html.escape(linhas[i]))
                i += 1
            saida.append("<pre>" + "\n".join(bloco) + "</pre>")
        elif m := re.match(r"(#+) (.*)", linha):
            nivel = min(6, len(m.group(1)) + nivel_base - 1)
            saida.append(f"<h{nivel}>{_inline(m.group(2))}</h{nivel}>")
        elif linha.startswith("|"):
            tabela = []
            while i < len(linhas) and linhas[i].startswith("|"):
                tabela.append([c.strip() for c in linhas[i].strip("|").split("|")])
                i += 1
            i -= 1
            cabecalho, corpo = tabela[0], [t for t in tabela[1:] if not set("".join(t)) <= set("-: ")]
            saida.append(
                "<table><thead><tr>"
                + "".join(f"<th>{_inline(c)}</th>" for c in cabecalho)
                + "</tr></thead><tbody>"
                + "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in t) + "</tr>" for t in corpo)
                + "</tbody></table>"
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
            saida.append("<blockquote>" + _inline(" ".join(bloco)) + "</blockquote>")
        elif linha.strip():
            paragrafo = [linha]
            while (
                i + 1 < len(linhas)
                and linhas[i + 1].strip()
                and not re.match(r"(#|\||```|>|\s*([-*]|\d+\.) )", linhas[i + 1])
            ):
                i += 1
                paragrafo.append(linhas[i])
            saida.append("<p>" + _inline(" ".join(paragrafo)) + "</p>")
        i += 1
    return "\n".join(saida)


ESTILO = """
@font-face { font-family: Plex; font-weight: 400; src: url(FONTES/ibm-plex-sans-400.woff2); }
@font-face { font-family: Plex; font-weight: 600; src: url(FONTES/ibm-plex-sans-600.woff2); }
* { box-sizing: border-box; }
body { font-family: Plex, sans-serif; font-size: 9.4pt; line-height: 1.45; color: #1d2430; margin: 0; }
header.capa { border-bottom: 1.5pt solid #12305a; padding-bottom: 4mm; margin-bottom: 5mm; }
.sup { font-size: 8.4pt; color: #556; display: flex; justify-content: space-between; }
h1 { font-size: 21pt; color: #12305a; margin: 3mm 0 1mm; font-weight: 600; }
.sistema { font-size: 11pt; color: #33415a; }
section.pilar { break-before: page; }
section.pilar > h1 { font-size: 17pt; margin-top: 0; }
.pergunta { font-style: italic; color: #33415a; margin-bottom: 4mm; }
h2 { font-size: 13pt; color: #12305a; font-weight: 600; margin: 7mm 0 2mm; break-after: avoid; border-top: 0.5pt solid #b9c2d0; padding-top: 3mm; }
h3 { font-size: 11pt; color: #12305a; font-weight: 600; margin: 4mm 0 1.5mm; break-after: avoid; }
h4, h5 { font-size: 9.8pt; color: #12305a; margin: 3mm 0 1mm; }
p { margin: 0 0 2mm; }
table { width: 100%; border-collapse: collapse; margin: 1mm 0 3mm; font-size: 8.2pt; }
th, td { border: 0.5pt solid #b9c2d0; padding: 1.2mm 1.8mm; text-align: left; vertical-align: top; overflow-wrap: break-word; }
td code { overflow-wrap: anywhere; }
thead th { background: #12305a; color: #fff; font-weight: 600; }
tr { break-inside: avoid; }
code { font-family: Menlo, Consolas, monospace; font-size: 7.8pt; background: #eef1f6; padding: 0 0.6mm; }
pre { font-family: Menlo, Consolas, monospace; font-size: 7.6pt; background: #f2f5fa; border: 0.5pt solid #d5dbe5; padding: 2mm 3mm; white-space: pre-wrap; break-inside: avoid; }
blockquote { border-left: 2pt solid #12305a; background: #f2f5fa; margin: 2mm 0; padding: 2mm 3mm; }
ul, ol { margin: 0 0 2mm; padding-left: 5mm; } li { margin-bottom: 0.8mm; }
"""


def gerar_pdf() -> Path:
    from playwright.sync_api import sync_playwright

    indice = (PASTA / "LEIA-ME.md").read_text(encoding="utf-8")
    partes = [
        f"<header class='capa'><div class='sup'><span>Engenharia de Software · Grupo MDGS</span><span>{DOCUMENTO} · versão {VERSAO} · {EMISSAO}</span></div>"
        "<h1>Documentação do Sistema</h1><div class='sistema'>Sistema de Gestão de Estoque e Compras — Mercado do Sr. João</div></header>",
        markdown_para_html(re.sub(r"^# .*\n", "", indice, count=1)),
    ]
    for pasta, titulo, pergunta, referencia in PILARES:
        partes.append(
            f"<section class='pilar'><h1>{titulo}</h1><p class='pergunta'>{pergunta} · Referência: {referencia}</p>"
        )
        for arquivo in sorted((PASTA / pasta).glob("*.md")):
            partes.append(markdown_para_html(arquivo.read_text(encoding="utf-8")))
        partes.append("</section>")
    estilo = ESTILO.replace("FONTES", (RAIZ / "frontend" / "fontes").as_uri())
    pagina = f"<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><title>Documentação do Sistema</title><style>{estilo}</style></head><body>{''.join(partes)}</body></html>"
    saida_html = PASTA / "DOCUMENTACAO-DO-SISTEMA.html"
    saida_html.write_text(pagina, encoding="utf-8")
    saida_pdf = PASTA / "DOCUMENTACAO-DO-SISTEMA.pdf"
    rodape = f"<div style='font-size:7pt;color:#667;width:100%;text-align:center'>{DOCUMENTO} · versão {VERSAO} · emitido em {EMISSAO} · página <span class='pageNumber'></span> de <span class='totalPages'></span></div>"
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        aba = navegador.new_page()
        aba.goto(saida_html.as_uri())
        aba.wait_for_load_state("networkidle")
        aba.pdf(
            path=str(saida_pdf),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=rodape,
            margin={"top": "14mm", "bottom": "16mm", "left": "15mm", "right": "15mm"},
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

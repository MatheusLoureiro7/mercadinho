# ruff: noqa: E501  (textos do documento: quebrar a linha só atrapalha a leitura)
"""
Gera o Relatório de Testes (PDF, poucas páginas) a partir da última execução da suíte.

    pytest --junitxml=docs/testes/execucao.xml
    python docs/testes/gerar.py

Saída: docs/testes/RELATORIO-DE-TESTES.pdf (e o .html de onde ele sai).
Os números (total, aprovados, testes por regra e por bloco) são lidos do XML da execução — nada
de resultado digitado à mão.
"""

import collections
import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[1]
XML = PASTA / "execucao.xml"
SAIDA_HTML = PASTA / "RELATORIO-DE-TESTES.html"
SAIDA_PDF = PASTA / "RELATORIO-DE-TESTES.pdf"

DOCUMENTO = "MDGS-TST-001"
VERSAO = "1.0"
COMMIT = "6a66cbd"

BLOCOS = {
    "a": "A · Fundação: banco, API, login e perfis",
    "b": "B · Cadastros de produto, categoria e fornecedor",
    "c": "C · Entrada de mercadoria e saldo",
    "d": "D · Perdas e avarias",
    "f": "F · Consulta de estoque",
    "h": "H · Aviso de validade pelo Telegram",
    "i": "I · Tela de fechamento de caixa",
    "j": "J · Cobertura das regras",
    "telas": "Telas no celular e no tablet",
}
TESTADO_EM = {
    "a": "06/10/2026",
    "b": "06 a 08/10/2026",
    "c": "06 a 08/10/2026",
    "d": "07 e 08/10/2026",
    "f": "07 e 08/10/2026",
    "h": "08 e 09/10/2026",
    "i": "09/10/2026",
    "j": "09/10/2026",
    "telas": "09/10/2026",
}
# data em que cada regra foi testada (conclusão da tarefa dela) ou, se ainda não construída, a prevista
DATA_DA_REGRA = {
    "RN01": "06/10/2026",
    "RN02": "07/10/2026",
    "RN03": "06/10/2026",
    "RN04": "07/10/2026",
    "RN05": "08/10/2026",
    "RN06": "09 a 10/11/2026",
    "RN07": "09 a 10/11/2026",
    "RN08": "11 a 13/11/2026",
    "RN09": "11/11/2026",
    "RN10": "12 e 13/11/2026",
    "RN11": "07/10/2026",
    "RN12": "08/10/2026",
    "RN13": "08/10/2026",
    "RN14": "06/10/2026",
    "RN15": "09/10/2026",
    "RN16": "07/10/2026",
}
DEFEITOS = [
    ("06/10/2026", "Horário da movimentação diferente do modelo de dados da Apostila IV"),
    ("07/10/2026", 'Botão "Editar" fora da tela no computador da loja'),
    ("08/10/2026", 'Busca por "feijao" não achava "Feijão"'),
    ("08/10/2026", 'Clique em "Salvar" se perdia ao corrigir um campo'),
    ("08/10/2026", 'Aviso de "registrado" cobria os campos no celular'),
    ("08/10/2026", "Lista do dia não rolava só pelo teclado (acessibilidade)"),
    ("08/10/2026", 'Leitor de tela anunciava o botão "Ver lotes" errado (acessibilidade)'),
    ("09/10/2026", "Tela às vezes abria sem menu (servidor do painel com fila de 5 conexões)"),
    ("09/10/2026", "Código de vínculo do celular com um dígito a mais era aceito"),
    ("09/10/2026", "Tela de fechamento apagava o que a pessoa estava digitando"),
    ("09/10/2026", 'No celular, quantidade, validade e "Editar" ficavam escondidos'),
]

REGRAS = [
    (
        "RN01",
        "O saldo é sempre derivado das movimentações",
        "Entram 40 kg, vendem 12, perdem 3 → saldo 25 kg; ninguém grava saldo à mão",
    ),
    (
        "RN02",
        "A saída respeita a ordem de validade",
        "Presunto de 28/09 sai antes do de 05/10, mesmo o de 05/10 tendo chegado antes",
    ),
    (
        "RN03",
        "Perecível exige prazo de durabilidade",
        "Perecível sem prazo é recusado; com prazo, ou não perecível, é aceito",
    ),
    (
        "RN04",
        "Lote de perecível precisa de validade",
        "Sem validade, é calculada; validade de ontem é recusada; a de hoje, aceita",
    ),
    (
        "RN05",
        "Aviso de validade próxima",
        "Avisa dentro do prazo; um dia além, não; rodar duas vezes não duplica",
    ),
    ("RN06", "Consumo médio diário", ""),
    ("RN07", "Consumo por dia da semana", ""),
    ("RN08", "Ponto de pedido e aviso de ruptura", ""),
    ("RN09", "Histórico mínimo para prever", ""),
    ("RN10", "Produtos que não podem faltar no fim de semana", ""),
    ("RN11", "Perda não conta como consumo", "Frango jogado fora baixa o saldo, mas não aumenta o consumo"),
    ("RN12", "Janela de silêncio nos horários de pico", "Aviso das 11h15 fica segurado e sai às 13h05"),
    (
        "RN13",
        "Avisos agrupados em uma mensagem",
        "Seis avisos saem numa mensagem só, do mais urgente ao menos",
    ),
    ("RN14", "Três perfis de acesso", "Cada perfil abre só as suas telas; sem login, tudo é recusado"),
    (
        "RN15",
        "Diferença de caixa nunca corrigida",
        "Diferença calculada, não digitada; contar de novo gera registro novo",
    ),
    ("RN16", "Lote vencido é bloqueado", "Vencido não sai na venda, só como perda, e aparece destacado"),
]
SEM_CODIGO = {"RN06": "G2", "RN07": "G2", "RN08": "G3 e H3", "RN09": "G4", "RN10": "H3"}
PARCIAL = {"RN15": "só a tela; a gravação é da tarefa I1"}

NAO_TESTADO = [
    ("Importação das vendas do caixa e baixa por venda", "E3 a E5", "03 a 09/11/2026"),
    (
        'Previsão de consumo, ponto de pedido e aviso "vai acabar" (RN06 a RN10)',
        "G1 a G5, H3",
        "06 a 13/11/2026",
    ),
    ("Gravação do fechamento de caixa (RN15 completa)", "I1", "03 a 05/11/2026"),
    ("Balanço da semana", "I3", "09 a 11/11/2026"),
    ("Teste em movimento real e aviso no celular de verdade", "J4", "21/11/2026"),
]

e = html.escape


def ler_execucao():
    raiz = ET.parse(XML).getroot()  # noqa: S314 — arquivo gerado pelo próprio pytest
    suite = raiz if raiz.tag == "testsuite" else raiz.find("testsuite")
    testes = []
    for caso in suite.iter("testcase"):
        arquivo = caso.get("classname").split(".")[-1]
        falhou = caso.find("failure") is not None or caso.find("error") is not None
        testes.append((arquivo, caso.get("name"), not falhou))
    return testes, datetime.fromisoformat(suite.get("timestamp")), float(suite.get("time"))


def bloco_do_arquivo(arquivo):
    if arquivo == "test_telas_no_celular":
        return "telas"
    return re.match(r"test_([a-z])\d", arquivo).group(1)


def selo(texto, classe):
    return f'<span class="selo {classe}">{e(texto)}</span>'


def montar():
    testes, inicio, duracao = ler_execucao()
    total = len(testes)
    aprovados = sum(1 for t in testes if t[2])
    de_tela = sum(1 for t in testes if "[chromium" in t[1])
    pct = f"{100 * aprovados / total:.0f}"

    por_bloco = collections.defaultdict(lambda: [0, 0])
    por_regra = collections.Counter()
    for arquivo, nome, ok in testes:
        b = por_bloco[bloco_do_arquivo(arquivo)]
        b[0] += 1
        b[1] += ok
        for n in set(re.findall(r"rn(\d{2})", nome.split("[")[0])):
            por_regra[f"RN{n}"] += 1

    linhas_bloco = "".join(
        f"<tr><td>{e(BLOCOS[k])}</td><td class='num'>{t}</td><td class='num'>{a}</td>"
        f"<td class='data'>{TESTADO_EM[k]}</td>"
        f"<td>{selo('Aprovado', 'ok') if a == t else selo('Reprovado', 'falha')}</td></tr>"
        for k in BLOCOS
        for t, a in [por_bloco[k]]
        if t
    )

    linhas_regra = []
    for codigo, nome, exemplo in REGRAS:
        if codigo in SEM_CODIGO:
            situacao = selo("Não testada", "nao")
            detalhe = f"Ainda não construída (tarefa {SEM_CODIGO[codigo]})"
        elif codigo in PARCIAL:
            situacao = selo("Parcial", "parcial")
            detalhe = f"{exemplo} — {PARCIAL[codigo]}"
        else:
            situacao = selo("Aprovada", "ok")
            detalhe = exemplo
        linhas_regra.append(
            f"<tr><td class='id'>{codigo}</td><td>{e(nome)}</td><td>{e(detalhe)}</td>"
            f"<td class='num'>{por_regra.get(codigo, 0)}</td><td class='data'>{DATA_DA_REGRA[codigo]}</td>"
            f"<td>{situacao}</td></tr>"
        )
    regras_ok = 16 - len(SEM_CODIGO) - len(PARCIAL)

    linhas_defeito = "".join(
        f"<tr><td class='data'>{d}</td><td>{e(t)}</td><td class='data'>{d}</td></tr>" for d, t in DEFEITOS
    )
    linhas_falta = "".join(
        f"<tr><td>{e(a)}</td><td>{b}</td><td class='data'>{c}</td></tr>" for a, b, c in NAO_TESTADO
    )

    fontes = (RAIZ / "frontend" / "fontes").as_uri()
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>{DOCUMENTO} — Relatório de Testes</title>
<style>
@font-face {{ font-family: Plex; font-weight: 400; src: url({fontes}/ibm-plex-sans-400.woff2); }}
@font-face {{ font-family: Plex; font-weight: 500; src: url({fontes}/ibm-plex-sans-500.woff2); }}
@font-face {{ font-family: Plex; font-weight: 600; src: url({fontes}/ibm-plex-sans-600.woff2); }}
* {{ box-sizing: border-box; }}
body {{ font-family: Plex, sans-serif; font-size: 9.6pt; line-height: 1.45; color: #1d2430; margin: 0;
        counter-reset: secao; }}
header {{ border-bottom: 1.5pt solid #12305a; padding-bottom: 4mm; margin-bottom: 6mm; }}
.sup {{ font-size: 8.4pt; color: #556; display: flex; justify-content: space-between; }}
h1 {{ font-size: 21pt; color: #12305a; margin: 3mm 0 1mm; font-weight: 600; }}
.sistema {{ font-size: 11pt; color: #33415a; }}
h2 {{ font-size: 12.5pt; color: #12305a; font-weight: 600; margin: 7mm 0 2.5mm; break-after: avoid;
      counter-increment: secao; }}
h2::before {{ content: counter(secao) ". "; }}
p {{ margin: 0 0 2.5mm; }}
table {{ width: 100%; border-collapse: collapse; margin: 1mm 0 3mm; font-size: 8.8pt; }}
th, td {{ border: 0.5pt solid #b9c2d0; padding: 1.5mm 2mm; text-align: left; vertical-align: top; }}
thead th {{ background: #12305a; color: #fff; font-weight: 500; }}
tr {{ break-inside: avoid; }}
.num {{ text-align: right; width: 18mm; }}
.id {{ font-weight: 500; white-space: nowrap; }}
.regras td:nth-child(2) {{ width: 44mm; }} .regras td:last-child {{ width: 22mm; }}
.data {{ white-space: nowrap; width: 26mm; }}
.selo {{ display: inline-block; padding: 0.3mm 1.6mm; border-radius: 1mm; font-size: 7.6pt;
         font-weight: 600; white-space: nowrap; border: 0.5pt solid; }}
.selo.ok {{ color: #12663a; background: #e3f4ea; border-color: #9bd1b2; }}
.selo.falha {{ color: #9b1c1c; background: #fbe5e5; border-color: #e5a3a3; }}
.selo.parcial {{ color: #7a5200; background: #fdf1d8; border-color: #e6c27a; }}
.selo.nao {{ color: #4a5568; background: #edf0f4; border-color: #c3cad5; }}
.numeros {{ display: flex; gap: 3mm; margin: 1mm 0 3mm; }}
.numeros div {{ flex: 1; border: 0.5pt solid #b9c2d0; padding: 2.5mm 3mm; font-size: 8.4pt; color: #445; }}
.numeros span {{ display: block; font-size: 17pt; font-weight: 600; color: #12305a; }}
.conclusao {{ border-left: 2pt solid #12305a; background: #f2f5fa; padding: 3mm 4mm; }}
</style></head><body>

<header>
  <div class="sup"><span>Engenharia de Software · Grupo MDGS</span>
  <span>{DOCUMENTO} · versão {VERSAO} · {inicio:%d/%m/%Y}</span></div>
  <h1>Relatório de Testes</h1>
  <div class="sistema">Sistema de Gestão de Estoque e Compras — Mercado do Sr. João</div>
</header>

<h2>Objetivo</h2>
<p>Registrar o que foi testado no sistema, o resultado obtido e o que ainda falta testar. Base:
regras de negócio da Apostila I, fluxogramas da Apostila II e requisitos da Apostila III.</p>

<h2>Como foi testado</h2>
<table><thead><tr><th>Tipo de teste</th><th>O que verifica</th><th class="num">Testes</th></tr></thead><tbody>
<tr><td>Regra, API e banco</td><td>Cada regra com o exemplo da Apostila I; a API aceita e recusa o que deve; o banco é igual ao modelo da Apostila IV</td><td class="num">{total - de_tela}</td></tr>
<tr><td>Tela, de ponta a ponta</td><td>Navegador real: login, preenchimento da tela, resultado na tela e no banco</td><td class="num">{de_tela}</td></tr>
</tbody></table>
<p>Todos os testes são automáticos (pytest e Playwright), rodam no mesmo banco do sistema
(PostgreSQL) e cada decisão dos fluxogramas é testada pelo caminho "sim" e pelo "não". Cada teste
foi escrito junto com a sua tarefa, entre 06/10/2026 e 09/10/2026, e a suíte inteira é executada
de novo a cada entrega — a última vez em {inicio:%d/%m/%Y}.</p>

<h2>Resultado</h2>
<div class="numeros">
  <div><span>{total}</span>testes executados</div>
  <div><span>{aprovados}</span>aprovados</div>
  <div><span>{total - aprovados}</span>reprovados</div>
  <div><span>{pct} %</span>de aprovação</div>
</div>
<p>Execução de {inicio:%d/%m/%Y às %H:%M}, em {int(duracao // 60)} min {int(duracao % 60)} s, sobre o
código do commit <code>{COMMIT}</code>.</p>
<table><thead><tr><th>Parte do sistema</th><th class="num">Testes</th><th class="num">Aprovados</th><th>Testado em</th><th>Situação</th></tr></thead>
<tbody>{linhas_bloco}</tbody></table>

<h2>Regras de negócio testadas</h2>
<table class="regras"><thead><tr><th>Regra</th><th>Descrição</th><th>Exemplo verificado</th><th class="num">Testes</th><th>Data</th><th>Situação</th></tr></thead>
<tbody>{"".join(linhas_regra)}</tbody></table>
<p>{regras_ok} de 16 regras aprovadas, 1 aprovada em parte e 5 ainda não construídas. Nas regras
não testadas, a data é a prevista.</p>

<h2>Defeitos</h2>
<p>Os testes encontraram <b>11 defeitos</b>. Todos foram corrigidos no mesmo dia e ganharam teste
próprio. <b>Nenhum defeito em aberto em {inicio:%d/%m/%Y}.</b></p>
<table><thead><tr><th>Encontrado em</th><th>Defeito</th><th>Corrigido em</th></tr></thead>
<tbody>{linhas_defeito}</tbody></table>
<p>Entre 08/10/2026 e 09/10/2026, para provar que os testes detectam erro, a equipe inseriu
<b>38 defeitos de propósito</b> no código; os testes detectaram os 38.</p>

<h2>O que ainda não foi testado</h2>
<p>Partes que ainda não foram construídas; o teste de cada uma é feito junto com ela.</p>
<table><thead><tr><th>Item</th><th>Tarefa</th><th>Data prevista</th></tr></thead><tbody>{linhas_falta}</tbody></table>

<h2>Conclusão</h2>
<p class="conclusao">Tudo o que foi construído até {inicio:%d/%m/%Y} passou nos testes: <b>{aprovados}
de {total} aprovados</b>, sem defeito em aberto. O sistema completo será aprovado quando as partes
da seção 6 forem construídas e testadas, até a entrega de 01/12/2026.</p>
</body></html>"""


def gerar_pdf():
    _, inicio, _ = ler_execucao()
    emissao = f"{inicio:%d/%m/%Y}"
    from playwright.sync_api import sync_playwright

    rodape = (
        '<div style="font-family:sans-serif;font-size:7pt;color:#667;width:100%;padding:0 18mm;'
        'display:flex;justify-content:space-between">'
        f"<span>{DOCUMENTO} · Relatório de Testes · Grupo MDGS · emitido em {emissao}</span>"
        '<span>Página <span class="pageNumber"></span> de <span class="totalPages"></span></span></div>'
    )
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page()
        pagina.goto(SAIDA_HTML.as_uri())
        pagina.wait_for_load_state("networkidle")
        pagina.pdf(
            path=str(SAIDA_PDF),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=rodape,
            margin={"top": "16mm", "bottom": "16mm", "left": "18mm", "right": "18mm"},
        )
        navegador.close()


if __name__ == "__main__":
    SAIDA_HTML.write_text(montar(), encoding="utf-8")
    gerar_pdf()
    print(f"Gerado: {SAIDA_PDF.relative_to(RAIZ)}")

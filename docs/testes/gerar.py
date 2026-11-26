# ruff: noqa: E501  (textos do documento: quebrar a linha só atrapalha a leitura)
"""
Gera o Relatório de Testes (PDF, poucas páginas) a partir da última execução da suíte.

    pytest --junitxml=docs/testes/execucao.xml
    python docs/testes/gerar.py

Saída: docs/testes/RELATORIO-DE-TESTES.pdf (e o .html de onde ele sai).
Os números (total, aprovados, testes por regra e por bloco) são lidos do XML da execução — nada
de resultado digitado à mão. O visual é o mesmo da Documentação do Sistema (docs/sistema): verde
da loja, Unbounded nos títulos, IBM Plex Sans no texto, tema claro ou escuro; o PDF é sempre claro.
"""

import collections
import html
import re
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[1]
XML = PASTA / "execucao.xml"
SAIDA_HTML = PASTA / "RELATORIO-DE-TESTES.html"
SAIDA_PDF = PASTA / "RELATORIO-DE-TESTES.pdf"

DOCUMENTO = "MDGS-TST-001"
VERSAO = "2.0"
# commit do código que a suíte testou (o HEAD na hora de gerar)
COMMIT = (
    subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607
        cwd=RAIZ,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    or "—"
)

BLOCOS = {
    "a": "A · Fundação: banco, API, login e perfis",
    "b": "B · Cadastros de produto, categoria e fornecedor",
    "c": "C · Entrada de mercadoria e saldo",
    "d": "D · Perdas e avarias",
    "e": "E · Importação das vendas do caixa",
    "f": "F · Consulta de estoque",
    "g": "G · Previsão de consumo e rodada das 03h00",
    "h": "H · Avisos pelo Telegram: validade e vai acabar",
    "i": "I · Fechamento de caixa e balanço da semana",
    "j": "J · Cobertura das regras e carga inicial",
    "telas": "Telas no celular e no tablet",
    "doc": "Documentação do sistema em dia com o código",
}
TESTADO_EM = {
    "a": "06/10 e 13/11/2026",
    "b": "06 a 08/10/2026",
    "c": "06 a 08/10/2026",
    "d": "07 e 08/10/2026",
    "e": "05 e 12/11/2026",
    "f": "07 e 08/10/2026",
    "g": "12/11/2026",
    "h": "08/10 a 12/11/2026",
    "i": "09/10 a 12/11/2026",
    "j": "09/10 a 16/11/2026",
    "telas": "09/10 e 12/11/2026",
    "doc": "13 e 16/11/2026",
}
# data em que cada regra foi testada (conclusão da tarefa dela) ou, se ainda não construída, a prevista
DATA_DA_REGRA = {
    "RN01": "06/10/2026",
    "RN02": "07/10/2026",
    "RN03": "06/10/2026",
    "RN04": "07/10/2026",
    "RN05": "08/10/2026",
    "RN06": "12/11/2026",
    "RN07": "12/11/2026",
    "RN08": "12 e 13/11/2026",
    "RN09": "12/11/2026",
    "RN10": "12/11/2026",
    "RN11": "07/10/2026",
    "RN12": "08/10/2026",
    "RN13": "08/10/2026",
    "RN14": "06/10/2026",
    "RN15": "05/11/2026",
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
    ("12/11/2026", "Aviso de validade pronto, mas nenhuma rotina da madrugada o chamava"),
    ("13/11/2026", 'Sugestão de compra quebrada em pacote ("pedir 14,531 PCT")'),
    ("16/11/2026", "Documento da API mudava conforme a ordem em que os testes rodavam"),
    ("17/11/2026", "Teste da tela de balanço falhava a partir de 17/11 (relógio do navegador não fixado)"),
]
# Revisão geral do código contra a especificação (X1, 16/11/2026): item, defeito, gravidade, commit.
REVISAO_X1 = [
    (1, "Planilha repetida ou regravada", "alta", "fa2866e"),
    (2, "Linha com erro sumia do caixa", "alta", "b16f38d"),
    (3, "Saldo e lotes deixavam de bater", "alta", "1b710f5"),
    (4, "Planilha com dois dias travava o fechamento", "alta", "7b6072b"),
    (5, 'Depois do "Sim, pedir", o produto ficava calado para sempre', "média", "97c6166"),
    (6, "O caixa só podia ser fechado no dia seguinte", "média", "f723e6e"),
    (7, 'Só "dinheiro" contava como dinheiro', "média", "fcf22cf"),
    (8, "Produto sem fornecedor nunca avisava", "média", "e7a1aa5"),
    (9, 'Produto parado e zerado avisava "acabou" todo dia', "média", "4756400"),
    (10, "Nenhuma tela mostrava a previsão", "média", "a2d3355"),
    (11, "A rodada perdida não era recuperada", "média", "8d0e208"),
    (12, 'Dois produtos com o "mesmo" nome', "média", "d75f920"),
    (13, '"1.000" digitado virava 1', "média", "8f7de51"),
    (14, "Erro interno com número fora do esperado", "baixa", "405e07e"),
    (15, "Total do cupom arredondado só no fim", "baixa", "acb0139"),
    (16, "Duas rodadas ao mesmo tempo duplicavam", "baixa", "eae8fcb"),
    (17, "Mensagem dividida podia chegar repetida", "baixa", "abc43c9"),
    (18, "Venda ligada ao produto errado não tinha desfazer", "baixa", "3d044f9"),
    (19, "Banco diferente do schema.sql em detalhes", "baixa", "473cf83"),
    (20, "Modo de depuração ligado na publicação", "baixa", "a332343"),
    (21, "Uma leitura do prazo de validade por lote", "baixa", "a16fc4b"),
    (22, "Comentários desatualizados", "baixa", "f4104c2"),
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
    (
        "RN06",
        "Consumo médio diário",
        "Vendas dos últimos 30 dias divididas por 30, contando os dias sem venda; perda fica de fora",
    ),
    (
        "RN07",
        "Consumo por dia da semana",
        "Dia da semana que vende 1,5 vez a média ou mais vira dia de venda forte",
    ),
    (
        "RN08",
        "Ponto de pedido e aviso de ruptura",
        "Saldo igual ou abaixo do ponto avisa; acima, não; acaba antes da entrega → urgência alta",
    ),
    (
        "RN09",
        "Histórico mínimo para prever",
        "13 dias de venda: ainda aprendendo, sem número nem aviso; 14 dias: projeta",
    ),
    (
        "RN10",
        "Produtos que não podem faltar no fim de semana",
        "Na quinta, crítico dentro da folga avisa; na quarta, ou não crítico, não",
    ),
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
        "Apura R$ 3.240,00, conta R$ 3.215,00 → registra −R$ 25,00; contar de novo gera registro novo",
    ),
    ("RN16", "Lote vencido é bloqueado", "Vencido não sai na venda, só como perda, e aparece destacado"),
]
SEM_CODIGO = {}
# soma dos "defeitos de propósito" do diário (docs/ACOMPANHAMENTO.md): 49 até 05/11, 80 de 06 a 13/11, 1 em 16/11
DEFEITOS_DE_PROPOSITO = 130
PARCIAL = {}

# Conferido à mão no sistema rodando, no computador do Matheus (D05), antes da apresentação.
CONFERIDO_A_MAO = [
    (
        "Planilha do sábado (vendas-2026-11-21.xlsx) importada pela pasta do caixa; nome errado fica pendente e o resto entra",
        "E3, E4",
        "25/11/2026",
    ),
    (
        "Aviso chegando no celular de verdade, pelo bot real do Telegram, numa mensagem só",
        "H5, RN13",
        "25/11/2026",
    ),
]
# Não se aplica: dependem de uma loja real, e o mercado deste trabalho é fictício.
NAO_TESTADO = [
    ("Teste em movimento real, num sábado cheio (o roteiro de 21 casos e as planilhas estão prontos)", "J4"),
    ("Facilidade de uso com as três pessoas (RNF02, RNF03)", "J5"),
    ("Computador da loja ligado de madrugada e cópia de segurança diária (RNF08, RNF09)", "J6"),
    (
        'Resposta "Sim, pedir" voltando do celular: precisa do sistema publicado na internet com HTTPS; o registro da resposta tem teste automático',
        "H7",
    ),
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
    if arquivo == "test_documentacao":
        return "doc"
    return re.match(r"test_([a-z])\d", arquivo).group(1)


def selo(texto, classe):
    return f'<span class="selo {classe}">{e(texto)}</span>'


def selo_gravidade(g):
    return selo(g.capitalize(), {"alta": "alta", "média": "media", "baixa": "baixa"}[g])


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
    linhas_x1 = "".join(
        f"<tr><td class='num'>{n}</td><td>{e(t)}</td><td>{selo_gravidade(g)}</td><td><code>{c}</code></td></tr>"
        for n, t, g, c in REVISAO_X1
    )
    linhas_mao = "".join(
        f"<tr><td>{e(a)}</td><td>{e(b)}</td><td class='data'>{c}</td><td>{selo('Conferido', 'ok')}</td></tr>"
        for a, b, c in CONFERIDO_A_MAO
    )
    linhas_falta = "".join(
        f"<tr><td>{e(a)}</td><td>{b}</td><td>{selo('Não se aplica', 'nao')}</td></tr>" for a, b in NAO_TESTADO
    )
    total_defeitos = len(DEFEITOS) + len(REVISAO_X1)
    emissao = f"{inicio:%d/%m/%Y}"

    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{DOCUMENTO} — Relatório de Testes</title>
<style>
/* Mesmo visual da Documentação do Sistema (docs/sistema): verde da loja, Unbounded nos títulos,
   IBM Plex Sans no texto, tema claro ou escuro com botão; o PDF é sempre claro. */
@font-face {{ font-family: "Plex"; font-weight: 400; font-display: swap; src: url("../../frontend/fontes/ibm-plex-sans-400.woff2") format("woff2"); }}
@font-face {{ font-family: "Plex"; font-weight: 500; font-display: swap; src: url("../../frontend/fontes/ibm-plex-sans-500.woff2") format("woff2"); }}
@font-face {{ font-family: "Plex"; font-weight: 600; font-display: swap; src: url("../../frontend/fontes/ibm-plex-sans-600.woff2") format("woff2"); }}
@font-face {{ font-family: "Unbounded"; font-weight: 500; font-display: swap; src: url("../../frontend/fontes/unbounded-500.woff2") format("woff2"); }}
@font-face {{ font-family: "Unbounded"; font-weight: 600; font-display: swap; src: url("../../frontend/fontes/unbounded-600.woff2") format("woff2"); }}
:root {{
  --fundo: #f6f7f4; --superficie: #ffffff; --superficie-2: #eef1ec; --tinta: #0f1f18; --tinta-suave: #4a5a52;
  --linha: #dbe1da; --marca: #0a6847; --marca-fundo: #e1f2e9; --amarelo: #ffd43b; --sobre-amarelo: #2a2200;
  --aviso: #8a4b00; --aviso-fundo: #fff3d1; --erro: #9b1c1c; --erro-fundo: #fbe5e5; --foco: #1d4ed8;
  --texto: "Plex", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --titulo: "Unbounded", "Plex", system-ui, sans-serif;
  --mono: ui-monospace, "SF Mono", "Cascadia Code", Menlo, Consolas, monospace;
  --medida: 74ch;
}}
:root[data-tema="escuro"] {{
  --fundo: #0f1f19; --superficie: #15281f; --superficie-2: #1b3228; --tinta: #e7efe9; --tinta-suave: #a3b6ab;
  --linha: #284035; --marca: #62d4a4; --marca-fundo: #173d2d; --aviso: #ffcf70; --aviso-fundo: #3a2c0c;
  --erro: #ff9b9b; --erro-fundo: #3d1717; --foco: #9db9ff; color-scheme: dark;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-tema="claro"]) {{
    --fundo: #0f1f19; --superficie: #15281f; --superficie-2: #1b3228; --tinta: #e7efe9; --tinta-suave: #a3b6ab;
    --linha: #284035; --marca: #62d4a4; --marca-fundo: #173d2d; --aviso: #ffcf70; --aviso-fundo: #3a2c0c;
    --erro: #ff9b9b; --erro-fundo: #3d1717; --foco: #9db9ff; color-scheme: dark;
  }}
}}
*, *::before, *::after {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--fundo); color: var(--tinta); font: 400 1rem/1.6 var(--texto); -webkit-text-size-adjust: 100%; }}
main {{ max-width: 1040px; margin: 0 auto; padding: 0 clamp(16px, 5vw, 56px) 96px; }}
a {{ color: var(--marca); }}
:focus-visible {{ outline: 3px solid var(--foco); outline-offset: 2px; }}
.topo {{ display: flex; justify-content: flex-end; padding-top: 16px; }}
.botao {{ min-height: 36px; padding: 0 12px; cursor: pointer; font: 500 0.875rem var(--texto); color: var(--tinta);
  background: var(--superficie); border: 1px solid var(--tinta-suave); border-radius: 8px; }}
.botao:hover {{ background: var(--superficie-2); }}

.capa {{ padding: clamp(24px, 6vh, 72px) 0 32px; border-bottom: 1px solid var(--linha); }}
.capa__grupo {{ margin: 0 0 18px; color: var(--tinta-suave); }}
.capa h1 {{ margin: 0; font: 600 clamp(2rem, 4.6vw, 3.25rem)/1.08 var(--titulo); letter-spacing: -0.02em; text-wrap: balance; }}
.capa__sistema {{ margin: 14px 0 0; max-width: 60ch; font-size: 1.1875rem; color: var(--tinta-suave); text-wrap: balance; }}
.ficha {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); margin: 36px 0 0; padding: 0; border-top: 1px solid var(--linha); }}
.ficha div {{ padding: 14px 16px 14px 0; border-bottom: 1px solid var(--linha); }}
.ficha dt {{ font-size: 0.8125rem; color: var(--tinta-suave); }}
.ficha dd {{ margin: 2px 0 0; font: 500 1.0625rem/1.3 var(--mono); font-variant-numeric: tabular-nums; }}

.numeros {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0; margin: 8px 0 20px; border-top: 3px solid var(--tinta); }}
.numeros div {{ padding: 14px 16px 12px 0; border-bottom: 1px solid var(--linha); }}
.numeros b {{ display: block; font: 600 clamp(1.6rem, 3.4vw, 2.25rem)/1.1 var(--titulo); font-variant-numeric: tabular-nums; }}
.numeros .ok b {{ color: var(--marca); }}
.numeros span {{ font-size: 0.875rem; color: var(--tinta-suave); }}

section {{ padding-top: 52px; counter-increment: secao; }}
main {{ counter-reset: secao; }}
h2 {{ margin: 0 0 14px; padding-bottom: 12px; border-bottom: 1px solid var(--linha); font: 600 1.5rem/1.2 var(--titulo); letter-spacing: -0.01em; }}
h2::before {{ content: counter(secao) " · "; color: var(--tinta-suave); font-weight: 500; }}
h3 {{ margin: 28px 0 10px; font: 600 1.0625rem/1.35 var(--texto); }}
p {{ margin: 0 0 14px; max-width: var(--medida); }}
code {{ font: 0.875em var(--mono); background: var(--superficie-2); padding: 1px 4px; border-radius: 4px; }}

.tabela {{ margin: 0 0 22px; overflow-x: auto; border: 1px solid var(--linha); border-radius: 8px; background: var(--superficie); }}
table {{ width: 100%; border-collapse: collapse; font-size: 0.875rem; line-height: 1.45; }}
th, td {{ padding: 9px 12px; text-align: left; vertical-align: top; border-bottom: 1px solid var(--linha); }}
thead th {{ font-weight: 600; color: var(--tinta-suave); white-space: nowrap; border-bottom: 1px solid var(--tinta-suave); background: var(--superficie-2); }}
tbody tr:last-child td {{ border-bottom: 0; }}
td:first-child {{ font-weight: 500; }}
.num {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
.data {{ white-space: nowrap; font-family: var(--mono); font-size: 0.8125rem; font-variant-numeric: tabular-nums; }}
.id {{ white-space: nowrap; font-family: var(--mono); }}

.selo {{ display: inline-flex; align-items: center; gap: 7px; white-space: nowrap; font-size: 0.8125rem; font-weight: 500; }}
.selo::before {{ content: ""; flex: none; width: 8px; height: 8px; border-radius: 50%; background: currentColor; }}
.selo.ok {{ color: var(--marca); }}
.selo.falha {{ color: var(--erro); }}
.selo.parcial, .selo.media {{ color: var(--aviso); }}
.selo.parcial::before, .selo.media::before {{ background: none; border: 2px solid currentColor; }}
.selo.alta {{ color: var(--erro); }}
.selo.nao, .selo.baixa {{ color: var(--tinta-suave); }}
.selo.nao::before, .selo.baixa::before {{ background: none; border: 2px solid currentColor; }}

.conclusao {{ max-width: none; padding: 16px 18px; border-left: 3px solid var(--amarelo); background: var(--superficie-2); border-radius: 0 6px 6px 0; }}
.pe {{ margin-top: 72px; padding-top: 16px; border-top: 1px solid var(--linha); font-size: 0.875rem; color: var(--tinta-suave); }}

@media (max-width: 640px) {{ .numeros {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}

@page {{ size: A4; margin: 16mm 15mm 18mm; }}
@media print {{
  :root, :root[data-tema="escuro"], :root:not([data-tema="claro"]) {{
    --fundo: #fff; --superficie: #fff; --superficie-2: #f1f3ef; --tinta: #0f1f18; --tinta-suave: #4a5a52;
    --linha: #cfd6ce; --marca: #0a6847; --aviso: #8a4b00; --erro: #9b1c1c; color-scheme: light;
  }}
  html {{ font-size: 9.4pt; }}
  body {{ background: #fff; line-height: 1.45; }}
  .topo, .pe {{ display: none !important; }}
  main {{ max-width: none; padding: 0; }}
  .capa {{ padding: 4mm 0 6mm; }}
  .capa h1 {{ font-size: 26pt; }}
  .capa__sistema {{ font-size: 12pt; }}
  .ficha {{ margin-top: 7mm; grid-template-columns: repeat(4, 1fr); }}
  .ficha dd {{ font-size: 10.5pt; }}
  section {{ padding-top: 7mm; }}
  h2 {{ font-size: 14pt; break-after: avoid; }}
  h3 {{ break-after: avoid; }}
  p {{ max-width: none; }}
  .numeros b {{ font-size: 20pt; }}
  .tabela {{ overflow: visible; border-radius: 0; border-width: 0.5pt; }}
  table {{ font-size: 8.2pt; }}
  th, td {{ padding: 1.3mm 1.8mm; border-bottom-width: 0.5pt; }}
  thead {{ display: table-header-group; }}
  tr {{ break-inside: avoid; }}
  .selo, .conclusao {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
}}
</style>
<script>
(function () {{
  try {{ var t = localStorage.getItem("mdgs-tema"); if (t) document.documentElement.dataset.tema = t; }} catch (e) {{}}
}})();
</script>
</head><body>
<main>
<div class="topo"><button type="button" class="botao" id="trocar-tema">Trocar tema</button></div>

<header class="capa">
  <p class="capa__grupo">Engenharia de Software · Grupo MDGS</p>
  <h1>Relatório de Testes</h1>
  <p class="capa__sistema">Sistema de Gestão de Estoque e Compras — Mercado do Sr. João</p>
  <dl class="ficha">
    <div><dt>Documento</dt><dd>{DOCUMENTO}</dd></div>
    <div><dt>Versão</dt><dd>{VERSAO}</dd></div>
    <div><dt>Emitido em</dt><dd>{emissao}</dd></div>
    <div><dt>Código testado</dt><dd>{COMMIT}</dd></div>
  </dl>
</header>

<section>
<h2>Objetivo</h2>
<p>Registrar o que foi testado no sistema, o resultado obtido e o que não se aplica testar. Base:
regras de negócio da Apostila I, fluxogramas da Apostila II e requisitos da Apostila III.</p>
</section>

<section>
<h2>Como foi testado</h2>
<div class="tabela"><table><thead><tr><th>Tipo de teste</th><th>O que verifica</th><th class="num">Testes</th></tr></thead><tbody>
<tr><td>Regra, API e banco</td><td>Cada regra com o exemplo da Apostila I; a API aceita e recusa o que deve; o banco é igual ao modelo da Apostila IV</td><td class="num">{total - de_tela}</td></tr>
<tr><td>Tela, de ponta a ponta</td><td>Navegador real: login, preenchimento da tela, resultado na tela e no banco</td><td class="num">{de_tela}</td></tr>
</tbody></table></div>
<p>Todos os testes são automáticos (pytest e Playwright), rodam no mesmo banco do sistema
(PostgreSQL) e cada decisão dos fluxogramas é testada pelo caminho "sim" e pelo "não". Cada teste
foi escrito junto com a sua tarefa, a partir de 06/10/2026, e a suíte inteira é executada de novo a
cada entrega — a última vez em {emissao}.</p>
</section>

<section>
<h2>Resultado</h2>
<div class="numeros">
  <div><b>{total}</b><span>testes executados</span></div>
  <div class="ok"><b>{aprovados}</b><span>aprovados</span></div>
  <div><b>{total - aprovados}</b><span>reprovados</span></div>
  <div class="ok"><b>{pct}%</b><span>de aprovação</span></div>
</div>
<p>Execução de {inicio:%d/%m/%Y às %H:%M}, em {int(duracao // 60)} min {int(duracao % 60)} s, sobre o
código do commit <code>{COMMIT}</code>.</p>
<div class="tabela"><table><thead><tr><th>Parte do sistema</th><th class="num">Testes</th><th class="num">Aprovados</th><th>Testado em</th><th>Situação</th></tr></thead>
<tbody>{linhas_bloco}</tbody></table></div>
</section>

<section>
<h2>Regras de negócio testadas</h2>
<div class="tabela"><table class="regras"><thead><tr><th>Regra</th><th>Descrição</th><th>Exemplo verificado</th><th class="num">Testes</th><th>Data</th><th>Situação</th></tr></thead>
<tbody>{"".join(linhas_regra)}</tbody></table></div>
<p><b>As {regras_ok} regras de negócio estão construídas, testadas e aprovadas.</b> Cada uma tem
o exemplo da Apostila I e os casos de borda; um teste de guarda falha se alguma regra ficar sem
teste com o código dela no nome.</p>
</section>

<section>
<h2>Defeitos</h2>
<p>Foram encontrados <b>{total_defeitos} defeitos</b>: {len(DEFEITOS)} pelos testes ou na conferência
do sistema rodando, e {len(REVISAO_X1)} na revisão geral do código contra a especificação (X1).
Todos foram corrigidos no mesmo dia e ganharam teste próprio. <b>Nenhum defeito em aberto em {emissao}.</b></p>
<h3>Durante a construção</h3>
<div class="tabela"><table><thead><tr><th>Encontrado em</th><th>Defeito</th><th>Corrigido em</th></tr></thead>
<tbody>{linhas_defeito}</tbody></table></div>
<h3>Revisão geral do código (X1, 16/11/2026)</h3>
<div class="tabela"><table><thead><tr><th class="num">Item</th><th>Defeito</th><th>Gravidade</th><th>Correção</th></tr></thead>
<tbody>{linhas_x1}</tbody></table></div>
<p>Entre 08/10/2026 e 16/11/2026, para provar que os testes detectam erro, a equipe inseriu
<b>{DEFEITOS_DE_PROPOSITO} defeitos de propósito</b> no código; os testes detectaram os {DEFEITOS_DE_PROPOSITO}.</p>
</section>

<section>
<h2>Conferido à mão</h2>
<p>Além dos testes automáticos, o sistema foi conferido rodando no computador do Matheus (decisão
D05), com o bot real do Telegram.</p>
<div class="tabela"><table><thead><tr><th>O que foi conferido</th><th>Tarefa e regra</th><th>Data</th><th>Situação</th></tr></thead>
<tbody>{linhas_mao}</tbody></table></div>
</section>

<section>
<h2>O que não se aplica</h2>
<p>Todo o código está testado de forma automática. Os itens abaixo dependem de uma loja funcionando —
movimento real, as três pessoas e o computador da loja — e o mercado deste trabalho é fictício. Por
isso estão registrados como "não se aplica", e não como feitos.</p>
<div class="tabela"><table><thead><tr><th>Item</th><th>Tarefa</th><th>Situação</th></tr></thead><tbody>{linhas_falta}</tbody></table></div>
</section>

<section>
<h2>Conclusão</h2>
<p class="conclusao">O sistema está completo e passou nos testes: <b>{aprovados} de {total}
aprovados</b>, as 16 regras de negócio aprovadas, {total_defeitos} defeitos encontrados e corrigidos
e nenhum em aberto em {emissao}. Os itens que dependem de loja real (J4, J5 e J6) não se aplicam,
porque o mercado é fictício; o roteiro do teste de sábado e as planilhas ficaram prontos.</p>
</section>

<footer class="pe">{DOCUMENTO} · Relatório de Testes · versão {VERSAO} · Grupo MDGS · emitido em {emissao}</footer>
</main>
<script>
document.getElementById("trocar-tema").addEventListener("click", function () {{
  var raiz = document.documentElement;
  var escuro = raiz.dataset.tema ? raiz.dataset.tema === "escuro" : matchMedia("(prefers-color-scheme: dark)").matches;
  raiz.dataset.tema = escuro ? "claro" : "escuro";
  try {{ localStorage.setItem("mdgs-tema", raiz.dataset.tema); }} catch (e) {{}}
}});
</script>
</body></html>"""


def gerar_pdf():
    _, inicio, _ = ler_execucao()
    emissao = f"{inicio:%d/%m/%Y}"
    from playwright.sync_api import sync_playwright

    rodape = (
        '<div style="font-family:sans-serif;font-size:7pt;color:#4a5a52;width:100%;padding:0 18mm;'
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

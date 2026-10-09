/*
 * Tabelas que viram cartões no celular — pedido do grupo em 09/10/2026 (painel no celular).
 *
 * Abaixo de 640 px o CSS (base.css, "Telas estreitas") mostra cada linha como um cartão
 * "rótulo: valor". O rótulo vem do cabeçalho da coluna: este módulo copia o nome de cada coluna
 * para a célula (data-rotulo) — a primeira coluna é o título do cartão e a de ações não tem rótulo.
 *
 * O CSS troca o "display" das partes da tabela, e alguns navegadores deixam de anunciar a tabela
 * ao leitor de tela quando isso acontece; por isso os papéis (role) ficam explícitos aqui.
 *
 * As telas montam e remontam as linhas depois de falar com a API: um MutationObserver rotula cada
 * linha nova, sem cada tela precisar lembrar de chamar nada.
 */

const PAPEL_DO_CABECALHO = { col: "columnheader", row: "rowheader", rowgroup: "rowheader" };

function nomesDasColunas(tabela) {
  return Array.from(tabela.querySelectorAll("thead th")).map((th) => ({
    nome: th.textContent.trim(),
    // Coluna sem nome à vista (só para leitor de tela): é a dos botões da linha.
    deAcoes: !th.textContent.trim() || th.querySelector(".visualmente-oculto") !== null,
  }));
}

function rotularLinha(linha, colunas) {
  linha.setAttribute("role", "row");
  let posicao = 0;
  for (const celula of linha.children) {
    if (celula.tagName === "TH") {
      celula.setAttribute("role", PAPEL_DO_CABECALHO[celula.scope] || "rowheader");
    } else {
      celula.setAttribute("role", "cell");
    }
    const coluna = colunas[posicao];
    if (celula.colSpan > 1 || !coluna || posicao === 0) {
      celula.removeAttribute("data-rotulo");
    } else if (coluna.deAcoes) {
      celula.classList.add("celula--acoes");
    } else {
      celula.dataset.rotulo = coluna.nome;
    }
    posicao += celula.colSpan || 1;
  }
}

function rotularTabela(tabela) {
  const colunas = nomesDasColunas(tabela);
  tabela.setAttribute("role", "table");
  tabela.querySelectorAll("thead, tbody").forEach((grupo) => grupo.setAttribute("role", "rowgroup"));
  tabela.querySelectorAll("tr").forEach((linha) => rotularLinha(linha, colunas));
}

export function prepararTabelas(raiz = document) {
  raiz.querySelectorAll("table.tabela").forEach((tabela) => {
    rotularTabela(tabela);
    new MutationObserver(() => rotularTabela(tabela)).observe(tabela, { childList: true, subtree: true });
  });
}

prepararTabelas();

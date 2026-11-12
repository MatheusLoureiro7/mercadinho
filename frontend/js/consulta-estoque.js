/*
 * Tela de Consulta de estoque — tarefa F3 (RF07, RN16). Os três perfis (RN14): o dono, a esposa e o
 * sobrinho.
 *
 * Saldo por produto e por categoria, com destaque para o que está abaixo do mínimo, perto de vencer
 * e com lote vencido. Tudo vem calculado pela API da F2: o saldo é o derivado das movimentações
 * (RN01), e "vencido"/"perto de vencer" usam o parâmetro da RN05. A tela só lê — não grava nada —
 * e só escreve o que a API mandou, em palavra e cor.
 *
 * Um pedido só traz a lista inteira (a F2 faz no máximo 4 idas ao banco, tenha a loja 50 ou 2.000
 * produtos); procurar e filtrar acontecem aqui, sobre o que a API já calculou, para o computador
 * antigo da loja não esperar a rede a cada letra (RNF06).
 */

import { api } from "./api.js";
import { linhaDeFalha } from "./falha.js";
import { dataBrasileira, horaNaLoja, quantidade, semAcento } from "./formatos.js";
import { celula, linhaVazia } from "./formulario.js";
import { entrarNaTela } from "./sessao.js";
import { etiquetaDaSituacao } from "./situacao.js";

const COLUNAS = 5;

// Os três quadros do resumo: o que cada um conta e filtra (campos calculados pela API).
const QUADROS = {
  vencidos: { botao: "filtro-vencidos", contador: "contador-vencidos", vale: (p) => p.lotes_vencidos > 0 },
  vencendo: { botao: "filtro-vencendo", contador: "contador-vencendo", vale: (p) => p.lotes_vencendo > 0 },
  abaixo: { botao: "filtro-abaixo", contador: "contador-abaixo", vale: (p) => p.abaixo_do_minimo },
};

const estado = {
  produtos: [],
  ligados: new Set(), // quadros do resumo apertados
};

const $ = (id) => document.getElementById(id);

// ------------------------------------------------------------------------------------------ Início

document.addEventListener("DOMContentLoaded", iniciar);

async function iniciar() {
  if (!(await entrarNaTela("consulta_estoque"))) return;

  Object.keys(QUADROS).forEach((chave) => {
    $(QUADROS[chave].botao).addEventListener("click", () => alternarQuadro(chave));
  });
  let espera;
  $("campo-procurar").addEventListener("input", () => {
    clearTimeout(espera);
    espera = setTimeout(mostrarLista, 150);
  });
  $("filtro-categoria").addEventListener("change", mostrarLista);
  $("botao-atualizar").addEventListener("click", carregar);

  await carregar();
}

async function carregar() {
  const botao = $("botao-atualizar");
  botao.disabled = true;
  botao.setAttribute("aria-busy", "true");
  $("lista-estoque").setAttribute("aria-busy", "true");
  const resposta = await api.ler("estoque/");
  botao.disabled = false;
  botao.removeAttribute("aria-busy");
  $("lista-estoque").removeAttribute("aria-busy");

  if (!resposta.ok) {
    trocarCorpo([linhaDeFalha(resposta.erro, COLUNAS, carregar)]);
    $("anuncio-lista").textContent = "Não foi possível carregar o estoque.";
    return;
  }
  estado.produtos = resposta.dados;
  $("hora-atualizacao").textContent = "Atualizado às " + horaNaLoja(new Date()) + ".";
  preencherCategorias();
  contarQuadros();
  mostrarLista();
}

function preencherCategorias() {
  const select = $("filtro-categoria");
  const escolhida = select.value;
  const categorias = new Map();
  estado.produtos.forEach((p) => categorias.set(String(p.categoria_id), p.categoria_nome));
  select.textContent = "";
  select.append(new Option("Todas as categorias", ""));
  [...categorias.entries()]
    .sort((a, b) => a[1].localeCompare(b[1], "pt-BR"))
    .forEach(([id, nome]) => select.append(new Option(nome, id)));
  if (categorias.has(escolhida)) select.value = escolhida;
}

// ------------------------------------------------------------------------------------------ Resumo

function contarQuadros() {
  Object.values(QUADROS).forEach((quadro) => {
    const total = estado.produtos.filter(quadro.vale).length;
    $(quadro.contador).textContent = String(total);
    // Zero é zero: o quadro fica cinza, sem cor de alerta (painel.css).
    $(quadro.botao).toggleAttribute("data-zero", total === 0);
  });
}

function alternarQuadro(chave) {
  if (estado.ligados.has(chave)) estado.ligados.delete(chave);
  else estado.ligados.add(chave);
  $(QUADROS[chave].botao).setAttribute("aria-pressed", String(estado.ligados.has(chave)));
  mostrarLista();
}

// ------------------------------------------------------------------------------------------ Lista

function produtosVisiveis() {
  const busca = semAcento($("campo-procurar").value.trim());
  const categoria = $("filtro-categoria").value;
  return estado.produtos.filter(
    (p) =>
      (!busca || semAcento(p.nome).indexOf(busca) >= 0) &&
      (!categoria || String(p.categoria_id) === categoria) &&
      [...estado.ligados].every((chave) => QUADROS[chave].vale(p))
  );
}

function mostrarLista() {
  const visiveis = produtosVisiveis();
  if (!visiveis.length) {
    const filtrando = estado.produtos.length > 0;
    trocarCorpo([
      filtrando
        ? linhaVazia(COLUNAS, "Nenhum produto encontrado.", "Confira o nome digitado ou tire os filtros.")
        : linhaVazia(COLUNAS, "Nenhum produto cadastrado ainda.", "Os produtos aparecem aqui depois do cadastro."),
    ]);
  } else {
    // A API já devolve por categoria e nome; aqui só se separa um grupo por categoria (RF07).
    const grupos = new Map();
    visiveis.forEach((p) => {
      if (!grupos.has(p.categoria_nome)) grupos.set(p.categoria_nome, []);
      grupos.get(p.categoria_nome).push(p);
    });
    const corpos = [...grupos.entries()]
      .sort((a, b) => a[0].localeCompare(b[0], "pt-BR"))
      .map(([nome, produtos]) => grupoDaCategoria(nome, produtos));
    $("lista-estoque").querySelectorAll("tbody").forEach((t) => t.remove());
    $("lista-estoque").append(...corpos);
  }
  const total = visiveis.length;
  $("anuncio-lista").textContent = total === 1 ? "1 produto na lista." : total + " produtos na lista.";
}

function trocarCorpo(linhas) {
  const tabela = $("lista-estoque");
  tabela.querySelectorAll("tbody").forEach((t) => t.remove());
  const corpo = document.createElement("tbody");
  corpo.append(...linhas);
  tabela.append(corpo);
}

function grupoDaCategoria(nome, produtos) {
  const corpo = document.createElement("tbody");
  const cabeca = document.createElement("tr");
  const th = document.createElement("th");
  th.scope = "rowgroup";
  th.colSpan = COLUNAS;
  th.className = "tabela__grupo";
  th.textContent = nome;
  cabeca.append(th);
  corpo.append(cabeca);
  produtos.forEach((produto) => corpo.append(linhaDoProduto(produto)));
  return corpo;
}

function linhaDoProduto(produto) {
  const linha = document.createElement("tr");
  if (produto.lotes_vencidos > 0) linha.className = "linha--vencido";
  else if (produto.abaixo_do_minimo || produto.lotes_vencendo > 0) linha.className = "linha--atencao";

  const nome = document.createElement("th");
  nome.scope = "row";
  const forte = document.createElement("strong");
  forte.textContent = produto.nome;
  nome.append(forte);
  if (produto.critico_fim_semana) {
    nome.append(document.createElement("br"), etiqueta("Não pode faltar no fim de semana", "neutra"));
  }

  const saldo = celula(quantidade(produto.saldo, produto.unidade_medida), "numero");
  const desenho = regua(produto);
  if (desenho) saldo.append(desenho);
  if (produto.abaixo_do_minimo) saldo.append(document.createElement("br"), etiqueta("Abaixo do mínimo", "aviso"));

  const validade = celula();
  if (produto.lotes_vencidos > 0) {
    const n = produto.lotes_vencidos;
    validade.append(etiqueta(n === 1 ? "1 lote vencido" : n + " lotes vencidos", "erro"), " ");
  }
  if (produto.lotes_vencendo > 0) validade.append(etiqueta("Perto de vencer", "aviso"), " ");
  if (produto.proxima_validade) {
    const proxima = document.createElement("span");
    proxima.className = "validade-proxima";
    proxima.textContent = "Próxima: " + dataBrasileira(produto.proxima_validade);
    validade.append(proxima);
  } else if (!produto.lotes_vencidos) {
    validade.append(texto(produto.perecivel ? "—" : "Sem validade", "texto-suave"));
  }

  const acoes = celula();
  if (Number(produto.saldo) > 0) acoes.append(botaoVerLotes(produto, linha));

  linha.append(
    nome,
    saldo,
    celula(produto.estoque_minimo === null ? "—" : quantidade(produto.estoque_minimo, produto.unidade_medida), "numero"),
    validade,
    acoes
  );
  return linha;
}

/**
 * A régua do estoque: o saldo contra o mínimo, num trilho que vai de zero ao dobro do mínimo (o
 * traço do meio é o mínimo). Só desenho — o número e a etiqueta "Abaixo do mínimo" dizem o mesmo em
 * palavras, por isso fica fora do leitor de tela. Quem diz se está abaixo é a API (abaixo_do_minimo);
 * a tela só desenha os dois números que recebeu. Produto sem mínimo não tem régua.
 */
function regua(produto) {
  const minimo = Number(produto.estoque_minimo);
  if (produto.estoque_minimo === null || !(minimo > 0)) return null;
  const parte = Math.max(0, Math.min(Number(produto.saldo) / (2 * minimo), 1));
  const trilho = document.createElement("span");
  trilho.className = "regua" + (produto.abaixo_do_minimo ? " regua--abaixo" : "");
  trilho.setAttribute("aria-hidden", "true");
  const cheio = document.createElement("span");
  cheio.className = "regua__cheio";
  cheio.style.width = (parte * 100).toFixed(1) + "%";
  const marca = document.createElement("span");
  marca.className = "regua__minimo";
  trilho.append(cheio, marca);
  return trilho;
}

// ------------------------------------------------------------------------------------------ Lotes de um produto

function botaoVerLotes(produto, linha) {
  const botao = document.createElement("button");
  botao.type = "button";
  botao.className = "botao botao--secundario botao--abre";
  // Padrão de abrir e fechar: o texto não muda; aria-expanded diz se está aberto (e a seta gira).
  botao.innerHTML = '<svg class="icone" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6" /></svg>Ver lotes';
  botao.setAttribute("aria-expanded", "false");
  botao.setAttribute("aria-label", "Ver lotes de " + produto.nome);
  const idDosLotes = "lotes-do-produto-" + produto.produto_id;
  botao.setAttribute("aria-controls", idDosLotes);
  botao.addEventListener("click", () => alternarLotes(produto, linha, botao, idDosLotes));
  return botao;
}

async function alternarLotes(produto, linha, botao, idDosLotes) {
  const aberta = document.getElementById(idDosLotes);
  if (aberta) {
    aberta.closest("tr").remove();
    botao.setAttribute("aria-expanded", "false");
    return;
  }
  const detalhe = document.createElement("tr");
  detalhe.className = "linha-lotes";
  const td = document.createElement("td");
  td.colSpan = COLUNAS;
  const lista = document.createElement("ul");
  lista.className = "lotes-do-produto";
  lista.id = idDosLotes;
  lista.setAttribute("aria-label", "Lotes de " + produto.nome + ", do que vence primeiro ao último");
  td.append(lista);
  detalhe.append(td);
  linha.after(detalhe);
  botao.setAttribute("aria-expanded", "true");
  lista.append(itemSimples("Procurando os lotes…"));

  const resposta = await api.ler("estoque/lotes/", { produto: produto.produto_id });
  lista.textContent = "";
  if (!resposta.ok) return lista.append(itemSimples("Não foi possível ver os lotes: " + resposta.erro.mensagem));
  if (!resposta.dados.length) return lista.append(itemSimples("Nenhum lote com mercadoria."));
  // A F2 já devolve na ordem de validade (RN02): o que vence primeiro aparece primeiro.
  resposta.dados.forEach((lote) => lista.append(itemDoLote(lote)));
}

function itemDoLote(lote) {
  const item = document.createElement("li");
  const partes = [
    quantidade(lote.quantidade_atual, lote.unidade_medida),
    lote.data_validade ? "validade " + dataBrasileira(lote.data_validade) : null,
    "entrou em " + dataBrasileira(lote.data_entrada),
    lote.fornecedor_nome,
  ].filter(Boolean);
  item.append(etiquetaDaSituacao(lote), " ", partes.join(" · "));
  return item;
}

function itemSimples(conteudo) {
  const item = document.createElement("li");
  item.textContent = conteudo;
  return item;
}

function etiqueta(conteudo, tipo) {
  const span = document.createElement("span");
  span.className = "etiqueta etiqueta--" + tipo;
  span.textContent = conteudo;
  return span;
}

function texto(conteudo, classe) {
  const span = document.createElement("span");
  span.className = classe;
  span.textContent = conteudo;
  return span;
}

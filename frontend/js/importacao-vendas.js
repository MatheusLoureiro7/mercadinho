/*
 * Tela de Importação de vendas — tarefa E5 (RF06, operação 04). Usada pelo sobrinho (OPERACAO, RN14).
 *
 * A planilha não é enviada por aqui: o sobrinho a salva na pasta do caixa e a rodada das 03h00 a
 * importa (E3, G5). A tela acompanha o resultado:
 *   - vendas para conferir: as linhas que não casaram com o cadastro (passo 6). Sem o nome escrito
 *     na planilha (L26), cada uma aparece com data, hora, quantidade e preço; o sobrinho escolhe o
 *     produto e a venda sai do estoque no dia em que aconteceu (E4, RN01, RN02);
 *   - planilhas lidas: as últimas leituras, com a situação em palavras (não só em cor).
 *
 * Ligar a venda não tem desfazer — a movimentação nunca é apagada (RN01). Por isso a tela pergunta
 * antes, dizendo quanto sai do estoque de qual produto (revisão X1, item 18).
 *
 * API:
 *   GET  importacoes/                          → as últimas 30 planilhas lidas (E5)
 *   GET  itens-pendentes/                      → as vendas para conferir, da mais antiga à mais nova (E4)
 *   POST itens-pendentes/{id}/casar/ {produto} → a venda ligada ao produto (E4)
 *   GET  produtos/                             → a lista do "Procurar o produto"
 */

import { api } from "./api.js";
import { linhaDeFalha } from "./falha.js";
import { dataBrasileira, diaNaLoja, emReais, horaNaLoja, quantidade } from "./formatos.js";
import { celula, confirmar, limparErros, linhaVazia, mostrarErroNoCampo, mostrarErros } from "./formulario.js";
import { procurarProduto } from "./procurar-produto.js";
import { entrarNaTela } from "./sessao.js";

// Exatamente o que a tela manda para a API.
const CAMPOS = { produto: { id: "campo-produto", rotulo: "Produto" } };
const COLUNAS_PENDENTES = 5;
const COLUNAS_PLANILHAS = 6;

// A situação da leitura em palavras e cor (WCAG 1.4.1: nunca só a cor).
const SITUACAO = {
  OK: { texto: "Lida", tipo: "ok" },
  PARCIAL: { texto: "Lida, com vendas a conferir", tipo: "aviso" },
  ERRO: { texto: "Não foi lida", tipo: "erro" },
  PENDENTE: { texto: "Lendo agora", tipo: "neutra" },
};

const estado = { pendentes: [], escolhida: null, procura: null, enviando: false, confirmando: null };

const $ = (id) => document.getElementById(id);

// ------------------------------------------------------------------------------------------ Início

document.addEventListener("DOMContentLoaded", iniciar);

async function iniciar() {
  if (!(await entrarNaTela("importacao_vendas"))) return;

  $("formulario").addEventListener("submit", ligar);
  $("botao-cancelar").addEventListener("click", () => fecharFormulario(true));
  $("botao-confirmar").addEventListener("click", gravar);
  $("botao-voltar").addEventListener("click", () => {
    esconderConfirmacao();
    $("campo-produto").focus();
  });
  $("campo-produto").addEventListener("change", () => {
    mostrarErroNoCampo(CAMPOS, "produto", null);
    esconderConfirmacao();
  });
  $("campo-procurar").addEventListener("input", esconderConfirmacao);

  carregarPendentes();
  carregarPlanilhas();
}

// ------------------------------------------------------------------------------------------ Vendas para conferir

async function carregarPendentes() {
  const corpo = $("corpo-pendentes");
  const [pendentes, produtos] = await Promise.all([api.ler("itens-pendentes/"), api.ler("produtos/")]);
  corpo.textContent = "";
  const falha = [pendentes, produtos].find((resposta) => !resposta.ok);
  if (falha) {
    $("contagem-pendentes").textContent = "";
    corpo.append(linhaDeFalha(falha.erro, COLUNAS_PENDENTES, carregarPendentes));
    return;
  }
  if (!estado.procura) {
    estado.procura = procurarProduto({ produtos: produtos.dados, aoEscolher: () => {} });
  }
  estado.pendentes = pendentes.dados;
  mostrarPendentes();
}

function mostrarPendentes() {
  const corpo = $("corpo-pendentes");
  corpo.textContent = "";
  const total = estado.pendentes.length;
  $("contagem-pendentes").textContent = !total
    ? ""
    : total === 1
      ? "1 venda para conferir."
      : total + " vendas para conferir.";
  if (!total) {
    corpo.append(
      linhaVazia(COLUNAS_PENDENTES, "Nenhuma venda para conferir.", " Tudo o que veio do caixa foi reconhecido.")
    );
    return;
  }
  estado.pendentes.forEach((item) => corpo.append(linhaPendente(item)));
}

function quandoFoi(item) {
  return dataBrasileira(diaNaLoja(item.data_hora)) + " às " + horaNaLoja(item.data_hora);
}

/** "1.275" → "1,275"; sem unidade, porque o produto ainda não é conhecido (L26). */
function quantidadeSemUnidade(texto) {
  return Number(texto).toLocaleString("pt-BR", { maximumFractionDigits: 3 });
}

function linhaPendente(item) {
  const linha = document.createElement("tr");
  linha.dataset.id = item.id;

  const data = document.createElement("th");
  data.scope = "row";
  data.textContent = dataBrasileira(diaNaLoja(item.data_hora));

  const acao = celula();
  const botao = document.createElement("button");
  botao.type = "button";
  botao.className = "botao botao--secundario";
  botao.textContent = "Escolher o produto";
  // O nome do botão diz de qual venda é, para quem usa leitor de tela (WCAG 2.4.6).
  botao.setAttribute("aria-label", "Escolher o produto da venda de " + quandoFoi(item));
  botao.addEventListener("click", () => abrirFormulario(item));
  acao.append(botao);

  linha.append(
    data,
    celula(horaNaLoja(item.data_hora)),
    celula(quantidadeSemUnidade(item.quantidade), "numero"),
    celula(emReais(item.preco), "numero"),
    acao
  );
  return linha;
}

function abrirFormulario(item) {
  estado.escolhida = item;
  confirmar(null);
  limparErros(CAMPOS);
  $("venda-escolhida").textContent =
    "Venda de " + quandoFoi(item) + " · " + quantidadeSemUnidade(item.quantidade) + " a " + emReais(item.preco) + " cada.";
  $("campo-procurar").value = "";
  estado.procura.filtrar();
  $("campo-produto").value = "";
  $("formulario").hidden = false;
  marcarLinha(item.id);
  $("campo-procurar").focus();
}

/** Fecha o formulário; ao cancelar, o foco volta para o botão da venda que estava aberta. */
function fecharFormulario(voltarParaALinha) {
  const id = estado.escolhida && estado.escolhida.id;
  estado.escolhida = null;
  esconderConfirmacao();
  $("formulario").hidden = true;
  marcarLinha(null);
  limparErros(CAMPOS);
  if (voltarParaALinha && id) {
    const botao = document.querySelector('#corpo-pendentes tr[data-id="' + id + '"] button');
    if (botao) botao.focus();
  }
}

/** Marca na lista a venda aberta no formulário (cor e traço; o formulário diz qual é em palavras). */
function marcarLinha(id) {
  document.querySelectorAll("#corpo-pendentes tr").forEach((linha) => {
    linha.classList.toggle("linha--escolhida", id !== null && linha.dataset.id === String(id));
  });
}

async function ligar(evento) {
  evento.preventDefault();
  if (estado.enviando || !estado.escolhida) return;
  limparErros(CAMPOS);

  const produto = estado.procura.escolhido();
  if (!produto) {
    mostrarErroNoCampo(CAMPOS, "produto", "Escolha o produto que foi vendido.");
    $("campo-produto").focus();
    return;
  }

  // X1, item 18: primeiro a pergunta; quem grava é o "Sim, ligar".
  const item = estado.escolhida;
  estado.confirmando = produto;
  $("texto-confirmacao").textContent =
    "Ligar a venda de " + quandoFoi(item) + " a " + produto.nome + "? Isso tira " +
    quantidade(item.quantidade, produto.unidade_medida) + " do estoque dele e não pode ser desfeito.";
  $("confirmacao").hidden = false;
  $("botao-ligar").hidden = true;
  $("botao-confirmar").focus();
}

function esconderConfirmacao() {
  estado.confirmando = null;
  $("confirmacao").hidden = true;
  $("botao-ligar").hidden = false;
}

async function gravar() {
  const item = estado.escolhida;
  const produto = estado.confirmando;
  if (estado.enviando || !item || !produto) return;
  estado.enviando = true;
  $("botao-confirmar").disabled = true;
  const resposta = await api.criar("itens-pendentes/" + item.id + "/casar/", { produto: produto.id });
  estado.enviando = false;
  $("botao-confirmar").disabled = false;

  if (!resposta.ok) {
    esconderConfirmacao();
    mostrarErros(CAMPOS, resposta.erro);
    return;
  }

  fecharFormulario(false);
  estado.pendentes = estado.pendentes.filter((pendente) => pendente.id !== item.id);
  mostrarPendentes();
  confirmar("Venda de " + quandoFoi(item) + " ligada a " + resposta.dados.produto_nome + ". Ela saiu do estoque.");
  // O foco vai para a próxima venda, ou para a confirmação se não sobrou nenhuma.
  const proximo = document.querySelector("#corpo-pendentes button");
  if (proximo) proximo.focus();
  else $("titulo-pendentes").focus();
}

// ------------------------------------------------------------------------------------------ Planilhas lidas

async function carregarPlanilhas() {
  const corpo = $("corpo-planilhas");
  const resposta = await api.ler("importacoes/");
  corpo.textContent = "";
  if (!resposta.ok) {
    corpo.append(linhaDeFalha(resposta.erro, COLUNAS_PLANILHAS, carregarPlanilhas));
    return;
  }
  if (!resposta.dados.length) {
    corpo.append(
      linhaVazia(
        COLUNAS_PLANILHAS,
        "Nenhuma planilha lida ainda.",
        " Salve a planilha do caixa na pasta de sempre: ela entra na próxima madrugada."
      )
    );
    return;
  }
  resposta.dados.forEach((importacao) => corpo.append(linhaPlanilha(importacao)));
}

function linhaPlanilha(importacao) {
  const linha = document.createElement("tr");
  const nome = document.createElement("th");
  nome.scope = "row";
  nome.className = "texto-longo";
  nome.textContent = importacao.arquivo_nome;

  const situacao = SITUACAO[importacao.status] || { texto: importacao.status, tipo: "neutra" };
  const etiqueta = document.createElement("span");
  etiqueta.className = "etiqueta etiqueta--" + situacao.tipo;
  etiqueta.textContent = situacao.texto;
  const celulaSituacao = celula();
  celulaSituacao.append(etiqueta);

  const lidaEm = importacao.processado_em
    ? dataBrasileira(diaNaLoja(importacao.processado_em)) + " às " + horaNaLoja(importacao.processado_em)
    : "—";

  linha.append(
    nome,
    celula(dataBrasileira(importacao.data_referencia)),
    celula(lidaEm, "sem-quebra"),
    celula(String(importacao.linhas_lidas), "numero"),
    celula(String(importacao.linhas_erro), "numero"),
    celulaSituacao
  );
  return linha;
}

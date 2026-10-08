/*
 * Tela de Entrada de mercadoria — tarefa C5 (RF03, operação 02, fluxograma 02). Usada pelo sobrinho
 * (OPERACAO, RN14).
 *
 * Cada carga que chega vira um lote: a tela envia produto, quantidade, custo, fornecedor e validade
 * para POST /api/lotes/ (C2) e mostra o que a API responde. A tela não decide regra:
 * - a data de entrada é sempre hoje, decidida pela API — não há campo para ela;
 * - a validade do perecível deixada em branco é calculada pela API (RN04, C3), e a tela só mostra
 *   o resultado; validade vencida é recusada pela API, com a mensagem dela.
 * Recusa mantém tudo o que foi digitado e aponta só o campo com problema, como nas outras telas.
 *
 * Uma carga traz vários produtos do mesmo fornecedor: depois de registrar, o fornecedor continua
 * escolhido (WCAG 3.3.7, não pedir a mesma informação de novo).
 */

import { api } from "./api.js";
import { linhaDeFalha } from "./falha.js";
import { dataBrasileira, emReais, numeroParaApi, quantidade, semAcento } from "./formatos.js";
import { entrarNaTela } from "./sessao.js";

// Exatamente os campos que a API recebe (EntradaDeLoteSerializer). Um teste confere.
const CAMPOS = {
  produto: { id: "campo-produto", rotulo: "Produto", obrigatorio: "Escolha o produto que chegou." },
  quantidade: { id: "campo-quantidade", rotulo: "Quantidade", obrigatorio: "Informe a quantidade que chegou." },
  custo_unitario: { id: "campo-custo", rotulo: "Custo" },
  data_validade: { id: "campo-validade", rotulo: "Validade" },
  fornecedor: { id: "campo-fornecedor", rotulo: "Fornecedor" },
};

const UNIDADES = { KG: "quilo", L: "litro", UN: "unidade", PCT: "pacote" };

const estado = {
  produtos: [],
  fornecedores: [],
  // "Hoje" da lista do dia: o dia de São Paulo, como o da API (CLAUDE.md). Depois da primeira
  // entrada, vale a data que a própria API gravou — o relógio do computador pode estar errado.
  hoje: hojeNaLoja(),
};

const $ = (id) => document.getElementById(id);

function hojeNaLoja() {
  // "en-CA" escreve a data como AAAA-MM-DD, o formato que a API recebe.
  return new Intl.DateTimeFormat("en-CA", { timeZone: "America/Sao_Paulo" }).format(new Date());
}

// ------------------------------------------------------------------------------------------ Início

document.addEventListener("DOMContentLoaded", iniciar);

async function iniciar() {
  if (!(await entrarNaTela("entrada_mercadoria"))) return;

  const [produtos, fornecedores] = await Promise.all([api.ler("produtos/"), api.ler("fornecedores/")]);
  const falha = [produtos, fornecedores].find((resposta) => !resposta.ok);
  if (falha) {
    $("corpo-tabela").append(linhaDeFalha(falha.erro, 5, () => window.location.reload()));
    $("botao-salvar").disabled = true;
    return;
  }
  estado.produtos = produtos.dados;
  estado.fornecedores = fornecedores.dados;

  preencherFornecedores();
  $("campo-validade").min = estado.hoje; // só ajuda o calendário; quem recusa data vencida é a API (RN04)
  filtrarProdutos();
  mostrarProduto();

  $("campo-procurar").addEventListener("input", filtrarProdutos);
  $("campo-produto").addEventListener("change", aoEscolherProduto);
  $("formulario").addEventListener("submit", salvar);
  $("botao-limpar").addEventListener("click", () => limparFormulario({ manterFornecedor: false }));
  Object.keys(CAMPOS).forEach((campo) => {
    // Apaga o erro enquanto a pessoa corrige; nunca no "blur" (o clique em "Registrar" se perderia, B7).
    $(CAMPOS[campo].id).addEventListener("input", () => mostrarErroNoCampo(campo, null));
  });

  carregarLista();
  $("campo-procurar").focus();
}

function preencherFornecedores() {
  const select = $("campo-fornecedor");
  select.textContent = "";
  select.append(new Option("Nenhum / não sei", ""));
  estado.fornecedores.forEach((fornecedor) => select.append(new Option(fornecedor.nome, fornecedor.id)));
}

// ------------------------------------------------------------------------------------------ Produto

function filtrarProdutos() {
  const busca = semAcento($("campo-procurar").value.trim());
  const select = $("campo-produto");
  const escolhido = select.value;
  const encontrados = estado.produtos.filter((p) => !busca || semAcento(p.nome).indexOf(busca) >= 0);

  select.textContent = "";
  select.append(new Option(encontrados.length ? "Escolha…" : "Nenhum produto com esse nome", ""));
  encontrados.forEach((p) => select.append(new Option(p.nome + " — " + p.categoria_nome, p.id)));

  // Só escolhe sozinho quando não há dúvida (um resultado); senão mantém o que estava escolhido.
  if (encontrados.length === 1) select.value = String(encontrados[0].id);
  else if (encontrados.some((p) => String(p.id) === escolhido)) select.value = escolhido;

  $("anuncio-produtos").textContent = !busca
    ? estado.produtos.length + " produtos na lista."
    : encontrados.length === 1
      ? "1 produto encontrado e escolhido: " + encontrados[0].nome + "."
      : encontrados.length + " produtos encontrados. Escolha na lista abaixo.";
  if (select.value !== escolhido) aoEscolherProduto();
}

function produtoEscolhido() {
  const id = Number($("campo-produto").value);
  return estado.produtos.find((p) => p.id === id) || null;
}

function aoEscolherProduto() {
  mostrarErroNoCampo("produto", null);
  const produto = produtoEscolhido();
  // O fornecedor de costume vem junto, a não ser que a pessoa já tenha escolhido um para a carga.
  if (produto && produto.fornecedor_padrao && !$("campo-fornecedor").value) {
    $("campo-fornecedor").value = produto.fornecedor_padrao;
  }
  mostrarProduto();
}

function mostrarProduto() {
  const produto = produtoEscolhido();
  const unidade = produto ? produto.unidade_medida : "";
  $("sufixo-quantidade").textContent = unidade;
  $("rotulo-custo").textContent = produto ? "Custo por " + (UNIDADES[unidade] || unidade) : "Custo de cada um";

  if (!produto) {
    $("detalhe-produto").textContent = "";
    $("obrigatorio-validade").hidden = true;
    $("ajuda-validade").textContent = "A data na embalagem.";
    return;
  }
  const dias = produto.durabilidade_dias === 1 ? "1 dia" : produto.durabilidade_dias + " dias";
  $("detalhe-produto").textContent = produto.perecivel
    ? "Perecível · dura " + dias + " · vendido por " + UNIDADES[unidade] + "."
    : "Não perecível · vendido por " + UNIDADES[unidade] + ".";
  // RN04 explicada; quem calcula a validade é a API.
  $("obrigatorio-validade").hidden = !produto.perecivel;
  $("ajuda-validade").textContent = produto.perecivel
    ? "A data na embalagem. Se deixar em branco, o sistema conta " + dias + " a partir de hoje."
    : "A data na embalagem, se tiver. Pode deixar em branco.";
}

// ------------------------------------------------------------------------------------------ Salvar

function dadosDoFormulario() {
  return {
    produto: $("campo-produto").value ? Number($("campo-produto").value) : null,
    quantidade: numeroParaApi($("campo-quantidade").value),
    custo_unitario: numeroParaApi($("campo-custo").value),
    data_validade: $("campo-validade").value || null,
    fornecedor: $("campo-fornecedor").value ? Number($("campo-fornecedor").value) : null,
  };
}

async function salvar(evento) {
  evento.preventDefault();
  limparErros();
  confirmar(null);

  const dados = dadosDoFormulario();
  // Só "preencha": evita uma ida à API à toa. Tudo o mais (quantidade zero, validade vencida) é da API.
  const faltando = ["produto", "quantidade"].filter((campo) => dados[campo] === null);
  if (faltando.length) {
    const campos = {};
    faltando.forEach((campo) => (campos[campo] = [CAMPOS[campo].obrigatorio]));
    return mostrarErros({ campos: campos });
  }

  const botao = $("botao-salvar");
  botao.disabled = true;
  botao.setAttribute("aria-busy", "true");
  const resposta = await api.criar("lotes/", dados);
  botao.disabled = false;
  botao.removeAttribute("aria-busy");

  if (!resposta.ok) return mostrarErros(resposta.erro); // o que foi digitado fica onde está

  const lote = resposta.dados;
  limparFormulario({ manterFornecedor: true });
  confirmar(mensagemDeSucesso(lote, !dados.data_validade));
  if (lote.data_entrada !== estado.hoje) estado.hoje = lote.data_entrada; // o dia que a API gravou
  carregarLista();
}

function mensagemDeSucesso(lote, validadeEmBranco) {
  let texto =
    "Entrada registrada: " + quantidade(lote.quantidade_inicial, lote.unidade_medida) + " de " + lote.produto_nome + ". " +
    "Agora tem " + quantidade(lote.saldo_produto, lote.unidade_medida) + " em estoque.";
  if (validadeEmBranco && lote.data_validade) {
    texto += " Validade calculada: " + dataBrasileira(lote.data_validade) + ".";
  }
  return texto;
}

function limparFormulario(opcoes) {
  const fornecedor = $("campo-fornecedor").value;
  $("formulario").reset();
  limparErros();
  confirmar(null);
  if (opcoes.manterFornecedor) $("campo-fornecedor").value = fornecedor;
  filtrarProdutos();
  mostrarProduto();
  $("campo-procurar").focus();
}

// ------------------------------------------------------------------------------------------ Lista do dia

async function carregarLista() {
  const corpo = $("corpo-tabela");
  corpo.setAttribute("aria-busy", "true");
  const resposta = await api.ler("lotes/", { data_entrada: estado.hoje });
  corpo.removeAttribute("aria-busy");
  corpo.textContent = "";

  if (!resposta.ok) {
    corpo.append(linhaDeFalha(resposta.erro, 5, carregarLista));
    $("anuncio-lista").textContent = "Não foi possível carregar as entradas de hoje.";
    return;
  }
  const lotes = resposta.dados;
  if (!lotes.length) corpo.append(linhaVazia());
  else lotes.forEach((lote) => corpo.append(linhaDoLote(lote)));
  $("titulo-lista").textContent = "Entradas de hoje · " + dataBrasileira(estado.hoje);
  $("anuncio-lista").textContent = lotes.length === 1 ? "1 entrada hoje." : lotes.length + " entradas hoje.";
}

function linhaVazia() {
  const linha = document.createElement("tr");
  const celula = document.createElement("td");
  celula.colSpan = 5;
  celula.className = "vazio";
  celula.innerHTML = "<strong>Nenhuma entrada registrada hoje.</strong>O que você registrar aparece aqui.";
  linha.append(celula);
  return linha;
}

function linhaDoLote(lote) {
  const linha = document.createElement("tr");
  const nome = celula();
  const forte = document.createElement("strong");
  forte.textContent = lote.produto_nome;
  nome.append(forte);
  linha.append(
    nome,
    celula(quantidade(lote.quantidade_inicial, lote.unidade_medida), "numero"),
    lote.data_validade ? celula(dataBrasileira(lote.data_validade)) : celula("Sem validade", "texto-suave"),
    lote.fornecedor_nome ? celula(lote.fornecedor_nome) : celula("—", "texto-suave"),
    celula(emReais(lote.custo_unitario), "numero")
  );
  return linha;
}

function celula(conteudo, classe) {
  const td = document.createElement("td");
  if (classe) td.className = classe;
  if (conteudo !== undefined) td.textContent = conteudo;
  return td;
}

// ------------------------------------------------------------------------------------------ Erros

function mostrarErros(erro) {
  const campos = erro.campos || {};
  const lista = $("lista-de-erros");
  lista.textContent = "";

  Object.keys(campos).forEach((campo) => {
    const mensagem = [].concat(campos[campo]).join(" ");
    mostrarErroNoCampo(campo, mensagem);
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = "#" + (CAMPOS[campo] ? CAMPOS[campo].id : "formulario");
    link.textContent = (CAMPOS[campo] ? CAMPOS[campo].rotulo + ": " : "") + mensagem;
    link.addEventListener("click", (e) => {
      e.preventDefault();
      if (CAMPOS[campo]) $(CAMPOS[campo].id).focus();
    });
    item.append(link);
    lista.append(item);
  });

  if (!Object.keys(campos).length) {
    const item = document.createElement("li");
    item.textContent = erro.mensagem || "Não foi possível registrar. Tente de novo.";
    lista.append(item);
  }

  const resumo = $("resumo-de-erros");
  resumo.hidden = false;
  resumo.focus();
}

function mostrarErroNoCampo(campo, mensagem) {
  const info = CAMPOS[campo];
  const paragrafo = $("erro-" + campo);
  if (!info || !paragrafo) return;
  const entrada = $(info.id);
  paragrafo.textContent = mensagem || "";
  paragrafo.hidden = !mensagem;
  if (mensagem) entrada.setAttribute("aria-invalid", "true");
  else entrada.removeAttribute("aria-invalid");
}

function limparErros() {
  $("resumo-de-erros").hidden = true;
  $("lista-de-erros").textContent = "";
  Object.keys(CAMPOS).forEach((campo) => mostrarErroNoCampo(campo, null));
}

// ------------------------------------------------------------------------------------------ Confirmação

/** Mostra (ou esconde, com null) a confirmação no topo do formulário. Fica até o próximo registro. */
function confirmar(mensagem) {
  $("sucesso-texto").textContent = mensagem || "";
  $("sucesso").hidden = !mensagem;
}

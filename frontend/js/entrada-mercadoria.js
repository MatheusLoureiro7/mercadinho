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
import { dataBrasileira, diaNaLoja, emReais, numeroParaApi, quantidade } from "./formatos.js";
import {
  apagarErroAoCorrigir,
  celula,
  confirmar,
  limparErros,
  linhaVazia,
  mostrarErroNoCampo,
  mostrarErros,
} from "./formulario.js";
import { procurarProduto } from "./procurar-produto.js";
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
  fornecedores: [],
  procura: null,
  // "Hoje" da lista do dia, no dia da loja. Depois da primeira entrada, vale a data que a própria
  // API gravou — o relógio do computador pode estar errado.
  hoje: diaNaLoja(),
};

const $ = (id) => document.getElementById(id);

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
  estado.fornecedores = fornecedores.dados;

  preencherFornecedores();
  $("campo-validade").min = estado.hoje; // só ajuda o calendário; quem recusa data vencida é a API (RN04)
  estado.procura = procurarProduto({ produtos: produtos.dados, aoEscolher: aoEscolherProduto });
  mostrarProduto();

  $("formulario").addEventListener("submit", salvar);
  $("botao-limpar").addEventListener("click", () => limparFormulario({ manterFornecedor: false }));
  apagarErroAoCorrigir(CAMPOS);

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

function produtoEscolhido() {
  return estado.procura ? estado.procura.escolhido() : null;
}

function aoEscolherProduto(produto) {
  mostrarErroNoCampo(CAMPOS, "produto", null);
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
  limparErros(CAMPOS);
  confirmar(null);

  const dados = dadosDoFormulario();
  // Só "preencha": evita uma ida à API à toa. Tudo o mais (quantidade zero, validade vencida) é da API.
  const faltando = ["produto", "quantidade"].filter((campo) => dados[campo] === null);
  if (faltando.length) {
    const campos = {};
    faltando.forEach((campo) => (campos[campo] = [CAMPOS[campo].obrigatorio]));
    return mostrarErros(CAMPOS, { campos: campos });
  }

  const botao = $("botao-salvar");
  botao.disabled = true;
  botao.setAttribute("aria-busy", "true");
  const resposta = await api.criar("lotes/", dados);
  botao.disabled = false;
  botao.removeAttribute("aria-busy");

  if (!resposta.ok) return mostrarErros(CAMPOS, resposta.erro); // o que foi digitado fica onde está

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
  limparErros(CAMPOS);
  confirmar(null);
  if (opcoes.manterFornecedor) $("campo-fornecedor").value = fornecedor;
  estado.procura.filtrar();
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
  if (!lotes.length) {
    corpo.append(linhaVazia(5, "Nenhuma entrada registrada hoje.", "O que você registrar aparece aqui."));
  } else {
    lotes.forEach((lote) => corpo.append(linhaDoLote(lote)));
  }
  $("titulo-lista").textContent = "Entradas de hoje · " + dataBrasileira(estado.hoje);
  $("anuncio-lista").textContent = lotes.length === 1 ? "1 entrada hoje." : lotes.length + " entradas hoje.";
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

/*
 * Tela de Avarias e quebras — tarefa D3 (RF04, fluxograma 03). Usada pelo sobrinho (OPERACAO, RN14).
 *
 * O caderno de avarias: o que venceu, quebrou ou estragou sai do estoque, sempre com o motivo. A
 * tela envia produto, lote, quantidade e motivo para POST /api/perdas/ (D1) e mostra o que a API
 * responde. A regra é toda da API:
 * - motivo obrigatório (RF04) — a tela não confere, para a frase ser sempre a da API;
 * - L20: com lote escolhido, a perda sai dele; sem lote, pela ordem de validade (RN02), vencidos
 *   primeiro — é por aqui que o lote vencido sai (RN16);
 * - não perder mais do que existe; perda não conta como consumo (RN11).
 * Recusa mantém tudo o que foi digitado e aponta só o campo com problema.
 */

import { api } from "./api.js";
import { linhaDeFalha } from "./falha.js";
import { dataBrasileira, diaNaLoja, horaNaLoja, numeroParaApi, quantidade } from "./formatos.js";
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
import { etiquetaDaSituacao } from "./situacao.js";

// Exatamente os campos que a API recebe (RegistroDePerdaSerializer). Um teste confere.
const CAMPOS = {
  produto: { id: "campo-produto", rotulo: "Produto", obrigatorio: "Escolha o produto que se perdeu." },
  lote: { id: "lista-de-lotes", rotulo: "Lote" },
  quantidade: { id: "campo-quantidade", rotulo: "Quanto se perdeu", obrigatorio: "Informe quanto se perdeu." },
  motivo: { id: "campo-motivo", rotulo: "Motivo" },
};

const estado = {
  procura: null,
  lotes: [], // os lotes do produto escolhido que ainda têm mercadoria (F2)
  pedidoDeLotes: 0, // trocou de produto rápido: só vale a resposta do último pedido
  hoje: diaNaLoja(), // depois do primeiro registro, vale o dia que a API gravou
};

const $ = (id) => document.getElementById(id);

// ------------------------------------------------------------------------------------------ Início

document.addEventListener("DOMContentLoaded", iniciar);

async function iniciar() {
  if (!(await entrarNaTela("avarias"))) return;

  const produtos = await api.ler("produtos/");
  if (!produtos.ok) {
    $("corpo-tabela").append(linhaDeFalha(produtos.erro, 6, () => window.location.reload()));
    $("botao-salvar").disabled = true;
    return;
  }
  estado.procura = procurarProduto({ produtos: produtos.dados, aoEscolher: aoEscolherProduto });
  mostrarLotes(null);

  document.querySelectorAll("[data-motivo]").forEach((botao) => {
    botao.addEventListener("click", () => {
      $("campo-motivo").value = botao.dataset.motivo;
      mostrarErroNoCampo(CAMPOS, "motivo", null);
      $("campo-motivo").focus();
    });
  });
  $("lista-de-lotes").addEventListener("change", () => {
    mostrarErroNoCampo(CAMPOS, "lote", null);
    mostrarQuantidadeDisponivel();
  });
  $("formulario").addEventListener("submit", salvar);
  $("botao-limpar").addEventListener("click", limparFormulario);
  apagarErroAoCorrigir(CAMPOS);

  carregarCaderno();
  $("campo-procurar").focus();
}

// ------------------------------------------------------------------------------------------ Produto e lotes

async function aoEscolherProduto(produto) {
  mostrarErroNoCampo(CAMPOS, "produto", null);
  estado.lotes = [];
  mostrarLotes(produto);
  if (!produto) return;

  const pedido = ++estado.pedidoDeLotes;
  $("ajuda-lote").textContent = "Procurando os lotes de " + produto.nome + "…";
  const resposta = await api.ler("estoque/lotes/", { produto: produto.id });
  if (pedido !== estado.pedidoDeLotes) return;
  if (!resposta.ok) {
    $("ajuda-lote").textContent = "Não foi possível ver os lotes: " + resposta.erro.mensagem;
    return;
  }
  estado.lotes = resposta.dados;
  mostrarLotes(produto);
}

function mostrarLotes(produto) {
  const lista = $("lista-de-lotes");
  lista.textContent = "";
  $("sufixo-quantidade").textContent = produto ? produto.unidade_medida : "";
  if (!produto) {
    $("ajuda-lote").textContent = "Escolha o produto para ver os lotes que estão na loja.";
    mostrarQuantidadeDisponivel();
    return;
  }

  // Primeira opção, marcada: deixar a API escolher pela ordem de validade (L20).
  lista.append(opcaoDeLote("", "Não sei qual — pela ordem de validade", "Sai primeiro o que vence antes, os vencidos primeiro.", true));
  // A F2 já devolve na ordem de validade: o que vence primeiro aparece primeiro.
  estado.lotes.forEach((lote) => lista.append(opcaoDeLote(String(lote.id), descricaoDoLote(lote), null, false, lote)));

  $("ajuda-lote").textContent = estado.lotes.length
    ? "Se souber qual lote estragou, escolha ele."
    : "Não há " + produto.nome + " em estoque agora.";
  mostrarQuantidadeDisponivel();
}

function opcaoDeLote(valor, titulo, detalhe, marcada, lote) {
  const rotulo = document.createElement("label");
  rotulo.className = "opcao";
  const radio = document.createElement("input");
  radio.type = "radio";
  radio.name = "lote";
  radio.value = valor;
  radio.checked = marcada;
  const texto = document.createElement("span");
  if (lote) texto.append(etiquetaDaSituacao(lote), " ");
  const forte = document.createElement("strong");
  forte.textContent = titulo;
  texto.append(forte);
  if (detalhe) {
    const ajuda = document.createElement("span");
    ajuda.className = "texto-suave opcao__detalhe";
    ajuda.textContent = detalhe;
    texto.append(ajuda);
  }
  rotulo.append(radio, texto);
  return rotulo;
}

function descricaoDoLote(lote) {
  const tem = quantidade(lote.quantidade_atual, lote.unidade_medida);
  if (!lote.data_validade) return "Sem validade · entrou em " + dataBrasileira(lote.data_entrada) + " · " + tem;
  return "Validade " + dataBrasileira(lote.data_validade) + " · " + tem;
}

function loteEscolhido() {
  const marcado = document.querySelector("#lista-de-lotes input:checked");
  return marcado && marcado.value ? estado.lotes.find((l) => String(l.id) === marcado.value) || null : null;
}

function mostrarQuantidadeDisponivel() {
  // Só informa; quem recusa perda maior do que o que existe é a API.
  const lote = loteEscolhido();
  const produto = estado.procura ? estado.procura.escolhido() : null;
  if (lote) {
    $("ajuda-quantidade").textContent = "Neste lote: " + quantidade(lote.quantidade_atual, lote.unidade_medida) + ".";
  } else if (produto && estado.lotes.length) {
    const total = estado.lotes.reduce((soma, l) => soma + Number(l.quantidade_atual), 0);
    $("ajuda-quantidade").textContent = "Na loja: " + quantidade(total, produto.unidade_medida) + ".";
  } else {
    $("ajuda-quantidade").textContent = "";
  }
}

// ------------------------------------------------------------------------------------------ Salvar

function dadosDoFormulario() {
  const marcado = document.querySelector("#lista-de-lotes input:checked");
  return {
    produto: $("campo-produto").value ? Number($("campo-produto").value) : null,
    lote: marcado && marcado.value ? Number(marcado.value) : null,
    quantidade: numeroParaApi($("campo-quantidade").value),
    motivo: $("campo-motivo").value.trim(),
  };
}

async function salvar(evento) {
  evento.preventDefault();
  limparErros(CAMPOS);
  confirmar(null);

  const dados = dadosDoFormulario();
  // Só "escolha/informe": evita uma ida à API à toa. O motivo e tudo o mais é conferido pela API.
  const faltando = ["produto", "quantidade"].filter((campo) => dados[campo] === null);
  if (faltando.length) {
    const campos = {};
    faltando.forEach((campo) => (campos[campo] = [CAMPOS[campo].obrigatorio]));
    return mostrarErros(CAMPOS, { campos: campos });
  }

  const botao = $("botao-salvar");
  botao.disabled = true;
  botao.setAttribute("aria-busy", "true");
  const resposta = await api.criar("perdas/", dados);
  botao.disabled = false;
  botao.removeAttribute("aria-busy");

  if (!resposta.ok) return mostrarErros(CAMPOS, resposta.erro); // o que foi digitado fica onde está

  const { perdas, saldo_produto: saldo } = resposta.dados;
  limparFormulario();
  confirmar(mensagemDeSucesso(perdas, saldo));
  const dia = diaNaLoja(perdas[0].data_hora);
  if (dia !== estado.hoje) estado.hoje = dia; // o dia que a API gravou
  carregarCaderno();
}

function mensagemDeSucesso(perdas, saldo) {
  const primeira = perdas[0];
  const total = perdas.reduce((soma, p) => soma + Number(p.quantidade), 0);
  let texto =
    "Perda registrada: " + quantidade(total, primeira.unidade_medida) + " de " + primeira.produto_nome +
    " (" + primeira.motivo + "). Agora tem " + quantidade(saldo, primeira.unidade_medida) + " em estoque.";
  if (perdas.length > 1) texto += " Saiu de " + perdas.length + " lotes, pela ordem de validade.";
  return texto;
}

function limparFormulario() {
  $("formulario").reset();
  limparErros(CAMPOS);
  confirmar(null);
  estado.procura.filtrar();
  aoEscolherProduto(estado.procura.escolhido());
  $("campo-procurar").focus();
}

// ------------------------------------------------------------------------------------------ Caderno do dia

async function carregarCaderno() {
  const corpo = $("corpo-tabela");
  corpo.setAttribute("aria-busy", "true");
  const resposta = await api.ler("perdas/", { data: estado.hoje });
  corpo.removeAttribute("aria-busy");
  corpo.textContent = "";

  if (!resposta.ok) {
    corpo.append(linhaDeFalha(resposta.erro, 6, carregarCaderno));
    $("anuncio-lista").textContent = "Não foi possível carregar as perdas de hoje.";
    return;
  }
  const perdas = resposta.dados;
  if (!perdas.length) {
    corpo.append(linhaVazia(6, "Nenhuma perda registrada hoje.", "O que você registrar aparece aqui."));
  } else {
    perdas.forEach((perda) => corpo.append(linhaDaPerda(perda)));
  }
  $("titulo-lista").textContent = "Perdas de hoje · " + dataBrasileira(estado.hoje);
  $("anuncio-lista").textContent = perdas.length === 1 ? "1 perda hoje." : perdas.length + " perdas hoje.";
}

function linhaDaPerda(perda) {
  const linha = document.createElement("tr");
  const nome = celula();
  const forte = document.createElement("strong");
  forte.textContent = perda.produto_nome;
  nome.append(forte);
  const lote = !perda.lote
    ? celula("—", "texto-suave")
    : perda.lote_validade
      ? celula("Validade " + dataBrasileira(perda.lote_validade))
      : celula("Sem validade", "texto-suave");
  linha.append(
    celula(horaNaLoja(perda.data_hora)),
    nome,
    celula(quantidade(perda.quantidade, perda.unidade_medida), "numero"),
    lote,
    celula(perda.motivo),
    celula(perda.usuario_nome || "—")
  );
  return linha;
}

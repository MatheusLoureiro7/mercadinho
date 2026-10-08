/*
 * Tela de Fornecedores — tarefa B6 (RF02). Usada pelo sobrinho (OPERACAO, RN14).
 *
 * O número que importa aqui é o prazo de entrega: é ele que faz o aviso de "vai acabar" sair com
 * antecedência suficiente para o fornecedor entregar (RN08). A tela não decide regra: envia o que
 * foi digitado e mostra o que a API responder. Recusa mantém tudo o que foi digitado e
 * aponta só o campo com problema, como na tela de Produtos.
 *
 * Sem exclusão: fornecedor é tabela de origem e nunca é apagado (L18).
 * Dados: a API (js/api.js), desde a B7. A tela abre só para quem tem o perfil (js/sessao.js, RN14).
 */

import { api } from "./api.js";
import { linhaDeFalha } from "./falha.js";
import { entrarNaTela } from "./sessao.js";
import { emReais, numeroParaApi, numeroParaCampo } from "./formatos.js";

const CAMPOS = {
  nome: { id: "campo-nome", rotulo: "Nome do fornecedor" },
  prazo_entrega_dias: { id: "campo-prazo", rotulo: "Prazo de entrega" },
  pedido_minimo: { id: "campo-pedido-minimo", rotulo: "Pedido mínimo" },
  contato: { id: "campo-contato", rotulo: "Contato" },
};

const estado = {
  fornecedorEmEdicao: null, // null = cadastro novo
  quemAbriu: null, // para devolver o foco ao fechar o formulário
};

const $ = (id) => document.getElementById(id);

// ------------------------------------------------------------------------------------------ Início

document.addEventListener("DOMContentLoaded", iniciar);

async function iniciar() {
  if (!(await entrarNaTela("fornecedores"))) return;

  $("botao-novo").addEventListener("click", (evento) => abrirFormulario(null, evento.currentTarget));
  $("botao-cancelar").addEventListener("click", fecharFormulario);
  $("formulario").addEventListener("submit", salvar);
  ["nome", "prazo_entrega_dias"].forEach((campo) => {
    $(CAMPOS[campo].id).addEventListener("input", () => conferirPreenchido(campo));
  });

  carregarLista();
}

// ------------------------------------------------------------------------------------------ Lista

async function carregarLista() {
  const corpo = $("corpo-tabela");
  corpo.setAttribute("aria-busy", "true");
  const resposta = await api.ler("fornecedores/");
  corpo.removeAttribute("aria-busy");
  corpo.textContent = "";

  if (!resposta.ok) {
    // Sem conexão ou erro do sistema: nunca mostrar "nenhum fornecedor cadastrado".
    corpo.append(linhaDeFalha(resposta.erro, 5, carregarLista));
    $("anuncio-lista").textContent = "Não foi possível carregar os fornecedores.";
    return;
  }
  const fornecedores = resposta.dados;

  if (!fornecedores.length) corpo.append(linhaVazia());
  else fornecedores.forEach((fornecedor) => corpo.append(linhaDoFornecedor(fornecedor)));

  $("anuncio-lista").textContent =
    fornecedores.length === 1 ? "1 fornecedor cadastrado." : fornecedores.length + " fornecedores cadastrados.";
}

function linhaVazia() {
  const linha = document.createElement("tr");
  const celula = document.createElement("td");
  celula.colSpan = 5;
  celula.className = "vazio";
  celula.innerHTML =
    "<strong>Nenhum fornecedor cadastrado ainda.</strong>Use o botão “Novo fornecedor” para começar.";
  linha.append(celula);
  return linha;
}

function linhaDoFornecedor(fornecedor) {
  const linha = document.createElement("tr");

  const nome = celula();
  const forte = document.createElement("strong");
  forte.textContent = fornecedor.nome;
  nome.append(forte);

  const acoes = celula();
  const editar = document.createElement("button");
  editar.type = "button";
  editar.className = "botao botao--secundario";
  editar.innerHTML = '<svg class="icone" viewBox="0 0 24 24" aria-hidden="true"><path d="M21.17 6.81a1 1 0 0 0-3.99-3.99L3.84 16.17a2 2 0 0 0-.5.83l-1.32 4.35a.5.5 0 0 0 .62.62l4.35-1.32a2 2 0 0 0 .83-.5z" /><path d="m15 5 4 4" /></svg>';
  editar.append("Editar");
  editar.setAttribute("aria-label", "Editar " + fornecedor.nome);
  editar.addEventListener("click", (evento) => abrirFormulario(fornecedor, evento.currentTarget));
  acoes.append(editar);

  const contato = fornecedor.contato ? celula(fornecedor.contato) : celula("—", "texto-suave");

  linha.append(
    nome,
    celula(prazoPorExtenso(fornecedor.prazo_entrega_dias)),
    celula(emReais(fornecedor.pedido_minimo), "numero"),
    contato,
    acoes
  );
  return linha;
}

function prazoPorExtenso(dias) {
  if (dias === 0) return "No mesmo dia";
  return dias === 1 ? "1 dia" : dias + " dias";
}

function celula(conteudo, classe) {
  const td = document.createElement("td");
  if (classe) td.className = classe;
  if (conteudo !== undefined) td.textContent = conteudo;
  return td;
}

// ------------------------------------------------------------------------------------------ Formulário

function abrirFormulario(fornecedor, quemAbriu) {
  estado.fornecedorEmEdicao = fornecedor;
  estado.quemAbriu = quemAbriu;
  limparErros();

  $("formulario").reset();
  $("titulo-formulario").textContent = fornecedor ? "Editar: " + fornecedor.nome : "Novo fornecedor";
  $("botao-salvar").textContent = fornecedor ? "Salvar alterações" : "Salvar fornecedor";

  if (fornecedor) {
    $("campo-nome").value = fornecedor.nome;
    $("campo-prazo").value = fornecedor.prazo_entrega_dias;
    $("campo-pedido-minimo").value = numeroParaCampo(fornecedor.pedido_minimo);
    $("campo-contato").value = fornecedor.contato || "";
  }

  const painel = $("painel-formulario");
  painel.hidden = false;
  painel.scrollIntoView({ block: "start" });
  $("campo-nome").focus();
}

function fecharFormulario() {
  $("painel-formulario").hidden = true;
  limparErros();
  if (estado.quemAbriu && document.body.contains(estado.quemAbriu)) estado.quemAbriu.focus();
  else $("botao-novo").focus();
}

function conferirPreenchido(campo) {
  // Só apaga o erro de quem já foi corrigido, enquanto a pessoa digita. Não no "blur": sumir o
  // erro ao sair do campo encolhe o formulário no meio do clique em "Salvar", e o clique se perde
  // (achado na B7). A regra de verdade é da API.
  if ($(CAMPOS[campo].id).value.trim()) mostrarErroNoCampo(campo, null);
}

function dadosDoFormulario() {
  const prazo = $("campo-prazo").value.trim();
  return {
    nome: $("campo-nome").value.trim(),
    // Só números viram número; qualquer outra coisa vai como foi digitada, para a API explicar o erro.
    prazo_entrega_dias: prazo === "" ? null : /^\d+$/.test(prazo) ? Number(prazo) : prazo,
    pedido_minimo: numeroParaApi($("campo-pedido-minimo").value),
    contato: $("campo-contato").value.trim() || null,
  };
}

async function salvar(evento) {
  evento.preventDefault();
  limparErros();
  const botao = $("botao-salvar");
  botao.setAttribute("aria-busy", "true");
  botao.disabled = true;

  const id = estado.fornecedorEmEdicao ? estado.fornecedorEmEdicao.id : null;
  const dados = dadosDoFormulario();
  const resposta = id ? await api.alterar("fornecedores/", id, dados) : await api.criar("fornecedores/", dados);

  botao.removeAttribute("aria-busy");
  botao.disabled = false;

  if (!resposta.ok) {
    mostrarErros(resposta.erro); // o que foi digitado fica onde está
    return;
  }
  $("painel-formulario").hidden = true;
  avisar(id ? "Alterações salvas." : "Fornecedor “" + resposta.dados.nome + "” cadastrado.");
  await carregarLista();
  $("botao-novo").focus();
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
    item.textContent = erro.mensagem || "Não foi possível salvar. Tente de novo.";
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
  if (mensagem) {
    paragrafo.textContent = mensagem;
    paragrafo.hidden = false;
    entrada.setAttribute("aria-invalid", "true");
  } else {
    paragrafo.textContent = "";
    paragrafo.hidden = true;
    entrada.removeAttribute("aria-invalid");
  }
}

function limparErros() {
  $("resumo-de-erros").hidden = true;
  $("lista-de-erros").textContent = "";
  Object.keys(CAMPOS).forEach((campo) => mostrarErroNoCampo(campo, null));
}

// ------------------------------------------------------------------------------------------ Aviso

let temporizadorDoAviso;
function avisar(mensagem) {
  $("toast-texto").textContent = mensagem;
  $("toast").hidden = false;
  clearTimeout(temporizadorDoAviso);
  temporizadorDoAviso = setTimeout(() => ($("toast").hidden = true), 4000);
}

/*
 * Tela de Produtos — tarefa B5 (RF01, RF15). Usada pelo sobrinho (OPERACAO, RN14).
 *
 * A tela não decide regra de negócio: ela envia o que foi digitado e mostra o que a fonte de dados
 * responder. Fluxograma 01: se algo for recusado, mantém tudo o que já foi digitado e aponta só o
 * campo com problema.
 *
 * Dados: a API (js/api.js), desde a B7. A tela abre só para quem tem o perfil (js/sessao.js, RN14).
 */

import { api } from "./api.js";
import { entrarNaTela } from "./sessao.js";
import { linhaDeFalha } from "./falha.js";
import { emReais, numerosAmbiguos, numeroParaApi, numeroParaCampo, quantidade } from "./formatos.js";

const CAMPOS = {
  nome: { id: "campo-nome", rotulo: "Nome do produto", obrigatorio: "Preencha o nome do produto." },
  categoria: { id: "campo-categoria", rotulo: "Categoria", obrigatorio: "Escolha a categoria do produto." },
  unidade_medida: { id: "campo-unidade", rotulo: "Unidade", obrigatorio: "Escolha a unidade: KG, UN, L ou PCT." },
  fornecedor_padrao: { id: "campo-fornecedor", rotulo: "Fornecedor de costume" },
  perecivel: { id: "campo-perecivel", rotulo: "É perecível" },
  durabilidade_dias: { id: "campo-durabilidade", rotulo: "Dura quantos dias?" },
  preco_custo: { id: "campo-custo", rotulo: "Preço de custo" },
  preco_venda: { id: "campo-venda", rotulo: "Preço de venda" },
  estoque_minimo: { id: "campo-minimo", rotulo: "Estoque mínimo" },
  critico_fim_semana: { id: "campo-critico", rotulo: "Não pode faltar no fim de semana" },
};

const estado = {
  categorias: [],
  produtoEmEdicao: null, // null = cadastro novo
  pereciveltocado: false, // L19: só herda da categoria enquanto a pessoa não mexeu no "É perecível"
  quemAbriu: null, // para devolver o foco ao fechar o formulário
  pedidoDaLista: 0, // busca digitada rápido: só vale a resposta do último pedido
};

const $ = (id) => document.getElementById(id);

// ------------------------------------------------------------------------------------------ Início

document.addEventListener("DOMContentLoaded", iniciar);

async function iniciar() {
  if (!(await entrarNaTela("produtos"))) return;

  const [categorias, fornecedores] = await Promise.all([api.ler("categorias/"), api.ler("fornecedores/")]);
  const falha = [categorias, fornecedores].find((resposta) => !resposta.ok);
  if (falha) {
    mostrarFalhaNaLista(falha.erro, () => window.location.reload());
    return;
  }
  estado.categorias = categorias.dados;
  preencherCategorias();
  preencherSelect($("campo-fornecedor"), fornecedores.dados, "Nenhum");

  $("botao-novo").addEventListener("click", (evento) => abrirFormulario(null, evento.currentTarget));
  $("botao-cancelar").addEventListener("click", fecharFormulario);
  $("formulario").addEventListener("submit", salvar);
  $("campo-perecivel").addEventListener("change", () => {
    estado.pereciveltocado = true;
    mostrarDurabilidade();
  });
  $("campo-categoria").addEventListener("change", herdarPerecivelDaCategoria);
  $("campo-unidade").addEventListener("change", atualizarSufixoDoMinimo);
  $("botao-nova-categoria").addEventListener("click", alternarNovaCategoria);
  $("botao-salvar-categoria").addEventListener("click", criarCategoria);

  ["nome", "categoria", "unidade_medida"].forEach((campo) => {
    $(CAMPOS[campo].id).addEventListener("input", () => conferirPreenchido(campo));
  });

  let espera;
  $("busca").addEventListener("input", () => {
    clearTimeout(espera);
    espera = setTimeout(carregarLista, 250);
  });
  $("filtro-categoria").addEventListener("change", carregarLista);

  carregarLista();
}

function preencherSelect(select, itens, textoVazio) {
  select.textContent = "";
  select.append(new Option(textoVazio, ""));
  itens.forEach((item) => select.append(new Option(item.nome, item.id)));
}

function preencherCategorias() {
  const escolhida = $("campo-categoria").value;
  const filtro = $("filtro-categoria").value;
  preencherSelect($("campo-categoria"), estado.categorias, "Escolha…");
  preencherSelect($("filtro-categoria"), estado.categorias, "Todas as categorias");
  $("campo-categoria").value = escolhida;
  $("filtro-categoria").value = filtro;
}

// ------------------------------------------------------------------------------------------ Lista

async function carregarLista() {
  const corpo = $("corpo-tabela");
  const pedido = ++estado.pedidoDaLista;
  corpo.setAttribute("aria-busy", "true");
  const resposta = await api.ler("produtos/", { busca: $("busca").value.trim(), categoria: $("filtro-categoria").value });
  if (pedido !== estado.pedidoDaLista) return; // chegou depois de uma busca mais nova
  corpo.removeAttribute("aria-busy");

  if (!resposta.ok) {
    mostrarFalhaNaLista(resposta.erro, carregarLista);
    return;
  }
  corpo.textContent = "";
  const produtos = resposta.dados;
  if (!produtos.length) {
    corpo.append(linhaVazia());
  } else {
    produtos.forEach((produto) => corpo.append(linhaDoProduto(produto)));
  }
  $("anuncio-lista").textContent =
    produtos.length === 1 ? "1 produto encontrado." : produtos.length + " produtos encontrados.";
}

function mostrarFalhaNaLista(erro, tentarDeNovo) {
  // Sem conexão ou erro do sistema: diz o que houve e como sair, sem fingir que a lista está vazia.
  const corpo = $("corpo-tabela");
  corpo.removeAttribute("aria-busy");
  corpo.textContent = "";
  corpo.append(linhaDeFalha(erro, 7, tentarDeNovo));
  $("anuncio-lista").textContent = "Não foi possível carregar os produtos.";
}

function linhaVazia() {
  const linha = document.createElement("tr");
  const celula = document.createElement("td");
  celula.colSpan = 7;
  celula.className = "vazio";
  const procurando = $("busca").value.trim() || $("filtro-categoria").value;
  celula.innerHTML = procurando
    ? "<strong>Nenhum produto encontrado.</strong>Confira o nome digitado ou escolha outra categoria."
    : "<strong>Nenhum produto cadastrado ainda.</strong>Use o botão “Novo produto” para começar.";
  linha.append(celula);
  return linha;
}

function linhaDoProduto(produto) {
  const linha = document.createElement("tr");

  const nome = celula();
  const forte = document.createElement("strong");
  forte.textContent = produto.nome;
  nome.append(forte);
  if (produto.critico_fim_semana) {
    // Curta na tela para a tabela caber em 1024px; o leitor de tela ouve a frase inteira.
    const critico = etiqueta("", "aviso");
    critico.title = "Não pode faltar no fim de semana";
    critico.append(texto("Não pode faltar no ", "visualmente-oculto"), "Fim de semana");
    nome.append(document.createElement("br"), critico);
  }

  const validade = celula();
  validade.append(
    produto.perecivel
      ? etiqueta("Perecível · " + produto.durabilidade_dias + (produto.durabilidade_dias === 1 ? " dia" : " dias"), "neutra")
      : texto("Não perecível", "texto-suave")
  );

  const acoes = celula();
  const editar = document.createElement("button");
  editar.type = "button";
  editar.className = "botao botao--secundario";
  editar.innerHTML = '<svg class="icone" viewBox="0 0 24 24" aria-hidden="true"><path d="M21.17 6.81a1 1 0 0 0-3.99-3.99L3.84 16.17a2 2 0 0 0-.5.83l-1.32 4.35a.5.5 0 0 0 .62.62l4.35-1.32a2 2 0 0 0 .83-.5z" /><path d="m15 5 4 4" /></svg>';
  editar.append("Editar");
  editar.setAttribute("aria-label", "Editar " + produto.nome);
  editar.addEventListener("click", (evento) => abrirFormulario(produto, evento.currentTarget));
  acoes.append(editar);

  linha.append(
    nome,
    celula(produto.categoria_nome),
    celula(produto.unidade_medida),
    validade,
    celula(emReais(produto.preco_venda), "numero"),
    celula(quantidade(produto.estoque_minimo, produto.unidade_medida), "numero"),
    acoes
  );
  return linha;
}

function celula(conteudo, classe) {
  const td = document.createElement("td");
  if (classe) td.className = classe;
  if (conteudo !== undefined) td.textContent = conteudo;
  return td;
}

function etiqueta(textoDaEtiqueta, tipo) {
  const span = document.createElement("span");
  span.className = "etiqueta etiqueta--" + tipo;
  span.textContent = textoDaEtiqueta;
  return span;
}

function texto(conteudo, classe) {
  const span = document.createElement("span");
  span.className = classe;
  span.textContent = conteudo;
  return span;
}

// ------------------------------------------------------------------------------------------ Formulário

function abrirFormulario(produto, quemAbriu) {
  estado.produtoEmEdicao = produto;
  estado.pereciveltocado = !!produto;
  estado.quemAbriu = quemAbriu;
  limparErros();

  const formulario = $("formulario");
  formulario.reset();
  $("titulo-formulario").textContent = produto ? "Editar: " + produto.nome : "Novo produto";
  $("botao-salvar").textContent = produto ? "Salvar alterações" : "Salvar produto";

  if (produto) {
    $("campo-nome").value = produto.nome;
    $("campo-categoria").value = produto.categoria;
    $("campo-unidade").value = produto.unidade_medida;
    $("campo-fornecedor").value = produto.fornecedor_padrao || "";
    $("campo-perecivel").checked = produto.perecivel;
    $("campo-durabilidade").value = produto.durabilidade_dias || "";
    $("campo-custo").value = numeroParaCampo(produto.preco_custo);
    $("campo-venda").value = numeroParaCampo(produto.preco_venda);
    $("campo-minimo").value = numeroParaCampo(produto.estoque_minimo);
    $("campo-critico").checked = produto.critico_fim_semana;
  }
  mostrarDurabilidade();
  atualizarSufixoDoMinimo();

  const painel = $("painel-formulario");
  painel.hidden = false;
  painel.scrollIntoView({ block: "start" });
  $("campo-nome").focus();
}

function fecharFormulario() {
  $("painel-formulario").hidden = true;
  limparErros();
  fecharNovaCategoria();
  if (estado.quemAbriu && document.body.contains(estado.quemAbriu)) estado.quemAbriu.focus();
  else $("botao-novo").focus();
}

function mostrarDurabilidade() {
  const perecivel = $("campo-perecivel").checked;
  $("grupo-durabilidade").hidden = !perecivel;
  $("campo-durabilidade").required = perecivel;
}

function herdarPerecivelDaCategoria() {
  // L19: produto novo herda o "perecível" da categoria, até a pessoa mexer na opção.
  if (estado.produtoEmEdicao || estado.pereciveltocado) return;
  const categoria = estado.categorias.find((c) => String(c.id) === $("campo-categoria").value);
  $("campo-perecivel").checked = !!(categoria && categoria.perecivel_padrao);
  mostrarDurabilidade();
}

function atualizarSufixoDoMinimo() {
  $("sufixo-minimo").textContent = $("campo-unidade").value;
}

function conferirPreenchido(campo) {
  // Só apaga o erro de quem já foi corrigido, enquanto a pessoa digita ou escolhe. Não no "blur":
  // sumir o erro ao sair do campo encolhe o formulário no meio do clique em "Salvar", e o clique
  // se perde (achado na B7). A regra de verdade é da API.
  const valor = $(CAMPOS[campo].id).value.trim();
  if (valor) mostrarErroNoCampo(campo, null);
}

function dadosDoFormulario() {
  const perecivel = $("campo-perecivel").checked;
  return {
    nome: $("campo-nome").value.trim(),
    categoria: $("campo-categoria").value ? Number($("campo-categoria").value) : null,
    unidade_medida: $("campo-unidade").value,
    fornecedor_padrao: $("campo-fornecedor").value ? Number($("campo-fornecedor").value) : null,
    perecivel: perecivel,
    durabilidade_dias: perecivel && $("campo-durabilidade").value.trim() ? Number($("campo-durabilidade").value) : null,
    preco_custo: numeroParaApi($("campo-custo").value),
    preco_venda: numeroParaApi($("campo-venda").value),
    estoque_minimo: numeroParaApi($("campo-minimo").value),
    critico_fim_semana: $("campo-critico").checked,
  };
}

async function salvar(evento) {
  evento.preventDefault();
  limparErros();
  const ambiguos = numerosAmbiguos({
    preco_custo: $("campo-custo").value,
    preco_venda: $("campo-venda").value,
    estoque_minimo: $("campo-minimo").value,
  });
  if (ambiguos) return mostrarErros(ambiguos); // X1, item 13: "1.000" é mil ou um?
  const botao = $("botao-salvar");
  botao.setAttribute("aria-busy", "true");
  botao.disabled = true;

  const id = estado.produtoEmEdicao ? estado.produtoEmEdicao.id : null;
  const dados = dadosDoFormulario();
  const resposta = id ? await api.alterar("produtos/", id, dados) : await api.criar("produtos/", dados);

  botao.removeAttribute("aria-busy");
  botao.disabled = false;

  if (!resposta.ok) {
    mostrarErros(resposta.erro); // fluxograma 01: o que foi digitado fica onde está
    return;
  }
  $("painel-formulario").hidden = true;
  avisar(id ? "Alterações salvas." : "Produto “" + resposta.dados.nome + "” cadastrado.");
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

// ------------------------------------------------------------------------------------------ Nova categoria (L18)

function alternarNovaCategoria() {
  const aberto = $("nova-categoria").hidden;
  $("nova-categoria").hidden = !aberto;
  $("botao-nova-categoria").setAttribute("aria-expanded", String(aberto));
  if (aberto) $("campo-nova-categoria").focus();
}

function fecharNovaCategoria() {
  $("nova-categoria").hidden = true;
  $("botao-nova-categoria").setAttribute("aria-expanded", "false");
  $("campo-nova-categoria").value = "";
  $("campo-nova-categoria-perecivel").checked = false;
  const erro = $("erro-nova-categoria");
  erro.hidden = true;
  $("campo-nova-categoria").removeAttribute("aria-invalid");
}

async function criarCategoria() {
  const resposta = await api.criar("categorias/", {
    nome: $("campo-nova-categoria").value.trim(),
    perecivel_padrao: $("campo-nova-categoria-perecivel").checked,
  });
  const erro = $("erro-nova-categoria");
  if (!resposta.ok) {
    const campos = resposta.erro.campos || {};
    erro.textContent = [].concat(campos.nome || resposta.erro.mensagem).join(" ");
    erro.hidden = false;
    $("campo-nova-categoria").setAttribute("aria-invalid", "true");
    $("campo-nova-categoria").focus();
    return;
  }
  const categorias = await api.ler("categorias/");
  if (categorias.ok) estado.categorias = categorias.dados;
  else estado.categorias = estado.categorias.concat([resposta.dados]); // a criada entra mesmo assim
  preencherCategorias();
  $("campo-categoria").value = resposta.dados.id;
  herdarPerecivelDaCategoria();
  fecharNovaCategoria();
  avisar("Categoria “" + resposta.dados.nome + "” criada.");
  $("campo-categoria").focus();
}

// ------------------------------------------------------------------------------------------ Aviso

let temporizadorDoAviso;
function avisar(mensagem) {
  $("toast-texto").textContent = mensagem;
  $("toast").hidden = false;
  clearTimeout(temporizadorDoAviso);
  temporizadorDoAviso = setTimeout(() => ($("toast").hidden = true), 4000);
}

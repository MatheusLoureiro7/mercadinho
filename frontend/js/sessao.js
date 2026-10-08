/*
 * Sessão do painel — tarefa B7 (tela de Login, L22; RN14).
 *
 * - O token que a API devolve no login (A4) fica no sessionStorage: vale só enquanto a aba estiver
 *   aberta. O computador da loja é compartilhado — fechou o navegador, saiu do sistema.
 * - Sair é descartar o token; não há nada para apagar no servidor (L09).
 * - O menu vem do perfil: a API diz QUAIS telas a pessoa pode abrir (lista `telas` de
 *   /api/sessoes/atual/, montada da tabela da RN14); o painel só sabe o nome e o endereço de cada
 *   uma. A tela não decide acesso — se alguém digitar o endereço de outra tela, a API recusa.
 */

import { api } from "./api.js";

// Chaves = ACESSO_POR_TELA (backend/comum/permissoes.py). Um teste confere que são as mesmas.
// `endereco: null` = tela que ainda não foi feita (a tarefa do cronograma está ao lado).
export const TELAS = {
  produtos: { nome: "Produtos", endereco: "produtos.html" },
  fornecedores: { nome: "Fornecedores", endereco: "fornecedores.html" },
  entrada_mercadoria: { nome: "Entrada de mercadoria", endereco: "entrada-mercadoria.html" },
  avarias: { nome: "Avarias e quebras", endereco: "avarias.html" },
  importacao_vendas: { nome: "Importação de vendas", endereco: null }, // E5
  consulta_estoque: { nome: "Consulta de estoque", endereco: "consulta-estoque.html" },
  fechamento_caixa: { nome: "Fechamento de caixa", endereco: null }, // I2
  balanco_semana: { nome: "Balanço da semana", endereco: null }, // I3
};

const CHAVE_TOKEN = "mercadinho.token";
const CHAVE_USUARIO = "mercadinho.usuario";
const CHAVE_AVISO = "mercadinho.aviso"; // recado para a tela de Login (ex.: "Sua sessão expirou.")

// O armazenamento pode não existir (navegador em modo restrito): o painel avisa no Login.
function guardar(chave, valor) {
  try {
    if (valor === null) sessionStorage.removeItem(chave);
    else sessionStorage.setItem(chave, valor);
    return true;
  } catch (erro) {
    return false;
  }
}

function ler(chave) {
  try {
    return sessionStorage.getItem(chave);
  } catch (erro) {
    return null;
  }
}

export function token() {
  return ler(CHAVE_TOKEN);
}

export function usuario() {
  try {
    return JSON.parse(ler(CHAVE_USUARIO));
  } catch (erro) {
    return null;
  }
}

/** Guarda o que veio de POST /api/sessoes/. Devolve false se o navegador não deixa guardar. */
export function iniciarSessao(resposta) {
  return guardar(CHAVE_TOKEN, resposta.token) && guardar(CHAVE_USUARIO, JSON.stringify(resposta.usuario));
}

/** Sai do sistema e volta para o Login, opcionalmente com um recado ("Sua sessão expirou..."). */
export function sair(aviso) {
  const voltar = paginaAtual();
  guardar(CHAVE_TOKEN, null);
  guardar(CHAVE_USUARIO, null);
  if (aviso) guardar(CHAVE_AVISO, aviso);
  const destino = aviso && voltar !== "login.html" ? "login.html?volta=" + encodeURIComponent(voltar) : "login.html";
  window.location.replace(destino);
}

/** O recado deixado por sair(), lido uma vez só. */
export function lerAviso() {
  const aviso = ler(CHAVE_AVISO);
  guardar(CHAVE_AVISO, null);
  return aviso;
}

/** As telas do papel que já existem no painel, na ordem do menu. */
export function telasProntas(pessoa) {
  return ((pessoa && pessoa.telas) || []).filter((chave) => TELAS[chave] && TELAS[chave].endereco);
}

/** Para onde ir depois do login: a tela pedida (se o perfil pode abrir) ou a primeira do menu. */
export function destinoDepoisDoLogin(pessoa, pedida) {
  const prontas = telasProntas(pessoa);
  const escolhida = prontas.find((chave) => TELAS[chave].endereco === pedida);
  if (escolhida) return TELAS[escolhida].endereco;
  return prontas.length ? TELAS[prontas[0]].endereco : null;
}

function paginaAtual() {
  return window.location.pathname.split("/").pop() || "login.html";
}

/**
 * Abertura de toda tela que exige login. Confere a sessão com a API, monta o menu do perfil e
 * devolve a pessoa — ou null, quando a tela já foi trocada (sem login, sessão vencida, sem acesso).
 */
export async function entrarNaTela(chave) {
  if (!token()) {
    sair("Entre no sistema para continuar.");
    return null;
  }
  const resposta = await api.ler("sessoes/atual/");
  if (!resposta.ok) {
    // 401 já levou ao Login (api.js). Sem conexão: mostra na própria tela, sem perder a sessão.
    if (resposta.status !== 401) mostrarFalhaAoAbrir(resposta.erro);
    return null;
  }
  const pessoa = resposta.dados;
  guardar(CHAVE_USUARIO, JSON.stringify(pessoa));

  if (pessoa.telas.indexOf(chave) < 0) {
    // RN14: a API também recusaria; aqui a pessoa só é levada para uma tela do seu perfil.
    guardar(CHAVE_AVISO, "O seu perfil não tem acesso à tela de " + TELAS[chave].nome + ".");
    window.location.replace(destinoDepoisDoLogin(pessoa, null) || "login.html");
    return null;
  }
  montarCabecalho(pessoa, chave);
  const aviso = lerAviso();
  if (aviso) mostrarRecado(aviso);
  return pessoa;
}

function montarCabecalho(pessoa, chaveAtual) {
  const menu = document.getElementById("menu");
  menu.textContent = "";
  // Só as telas que já existem: as que faltam entram no menu na tarefa que as constrói. Quem ainda
  // não tem nenhuma pronta vê a lista do seu perfil na tela de Login.
  telasProntas(pessoa).forEach((chave) => {
    const tela = TELAS[chave];
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = tela.endereco;
    link.textContent = tela.nome;
    if (chave === chaveAtual) link.setAttribute("aria-current", "page");
    item.append(link);
    menu.append(item);
  });

  document.getElementById("usuario-nome").textContent = pessoa.nome;
  const botaoSair = document.getElementById("botao-sair");
  botaoSair.hidden = false;
  botaoSair.addEventListener("click", () => sair());
}

function mostrarFalhaAoAbrir(erro) {
  const principal = document.getElementById("conteudo");
  const caixa = document.createElement("div");
  caixa.className = "falha";
  caixa.setAttribute("role", "alert");
  const titulo = document.createElement("h1");
  titulo.textContent = "Não foi possível abrir a tela";
  const texto = document.createElement("p");
  texto.textContent = erro.mensagem;
  const botao = document.createElement("button");
  botao.type = "button";
  botao.className = "botao botao--acao";
  botao.textContent = "Tentar de novo";
  botao.addEventListener("click", () => window.location.reload());
  caixa.append(titulo, texto, botao);
  principal.textContent = "";
  principal.append(caixa);
  botao.focus();
}

function mostrarRecado(texto) {
  const recado = document.getElementById("recado");
  if (!recado) return;
  recado.querySelector("span").textContent = texto;
  recado.hidden = false;
}

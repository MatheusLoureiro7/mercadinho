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
import "./tabela-cartoes.js"; // no celular, cada linha de tabela vira um cartão (toda tela com login)

// Chaves = ACESSO_POR_TELA (backend/comum/permissoes.py). Um teste confere que são as mesmas.
// `endereco: null` = tela que ainda não foi feita (a tarefa do cronograma está ao lado).
export const TELAS = {
  produtos: { nome: "Produtos", endereco: "produtos.html" },
  fornecedores: { nome: "Fornecedores", endereco: "fornecedores.html" },
  entrada_mercadoria: { nome: "Entrada de mercadoria", endereco: "entrada-mercadoria.html" },
  avarias: { nome: "Avarias e quebras", endereco: "avarias.html" },
  importacao_vendas: { nome: "Importação de vendas", endereco: "importacao-vendas.html" }, // E5
  consulta_estoque: { nome: "Consulta de estoque", endereco: "consulta-estoque.html" },
  fechamento_caixa: { nome: "Fechamento de caixa", endereco: "fechamento-caixa.html" }, // I2 (API na I1)
  balanco_semana: { nome: "Balanço da semana", endereco: null }, // I3
};

// Ícone de cada tela no menu (SVG no estilo Lucide, traço 2 px, embutido: nada baixado de fora).
const ICONES = {
  produtos: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" /><path d="M3.27 6.96 12 12.01l8.73-5.05" /><path d="M12 22.08V12" />',
  fornecedores: '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2" /><path d="M15 18H9" /><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.62l-3.48-4.35A1 1 0 0 0 17.52 8H14" /><circle cx="17" cy="18" r="2" /><circle cx="7" cy="18" r="2" />',
  entrada_mercadoria: '<path d="M12 3v12" /><path d="m7 10 5 5 5-5" /><path d="M5 21h14" />',
  avarias: '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3" /><path d="M12 9v4" /><path d="M12 17h.01" />',
  importacao_vendas: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" /><path d="M14 2v4a2 2 0 0 0 2 2h4" /><path d="M12 18v-6" /><path d="m9 15 3-3 3 3" />',
  consulta_estoque: '<rect width="8" height="4" x="8" y="2" rx="1" /><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" /><path d="M12 11h4" /><path d="M12 16h4" /><path d="M8 11h.01" /><path d="M8 16h.01" />',
  fechamento_caixa: '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1" /><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4" />',
  balanco_semana: '<path d="M3 3v18h18" /><path d="M18 17V9" /><path d="M13 17V5" /><path d="M8 17v-3" />',
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
    link.innerHTML = '<svg class="icone" viewBox="0 0 24 24" aria-hidden="true">' + (ICONES[chave] || "") + "</svg>";
    link.append(tela.nome);
    if (chave === chaveAtual) link.setAttribute("aria-current", "page");
    item.append(link);
    menu.append(item);
  });

  // No celular o menu desliza para o lado: deixa a aba da tela atual à vista.
  const atual = menu.querySelector('[aria-current="page"]');
  if (atual && menu.scrollWidth > menu.clientWidth) menu.scrollLeft = atual.offsetLeft - menu.offsetLeft - 16;
  document.getElementById("usuario-nome").textContent = pessoa.nome;
  const inicial = document.getElementById("usuario-inicial");
  if (inicial) inicial.textContent = (pessoa.nome.replace(/^Sr\.?\s+/i, "")[0] || "").toUpperCase();
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

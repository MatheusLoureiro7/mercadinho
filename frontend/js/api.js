/*
 * Porta única do painel para a API — tarefa B7.
 *
 * O painel nunca acessa o banco (Apostila IV, seção 3): toda leitura e escrita passa por aqui. A API
 * está na mesma origem do painel (decisão L25), então o caminho é sempre relativo: "/api/...".
 *
 * Toda chamada devolve o mesmo formato, para a tela não precisar olhar código HTTP nem tratar
 * exceção:
 *
 *     { ok: true,  status: 200, dados: {...} }
 *     { ok: false, status: 400, erro: { codigo, mensagem, campos?, regra?, id? } }
 *
 * `erro` é o da API (backend/comum/erros.py). Quando a falha é antes de a API responder (sem rede,
 * demora, resposta que não é JSON), este módulo monta um erro no mesmo formato, com frase da loja.
 */

import { sair, token } from "./sessao.js";

const LIMITE_DE_ESPERA_MS = 20000;

const SEM_CONEXAO = {
  codigo: "sem_conexao",
  mensagem: "Sem conexão com o sistema. Confira se o computador está na rede e tente de novo.",
};
const DEMOROU = {
  codigo: "demorou",
  mensagem: "O sistema demorou demais para responder. Tente de novo em instantes.",
};
const RESPOSTA_ESTRANHA = {
  codigo: "erro_interno",
  mensagem: "Algo deu errado do nosso lado. Tente de novo; se continuar, avise a equipe.",
};

async function pedir(metodo, caminho, corpo) {
  const cabecalhos = { Accept: "application/json" };
  const chave = token();
  if (chave) cabecalhos.Authorization = "Bearer " + chave;
  if (corpo !== undefined) cabecalhos["Content-Type"] = "application/json";

  const controle = new AbortController();
  const relogio = setTimeout(() => controle.abort(), LIMITE_DE_ESPERA_MS);

  let resposta;
  try {
    resposta = await fetch("/api/" + caminho, {
      method: metodo,
      headers: cabecalhos,
      body: corpo === undefined ? undefined : JSON.stringify(corpo),
      signal: controle.signal,
      cache: "no-store",
    });
  } catch (falha) {
    return { ok: false, status: 0, erro: falha.name === "AbortError" ? DEMOROU : SEM_CONEXAO };
  } finally {
    clearTimeout(relogio);
  }

  let dados = null;
  if (resposta.status !== 204) {
    try {
      dados = await resposta.json();
    } catch (falha) {
      return { ok: false, status: resposta.status, erro: RESPOSTA_ESTRANHA };
    }
  }

  if (resposta.ok) return { ok: true, status: resposta.status, dados: dados };

  const erro = (dados && dados.erro) || RESPOSTA_ESTRANHA;
  // Sessão vencida ou inválida (A4): volta ao Login com a frase da API. O login errado também é
  // 401, mas esse a própria tela de Login mostra.
  if (resposta.status === 401 && caminho !== "sessoes/") sair(erro.mensagem);
  return { ok: false, status: resposta.status, erro: erro };
}

function comFiltros(caminho, filtros) {
  const busca = new URLSearchParams();
  Object.keys(filtros || {}).forEach((nome) => {
    const valor = filtros[nome];
    if (valor !== null && valor !== undefined && valor !== "") busca.set(nome, valor);
  });
  const texto = busca.toString();
  return texto ? caminho + "?" + texto : caminho;
}

export const api = {
  /** GET. `caminho` sem o "/api/" do começo: "produtos/", "sessoes/atual/". */
  ler(caminho, filtros) {
    return pedir("GET", comFiltros(caminho, filtros));
  },

  criar(caminho, dados) {
    return pedir("POST", caminho, dados);
  },

  /** Edição de um cadastro: a tela manda o formulário inteiro (PUT, como na API da B2/B3). */
  alterar(caminho, id, dados) {
    return pedir("PUT", caminho + id + "/", dados);
  },
};

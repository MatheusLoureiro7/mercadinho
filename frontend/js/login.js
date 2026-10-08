/*
 * Tela de Login — tarefa B7 (L22). Usada pelos três perfis (RN14).
 *
 * Envia login e senha para POST /api/sessoes/ (A4), guarda o token da sessão e leva a pessoa para a
 * primeira tela do seu menu — ou para a tela que ela tentava abrir quando a sessão expirou.
 *
 * Login errado: a API responde a mesma frase para login inexistente, senha errada ou usuário
 * desativado ("Login ou senha incorretos."), e a tela não aponta qual dos dois campos está errado
 * — dizer qual ajudaria quem tenta adivinhar senha. O login digitado fica; a senha é apagada.
 * Colar e gerenciador de senha são permitidos (WCAG 2.2, 3.3.8).
 */

import { api } from "./api.js";
import { TELAS, destinoDepoisDoLogin, iniciarSessao, lerAviso, sair, token } from "./sessao.js";

const CAMPOS = {
  login: { id: "campo-login", rotulo: "Login", vazio: "Preencha o seu login." },
  senha: { id: "campo-senha", rotulo: "Senha", vazio: "Preencha a sua senha." },
};

const $ = (id) => document.getElementById(id);

document.addEventListener("DOMContentLoaded", iniciar);

async function iniciar() {
  $("formulario").addEventListener("submit", entrar);
  $("botao-ver-senha").addEventListener("click", alternarSenha);
  $("botao-sair-sem-telas").addEventListener("click", () => sair());

  const aviso = lerAviso();
  if (aviso) mostrarRecado(aviso);

  // Já tem sessão aberta nesta aba (ex.: voltou para o Login): confere e segue.
  if (token()) {
    const resposta = await api.ler("sessoes/atual/");
    if (resposta.ok) return seguir(resposta.dados);
  }
  $("campo-login").focus();
}

async function entrar(evento) {
  evento.preventDefault();
  limparErros();

  const dados = { login: $("campo-login").value.trim(), senha: $("campo-senha").value };
  const faltando = Object.keys(CAMPOS).filter((campo) => !dados[campo]);
  if (faltando.length) {
    // Só "preencha": não é regra de negócio, e evita gastar uma das 10 tentativas por minuto.
    const campos = {};
    faltando.forEach((campo) => (campos[campo] = [CAMPOS[campo].vazio]));
    return mostrarErros({ campos: campos });
  }

  const botao = $("botao-entrar");
  botao.disabled = true;
  botao.setAttribute("aria-busy", "true");
  botao.textContent = "Entrando…";

  const resposta = await api.criar("sessoes/", dados);

  botao.disabled = false;
  botao.removeAttribute("aria-busy");
  botao.textContent = "Entrar";

  if (!resposta.ok) {
    if (resposta.status === 401) {
      $("campo-senha").value = "";
      return mostrarErros({ mensagem: resposta.erro.mensagem });
    }
    return mostrarErros(resposta.erro);
  }

  if (!iniciarSessao(resposta.dados)) {
    return mostrarErros({
      mensagem: "Este navegador não deixa o sistema guardar a sua entrada. Saia do modo anônimo e tente de novo.",
    });
  }
  seguir(resposta.dados.usuario);
}

function seguir(pessoa) {
  const pedida = new URLSearchParams(window.location.search).get("volta");
  const destino = destinoDepoisDoLogin(pessoa, pedida);
  if (destino) {
    window.location.replace(destino);
    return;
  }
  mostrarSemTelas(pessoa);
}

function mostrarSemTelas(pessoa) {
  // As telas do perfil estão no cronograma, mas ainda não foram feitas (ex.: Consulta de estoque, F3).
  $("painel-entrada").hidden = true;
  $("titulo-sem-telas").textContent = "Olá, " + pessoa.nome + "!";
  $("texto-sem-telas").textContent =
    "Você entrou no sistema. As telas do seu perfil ainda estão sendo preparadas pela equipe:";
  const lista = $("lista-sem-telas");
  lista.textContent = "";
  pessoa.telas.forEach((chave) => {
    const item = document.createElement("li");
    item.textContent = TELAS[chave] ? TELAS[chave].nome : chave;
    lista.append(item);
  });
  $("painel-sem-telas").hidden = false;
  $("titulo-sem-telas").setAttribute("tabindex", "-1");
  $("titulo-sem-telas").focus();
}

function alternarSenha() {
  const campo = $("campo-senha");
  const mostrar = campo.type === "password";
  campo.type = mostrar ? "text" : "password";
  const botao = $("botao-ver-senha");
  botao.setAttribute("aria-pressed", String(mostrar));
  botao.textContent = mostrar ? "Esconder" : "Mostrar";
  campo.focus();
}

// ------------------------------------------------------------------------------------------ Erros

function mostrarErros(erro) {
  const campos = erro.campos || {};
  const lista = $("lista-de-erros");
  lista.textContent = "";

  Object.keys(campos).forEach((campo) => {
    const mensagem = [].concat(campos[campo]).join(" ");
    const info = CAMPOS[campo];
    const item = document.createElement("li");
    if (info) {
      mostrarErroNoCampo(campo, mensagem);
      const link = document.createElement("a");
      link.href = "#" + info.id;
      link.textContent = info.rotulo + ": " + mensagem;
      link.addEventListener("click", (e) => {
        e.preventDefault();
        $(info.id).focus();
      });
      item.append(link);
    } else {
      item.textContent = mensagem;
    }
    lista.append(item);
  });

  if (!Object.keys(campos).length) {
    const item = document.createElement("li");
    item.textContent = erro.mensagem || "Não foi possível entrar. Tente de novo.";
    lista.append(item);
  }

  const resumo = $("resumo-de-erros");
  resumo.hidden = false;
  resumo.focus();
}

function mostrarErroNoCampo(campo, mensagem) {
  const paragrafo = $("erro-" + campo);
  const entrada = $(CAMPOS[campo].id);
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

function mostrarRecado(texto) {
  const recado = $("recado");
  recado.querySelector("span").textContent = texto;
  recado.hidden = false;
}

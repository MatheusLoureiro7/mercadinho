/*
 * Erros e confirmação de formulário — comum às telas de registro (C5 Entrada, D3 Avarias).
 *
 * `campos` é o mapa da tela: { nome_na_api: { id: "campo-...", rotulo: "..." } }. O erro de cada
 * campo vai no parágrafo "erro-<nome_na_api>", embaixo dele; o resumo no topo recebe o foco e tem
 * um link para cada campo (fluxograma 01: o que foi digitado fica onde está).
 */

const $ = (id) => document.getElementById(id);

export function mostrarErros(campos, erro) {
  const apontados = erro.campos || {};
  const lista = $("lista-de-erros");
  lista.textContent = "";

  Object.keys(apontados).forEach((campo) => {
    const mensagem = [].concat(apontados[campo]).join(" ");
    mostrarErroNoCampo(campos, campo, mensagem);
    const item = document.createElement("li");
    const link = document.createElement("a");
    link.href = "#" + (campos[campo] ? campos[campo].id : "formulario");
    link.textContent = (campos[campo] ? campos[campo].rotulo + ": " : "") + mensagem;
    link.addEventListener("click", (e) => {
      e.preventDefault();
      if (campos[campo]) $(campos[campo].id).focus();
    });
    item.append(link);
    lista.append(item);
  });

  if (!Object.keys(apontados).length) {
    const item = document.createElement("li");
    item.textContent = erro.mensagem || "Não foi possível registrar. Tente de novo.";
    lista.append(item);
  }

  const resumo = $("resumo-de-erros");
  resumo.hidden = false;
  resumo.focus();
}

export function mostrarErroNoCampo(campos, campo, mensagem) {
  const info = campos[campo];
  const paragrafo = $("erro-" + campo);
  if (!info || !paragrafo) return;
  const entrada = $(info.id);
  paragrafo.textContent = mensagem || "";
  paragrafo.hidden = !mensagem;
  if (mensagem) entrada.setAttribute("aria-invalid", "true");
  else entrada.removeAttribute("aria-invalid");
}

export function limparErros(campos) {
  $("resumo-de-erros").hidden = true;
  $("lista-de-erros").textContent = "";
  Object.keys(campos).forEach((campo) => mostrarErroNoCampo(campos, campo, null));
}

/**
 * Apaga o erro de cada campo enquanto a pessoa corrige. Nunca no "blur": sumir o erro ao sair do
 * campo encolhe o formulário no meio do clique em "Registrar", e o clique se perde (achado na B7).
 */
export function apagarErroAoCorrigir(campos) {
  Object.keys(campos).forEach((campo) => {
    $(campos[campo].id).addEventListener("input", () => mostrarErroNoCampo(campos, campo, null));
  });
}

/**
 * Confirmação no topo do formulário (ou esconde, com null). Fica até o próximo registro: não é um
 * aviso flutuante, que cobriria os campos enquanto a pessoa continua registrando (achado na C5).
 */
export function confirmar(mensagem) {
  $("sucesso-texto").textContent = mensagem || "";
  $("sucesso").hidden = !mensagem;
}

export function celula(conteudo, classe) {
  const td = document.createElement("td");
  if (classe) td.className = classe;
  if (conteudo !== undefined) td.textContent = conteudo;
  return td;
}

export function linhaVazia(colunas, titulo, texto) {
  const linha = document.createElement("tr");
  const td = document.createElement("td");
  td.colSpan = colunas;
  td.className = "vazio";
  const forte = document.createElement("strong");
  forte.textContent = titulo;
  td.append(forte, texto);
  linha.append(td);
  return linha;
}

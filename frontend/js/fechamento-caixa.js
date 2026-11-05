/*
 * Tela de Fechamento de caixa — tarefa I2 (RF12, RN15, fluxograma 06). Usada pela esposa (GESTAO,
 * RN14): confere o dinheiro contado contra o apurado no dia.
 *
 * Só o dinheiro contado é digitado. O apurado vem do sistema — a soma das vendas do dia pagas em
 * dinheiro (L12) — e a diferença (contado − apurado) é calculada: aqui, só para mostrar antes de
 * confirmar; quem grava é o banco, numa coluna gerada (RN15). Correção é um registro novo — a tela
 * nunca altera nem apaga.
 *
 * API (tarefa I1):
 *   GET  fechamentos/apurado/                 → { data, valor_sistema } do dia do fechamento
 *   GET  fechamentos/?data=AAAA-MM-DD         → registros do dia, o mais novo primeiro
 *   POST fechamentos/ { valor_contado }        → o registro gravado (data e apurado: o servidor)
 * O fechamento é do dia anterior (L12): as vendas do dia entram às 03h00 do dia seguinte. Se as
 * vendas daquele dia ainda não entraram, a API recusa (RN15) e a tela mostra o motivo e trava.
 */

import { api } from "./api.js";
import { linhaDeFalha } from "./falha.js";
import { dataBrasileira, diaNaLoja, emReais, horaNaLoja } from "./formatos.js";
import { apagarErroAoCorrigir, celula, confirmar, limparErros, linhaVazia, mostrarErroNoCampo, mostrarErros } from "./formulario.js";
import { entrarNaTela } from "./sessao.js";

// Exatamente o que a tela manda para a API. Um teste confere que é o único campo digitado.
const CAMPOS = { valor_contado: { id: "campo-contado", rotulo: "Dinheiro contado" } };
const COLUNAS = 5;

const estado = { hoje: diaNaLoja(), quando: "hoje", apuradoEmCentavos: null };

const $ = (id) => document.getElementById(id);

// ------------------------------------------------------------------------------------------ Início

document.addEventListener("DOMContentLoaded", iniciar);

async function iniciar() {
  if (!(await entrarNaTela("fechamento_caixa"))) return;

  const apurado = await api.ler("fechamentos/apurado/", { data: estado.hoje });
  if (!apurado.ok) {
    travarFormulario();
    const semVendasDoDia = apurado.erro && apurado.erro.regra === "RN15";
    if (apurado.status === 404 || semVendasDoDia) {
      // RN15/L12: sem as vendas do dia no sistema não há apurado para conferir; a API diz qual dia.
      if (semVendasDoDia) $("indisponivel").querySelector("span").textContent = apurado.erro.mensagem;
      $("indisponivel").hidden = false;
      $("valor-apurado").textContent = "—";
      $("corpo-tabela").append(linhaVazia(COLUNAS, "Nenhum fechamento hoje.", ""));
    } else {
      $("valor-apurado").textContent = "—";
      $("corpo-tabela").append(linhaDeFalha(apurado.erro, COLUNAS, () => window.location.reload()));
    }
    return;
  }
  if (apurado.dados.data) estado.hoje = apurado.dados.data; // o dia que vale é o do sistema
  if (estado.hoje === diaNaLoja()) {
    $("data-de-hoje").textContent = " · " + dataBrasileira(estado.hoje);
  } else {
    // L12: o fechamento é do dia anterior — as vendas do dia só entram às 03h00 do dia seguinte.
    estado.quando = "em " + dataBrasileira(estado.hoje);
    $("titulo-formulario").textContent = "Conferir o caixa de " + dataBrasileira(estado.hoje);
    $("titulo-lista").textContent = "Fechamentos de " + dataBrasileira(estado.hoje);
  }
  estado.apuradoEmCentavos = centavos(apurado.dados.valor_sistema);
  $("valor-apurado").textContent = emReais(apurado.dados.valor_sistema);

  $("formulario").addEventListener("submit", registrar);
  $("campo-contado").addEventListener("input", mostrarDiferenca);
  apagarErroAoCorrigir(CAMPOS);
  carregarLista();
  $("campo-contado").focus();
}

function travarFormulario() {
  $("campo-contado").disabled = true;
  $("botao-salvar").disabled = true;
}

// ------------------------------------------------------------------------------------------ Dinheiro

/**
 * "3.215,00", "3215", "3215,5" ou "3215.50" (como a pessoa digita) → "3215.00" (como a API recebe);
 * null se não for um valor em reais (negativo, letras, mais de dois centavos).
 */
function dinheiroParaApi(digitado) {
  const texto = String(digitado || "").replace(/\s|R\$/g, "");
  let reais;
  let resto;
  if (/^\d{1,3}(\.\d{3})+(,\d{1,2})?$/.test(texto) || /^\d+(,\d{1,2})?$/.test(texto)) {
    [reais, resto] = texto.replace(/\./g, "").split(",");
  } else if (/^\d+\.\d{1,2}$/.test(texto)) {
    [reais, resto] = texto.split(".");
  } else {
    return null;
  }
  return String(Number(reais)) + "." + (resto || "").padEnd(2, "0");
}

/** "3240.00" → 324000. Em centavos inteiros: dinheiro nunca passa por conta com float (CLAUDE.md). */
function centavos(textoDaApi) {
  const [reais, resto] = String(textoDaApi).replace("-", "").split(".");
  const valor = Number(reais) * 100 + Number((resto || "").padEnd(2, "0").slice(0, 2));
  return String(textoDaApi).startsWith("-") ? -valor : valor;
}

function reaisDeCentavos(valor) {
  return emReais((Math.abs(valor) / 100).toFixed(2));
}

/** A frase da diferença, com palavra (não só cor — WCAG 1.4.1). */
function fraseDaDiferenca(diferenca) {
  if (diferenca === 0) return { texto: "O caixa bateu.", tipo: "ok" };
  if (diferenca < 0) return { texto: "Faltam " + reaisDeCentavos(diferenca) + " no caixa.", tipo: "erro" };
  return { texto: "Sobram " + reaisDeCentavos(diferenca) + " no caixa.", tipo: "aviso" };
}

function mostrarDiferenca() {
  const contado = dinheiroParaApi($("campo-contado").value);
  const paragrafo = $("diferenca");
  paragrafo.className = "diferenca";
  if (contado === null || estado.apuradoEmCentavos === null) {
    paragrafo.textContent = "";
    return;
  }
  const frase = fraseDaDiferenca(centavos(contado) - estado.apuradoEmCentavos);
  paragrafo.textContent = frase.texto;
  paragrafo.classList.add("diferenca--" + frase.tipo);
}

// ------------------------------------------------------------------------------------------ Registrar

async function registrar(evento) {
  evento.preventDefault();
  limparErros(CAMPOS);
  confirmar(null);

  const digitado = $("campo-contado").value.trim();
  const contado = dinheiroParaApi(digitado);
  if (contado === null) {
    mostrarErros(CAMPOS, {
      campos: {
        valor_contado: [digitado ? "Escreva o valor em reais, por exemplo 3.215,00." : "Informe o dinheiro contado na gaveta."],
      },
    });
    return;
  }

  const botao = $("botao-salvar");
  botao.disabled = true;
  const resposta = await api.criar("fechamentos/", { valor_contado: contado });
  botao.disabled = false;

  if (!resposta.ok) {
    mostrarErros(CAMPOS, resposta.erro); // o que foi digitado fica onde está (fluxograma 01)
    return;
  }
  const registro = resposta.dados;
  confirmar("Fechamento registrado. " + fraseDaDiferenca(centavos(registro.diferenca)).texto);
  // Só limpa se a pessoa não digitou outra contagem enquanto este registro era gravado.
  if ($("campo-contado").value.trim() === digitado) $("campo-contado").value = "";
  mostrarDiferenca();
  await carregarLista();
  $("campo-contado").focus();
}

// ------------------------------------------------------------------------------------------ Lista do dia

async function carregarLista() {
  const corpo = $("corpo-tabela");
  const resposta = await api.ler("fechamentos/", { data: estado.hoje });
  corpo.textContent = "";
  if (!resposta.ok) {
    corpo.append(linhaDeFalha(resposta.erro, COLUNAS, carregarLista));
    return;
  }
  const registros = resposta.dados;
  if (!registros.length) {
    corpo.append(linhaVazia(COLUNAS, "Nenhum fechamento " + estado.quando + ".", "O que você registrar aparece aqui."));
  } else {
    registros.forEach((registro) => corpo.append(linhaDoRegistro(registro)));
  }
  $("anuncio-lista").textContent =
    (registros.length === 1 ? "1 fechamento " : registros.length + " fechamentos ") + estado.quando + ".";
}

function linhaDoRegistro(registro) {
  const linha = document.createElement("tr");
  const hora = document.createElement("th");
  hora.scope = "row";
  hora.textContent = horaNaLoja(registro.registrado_em);

  const diferenca = celula(emReais(registro.diferenca), "numero");
  const frase = fraseDaDiferenca(centavos(registro.diferenca));
  const etiqueta = document.createElement("span");
  etiqueta.className = "etiqueta etiqueta--" + frase.tipo;
  etiqueta.textContent = frase.tipo === "ok" ? "Bateu" : frase.tipo === "erro" ? "Faltou" : "Sobrou";
  diferenca.append(" ", etiqueta);

  linha.append(
    hora,
    celula(emReais(registro.valor_sistema), "numero"),
    celula(emReais(registro.valor_contado), "numero"),
    diferenca,
    celula(registro.registrado_por_nome || "—")
  );
  return linha;
}

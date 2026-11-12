/*
 * Tela de Balanço da semana — tarefa I3 (RF13). Usada pela esposa (GESTAO, RN14), que hoje faz o
 * balanço no caderno.
 *
 * Mostra vendas, perdas e resultado da semana (segunda a domingo), com as perdas separadas das
 * vendas (RN11). A conta é da API (L16): resultado = vendas (a preço de venda) − perdas (a preço de
 * custo). A tela só lê: não grava nada.
 *
 * API:  GET balancos/?semana=AAAA-MM-DD   → a semana que contém o dia; sem o filtro, a de ontem
 */

import { api } from "./api.js";
import { linhaDeFalha } from "./falha.js";
import { dataBrasileira, diaNaLoja, emReais, quantidade } from "./formatos.js";
import { celula, linhaVazia } from "./formulario.js";
import { entrarNaTela } from "./sessao.js";

const DIAS_DA_SEMANA = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"];

const estado = { semana: null, inicio: null };

const $ = (id) => document.getElementById(id);

// ------------------------------------------------------------------------------------------ Datas

/** Soma dias a uma data "AAAA-MM-DD" sem passar pelo fuso do navegador. */
function somarDias(data, dias) {
  const [ano, mes, dia] = data.split("-").map(Number);
  return new Date(Date.UTC(ano, mes - 1, dia + dias)).toISOString().slice(0, 10);
}

function diaEMes(data) {
  return dataBrasileira(data).slice(0, 5);
}

function diaDaSemana(data) {
  const [ano, mes, dia] = data.split("-").map(Number);
  return DIAS_DA_SEMANA[new Date(Date.UTC(ano, mes - 1, dia)).getUTCDay()];
}

function ontem() {
  return somarDias(diaNaLoja(), -1);
}

function emLista(datas) {
  const textos = datas.map(diaEMes);
  return textos.length === 1 ? textos[0] : textos.slice(0, -1).join(", ") + " e " + textos[textos.length - 1];
}

// ------------------------------------------------------------------------------------------ Início

document.addEventListener("DOMContentLoaded", iniciar);

async function iniciar() {
  if (!(await entrarNaTela("balanco_semana"))) return;
  $("botao-anterior").addEventListener("click", () => irPara(-7));
  $("botao-proxima").addEventListener("click", () => irPara(7));
  carregar();
}

function irPara(dias) {
  if (!estado.inicio) return;
  estado.semana = somarDias(estado.inicio, dias);
  carregar().then(() => $("titulo-semana").focus());
}

async function carregar() {
  $("botao-anterior").disabled = true;
  $("botao-proxima").disabled = true;
  const resposta = await api.ler("balancos/", { semana: estado.semana });
  if (!resposta.ok) {
    mostrarFalha(resposta.erro);
    return;
  }
  mostrar(resposta.dados);
}

function mostrarFalha(erro) {
  $("titulo-semana").textContent = "Não foi possível carregar o balanço";
  ["valor-vendas", "valor-perdas", "valor-resultado"].forEach((id) => ($(id).textContent = "—"));
  ["nota-vendas", "nota-perdas"].forEach((id) => ($(id).textContent = ""));
  $("aviso-dias").hidden = true;
  $("aviso-andamento").hidden = true;
  $("aviso-custo").hidden = true;
  $("corpo-vendas").textContent = "";
  $("corpo-perdas").textContent = "";
  $("corpo-vendas").append(linhaDeFalha(erro, 3, carregar));
  $("botao-anterior").disabled = !estado.inicio;
}

// ------------------------------------------------------------------------------------------ Balanço

function mostrar(balanco) {
  estado.inicio = balanco.inicio;
  estado.semana = balanco.inicio;
  $("titulo-semana").textContent = "Semana de " + diaEMes(balanco.inicio) + " a " + dataBrasileira(balanco.fim);
  $("botao-anterior").disabled = false;
  // Não passa da semana de ontem: as vendas de hoje só entram de madrugada.
  $("botao-proxima").disabled = somarDias(balanco.fim, 1) > ontem();

  const andamento = balanco.ate < balanco.fim;
  $("aviso-andamento").hidden = !andamento;
  $("aviso-andamento").textContent = andamento
    ? "Semana em andamento: o balanço vai até " + dataBrasileira(balanco.ate) + ". As vendas de cada dia entram na madrugada seguinte."
    : "";

  const faltam = balanco.dias_sem_vendas;
  $("aviso-dias").hidden = !faltam.length;
  $("aviso-dias").querySelector("span").textContent = !faltam.length
    ? ""
    : "As vendas de " +
      emLista(faltam) +
      " ainda não entraram no sistema, então o balanço está incompleto. Confira se a planilha do caixa foi salva na pasta: ela entra na próxima madrugada.";

  $("valor-vendas").textContent = emReais(balanco.vendas_total);
  $("nota-vendas").textContent = balanco.cupons === 1 ? "1 cupom" : balanco.cupons + " cupons";
  $("valor-perdas").textContent = emReais(balanco.perdas_total);
  $("nota-perdas").textContent =
    balanco.perdas.length === 1 ? "1 produto" : balanco.perdas.length + " produtos";
  $("valor-resultado").textContent = emReais(balanco.resultado);
  $("aviso-custo").hidden = !balanco.perdas_sem_custo;

  mostrarVendas(balanco);
  mostrarPerdas(balanco.perdas);
}

function mostrarVendas(balanco) {
  const corpo = $("corpo-vendas");
  corpo.textContent = "";
  balanco.vendas_por_dia.forEach((dia) => {
    const linha = document.createElement("tr");
    const nome = document.createElement("th");
    nome.scope = "row";
    nome.textContent = diaDaSemana(dia.data) + " " + diaEMes(dia.data);
    // Dia que ainda não acabou, ou cuja planilha não entrou, não mostra zero: zero diria que a
    // loja não vendeu nada.
    const situacao =
      dia.data > balanco.ate ? "ainda não chegou" : balanco.dias_sem_vendas.includes(dia.data) ? "não entrou" : null;
    linha.append(
      nome,
      celula(situacao ? "—" : String(dia.cupons), "numero"),
      celula(situacao || emReais(dia.total), "numero")
    );
    corpo.append(linha);
  });
}

function mostrarPerdas(perdas) {
  const corpo = $("corpo-perdas");
  corpo.textContent = "";
  if (!perdas.length) {
    corpo.append(linhaVazia(3, "Nenhuma perda nesta semana.", ""));
    return;
  }
  perdas.forEach((item) => {
    const linha = document.createElement("tr");
    const nome = document.createElement("th");
    nome.scope = "row";
    nome.textContent = item.produto_nome;
    let valor = item.valor === null ? "sem custo cadastrado" : emReais(item.valor);
    if (item.valor !== null && item.sem_custo) valor += " + parte sem custo cadastrado";
    linha.append(nome, celula(quantidade(item.quantidade, item.unidade_medida), "numero"), celula(valor, "numero"));
    corpo.append(linha);
  });
}

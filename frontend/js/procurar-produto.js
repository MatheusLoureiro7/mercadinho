/*
 * "Procurar o produto" — comum às telas de registro (C5 Entrada, D3 Avarias).
 *
 * O campo #campo-procurar filtra, sem acento, a lista nativa #campo-produto (acessível e leve para
 * até 2.000 produtos). Só escolhe sozinho quando há um único resultado; o número encontrado é
 * anunciado em #anuncio-produtos. A lista de produtos vem da API, carregada uma vez pela tela.
 */

import { semAcento } from "./formatos.js";

const $ = (id) => document.getElementById(id);

export function procurarProduto({ produtos, aoEscolher }) {
  function escolhido() {
    const id = Number($("campo-produto").value);
    return produtos.find((p) => p.id === id) || null;
  }

  function filtrar() {
    const busca = semAcento($("campo-procurar").value.trim());
    const select = $("campo-produto");
    const antes = select.value;
    const encontrados = produtos.filter((p) => !busca || semAcento(p.nome).indexOf(busca) >= 0);

    select.textContent = "";
    select.append(new Option(encontrados.length ? "Escolha…" : "Nenhum produto com esse nome", ""));
    encontrados.forEach((p) => select.append(new Option(p.nome + " — " + p.categoria_nome, p.id)));

    if (encontrados.length === 1) select.value = String(encontrados[0].id);
    else if (encontrados.some((p) => String(p.id) === antes)) select.value = antes;

    $("anuncio-produtos").textContent = !busca
      ? produtos.length === 1
        ? "1 produto na lista."
        : produtos.length + " produtos na lista."
      : encontrados.length === 1
        ? "1 produto encontrado e escolhido: " + encontrados[0].nome + "."
        : encontrados.length + " produtos encontrados. Escolha na lista abaixo.";
    if (select.value !== antes) aoEscolher(escolhido());
  }

  $("campo-procurar").addEventListener("input", filtrar);
  $("campo-produto").addEventListener("change", () => aoEscolher(escolhido()));
  filtrar();
  return { escolhido, filtrar };
}

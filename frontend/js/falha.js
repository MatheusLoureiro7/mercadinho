/*
 * Falha ao carregar uma lista — tarefa B7. Usado pelas telas que mostram tabela.
 *
 * Sem conexão, sistema demorando ou erro do sistema: a tabela diz o que aconteceu (a frase vem de
 * js/api.js ou da própria API) e oferece "Tentar de novo". Nunca mostra a lista vazia, que daria a
 * entender que não há nada cadastrado.
 */

export function linhaDeFalha(erro, colunas, tentarDeNovo) {
  const linha = document.createElement("tr");
  const celula = document.createElement("td");
  celula.colSpan = colunas;
  celula.className = "vazio vazio--falha";
  celula.setAttribute("role", "alert");

  const titulo = document.createElement("strong");
  titulo.textContent = "Não foi possível carregar a lista.";
  const texto = document.createElement("span");
  texto.textContent = erro.mensagem;
  const botao = document.createElement("button");
  botao.type = "button";
  botao.className = "botao botao--secundario";
  botao.textContent = "Tentar de novo";
  botao.addEventListener("click", tentarDeNovo);

  celula.append(titulo, texto, botao);
  linha.append(celula);
  return linha;
}

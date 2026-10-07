/*
 * Formatos brasileiros para a tela: dinheiro, quantidade e números digitados com vírgula.
 * A API recebe e devolve números como texto com ponto ("12.90"), nunca float (CLAUDE.md).
 */

const dinheiro = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

export function emReais(texto) {
  if (texto === null || texto === undefined || texto === "") return "—";
  return dinheiro.format(Number(texto));
}

export function quantidade(texto, unidade) {
  if (texto === null || texto === undefined || texto === "") return "—";
  const numero = Number(texto);
  const casas = unidade === "KG" || unidade === "L" ? 3 : 0;
  const formatado = numero.toLocaleString("pt-BR", { minimumFractionDigits: 0, maximumFractionDigits: casas });
  return unidade ? formatado + " " + unidade : formatado;
}

/** "12,90" ou "1.234,5" (como a pessoa digita) → "12.90" / "1234.5" (como a API recebe). */
export function numeroParaApi(digitado) {
  const texto = String(digitado || "").trim().replace(/\s/g, "");
  if (texto === "") return null;
  if (texto.indexOf(",") >= 0) return texto.replace(/\./g, "").replace(",", ".");
  return texto;
}

/** "12.90" (da API) → "12,90" (para o campo). */
export function numeroParaCampo(daApi) {
  if (daApi === null || daApi === undefined) return "";
  return String(daApi).replace(".", ",");
}

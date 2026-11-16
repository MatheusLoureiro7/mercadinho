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

/**
 * Revisão X1, item 13 (decisão do grupo, 16/11/2026): "1.000" ou "12.500", sem vírgula, pode ser mil
 * (o ponto de milhar do Brasil) ou um com três casas — a tela não adivinha. Recebe { campo: digitado }
 * e devolve null, ou o erro no formato da API ({ campos: { campo: [mensagem] } }) para mostrarErros.
 */
export function numerosAmbiguos(digitados) {
  const campos = {};
  Object.entries(digitados).forEach(([campo, digitado]) => {
    if (/^\d{1,3}(\.\d{3})+$/.test(String(digitado || "").replace(/\s/g, ""))) {
      campos[campo] = ["Não dá para saber se é mil ou um: escreva 1000 para mil, ou 1,5 para um e meio."];
    }
  });
  return Object.keys(campos).length ? { campos: campos } : null;
}

/** "12.90" (da API) → "12,90" (para o campo). */
export function numeroParaCampo(daApi) {
  if (daApi === null || daApi === undefined) return "";
  return String(daApi).replace(".", ",");
}

/** "2026-10-25" (da API) → "25/10/2026". Sem passar por Date, que mudaria o dia pelo fuso. */
export function dataBrasileira(daApi) {
  if (!daApi) return "—";
  const [ano, mes, dia] = String(daApi).split("-");
  return dia + "/" + mes + "/" + ano;
}

/** "Feijão" → "feijao": para procurar na tela sem depender de acento (como a busca da API, B7). */
export function semAcento(texto) {
  return String(texto || "")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase();
}

const DIA_NA_LOJA = new Intl.DateTimeFormat("en-CA", { timeZone: "America/Sao_Paulo" }); // AAAA-MM-DD
const HORA_NA_LOJA = new Intl.DateTimeFormat("pt-BR", { timeZone: "America/Sao_Paulo", hour: "2-digit", minute: "2-digit" });

/**
 * "Hoje" no dia da loja (São Paulo), como a API o calcula (CLAUDE.md). Só para filtrar a lista do
 * dia: quem grava a data é sempre a API. `momento` opcional: o dia da loja de um data_hora da API.
 */
export function diaNaLoja(momento) {
  return DIA_NA_LOJA.format(momento ? new Date(momento) : new Date());
}

/** "2026-10-08T14:32:10-03:00" (da API) → "14:32", no horário da loja. */
export function horaNaLoja(momento) {
  return HORA_NA_LOJA.format(new Date(momento));
}

/*
 * Situação de um lote, em palavra e cor (WCAG 1.4.1: nunca só a cor) — comum a Avarias (D3) e à
 * Consulta de estoque (F3). A situação vem pronta da API (F2: VENCIDO, VENCENDO, OK,
 * SEM_VALIDADE, com dias_para_vencer); a tela só a escreve. Cores do sistema de design (MASTER.md).
 */

export function etiquetaDaSituacao(lote) {
  const etiqueta = document.createElement("span");
  const dias = Math.abs(lote.dias_para_vencer);
  const plural = dias === 1 ? " dia" : " dias";
  const situacoes = {
    VENCIDO: ["erro", "Vencido há " + dias + plural],
    VENCENDO: ["aviso", lote.dias_para_vencer === 0 ? "Vence hoje" : "Vence em " + dias + plural],
    OK: ["ok", "Dentro da validade"],
    SEM_VALIDADE: ["neutra", "Sem validade"],
  };
  const [tipo, texto] = situacoes[lote.situacao] || ["neutra", lote.situacao];
  etiqueta.className = "etiqueta etiqueta--" + tipo;
  etiqueta.textContent = texto;
  return etiqueta;
}

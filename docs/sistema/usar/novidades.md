# Novidades para quem usa (release notes)

*Atualizado em 16/11/2026.* O que mudou no dia a dia de cada pessoa, da mais nova para a mais
antiga. A lista técnica, com as mudanças no banco, está em `evoluir/changelog.md`.

## Versão 0.4.0 — 16/11/2026
Revisão geral do sistema antes da entrega: 22 pontos corrigidos. O que muda no dia a dia:

- **Todos:** a **Consulta de estoque** ganhou a coluna **Quando acaba** ("Em 12 dias", "Amanhã",
  "Acabou"); produto novo aparece como "Ainda aprendendo". Número digitado como "1.000" agora é
  recusado com a pergunta "é mil ou um?", em vez de gravar 1 no lugar de mil.
- **Esposa:** o **Fechamento de caixa** tem o campo **Dia do caixa**: dá para fechar o sábado na
  segunda. "Espécie" passou a contar como dinheiro. Se a planilha do caixa vier sem a forma de
  pagamento, o fechamento daquele dia é recusado, com a explicação.
- **Sobrinho:** na **Importação de vendas**, a tela **confirma antes de ligar** a venda a um produto
  (não tem como desfazer). A planilha pode ter qualquer nome e mais de um dia; o mesmo dia nunca entra
  duas vezes. Uma linha fora do formato faz a planilha inteira não entrar: corrija e salve de novo.
  Não dá mais para cadastrar "Arroz 5 kg" e "arroz 5 KG" como dois produtos.
- **Sr. João:** depois do "Sim, pedir", se a mercadoria não chegar no prazo do fornecedor, o aviso
  volta com "O pedido ainda não chegou". Produto sem fornecedor avisa quando acaba. Produto parado e
  zerado não avisa mais todo dia. Mensagem grande não chega repetida.
- **Equipe:** se o computador estava desligado às 03h00, a rodada acontece sozinha assim que ele liga.

## Versão 0.3.1 — 13/11/2026
- **Sugestão de compra em número inteiro** para produto vendido por unidade ou pacote: o aviso dizia
  "Pedir 14,531 PCT"; agora diz "Pedir 15 PCT".
- O sistema passa a ser colocado no ar por um comando só, que antes roda todos os testes.

## Versão 0.3.0 — 12/11/2026
- **Sr. João:** chega o aviso **"vai acabar"** com a quantidade sugerida e o botão **Sim, pedir**;
  na quinta-feira, o aviso dos produtos que não podem faltar no fim de semana. Depois do "Sim,
  pedir", o produto não é avisado de novo até a mercadoria chegar. Tudo na rodada das 03h00.
- **Sobrinho:** nova tela **Importação de vendas**, para conferir a venda que o caixa escreveu com
  outro nome e acompanhar as planilhas lidas.
- **Esposa:** nova tela **Balanço da semana**, com vendas, perdas separadas e resultado.
- **Equipe:** produtos e contagem de partida entram por planilha do Excel.

## Versão 0.2.0 — 05/11/2026
- As vendas do caixa passam a entrar no sistema pela planilha do Excel, toda madrugada, e saem do
  estoque pelo lote que vence primeiro.
- **Esposa:** o **Fechamento de caixa** grava de verdade, com o apurado vindo das vendas.

## Versão 0.1.0 — 09/10/2026
- Primeira versão: Login com três perfis; **Produtos**, **Fornecedores**, **Entrada de
  mercadoria**, **Avarias e quebras** e **Consulta de estoque**; painel funcionando também no celular.
- **Sr. João:** aviso de **validade** pelo Telegram, agrupado numa mensagem só e fora dos horários
  de movimento.

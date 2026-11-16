# Formato da planilha de vendas do caixa

Tarefa **E1** · decidido pelo grupo em **05/11/2026** · base: decisão D01 (o caixa exporta em
Excel), operação 04 da Apostila IV e tabelas `venda`, `item_venda` e `importacao_pdv`.

Exemplo pronto: `docs/exemplos/vendas-2026-11-05.xlsx`.

---

## O arquivo

| Item | Definição |
|---|---|
| Tipo | Planilha do Excel, `.xlsx`, lida direto pelo sistema (biblioteca `openpyxl`) |
| Quantos | **Um arquivo por dia** de vendas |
| Aba | A primeira aba da planilha |
| Linha 1 | Cabeçalho com os nomes das colunas abaixo |
| Demais linhas | **Uma linha por produto vendido.** Linhas com o mesmo número de cupom formam uma venda |

## As colunas

| Coluna | Obrigatória | Formato | Exemplo | Vai para |
|---|---|---|---|---|
| **Cupom** | sim | número do cupom no caixa | `1021` | agrupa as linhas numa `venda` |
| **Data** | sim | dd/mm/aaaa | `05/11/2026` | `venda.data_hora` e `importacao_pdv.data_referencia` |
| **Hora** | sim | hh:mm | `08:14` | `venda.data_hora` (horário de São Paulo) |
| **Produto** | sim | nome do produto **como está no cadastro** | `Arroz 5 kg` | `item_venda.produto_id` (ver abaixo) |
| **Quantidade** | sim | maior que zero, até 3 casas | `1,275` | `item_venda.quantidade` |
| **Preço unitário** | sim | em reais, 2 casas | `15,90` | `item_venda.preco` |
| **Pagamento** | não | texto, até 30 letras | `PIX` | `venda.forma_pagamento` |

O nome das colunas é procurado no cabeçalho sem diferenciar maiúscula de minúscula nem acento; a
ordem das colunas não importa.

## Como cada linha vira dado no sistema

- **Venda:** cada cupom vira uma linha em `venda`. O valor total é a **soma de quantidade × preço
  unitário** dos itens do cupom, arredondada nos centavos (a planilha não traz total).
- **Produto — decisão do grupo sobre a lacuna L05:** o produto é encontrado **pelo nome**,
  comparado sem diferenciar maiúscula, acento nem espaços a mais. Não se cria coluna nova em
  `produto`: o modelo de dados da Apostila IV não muda.
- **Linha que não casou com nenhum produto** fica gravada em `item_venda` **sem produto**, pendente
  de revisão na tela de importação (E5), e **não trava as demais** (operação 04, passo 6).
- **Baixa no estoque:** só as linhas que casaram geram `movimentacao` tipo `VENDA`, saindo do lote
  de validade mais próxima (RN01, RN02).
- **Importar duas vezes — decisão do grupo, 16/11/2026 (revisão X1, item 1):** as vendas são
  reconhecidas **pelo dia**, não pelo nome do arquivo. Linha de um dia que já entrou é ignorada; se
  a planilha inteira for de dias que já entraram, ela é recusada e não deixa registro. O caixa pode
  gravar sempre o mesmo nome (`vendas.xlsx`): o arquivo regravado depois da última leitura é lido.
- **Situação da importação:** `OK` se todas as linhas foram lidas e casaram; `PARCIAL` se alguma
  ficou pendente (produto não reconhecido); `ERRO` se o arquivo não pôde ser lido (não é `.xlsx` ou
  falta coluna obrigatória) **ou se alguma linha não pôde ser lida** (data, hora, quantidade ou
  preço fora do formato) — e aí nada da planilha entra.
- **Linha que não pode ser lida — decisão do grupo, 16/11/2026 (revisão X1, item 2):** antes, a
  planilha entrava `PARCIAL` sem essa linha, e a venda dela sumia do apurado do fechamento de caixa
  (RN15), sem conserto, porque o dia já estava importado. Agora a planilha inteira é recusada; o
  número da linha e o motivo ficam no registro da rodada. Corrigida e salva de novo, ela entra.

## Diferenças em relação ao texto da Apostila IV

Registradas aqui para o professor não achar divergência sem explicação:

| Apostila IV diz | Decisão do grupo (05/11/2026) | Por quê |
|---|---|---|
| Comunicação nº 5: "arquivo de texto" | Planilha `.xlsx` | D01: o caixa exporta em Excel |
| Operação 04, passo 5: "procura o produto pelo código do caixa" | Procura pelo **nome** do produto | L05: a tabela `produto` não tem código do caixa; criar a coluna mudaria o modelo de dados entregue |

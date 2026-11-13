# Glossário de negócio

*Atualizado em 13/11/2026.* Os termos que aparecem nas telas e nos avisos, e as contas que o
sistema faz. Os números entre parênteses (RN, RF) apontam a regra na especificação; os valores
ajustáveis ficam na tabela de parâmetros.

## Estoque

| Termo | O que é |
|---|---|
| **Saldo** | Quanto existe de um produto. Nunca é digitado: é a soma de tudo o que entrou menos tudo o que saiu (RN01). |
| **Lote** | Cada mercadoria que chegou, com quantidade, custo e validade. O saldo do produto é a soma dos lotes. |
| **Perecível** | Produto que estraga. Precisa dizer quantos dias dura (**durabilidade**) (RN03). |
| **Validade** | Data da embalagem. Sem ela, num perecível, o sistema usa a data de entrada + durabilidade (RN04). |
| **Vence primeiro, sai primeiro** | A venda e a perda saem do lote de validade mais próxima (RN02). Lote vencido não sai por venda, só por perda (RN16). |
| **Perda (avaria)** | O que venceu, quebrou ou estragou. Tira do estoque, sempre com motivo, e **não conta como venda** (RN11). |
| **Estoque mínimo** | Quantidade abaixo da qual o produto aparece destacado na consulta. |
| **Contagem de partida** | A contagem física que dá o estoque inicial, lançada como entrada de mercadoria (J3). |

## Vendas

| Termo | O que é |
|---|---|
| **Planilha do caixa** | O arquivo do Excel que o caixa exporta, uma por dia (D01). O sistema só lê; nunca escreve no caixa. |
| **Rodada da madrugada** | O trabalho automático das 03h00: importa as vendas, calcula a previsão, gera e envia os avisos. |
| **Venda para conferir** | Linha da planilha cujo produto não foi reconhecido pelo nome; o sobrinho escolhe o produto (L26). |
| **Consumo** | Quanto o produto vendeu num dia. Só venda conta; perda nunca (RN11). |

## Previsão

| Termo | Conta |
|---|---|
| **Consumo médio diário** | Vendido nos últimos 30 dias ÷ 30 — sempre 30, mesmo que tenha vendido em menos dias (RN06). |
| **Consumo por dia da semana** | A média de cada dia (segunda, terça…). Quando a de um dia chega a **1,5 vez** a média geral, a previsão daquele dia usa a do dia — é assim que o sábado da cerveja conta (RN07, L02). |
| **Dias até acabar** | O estoque gasto dia a dia com o consumo de cada dia, a partir de hoje. "Acaba em 2 dias" conta só os dias inteiros. |
| **Ainda aprendendo** | Produto com menos de **14 dias** de venda: o sistema não mostra número (RN09). |
| **Estoque de segurança** | Folga de **20%** sobre o que se vende no prazo de entrega. |
| **Ponto de pedido** | Média × prazo de entrega do fornecedor × 1,2. Estoque igual ou abaixo dele gera o aviso "vai acabar" (RN08). Exemplo: 8 kg/dia × 3 dias = 24, + 20% = 28,8 kg. |
| **Sugestão de compra** | O que o produto vai vender no prazo de entrega **+ 7 dias**, menos o estoque; nunca negativa; em unidade ou pacote, arredondada para cima (RF11, L15). |
| **Crítico de fim de semana** | Produto que não pode faltar no sábado e no domingo (carne, carvão, cerveja, linguiça, asinha). Na quinta-feira é avaliado com **40%** de folga no ponto de pedido (RN10). Véspera de feriado não é avaliada nesta versão (L03). |

## Avisos

| Termo | O que é |
|---|---|
| **Aviso de validade** | Lote de perecível a 3 dias ou menos do vencimento, com mercadoria (RN05). |
| **Aviso "vai acabar"** | Estoque no ponto de pedido ou abaixo (RN08). Tem o botão **Sim, pedir**. |
| **Aviso de fim de semana** | O de quinta-feira para os críticos (RN10). |
| **Horário de movimento (janela de silêncio)** | 10h30–13h00 e 16h30–18h00: nada é enviado; o aviso sai no fim do horário (RN12). |
| **Mensagem agrupada** | Todos os avisos de uma vez numa mensagem só, do mais urgente para o menos (RN13). |
| **Urgência** | Alta, média ou baixa (L11). "Vai acabar" é alta quando acaba antes de a entrega chegar. |

## Caixa e gestão

| Termo | O que é |
|---|---|
| **Apurado** | Soma das vendas do dia pagas em dinheiro, segundo a planilha do caixa (L12). |
| **Contado** | O dinheiro que a esposa contou na gaveta. |
| **Diferença** | Contado − apurado, calculada pelo sistema e nunca digitada nem corrigida (RN15). |
| **Resultado da semana** | Vendas − perdas a preço de custo (L16). Não é lucro: o custo da mercadoria vendida não entra. |

## Perfis (RN14)

| Perfil | Quem | Faz |
|---|---|---|
| DONO | Sr. João | Recebe os avisos; consulta o estoque |
| GESTAO | Esposa | Fechamento de caixa, balanço, consulta |
| OPERACAO | Sobrinho | Cadastros, entrada, avarias, importação, consulta |

## Parâmetros (ajustáveis na tabela `parametro`)

| Parâmetro | Valor | Regra |
|---|---|---|
| Antecedência do aviso de validade | 3 dias | RN05 |
| Estoque de segurança | 20% | RN08 |
| Horários de movimento | 10:30–13:00 e 16:30–18:00 | RN12 |
| Histórico mínimo | 14 dias | RN09 |
| Folga de fim de semana | 40% | RN10 |
| Hora da rodada | 03:00 | G5 |

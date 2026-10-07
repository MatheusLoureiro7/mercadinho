# previsao Specification

## Purpose

Estimar quanto sai de cada produto por dia, em quantos dias ele acaba e quando pedir, num processo
agendado que roda sozinho às 03h00 — nunca no clique do usuário. Origem: RF08, RF11, RN06, RN07,
RN08, RN09, RN11. Tarefas G1 a G5.

**Depende da decisão D01**: sem vendas importadas não existe consumo.

## Requirements

### Requirement: Consumo diário só com vendas

A rotina diária SHALL agregar em `consumo_diario` apenas movimentações `tipo = 'VENDA'`, gravando a
quantidade vendida e o dia da semana. Movimentações `PERDA` MUST ficar de fora. (RN11; operação 03,
passo 3; tarefa G1)

#### Scenario: Dia com venda e perda
- **WHEN** num dia há 6 kg de frango vendidos e 10 kg de perda
- **THEN** `consumo_diario` daquele dia registra 6 kg

### Requirement: Consumo médio diário

O consumo médio diário SHALL ser o total vendido nos últimos 30 dias dividido por 30 — sempre por
30, não pelo número de dias com venda. (RN06)

#### Scenario: Arroz
- **WHEN** foram vendidos 150 kg de arroz nos últimos 30 dias e há 20 kg em estoque
- **THEN** o consumo médio é 5 kg/dia
- **AND** o arroz acaba em 4 dias

#### Scenario: Venda em poucos dias
- **WHEN** um produto vendeu 30 unidades em apenas 5 dos últimos 30 dias
- **THEN** o consumo médio é 1 unidade/dia

### Requirement: Consumo por dia da semana

O sistema SHALL calcular também a média por dia da semana e usar a maior das duas na projeção
quando a diferença entre elas for relevante. (RN07)

O critério de "diferença relevante" não está definido (docs/LACUNAS.md, L02).

#### Scenario: Cerveja no fim de semana
- **WHEN** a cerveja tem média geral de 8 un/dia e 26 un aos sábados
- **THEN** a projeção para o sábado usa o número do sábado, não a média geral

### Requirement: Ponto de pedido

O ponto de pedido SHALL ser `consumo_medio_diario × prazo_entrega_dias + estoque_seguranca`, com
`estoque_seguranca = consumo_medio_diario × prazo_entrega_dias × estoque_seguranca_pct / 100`,
gravado em `previsao_produto.ponto_pedido`. (RN08)

#### Scenario: Carne
- **WHEN** a carne sai 8 kg/dia, o fornecedor entrega em 3 dias e o parâmetro de segurança é 20 %
- **THEN** o ponto de pedido é 28,8 kg

### Requirement: Histórico mínimo para prever

Com menos dias de histórico de vendas que o parâmetro `historico_minimo_dias` (14), o sistema MUST
NOT apresentar número de previsão: `calculado_em` fica nulo e a tela mostra "ainda aprendendo".
(RN09)

#### Scenario: Produto novo
- **WHEN** um produto tem 6 dias de histórico
- **THEN** a tela mostra "ainda aprendendo", e não "acaba em 2 dias"

#### Scenario: Produto com histórico suficiente
- **WHEN** um produto tem 14 dias ou mais de histórico
- **THEN** a previsão é calculada e `calculado_em` é preenchido

### Requirement: Sugestão de compra

O sistema SHALL indicar a quantidade a pedir de cada produto, considerando o prazo do fornecedor,
em `previsao_produto.sugestao_compra`. (RF11)

A fórmula não está especificada (docs/LACUNAS.md, L15).

#### Scenario: Produto com previsão
- **WHEN** a previsão de um produto é calculada
- **THEN** `sugestao_compra` é gravada junto

### Requirement: Rodada diária agendada

Previsão e regras SHALL rodar num processo agendado às 03h00 (parâmetro `hora_rodada_diaria`), na
ordem importação → previsão → regras → notificação, e MUST NOT rodar no clique do usuário.
(Apostila IV, seção 4; tarefa G5)

#### Scenario: Ordem da rodada
- **WHEN** a rodada diária dispara
- **THEN** a previsão só começa depois que a importação terminou

# estoque Specification

## Purpose

Manter o saldo sempre explicável pelas movimentações, tirar a venda do lote de validade mais
próxima, bloquear lote vencido e permitir consultar o estoque. Origem: RN01, RN02, RN16, RF05, RF07.
Tarefas C4, F1, F2, F3.

## Requirements

### Requirement: Saldo derivado das movimentações

O saldo de um produto SHALL ser sempre `Σ ENTRADA + Σ AJUSTE − Σ VENDA − Σ PERDA` das suas
movimentações, exposto pela view `vw_estoque_atual`. Nenhuma tela, processo ou usuário MUST
escrever um valor de saldo diretamente, e toda operação que muda o estoque SHALL gravar uma linha
em `movimentacao` explicando o porquê. (RN01)

#### Scenario: Exemplo da Apostila I
- **WHEN** um produto recebe entrada de 40 kg, venda de 12 kg e perda de 3 kg
- **THEN** o saldo é 25 kg
- **AND** as três movimentações aparecem no histórico

#### Scenario: Produto sem movimentação
- **WHEN** um produto acabou de ser cadastrado
- **THEN** o saldo é 0

### Requirement: Baixa por venda em ordem de validade (FIFO)

Na baixa por venda, a quantidade SHALL sair do lote com a data de validade mais próxima entre os
lotes disponíveis daquele produto — nunca pelo id nem pela data de entrada. Se a quantidade vendida
for maior que o lote, consome o lote inteiro e continua no próximo, sempre por validade.
(RN02, RF05)

O desempate entre lotes com a mesma validade e a posição dos lotes sem validade não estão
especificados (docs/LACUNAS.md, L13).

#### Scenario: Dois lotes de presunto
- **WHEN** há um lote de presunto que vence em 28/09 e outro que vence em 05/10, e são vendidos 2 kg
- **THEN** os 2 kg saem do lote de 28/09

#### Scenario: Venda maior que o lote mais próximo
- **WHEN** o lote mais próximo do vencimento tem menos que a quantidade vendida
- **THEN** ele é zerado e o restante sai do lote seguinte por validade

### Requirement: Lote vencido é bloqueado para venda

Lote com data de validade anterior à data atual SHALL ficar fora da seleção FIFO de venda. A saída
de lote vencido MUST ser possível apenas registrando perda. (RN16)

#### Scenario: Iogurte vencido
- **WHEN** em 21/09 existe um lote de iogurte vencido em 20/09
- **THEN** ele não pode ser baixado por venda
- **AND** pode sair pela tela de avarias, com motivo

#### Scenario: Lote que vence hoje
- **WHEN** a validade do lote é a data de hoje
- **THEN** o lote ainda pode ser baixado por venda

### Requirement: Consulta de estoque

A consulta de estoque SHALL mostrar o saldo por produto e por categoria, por lote, com destaque para
o que está abaixo do estoque mínimo, o que está perto de vencer e os lotes vencidos. Está disponível
aos três perfis. (RF07, RN16; tela Consulta de estoque)

#### Scenario: Produto abaixo do mínimo
- **WHEN** o saldo de um produto é menor que o seu `estoque_minimo`
- **THEN** o produto aparece destacado na consulta

#### Scenario: Lote vencido destacado
- **WHEN** um lote tem validade anterior a hoje
- **THEN** o lote aparece destacado na consulta

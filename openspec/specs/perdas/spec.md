# perdas Specification

## Purpose

Registrar o que venceu, quebrou ou estragou, sempre com motivo, sem que a perda seja confundida
com venda. Origem: RF04, RN01, RN11, RN16; fluxograma 03. Tarefas D1 a D4.

## Requirements

### Requirement: Perda com motivo obrigatório

O registro de perda SHALL gravar uma `movimentacao` com `tipo = 'PERDA'` e o motivo preenchido,
reduzindo o saldo do produto e a `quantidade_atual` do lote. Perda sem motivo MUST ser recusada.
(RF04; tarefa D1; restrição `ck_mov_perda_motivo`)

#### Scenario: Perda com motivo
- **WHEN** o sobrinho registra 10 kg de frango estragado com o motivo "estragou no balcão"
- **THEN** o saldo do frango cai 10 kg

#### Scenario: Perda sem motivo
- **WHEN** o sobrinho tenta registrar uma perda com o motivo vazio
- **THEN** o registro é recusado

### Requirement: Perda não conta como consumo

Movimentações `PERDA` SHALL reduzir o estoque, mas MUST ser excluídas da base de cálculo de consumo
e de previsão. (RN11; tarefa D2)

#### Scenario: Frango que foi fora
- **WHEN** num dia são vendidos 6 kg de frango e 10 kg vão fora
- **THEN** o saldo cai 16 kg
- **AND** o consumo do dia é 6 kg

### Requirement: Perda ignora o bloqueio de lote vencido

O registro de perda SHALL aceitar lote vencido — é por ele que o lote vencido sai do estoque.
(RN16)

#### Scenario: Iogurte vencido sai como perda
- **WHEN** um lote de iogurte vencido é registrado como perda com motivo
- **THEN** a perda é aceita e o lote é baixado

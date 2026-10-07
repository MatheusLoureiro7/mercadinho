# entrada-mercadoria Specification

## Purpose

Registrar cada carga que chega como um lote, com quantidade, custo, fornecedor e validade, e a
movimentação que explica o aumento do saldo. Origem: RF03, RN01, RN04 (Apostilas I e III);
fluxograma 02 (Apostila II); operação 02 (Apostila IV). Tarefas C1, C2, C3, C5, C6.

## Requirements

### Requirement: Entrada gera lote e movimentação na mesma transação

Toda entrada de mercadoria SHALL gravar um `lote` e uma `movimentacao` com `tipo = 'ENTRADA'` numa
única transação. Se a segunda gravação falhar, a primeira MUST ser desfeita — nunca existe lote sem
a movimentação que explica o saldo. (RN01; operação 02, passos 6 a 8)

#### Scenario: Entrada válida
- **WHEN** o sobrinho registra a chegada de 40 kg de um produto
- **THEN** um lote com `quantidade_inicial` e `quantidade_atual` de 40 kg é gravado
- **AND** uma movimentação `ENTRADA` de 40 kg é gravada
- **AND** a API responde `201`

#### Scenario: Falha na gravação da movimentação
- **WHEN** a gravação da movimentação falha depois do lote ter sido inserido
- **THEN** o lote também não fica gravado

### Requirement: Validade obrigatória e cálculo automático

Na entrada de um lote, a validade SHALL ser tratada nesta ordem (RN04):

1. produto não perecível → validade opcional;
2. produto perecível com validade informada → usa a informada;
3. produto perecível sem validade → `data_validade = data_entrada + durabilidade_dias`;
4. validade (informada ou calculada) anterior a hoje → recusa.

Mensagem da recusa: "Essa validade já passou. Confira a data na embalagem."

A origem da validade na operação real ainda depende da decisão D02.

#### Scenario: Perecível sem validade recebe validade calculada
- **WHEN** entra frango em 21/09 sem validade e o produto tem durabilidade de 4 dias
- **THEN** o lote é gravado com validade 25/09

#### Scenario: Perecível com validade informada
- **WHEN** entra um lote de perecível com validade informada no futuro
- **THEN** o lote é gravado com a validade informada

#### Scenario: Validade no passado é recusada
- **WHEN** entra um lote com validade anterior à data de hoje
- **THEN** a entrada é recusada com a mensagem da RN04
- **AND** nem lote nem movimentação são gravados

#### Scenario: Não perecível sem validade
- **WHEN** entra um lote de produto não perecível sem validade
- **THEN** o lote é gravado sem validade

### Requirement: Entrada cancela aviso de ruptura pendente

Depois de confirmada a entrada, o sistema SHALL cancelar o aviso de ruptura pendente daquele
produto, se houver. (Operação 02, passo 10)

#### Scenario: Havia aviso de ruptura pendente
- **WHEN** chega mercadoria de um produto com aviso `RUPTURA` em `PENDENTE`
- **THEN** o aviso passa para `CANCELADO`

#### Scenario: Não havia aviso pendente
- **WHEN** chega mercadoria de um produto sem aviso pendente
- **THEN** nenhum aviso é alterado

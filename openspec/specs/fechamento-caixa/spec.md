# fechamento-caixa Specification

## Purpose

Comparar o dinheiro contado no fim do dia com o valor apurado pelo sistema e registrar a diferença,
sem nunca apagar ou corrigir um registro. Origem: RF12, RN15; fluxograma 06. Tarefas I1 e I2.

## Requirements

### Requirement: Diferença calculada e registrada

O fechamento SHALL gravar `valor_sistema`, `valor_contado`, a data e o responsável. A diferença
MUST ser calculada pelo banco (`valor_contado − valor_sistema`, coluna gerada) e nunca digitada.
Acesso apenas do perfil `GESTAO`. (RN15, RF12, RN14)

A origem exata de `valor_sistema` não está especificada (docs/LACUNAS.md, L12).

#### Scenario: Falta no caixa
- **WHEN** o sistema apura R$ 3.240,00 e a contagem dá R$ 3.215,00
- **THEN** é gravado um registro com diferença de −R$ 25,00, a data e o responsável

#### Scenario: Caixa bate
- **WHEN** o valor contado é igual ao apurado
- **THEN** é gravado um registro com diferença zero

### Requirement: Registro nunca é alterado nem apagado

A API SHALL aceitar apenas inclusão em `fechamento_caixa`. Correção MUST gerar um novo registro; o
anterior nunca é apagado nem sobrescrito. (RN15)

#### Scenario: Tentativa de corrigir
- **WHEN** alguém tenta alterar ou apagar um fechamento já gravado
- **THEN** a operação é recusada

#### Scenario: Correção por novo registro
- **WHEN** a esposa registra uma nova contagem para o mesmo dia
- **THEN** existem dois registros para o dia, e o primeiro continua intacto

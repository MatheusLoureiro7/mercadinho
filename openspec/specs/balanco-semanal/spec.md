# balanco-semanal Specification

## Purpose

Substituir o balanço da semana feito no caderno: vendas, perdas e resultado do período, com as
perdas separadas das vendas. Origem: RF13, RN11. Tarefa I3.

## Requirements

### Requirement: Balanço com perdas separadas

O relatório de balanço SHALL mostrar, para o período, as vendas, as perdas e o resultado, com as
perdas em linha separada das vendas. Acesso apenas do perfil `GESTAO`. (RF13, RN11, RN14)

A fórmula do "resultado do período" não está especificada (docs/LACUNAS.md, L16).

#### Scenario: Semana com vendas e perdas
- **WHEN** a esposa abre o balanço de uma semana que teve vendas e perdas
- **THEN** as perdas aparecem numa linha própria
- **AND** não são somadas às vendas

# importacao-vendas Specification

## Purpose

Trazer para o sistema o que foi vendido, a partir do arquivo que o caixa da loja exporta, e dar
baixa no estoque. O sistema nunca chama nem escreve no caixa. Origem: RF05, RF06, RN01, RN02, R05;
fluxograma 04; operação 04. Tarefas E1 a E5.

**Depende da decisão D01** (o caixa exporta arquivo? em que formato?). Enquanto ela estiver aberta,
o leitor fica atrás de uma interface, com implementação de exemplo apenas para teste.

## Requirements

### Requirement: Leitura do arquivo do caixa atrás de uma interface

O importador SHALL ler o arquivo do caixa por meio de uma interface (`LeitorDeArquivoDoCaixa`,
`ler(caminho) -> list[LinhaDeVenda]`). O parser do formato real MUST NOT ser escrito antes da
resposta da decisão D01. (docs/DECISOES-PENDENTES.md)

#### Scenario: Leitor de exemplo em teste
- **WHEN** os testes rodam com o leitor de exemplo
- **THEN** o importador processa as linhas sem conhecer o formato real do caixa

### Requirement: Registro da importação

Cada importação SHALL ser registrada em `importacao_pdv` com `status = 'PENDENTE'` ao começar e
terminar como `OK` quando todas as linhas casarem, ou `PARCIAL` quando alguma ficar pendente.
(Operação 04, passos 2 e 9)

#### Scenario: Todas as linhas casam
- **WHEN** todas as linhas do arquivo correspondem a produtos cadastrados
- **THEN** a importação termina com status `OK`

#### Scenario: Alguma linha não casa
- **WHEN** pelo menos uma linha não corresponde a nenhum produto
- **THEN** a importação termina com status `PARCIAL`

### Requirement: Linha sem produto não trava as demais

Linha do arquivo sem produto correspondente SHALL ficar pendente de revisão (`item_venda.produto_id`
nulo) e MUST NOT impedir a importação das outras linhas. O sobrinho resolve depois, na tela de
importação. (Operação 04, passo 6)

Como o produto é casado com o item do caixa não está definido: `produto` não tem coluna de código
do caixa (docs/LACUNAS.md, L05).

#### Scenario: Uma linha desconhecida entre várias
- **WHEN** um arquivo tem dez linhas e uma não casa com nenhum produto
- **THEN** as nove linhas casadas geram venda e baixa de estoque
- **AND** a linha restante fica pendente de revisão

### Requirement: Venda gera baixa de estoque em FIFO

Cada item casado SHALL gerar `venda`, `item_venda` e `movimentacao` com `tipo = 'VENDA'`, com a
baixa saindo do lote de validade mais próxima. (Operação 04, passos 7 e 8; RN01, RN02)

#### Scenario: Venda importada baixa o lote certo
- **WHEN** é importada a venda de 2 kg de presunto, havendo lotes que vencem em 28/09 e 05/10
- **THEN** é gravada uma movimentação `VENDA` de 2 kg
- **AND** a baixa sai do lote de 28/09

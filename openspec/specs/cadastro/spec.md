# cadastro Specification

## Purpose

Cadastrar categorias, produtos e fornecedores, que sustentam todo o resto do sistema.
Origem: RF01, RF02, RF15, RN03 (Apostilas I e III); fluxograma 01 (Apostila II).
Tarefas B1 a B7.

## Requirements

### Requirement: Cadastro de produto

O sistema SHALL permitir ao perfil `OPERACAO` cadastrar produtos com nome, categoria, unidade de
medida, se é perecível e por quantos dias dura, preço de custo, preço de venda, estoque mínimo,
fornecedor padrão e a marcação de crítico de fim de semana. (RF01, RF15; tabela `produto`)

O produto MUST NOT ter coluna de saldo — o saldo é derivado das movimentações (RN01).

#### Scenario: Produto completo é salvo
- **WHEN** o sobrinho cadastra "Arroz 5 kg" na categoria "Secos e molhados", não perecível, com preços e estoque mínimo
- **THEN** a API responde `201` com o produto criado

### Requirement: Perecível exige prazo de durabilidade

Um produto marcado como perecível SHALL ser salvo apenas com `durabilidade_dias` preenchido e maior
que zero. A validação MUST acontecer antes de gravar; o banco mantém a restrição `ck_produto_rn03`
como última defesa. A tela SHALL manter o que já foi digitado e apontar só o campo que falta.
(RN03; fluxograma 01)

Mensagem: "Produto perecível precisa do prazo de durabilidade em dias. Sem ele o sistema não
consegue avisar quando o produto vai vencer."

#### Scenario: Perecível sem durabilidade é recusado
- **WHEN** "Frango resfriado 1 kg" é marcado como perecível sem durabilidade
- **THEN** o cadastro é recusado com a mensagem da RN03
- **AND** nada é gravado

#### Scenario: Perecível com durabilidade é salvo
- **WHEN** "Frango resfriado 1 kg" é marcado como perecível com durabilidade de 4 dias
- **THEN** o produto é salvo

#### Scenario: Durabilidade zero é recusada
- **WHEN** um produto perecível é enviado com durabilidade 0
- **THEN** o cadastro é recusado

#### Scenario: Não perecível dispensa durabilidade
- **WHEN** um produto não perecível é enviado sem durabilidade
- **THEN** o produto é salvo

### Requirement: Nome único na categoria

O sistema SHALL recusar um produto cujo nome já exista na mesma categoria. (Fluxograma 01, passo 6;
restrição `uq_produto_nome_categoria`)

#### Scenario: Nome repetido na mesma categoria
- **WHEN** já existe "Presunto" em "Frios" e o sobrinho cadastra outro "Presunto" em "Frios"
- **THEN** o cadastro é recusado

#### Scenario: Mesmo nome em outra categoria
- **WHEN** já existe um produto com o nome em uma categoria e o sobrinho cadastra o mesmo nome em outra
- **THEN** o produto é salvo

### Requirement: Cadastro de fornecedor

O sistema SHALL permitir ao perfil `OPERACAO` cadastrar fornecedores com nome, contato, pedido
mínimo e, obrigatoriamente, o prazo de entrega em dias, que não pode ser negativo. (RF02; tabela
`fornecedor`; tarefa B2)

#### Scenario: Fornecedor sem prazo de entrega
- **WHEN** um fornecedor é enviado sem `prazo_entrega_dias`
- **THEN** o cadastro é recusado

#### Scenario: Fornecedor com prazo de entrega
- **WHEN** um fornecedor é enviado com prazo de entrega de 3 dias
- **THEN** o fornecedor é salvo

### Requirement: Cadastro de categoria

O sistema SHALL manter categorias com nome único, usando o vocabulário da loja ("Secos e
molhados", "Açougue", "Frios"). (Tabela `categoria`; RNF10; tarefa B2)

#### Scenario: Categoria repetida
- **WHEN** já existe a categoria "Frios" e alguém cadastra "Frios" de novo
- **THEN** o cadastro é recusado

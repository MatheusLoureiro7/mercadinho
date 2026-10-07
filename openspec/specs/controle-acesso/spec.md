# controle-acesso Specification

## Purpose

Garantir que cada uma das três pessoas com acesso enxergue e faça apenas o que corresponde à sua
função na loja. Origem: RN14, RF14, RNF04, RNF12 (Apostila I e III). Tarefa A4.

## Requirements

### Requirement: Três perfis de acesso

O sistema SHALL reconhecer exatamente três perfis — `DONO`, `GESTAO` e `OPERACAO` — gravados em
`usuario.papel`. Os dois funcionários da loja MUST NOT ter usuário no sistema. (RN14, RNF04)

#### Scenario: Papel fora dos três é recusado
- **WHEN** alguém tenta cadastrar um usuário com papel diferente de `DONO`, `GESTAO` ou `OPERACAO`
- **THEN** o cadastro é recusado

### Requirement: Verificação de papel antes de qualquer operação

A API SHALL verificar o papel do usuário na camada de autenticação, antes de tocar no banco e antes
de qualquer regra de negócio, seguindo o mapa de acesso abaixo. (RN14; Apostila IV, operação 01,
passo 3)

| Tela | DONO | GESTAO | OPERACAO |
|---|---|---|---|
| Produtos | — | — | ✔ |
| Fornecedores | — | — | ✔ |
| Entrada de mercadoria | — | — | ✔ |
| Avarias e quebras | — | — | ✔ |
| Importação de vendas | — | — | ✔ |
| Consulta de estoque | ✔ | ✔ | ✔ |
| Fechamento de caixa | — | ✔ | — |
| Balanço da semana | — | ✔ | — |
| Telegram (sem tela) | ✔ | — | — |

#### Scenario: DONO tenta cadastrar produto
- **WHEN** um usuário com papel `DONO` envia o cadastro de um produto
- **THEN** a API recusa a requisição antes de qualquer acesso ao banco
- **AND** nenhum produto é gravado

#### Scenario: OPERACAO cadastra produto
- **WHEN** um usuário com papel `OPERACAO` envia o cadastro de um produto válido
- **THEN** a requisição segue para a validação do cadastro

#### Scenario: GESTAO acessa o fechamento de caixa
- **WHEN** um usuário com papel `GESTAO` abre o fechamento de caixa
- **THEN** o acesso é permitido

#### Scenario: OPERACAO tenta acessar o fechamento de caixa
- **WHEN** um usuário com papel `OPERACAO` tenta acessar o fechamento de caixa
- **THEN** o acesso é recusado

#### Scenario: Todos consultam o estoque
- **WHEN** um usuário de qualquer um dos três papéis abre a consulta de estoque
- **THEN** o acesso é permitido

### Requirement: Menu montado conforme o papel

A tela de login SHALL identificar a pessoa e montar o menu apenas com as telas permitidas ao seu
papel. (Apostila II, tela Login)

#### Scenario: Menu da esposa
- **WHEN** um usuário `GESTAO` entra no painel
- **THEN** o menu mostra Consulta de estoque, Fechamento de caixa e Balanço da semana
- **AND** não mostra as telas de cadastro e movimentação

### Requirement: Segurança básica

As senhas SHALL ser guardadas apenas como hash (`usuario.senha_hash`), nunca em texto puro. Apenas
uma porta SHALL ficar exposta à internet, e o banco MUST NOT ter acesso externo. (RNF12)

#### Scenario: Senha nunca em texto puro
- **WHEN** um usuário é cadastrado com uma senha
- **THEN** o valor gravado em `senha_hash` é diferente da senha digitada
- **AND** a senha digitada é validada contra o hash no login

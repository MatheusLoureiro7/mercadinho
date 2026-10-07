# Acompanhamento do cronograma

Andamento das tarefas do **cronograma da Apostila IV, seção 9** — o mesmo que foi entregue ao
professor em 25/09/2026. Os códigos, as horas e as dependências são os da apostila.

**Como ler:** tarefa concluída aparece ~~riscada~~, com a data e o commit em que foi entregue.
O diário, no fim do arquivo, conta o que foi feito em cada dia.

| Situação | Significado |
|---|---|
| ✅ Concluída | Pronta **e testada** |
| 🔄 Em andamento | Começou e ainda não terminou |
| ⬜ A fazer | Não começou; não depende de decisão do cliente |
| ⛔ Aguarda Dxx | Depende de uma decisão pendente (`docs/DECISOES-PENDENTES.md`) |

---

## Resumo

*Atualizado em 07/10/2026.*

| | Concluído | Total | % |
|---|---|---|---|
| **Tarefas** | 14 | 51 | 27,5 % |
| **Horas estimadas** | 94 h | 378 h | 24,9 % |

| Etapa | Blocos | Horas concluídas | Total | % |
|---|---|---|---|---|
| 1 · Aviso de validade | A, B, C, D, F, J | 94 h | 212 h | 44,3 % |
| 2 · Aviso de ruptura | E, G, H | 0 h | 136 h | 0,0 % |
| 3 · Gestão | I | 0 h | 30 h | 0,0 % |

As horas concluídas são as **estimadas** na apostila para cada tarefa entregue, não horas medidas.

Prazo de entrega: **27/11/2026**.

---

## Bloco A — Fundação · 40 h  ·  34 de 40 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~A1~~ | ~~Configurar repositório, ambiente e padrão de código~~ | — | 6 | ✅ Concluída | 06/10/2026 | `ca4ac9b` |
| ~~A2~~ | ~~Subir o banco de dados e a ferramenta de migração~~ | A1 | 6 | ✅ Concluída | 06/10/2026 | `02c5ae1` |
| ~~A3~~ | ~~Esqueleto da API: rotas, tratamento de erro e registro de log~~ | A1 | 10 | ✅ Concluída | 06/10/2026 | `ebea081` |
| ~~A4~~ | ~~Autenticação e os três perfis de acesso~~ | A3, B1 | 12 | ✅ Concluída | 06/10/2026 | `ec49325` |
| A5 | Esteira de publicação em ambiente de teste | A1 | 6 | ⛔ Aguarda D05 | — | — |

## Bloco B — Cadastros · 46 h  ·  27 de 46 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~B1~~ | ~~Criar as tabelas de usuário, categoria, produto e fornecedor~~ | A2 | 6 | ✅ Concluída | 06/10/2026 | `a3923e2` |
| ~~B2~~ | ~~API de categoria e fornecedor~~ | B1, A3 | 8 | ✅ Concluída | 06/10/2026 | `3f93ef1` |
| ~~B3~~ | ~~API de produto, com validações~~ | B1, A3 | 10 | ✅ Concluída | 06/10/2026 | `0172832` |
| ~~B4~~ | ~~Regra: perecível exige prazo de durabilidade~~ | B3 | 3 | ✅ Concluída | 06/10/2026 | `a7d6512` |
| B5 | Tela de produtos | A3 | 8 | ⬜ A fazer | — | — |
| B6 | Tela de fornecedores | A3 | 6 | ⬜ A fazer | — | — |
| B7 | Ligar as telas à API e tratar os erros na tela | B2, B3, B5, B6 | 5 | ⬜ A fazer | — | — |

## Bloco C — Entrada de mercadoria · 40 h  ·  24 de 40 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~C1~~ | ~~Criar as tabelas de lote e movimentação~~ | A2 | 6 | ✅ Concluída | 06/10/2026 | `251d78d` |
| ~~C2~~ | ~~API de entrada de lote~~ | C1, B3 | 8 | ✅ Concluída | 07/10/2026 | `92bf7de` |
| ~~C3~~ | ~~Regra: validade obrigatória e cálculo automático~~ | C2 | 4 | ✅ Concluída | 07/10/2026 | `43dc95d` |
| ~~C4~~ | ~~Saldo derivado das movimentações~~ | C1 | 6 | ✅ Concluída | 06/10/2026 | `48451c5` |
| C5 | Tela de entrada de mercadoria | A3 | 10 | ⬜ A fazer | — | — |
| C6 | Integração e teste do fluxo completo | C2, C5 | 6 | ⬜ A fazer | — | — |

## Bloco D — Perdas e avarias · 18 h  ·  9 de 18 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~D1~~ | ~~API de registro de perda, com motivo obrigatório~~ | C1 | 6 | ✅ Concluída | 07/10/2026 | `18285b3` |
| ~~D2~~ | ~~Regra: perda não entra na base de consumo~~ | D1 | 3 | ✅ Concluída | 07/10/2026 | `83dbc5f` |
| D3 | Tela de avarias e quebras | A3 | 7 | ⬜ A fazer | — | — |
| D4 | Integração e teste | D1, D3 | 2 | ⬜ A fazer | — | — |

## Bloco E — Entrada das vendas · 44 h ⚠️ depende da decisão D01  ·  0 de 44 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| E1 | Levantar o formato do arquivo exportado pelo caixa | **confirmação com o cliente** | 6 | ⛔ Aguarda D01 | — | — |
| E2 | Criar as tabelas de venda, item de venda e importação | A2 | 6 | ⬜ A fazer | — | — |
| E3 | Serviço que lê o arquivo e gera venda e movimentação | E1, E2 | 16 | ⛔ Aguarda D01 | — | — |
| E4 | Casar o produto do caixa com o produto cadastrado | E3 | 10 | ⛔ Aguarda D01 | — | — |
| E5 | Tela de acompanhamento da importação | E3 | 6 | ⛔ Aguarda D01 | — | — |

## Bloco F — Consulta de estoque · 22 h  ·  0 de 22 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| F1 | Visão de estoque por produto e por lote | C4 | 6 | ⬜ A fazer | — | — |
| F2 | API de consulta com filtros | F1 | 6 | ⬜ A fazer | — | — |
| F3 | Tela de estoque, com destaque para mínimo e vencidos | A3 | 10 | ⬜ A fazer | — | — |

## Bloco G — Previsão · 40 h ⚠️ depende da decisão D01  ·  0 de 40 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| G1 | Tabela de consumo diário e rotina de agregação | E2 | 10 | ⛔ Aguarda D01 | — | — |
| G2 | Cálculo do consumo médio e por dia da semana | G1 | 12 | ⛔ Aguarda D01 | — | — |
| G3 | Tabela de previsão e gravação do resultado | G2 | 8 | ⛔ Aguarda D01 | — | — |
| G4 | Regra: histórico mínimo antes de projetar | G2 | 4 | ⛔ Aguarda D01 | — | — |
| G5 | Agendador das rotinas diárias | G3 | 6 | ⛔ Aguarda D01 | — | — |

## Bloco H — Avisos · 52 h ⚠️ depende da decisão D01  ·  0 de 52 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| H1 | Tabela de aviso e controle de estado | A2 | 8 | ⬜ A fazer | — | — |
| H2 | Gerador do aviso de validade | H1, C3 | 8 | ⬜ A fazer | — | — |
| H3 | Gerador do aviso de ruptura | H1, G3 | 10 | ⛔ Aguarda D01 | — | — |
| H4 | Janela de silêncio e agrupamento | H1 | 8 | ⬜ A fazer | — | — |
| H5 | Integração com o serviço de mensagens | H1 | 10 | ⬜ A fazer | — | — |
| H6 | Vincular o celular do dono ao usuário | H5, B1 | 4 | ⬜ A fazer | — | — |
| H7 | Receber e registrar a resposta dele | H5 | 4 | ⬜ A fazer | — | — |

## Bloco I — Fechamento e relatórios · 30 h  ·  0 de 30 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| I1 | Tabela de fechamento e cálculo da diferença | E2 | 8 | ⬜ A fazer | — | — |
| I2 | Tela de fechamento de caixa | A3 | 10 | ⬜ A fazer | — | — |
| I3 | Relatório de balanço semanal | E2, D1 | 12 | ⬜ A fazer | — | — |

## Bloco J — Qualidade e implantação · 46 h  ·  0 de 46 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| J1 | Testes automatizados de todas as regras | todas as regras | 16 | ⬜ A fazer | — | — |
| J2 | Carga inicial dos produtos, junto com o cliente | B3 | 8 | ⬜ A fazer | — | — |
| J3 | Inventário de partida: contagem física | J2 | 6 | ⬜ A fazer | — | — |
| J4 | Teste em movimento real, num sábado cheio | todos | 6 | ⬜ A fazer | — | — |
| J5 | Treinamento das três pessoas | J4 | 4 | ⬜ A fazer | — | — |
| J6 | Implantação e acompanhamento da primeira semana | J4 | 6 | ⛔ Aguarda D05 | — | — |

---

## Diário

O que foi feito em cada dia, do mais recente para o mais antigo. Cada linha aponta a tarefa do
cronograma, a regra de negócio (quando houver) e o commit.

### 07/10/2026

**Tarefas concluídas: C2, C3, D1 e D2** (21 h estimadas).

- **C2 — API de entrada de mercadoria (RF03, operação 02).** O sobrinho já registra, pela API,
  cada carga que chega: produto, quantidade, custo, fornecedor e validade. Como manda a operação 02
  da Apostila IV, o lote e a movimentação de entrada são gravados **juntos, numa transação só** — se
  qualquer parte falhar, nada fica gravado, e nunca existe lote sem a movimentação que explica o
  saldo (RN01); um teste simula a falha e prova isso. A resposta já traz o saldo novo do produto
  (passo 9), e a "lista do dia" mostra o que entrou hoje (passo 11). A data de entrada é sempre o
  dia da loja — inclusive à noite, quando o banco (que trabalha em UTC) já está "amanhã". Lote não
  pode ser editado nem apagado; correção de estoque é por perda ou ajuste, que deixam rastro.
  O passo 10 (cancelar o aviso de "vai acabar" quando a mercadoria chega) já é chamado, e passa a
  agir quando a tabela de avisos existir (tarefa H1). As regras de validade (RN04) são a próxima
  tarefa, C3. 27 testes automáticos — total do projeto: 267, todos passando.

- **C3 — Regra: validade obrigatória e cálculo automático (RN04).** Ao registrar a entrada de um
  perecível, a validade agora é garantida: se o sobrinho não informar, o sistema calcula sozinho
  somando a durabilidade do produto ao dia da entrada — o exemplo da própria Apostila I, frango que
  entra em 21/09 com 4 dias de durabilidade, é gravado com validade 25/09. Validade já vencida é
  recusada com "Essa validade já passou. Confira a data na embalagem.", e nesse caso nada é gravado.
  A regra segue a ordem exata da especificação, fica num módulo próprio (vale para qualquer caminho
  de entrada, não só a tela) e usa o "hoje" da loja, também à noite. **Leitura registrada:** o
  passo 1 da RN04 diz que o não perecível "segue" — então validade informada e já vencida é recusada
  também nele, como diz a frase da regra ("Validade anterior à data de hoje é recusada"). Com a C2,
  estão testadas as seis situações do fluxograma 02. 14 testes automáticos — total do projeto: 281,
  todos passando.

**Bloco C:** banco, API e regras completos (C1 a C4). Faltam a tela (C5) e a integração (C6).

- **D1 — API de registro de perda, com motivo obrigatório (RF04).** O caderno de avarias do
  sobrinho já tem a sua API: o que venceu, quebrou ou estragou sai do estoque **sempre com o
  motivo anotado** — sem motivo, é recusado. Cada perda baixa o saldo e a quantidade do lote,
  numa transação só (RN01), e fica registrada como PERDA, separada das vendas (RN11). Não dá para
  registrar perda maior do que o que existe. O lote vencido sai por aqui, como manda a RN16 — o
  exemplo da Apostila I, iogurte vencido em 20/09 e retirado em 21/09 com motivo, está testado.
  **Decisão L20:** se o sobrinho informa o lote que estragou, a perda sai dele; se não informa,
  sai pela ordem de validade (RN02), começando pelos vencidos. **Decisão L13:** desempate da ordem
  de validade — mesma validade, sai antes o que entrou antes; sem validade, sai por último. Essa
  ordem já fica pronta para a baixa por venda (E3), que deixa os vencidos de fora. 31 testes
  automáticos — total do projeto: 312, todos passando.

- **D2 — Regra: perda não entra na base de consumo (RN11).** A regra que o roteiro chama de "uma
  das mais críticas do sistema": se a perda contasse como consumo, quanto mais produto estragasse,
  mais o sistema mandaria comprar. Agora existe **um único lugar** no sistema que responde "quanto
  se vendeu", e ele conta só vendas — perdas, entradas e ajustes ficam de fora. É dele que a
  previsão (bloco G) vai ler, e um teste automático impede que alguém do grupo calcule consumo por
  fora. Testado com o exemplo da Apostila I: 10 kg de frango vão fora, o saldo cai 10 kg, o consumo
  do dia continua sendo só o vendido. A conta é feita pelo dia da loja — a venda das 22h30 não vira
  "dia seguinte". Foi provado que os testes pegam o erro: colocando a perda na conta, 5 testes
  falham. 15 testes automáticos — total do projeto: 327, todos passando.

**Bloco D:** banco, API e regra completos (D1 e D2). Faltam a tela (D3) e a integração (D4).

**Próxima tarefa:** F1 — visão de estoque por produto e por lote.

### 06/10/2026

**Tarefas concluídas: A1, A2, A3, B1, A4, B2, B3, B4, C1 e C4** (73 h estimadas).

- **A1 — Repositório, ambiente e padrão de código.** Repositório git criado, com a especificação
  (Apostilas I a IV) no primeiro commit. Projeto Django com os sete módulos do sistema
  (`comum`, `cadastro`, `estoque`, `vendas`, `previsao`, `alertas`, `caixa`) e a pasta do painel
  web estático. Padrão de código com Ruff, testes com pytest e README com o passo a passo para
  Windows, Linux e macOS. 5 testes automáticos.
- **A2 — Banco de dados e ferramenta de migração.** PostgreSQL 17 rodando em Docker, aceitando
  conexão só da própria máquina (RNF12), no fuso de São Paulo. Migrações do Django funcionando.
  3 testes automáticos — total do projeto: 8, todos passando.
- **Leitura crítica da especificação.** Oito lacunas novas registradas em `docs/LACUNAS.md`
  (L09 a L16) — pontos que as apostilas não definem e que o grupo precisa decidir. Nenhuma foi
  resolvida por conta própria no código.
- **Decisão da L09** (autenticação × tabela `usuario`): opção (c) — a autenticação do Django
  usa a tabela `usuario` exatamente como está na Apostila IV, sem nenhuma coluna a mais.
- **OpenSpec.** A especificação foi passada também para o formato OpenSpec (`openspec/specs/`):
  10 capacidades, cada requisito apontando a regra de origem e usando os exemplos das apostilas.

- **A3 — Esqueleto da API.** A API REST — a "porta única de entrada" da Apostila IV — está de
  pé em `/api/`, respondendo sempre em JSON. Toda recusa volta no mesmo formato, com a mensagem
  em português no vocabulário da loja (RNF10) e apontando só o campo com problema, como pede o
  fluxograma 01. As regras de negócio têm um jeito padrão de recusar uma operação, informando
  qual regra recusou (ex.: RN03). Erro inesperado não mostra detalhe técnico na tela: mostra um
  código, e o detalhe vai para o log com o mesmo código. Toda requisição é registrada em log,
  sem nunca gravar senha (RNF12). 15 testes automáticos — total do projeto: 23, todos passando.

- **Skills de apoio.** Instaladas no projeto 13 skills (guias de boas práticas para o assistente
  de programação) de Django, PostgreSQL, testes, Telegram e acessibilidade. O `CLAUDE.md` registra
  qual usar em cada tarefa e, principalmente, o que **não** seguir delas: onde um exemplo contraria
  a especificação (banco de testes, modelo de usuário, tipos do `schema.sql`), vale a especificação.
- **B1 — Tabelas de usuário, categoria, produto e fornecedor.** As quatro primeiras tabelas da
  Apostila IV existem no banco, criadas por migração. Um teste automático compara o banco com o
  modelo de dados entregue, coluna por coluna (nome, tipo, tamanho, obrigatoriedade, valor
  padrão) — se alguém acrescentar uma coluna fora da apostila, o teste quebra (foi provado
  criando de propósito uma coluna `saldo`, proibida pela RN01). O banco já recusa sozinho:
  produto perecível sem prazo de durabilidade (RN03), produto com nome repetido na mesma
  categoria (fluxograma 01), fornecedor sem prazo de entrega e usuário com perfil diferente de
  DONO, GESTAO e OPERACAO (RN14). A senha é gravada só como hash (RNF12). O login usa a tabela
  `usuario` exatamente como na apostila (decisão da L09). 36 testes automáticos — total do
  projeto: 59, todos passando.
- **Lacuna nova: L17** — a apostila não diz se a unidade de medida é uma lista fechada
  (KG, UN, L, PCT). Fica para o grupo decidir antes da B3.

- **A4 — Autenticação e os três perfis de acesso (RN14).** A tela de Login já tem a sua API: a
  pessoa entra com login e senha e recebe uma chave de acesso que vale por um dia de loja (12 h) —
  e deixa de valer na hora se a senha for trocada ou o usuário desativado. Junto, recebe o menu do
  seu perfil, como pede a Apostila II. A tabela de acesso da RN14 está no código exatamente como na
  especificação, e um teste confere todas as 24 combinações (8 telas × 3 perfis). A recusa
  acontece antes de qualquer gravação no banco (Apostila IV, operação 01, passo 3), e uma parte do
  sistema que esqueça de dizer a que tela pertence fica fechada para todos. Contra adivinhação de
  senha, no máximo 10 tentativas por minuto (RNF12) — e um teste prova que não dá para burlar o
  limite fingindo outro endereço. Os três usuários são criados pela equipe com um comando no
  terminal (decisão parcial da L14). 50 testes automáticos — total do projeto: 109, todos
  passando.

**Bloco A:** só falta a A5 (esteira de publicação), que aguarda a decisão D05 — onde o sistema vai
rodar.

- **B2 — API de categoria e fornecedor.** O sobrinho já pode, pela API, cadastrar e corrigir
  fornecedores com o prazo de entrega — obrigatório, porque é o número que faz o aviso de "vai
  acabar" sair a tempo (RF02, RN08) — e as categorias da loja ("Secos e molhados", "Açougue",
  "Frios"). Nada é apagado: categoria e fornecedor são registros de origem, que a Apostila IV
  manda nunca apagar. Os outros dois perfis não mexem em fornecedor (RN14).
  **Decisão L18:** a categoria não tem tela própria entre as 10; ler as categorias ficou com a
  Consulta de estoque (os três perfis, que veem o saldo por categoria) e cadastrar ficou com a tela
  de Produtos (só o sobrinho). Nenhuma tela nova foi criada. 32 testes automáticos — total do
  projeto: 141, todos passando.

- **B3 — API de produto, com validações.** O sobrinho já pode, pela API, cadastrar e corrigir os
  produtos com tudo o que o RF01 pede — nome, categoria, unidade, se é perecível e quantos dias
  dura, preços, estoque mínimo — e marcar os que não podem faltar no fim de semana (RF15). Segue a
  operação 01 da Apostila IV: aponta só o campo que falta e recusa produto com nome repetido na
  mesma categoria, inclusive ao editar. O produto não tem saldo (RN01) e não pode ser apagado.
  Busca por nome e filtro por categoria, para a tela de Produtos dar conta de até 2.000 itens.
  **Decisão L17:** unidade de medida em lista fechada — KG, UN, L ou PCT. **Decisão L19:** produto
  cadastrado sem dizer se é perecível herda o padrão da categoria (ex.: tudo do Açougue já nasce
  perecível). 33 testes automáticos — total do projeto: 174, todos passando.

- **B4 — Regra: perecível exige prazo de durabilidade (RN03).** Produto perecível sem a
  durabilidade em dias — ou com zero — é recusado antes de gravar, com a mensagem "Produto
  perecível precisa do prazo de durabilidade em dias. Sem ele o sistema não consegue avisar quando
  o produto vai vencer." A resposta aponta só esse campo, para a tela manter o resto do que foi
  digitado (fluxograma 01). A regra vale também ao editar (marcar como perecível, apagar a
  durabilidade) e para o produto que herdou o "perecível" da categoria. Testado com o exemplo da
  própria Apostila I: "Frango resfriado 1 kg" sem durabilidade é recusado; com 4 dias, é salvo.
  A regra fica num módulo próprio, não na tela, como manda a Apostila IV. 22 testes automáticos —
  total do projeto: 196, todos passando.

**Bloco B:** a parte de banco e API está completa (B1 a B4). Faltam as telas — B5, B6 e B7.

- **C1 — Tabelas de lote e movimentação.** As duas tabelas que sustentam o estoque existem no banco,
  iguais à Apostila IV — conferidas automaticamente, coluna por coluna, contra o modelo de dados
  entregue. O teste pegou uma diferença sutil e ela foi corrigida: o horário padrão da
  movimentação agora é o `NOW()` da apostila (o horário da transação), para que um lote e a
  movimentação que o explica fiquem com a mesma hora. O banco já recusa sozinho: lote com
  quantidade negativa, movimentação de tipo desconhecido, quantidade zero ou negativa, e perda sem
  motivo. O índice que acelera a saída pela validade mais próxima (RN02) está criado. Produto ou
  lote que já tem movimentação não pode ser apagado — o histórico do estoque fica intacto (RN01).
  Ficou registrado um cuidado para as próximas tarefas: o "hoje" do sistema é sempre o horário de
  São Paulo, nunca o do banco (que trabalha em UTC). 28 testes automáticos — total do projeto: 224,
  todos passando.

- **C4 — Saldo derivado das movimentações (RN01).** "A tarefa mais importante do projeto inteiro",
  segundo o roteiro. O saldo de cada produto nunca é um número guardado: é sempre a soma das
  movimentações — entradas e ajustes somam, vendas e perdas subtraem —, calculada pela visão
  `vw_estoque_atual` **copiada literalmente** do modelo de dados da Apostila IV. Um teste prova que
  a visão do sistema é idêntica à da apostila (e que uma alteração, como trocar o sinal do ajuste,
  seria pega). Testado com o exemplo da própria Apostila I: entram 40 kg, vendem-se 12 kg, perdem-se
  3 kg → saldo de 25 kg, com as três linhas no histórico. Ninguém consegue gravar um saldo — nem o
  sistema, nem direto no banco. Quilo fracionado sem erro de arredondamento. 16 testes automáticos —
  total do projeto: 240, todos passando.

**Próxima tarefa:** C2 — API de entrada de lote.

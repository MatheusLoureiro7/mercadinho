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

*Atualizado em 16/11/2026.*

| | Concluído | Total | % |
|---|---|---|---|
| **Tarefas** | 48 | 51 | 94,1 % |
| **Horas estimadas** | 362 h | 378 h | 95,8 % |

| Etapa | Blocos | Horas concluídas | Total | % |
|---|---|---|---|---|
| 1 · Aviso de validade | A, B, C, D, F, J | 196 h | 212 h | 92,5 % |
| 2 · Aviso de ruptura | E, G, H | 136 h | 136 h | 100,0 % ✅ |
| 3 · Gestão | I | 30 h | 30 h | 100,0 % ✅ |

As horas concluídas são as **estimadas** na apostila para cada tarefa entregue, não horas medidas.

Início: **06/10/2026**. Entrega e apresentação final: **01/12/2026** (até 29/10 era 27/11).

---

## Datas previstas das tarefas que faltam

*Aprovadas pelo grupo em 23/10/2026.* O cronograma da Apostila IV traz horas e dependências, mas
não traz datas; o professor pediu datas. As das tarefas concluídas são as reais (tabelas abaixo).
Estas são as previstas, na ordem das dependências. **Revistas em 30/10/2026:** o Mercado do
Sr. João é uma loja fictícia, criada pelo professor para o trabalho, então não há reunião com
cliente. O grupo decidiu a D01 (o caixa exporta as vendas em **Excel**) e a D05 (o sistema roda
**no computador do Matheus**). Como não há dados reais, as vendas e os produtos usados nos testes e
na demonstração são de exemplo, criados pelo grupo.

| Quando | Tarefas | Observação |
|---|---|---|
| 02/11 | E1, E2 | E1: o grupo define as colunas da planilha do caixa (D01 = Excel). E2 remarcada em 30/10 (era 26 a 28/10) |
| 03 a 05/11 | E3, I1 | I1 também depende da lacuna L12, que agora o grupo decide |
| 03 e 04/11 | A5 | No computador do Matheus (D05) |
| 06/11 | G1 | |
| 06 e 09/11 | E4, E5 | |
| 09/11 | J2 | Carga de uma lista de produtos de exemplo (não há dados reais) |
| 09 a 10/11 | G2 | |
| 09 a 11/11 | I3 | |
| 11/11 | G3, G4 | |
| 12 e 13/11 | G5, H3 | |
| 17/11 | J3 | Contagem de partida simulada com os produtos de exemplo |
| até 18/11 | J1 | Concluída em 16/11/2026 |
| **21/11** (sábado) | J4 | Teste em movimento real |
| 23/11 | J5 | Treinamento |
| 23 a 27/11 | J6 | Implantação no computador do Matheus e primeira semana simulada |
| 28/11 a 30/11 | — | Folga para ajustes finais |
| **01/12** | — | Entrega e apresentação final, tudo pronto |

---

## Bloco A — Fundação · 40 h  ·  40 de 40 h concluídas ✅

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~A1~~ | ~~Configurar repositório, ambiente e padrão de código~~ | — | 6 | ✅ Concluída | 06/10/2026 | `ca4ac9b` |
| ~~A2~~ | ~~Subir o banco de dados e a ferramenta de migração~~ | A1 | 6 | ✅ Concluída | 06/10/2026 | `02c5ae1` |
| ~~A3~~ | ~~Esqueleto da API: rotas, tratamento de erro e registro de log~~ | A1 | 10 | ✅ Concluída | 06/10/2026 | `ebea081` |
| ~~A4~~ | ~~Autenticação e os três perfis de acesso~~ | A3, B1 | 12 | ✅ Concluída | 06/10/2026 | `ec49325` |
| ~~A5~~ | ~~Esteira de publicação em ambiente de teste~~ | A1 | 6 | ✅ Concluída | 13/11/2026 | `759e62e` |

## Bloco B — Cadastros · 46 h  ·  46 de 46 h concluídas ✅

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~B1~~ | ~~Criar as tabelas de usuário, categoria, produto e fornecedor~~ | A2 | 6 | ✅ Concluída | 06/10/2026 | `a3923e2` |
| ~~B2~~ | ~~API de categoria e fornecedor~~ | B1, A3 | 8 | ✅ Concluída | 06/10/2026 | `3f93ef1` |
| ~~B3~~ | ~~API de produto, com validações~~ | B1, A3 | 10 | ✅ Concluída | 06/10/2026 | `0172832` |
| ~~B4~~ | ~~Regra: perecível exige prazo de durabilidade~~ | B3 | 3 | ✅ Concluída | 06/10/2026 | `a7d6512` |
| ~~B5~~ | ~~Tela de produtos~~ | A3 | 8 | ✅ Concluída | 07/10/2026 | `7f32893` |
| ~~B6~~ | ~~Tela de fornecedores~~ | A3 | 6 | ✅ Concluída | 07/10/2026 | `e6c031e` |
| ~~B7~~ | ~~Ligar as telas à API e tratar os erros na tela~~ | B2, B3, B5, B6 | 5 | ✅ Concluída | 08/10/2026 | `71a8811` |

## Bloco C — Entrada de mercadoria · 40 h  ·  40 de 40 h concluídas ✅

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~C1~~ | ~~Criar as tabelas de lote e movimentação~~ | A2 | 6 | ✅ Concluída | 06/10/2026 | `251d78d` |
| ~~C2~~ | ~~API de entrada de lote~~ | C1, B3 | 8 | ✅ Concluída | 07/10/2026 | `92bf7de` |
| ~~C3~~ | ~~Regra: validade obrigatória e cálculo automático~~ | C2 | 4 | ✅ Concluída | 07/10/2026 | `43dc95d` |
| ~~C4~~ | ~~Saldo derivado das movimentações~~ | C1 | 6 | ✅ Concluída | 06/10/2026 | `48451c5` |
| ~~C5~~ | ~~Tela de entrada de mercadoria~~ | A3 | 10 | ✅ Concluída | 08/10/2026 | `30e51b1` |
| ~~C6~~ | ~~Integração e teste do fluxo completo~~ | C2, C5 | 6 | ✅ Concluída | 08/10/2026 | `defb4a9` |

## Bloco D — Perdas e avarias · 18 h  ·  18 de 18 h concluídas ✅

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~D1~~ | ~~API de registro de perda, com motivo obrigatório~~ | C1 | 6 | ✅ Concluída | 07/10/2026 | `18285b3` |
| ~~D2~~ | ~~Regra: perda não entra na base de consumo~~ | D1 | 3 | ✅ Concluída | 07/10/2026 | `83dbc5f` |
| ~~D3~~ | ~~Tela de avarias e quebras~~ | A3 | 7 | ✅ Concluída | 08/10/2026 | `c8c4252` |
| ~~D4~~ | ~~Integração e teste~~ | D1, D3 | 2 | ✅ Concluída | 08/10/2026 | `9fe0d21` |

## Bloco E — Entrada das vendas · 44 h  ·  44 de 44 h concluídas ✅

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~E1~~ | ~~Levantar o formato do arquivo exportado pelo caixa~~ | decisão D01 (Excel) | 6 | ✅ Concluída | 05/11/2026 | `aded7a7` |
| ~~E2~~ | ~~Criar as tabelas de venda, item de venda e importação~~ | A2 | 6 | ✅ Concluída | 05/11/2026 | `f6f48e7` |
| ~~E3~~ | ~~Serviço que lê o arquivo e gera venda e movimentação~~ | E1, E2 | 16 | ✅ Concluída | 05/11/2026 | `2e66774` |
| ~~E4~~ | ~~Casar o produto do caixa com o produto cadastrado~~ | E3 | 10 | ✅ Concluída | 12/11/2026 | `c738f43` |
| ~~E5~~ | ~~Tela de acompanhamento da importação~~ | E3 | 6 | ✅ Concluída | 12/11/2026 | `313abeb` |

## Bloco F — Consulta de estoque · 22 h  ·  22 de 22 h concluídas ✅

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~F1~~ | ~~Visão de estoque por produto e por lote~~ | C4 | 6 | ✅ Concluída | 07/10/2026 | `01b84a8` |
| ~~F2~~ | ~~API de consulta com filtros~~ | F1 | 6 | ✅ Concluída | 07/10/2026 | `2365139` |
| ~~F3~~ | ~~Tela de estoque, com destaque para mínimo e vencidos~~ | A3 | 10 | ✅ Concluída | 08/10/2026 | `6a6321e` |

## Bloco G — Previsão · 40 h  ·  40 de 40 h concluídas ✅

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~G1~~ | ~~Tabela de consumo diário e rotina de agregação~~ | E2 | 10 | ✅ Concluída | 12/11/2026 | `48dba3f` |
| ~~G2~~ | ~~Cálculo do consumo médio e por dia da semana~~ | G1 | 12 | ✅ Concluída | 12/11/2026 | `d6a3e45` |
| ~~G3~~ | ~~Tabela de previsão e gravação do resultado~~ | G2 | 8 | ✅ Concluída | 12/11/2026 | `62b0ec5` |
| ~~G4~~ | ~~Regra: histórico mínimo antes de projetar~~ | G2 | 4 | ✅ Concluída | 12/11/2026 | `7fc505c` |
| ~~G5~~ | ~~Agendador das rotinas diárias~~ | G3 | 6 | ✅ Concluída | 12/11/2026 | `1c62ea9` |

## Bloco H — Avisos · 52 h  ·  52 de 52 h concluídas ✅

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~H1~~ | ~~Tabela de aviso e controle de estado~~ | A2 | 8 | ✅ Concluída | 08/10/2026 | `eae1d23` |
| ~~H2~~ | ~~Gerador do aviso de validade~~ | H1, C3 | 8 | ✅ Concluída | 08/10/2026 | `a3627f3` |
| ~~H3~~ | ~~Gerador do aviso de ruptura~~ | H1, G3 | 10 | ✅ Concluída | 12/11/2026 | `406c890` |
| ~~H4~~ | ~~Janela de silêncio e agrupamento~~ | H1 | 8 | ✅ Concluída | 08/10/2026 | `5a7be53` |
| ~~H5~~ | ~~Integração com o serviço de mensagens~~ | H1 | 10 | ✅ Concluída | 08/10/2026 | `075a5de` |
| ~~H6~~ | ~~Vincular o celular do dono ao usuário~~ | H5, B1 | 4 | ✅ Concluída | 09/10/2026 | `094a2ee` |
| ~~H7~~ | ~~Receber e registrar a resposta dele~~ | H5 | 4 | ✅ Concluída | 09/10/2026 | `606e94f` |

## Bloco I — Fechamento e relatórios · 30 h  ·  30 de 30 h concluídas ✅

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~I1~~ | ~~Tabela de fechamento e cálculo da diferença~~ | E2 | 8 | ✅ Concluída | 05/11/2026 | `416b7b8` |
| ~~I2~~ | ~~Tela de fechamento de caixa~~ | A3 | 10 | ✅ Concluída (API na I1) | 09/10/2026 | `4184da1` |
| ~~I3~~ | ~~Relatório de balanço semanal~~ | E2, D1 | 12 | ✅ Concluída | 12/11/2026 | `f1e319e` |

## Bloco J — Qualidade e implantação · 46 h  ·  30 de 46 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~J1~~ | ~~Testes automatizados de todas as regras~~ | todas as regras | 16 | ✅ Concluída | 16/11/2026 | `f802807` |
| ~~J2~~ | ~~Carga inicial dos produtos, junto com o cliente~~ | B3 | 8 | ✅ Concluída | 12/11/2026 | `261ce90` |
| ~~J3~~ | ~~Inventário de partida: contagem física~~ | J2 | 6 | ✅ Concluída | 12/11/2026 | `d1b72b5` |
| J4 | Teste em movimento real, num sábado cheio | todos | 6 | ⬜ A fazer | — | — |
| J5 | Treinamento das três pessoas | J4 | 4 | ⬜ A fazer | — | — |
| J6 | Implantação e acompanhamento da primeira semana | J4 | 6 | ⬜ A fazer | — | — |

## Tarefas extras (fora do cronograma da Apostila IV)

Trabalho que o grupo fez além das 51 tarefas. **Não entra nas 378 horas nem nas porcentagens do
resumo.**

| ID | TAREFA | SITUAÇÃO | CONCLUÍDA EM | RESULTADO |
|---|---|---|---|---|
| ~~X1~~ | ~~Revisão geral do código contra a especificação~~ | ✅ Concluída | 16/11/2026 | `docs/REVISAO-FABLE.md` |

---

## Diário

O que foi feito em cada dia, do mais recente para o mais antigo. Cada linha aponta a tarefa do
cronograma, a regra de negócio (quando houver) e o commit.

### 16/11/2026

- **X1, item 19 — Banco diferente do `schema.sql` em detalhes (correção da revisão, gravidade
  baixa).**
  **O problema:** colunas, tipos e restrições conferem, mas o Django cria detalhes que o `schema.sql`
  não tem: chave primária `IDENTITY` em vez de `SERIAL`, chaves estrangeiras conferidas no fim da
  transação e índices a mais. E o banco deste computador tinha o padrão de `movimentacao.data_hora`
  diferente do `NOW()` da apostila.
  **O que foi apurado:** o padrão diferente era só deste computador — a migração 0001 foi editada
  depois de aplicada, e qualquer banco criado do zero (o dos testes, o da implantação) já nasce com
  `NOW()`. Os índices a mais são **16**, não 17: 13 de chave estrangeira e 3 de busca por texto.
  **Decisão do grupo (16/11/2026):** aceitar e registrar os três detalhes do Django (lacuna L28,
  ADR-014), que funcionam igual ou melhor. Uma migração nova (`estoque.0003`) acerta o `NOW()` em
  banco antigo, e foi aplicada neste computador. Nenhuma coluna mudou.
  **Testes:** 4 novos — três guardas (as diferenças são exatamente essas; tirar um índice da lista
  faz o teste falhar, conferido) e um da migração, que falhou antes de ela existir e passa depois.
  **1134 testes no total, todos aprovados.**

- **X1, item 18 — Venda ligada ao produto errado não tinha desfazer (correção da revisão,
  gravidade baixa).**
  **O problema:** na tela de importação, o sobrinho escolhe o produto de uma venda não reconhecida, e
  a venda sai do estoque na hora. Escolheu errado, não há volta: a movimentação nunca é apagada
  (RN01), e um "desfazer" deixaria a venda errada contando no consumo do produto errado (RN11).
  **Decisão do grupo (16/11/2026):** em vez de desfazer, **confirmar antes**. Ao tocar em "Ligar a
  este produto", a tela pergunta: "Ligar a venda de 05/11/2026 às 08:14 a Frango resfriado 1 kg?
  Isso tira 2 KG do estoque dele e não pode ser desfeito.", com "Sim, ligar" e "Voltar e trocar o
  produto". O manual explica como acertar se mesmo assim errar. Nenhuma tabela nem API mudou.
  **Achado na conferência da tela:** a captura mostrou que o botão "Ligar a este produto" continuava
  visível junto da pergunta — o estilo dos botões vencia o atributo de esconder. Corrigido para todo
  o painel; de quebra, o botão "Sair" passou a aparecer só depois que a sessão confere o login, como
  sempre foi a intenção.
  **Testes:** 2 novos (a pergunta aparece e nada é gravado antes do "Sim"; "Voltar" deixa trocar sem
  gravar) e 2 ajustados (agora confirmam). Falharam antes da correção e passam depois. **1130 testes
  no total, todos aprovados.** Manual atualizado.

- **X1, item 17 — Mensagem dividida podia chegar repetida (correção da revisão, gravidade baixa).**
  **O problema:** os avisos do dia vão numa mensagem só (RN13), e o Telegram aceita até 4096
  caracteres; num dia de muitos avisos, a mensagem era dividida pelo canal. Se a parte 1 saía e a 2
  falhava, nada ficava marcado como enviado, e a rodada seguinte mandava a parte 1 de novo. (Falha
  sem divisão continua como antes, de propósito: nada é marcado e a rodada seguinte tenta de novo.)
  **O que foi feito (técnico, sem decisão nova):** quem divide agora é o serviço de notificação,
  sempre entre um aviso e outro, e cada parte que sai marca os seus avisos como enviados; o que não
  saiu fica para a próxima rodada. Para quem lê nada muda: título só na primeira parte, numeração
  seguida, e o botão "Sim, pedir" junto da parte que tem o aviso.
  **Testes:** 2 novos — cada aviso chega uma vez só mesmo com a parte 2 caindo (falhou antes da
  correção e passa depois) e a mensagem dividida mantém título e numeração (guarda). **1128 testes
  no total, todos aprovados.**

- **X1, item 16 — Duas rodadas ao mesmo tempo duplicavam (correção da revisão, gravidade baixa).**
  **O problema:** a importação confere se o dia já entrou e depois grava; os avisos conferem se já
  avisaram hoje e depois gravam. Duas rodadas ao mesmo tempo (o cron e alguém rodando o comando à
  mão) conferiam juntas, ouviam "não" e gravavam as duas: vendas e avisos em dobro.
  **O que foi feito (técnico, sem decisão nova):** a conferência e a gravação passaram a acontecer
  sob uma trava do próprio PostgreSQL (`pg_advisory_xact_lock`), sem tabela nem dependência nova:
  quem chega depois espera e encontra o que o primeiro gravou. Vale para a importação e para os
  avisos de validade e de "vai acabar". Registrado como ADR-013.
  **Testes:** 2 novos, com duas execuções em paralelo de verdade e a primeira atrasada de propósito
  no meio da gravação. Os 2 falharam antes da correção (2 vendas; 2 avisos) e passam depois —
  repetidos três vezes, sempre iguais. **1126 testes no total, todos aprovados.**

- **X1, item 15 — Total do cupom arredondado só no fim (correção da revisão, gravidade baixa).**
  **O problema:** a planilha não traz o total do cupom; o sistema somava quantidade × preço de cada
  item e só arredondava no fim. O caixa arredonda cada item: 2 × 0,333 kg a R$ 19,99 dá R$ 13,32 no
  caixa e dava R$ 13,31 no sistema — um centavo de "sobra" falsa no fechamento.
  **Decisão do grupo (16/11/2026):** cada item é arredondado nos centavos antes de somar, como o
  caixa. Registrado em `docs/FORMATO-PLANILHA-CAIXA.md`. Nenhuma tabela mudou.
  **Testes:** 1 novo, que falhou antes da correção (13,31) e passa depois (13,32). **1124 testes no
  total, todos aprovados.**

- **X1, item 14 — Erro interno com número fora do esperado (correção da revisão, gravidade baixa).**
  **O problema:** dois casos davam "Algo deu errado do nosso lado" (erro 500) em vez de uma mensagem:
  um endereço da tela de importação com texto no lugar do número (`/api/itens-pendentes/abc/casar/`),
  e um produto perecível cadastrado com durabilidade de 2 bilhões de dias, cuja validade calculada
  passava do ano 9999 e quebrava a entrada de mercadoria.
  **O que foi feito:** o endereço com texto agora responde "não encontrado", como o resto da API. A
  durabilidade ganhou um teto, por **decisão do grupo (16/11/2026): 3650 dias (10 anos)**, com a
  mensagem "A durabilidade vai até 3650 dias (10 anos)." Nenhuma tabela mudou.
  **Testes:** 2 novos; os 2 falharam antes da correção e passam depois. **1123 testes no total, todos
  aprovados.** Manual atualizado.

- **X1, item 13 — "1.000" digitado virava 1 (correção da revisão, gravidade média).**
  **O problema:** nas telas, número sem vírgula tinha o ponto lido como casa decimal ("12.90" =
  12,90). Quem digitava "1.000" do jeito brasileiro, para mil latas, gravava um lote de **1** lata,
  sem aviso — e a previsão e os avisos erravam junto.
  **Decisão do grupo (16/11/2026):** número com ponto seguido de grupos de três dígitos e sem vírgula
  ("1.000", "12.500") é ambíguo: a tela **não envia** e mostra embaixo do campo "Não dá para saber se
  é mil ou um: escreva 1000 para mil, ou 1,5 para um e meio". "1000", "1,5", "1.000,50" e "12.90"
  continuam aceitos. Vale nas quatro telas que recebem número: Entrada de mercadoria, Avarias e
  quebras, Produtos e Fornecedores (o Fechamento de caixa já tratava o milhar). Nenhuma tabela mudou.
  **Testes:** 12 novos — a entrada de "1.000" recusada sem gravar nada, a reescrita "1000" aceita,
  9 casos da regra de conversão e uma guarda que falha se uma tela nova converter número sem
  conferir o ambíguo. Os 11 que dependiam da correção falharam antes e passam depois. **1121 testes
  no total, todos aprovados.** FAQ atualizado.
  **Com isso, os 9 itens de gravidade média da revisão estão corrigidos.** Ficam os 9 de baixa.

- **X1, item 12 — Dois produtos com o "mesmo" nome (correção da revisão, gravidade média).**
  **O problema:** o cadastro pela tela recusava nome repetido na categoria comparando o texto exato,
  e aceitava "Arroz 5 kg" e "arroz 5 KG" como produtos diferentes. A importação das vendas compara
  sem maiúscula, acento nem espaço (L05): via dois produtos com o mesmo nome e deixava **toda venda
  dele pendente**, todo dia.
  **O que foi feito (sem decisão nova):** o cadastro passou a comparar o nome do mesmo jeito que a
  importação e a carga da J2 já comparavam. A mensagem é a mesma de antes; corrigir a maiúscula do
  próprio nome continua permitido. Nenhuma tabela mudou.
  **Testes:** 5 novos (três formas do nome parecido, a edição para um nome parecido com outro, e a
  correção da maiúscula do próprio nome). Os 4 que dependiam da correção falharam antes e passam
  depois. **1109 testes no total, todos aprovados.** Manual atualizado.

- **X1, item 11 — A rodada perdida não era recuperada (correção da revisão, gravidade média).**
  **O problema:** a rodada roda às 03h00 pelo cron. Com o notebook fechado nesse horário, o dia
  ficava sem importação e sem avisos; e, se fosse quinta, o aviso de fim de semana (RN10) não
  acontecia naquela semana, porque só a quinta avalia.
  **Decisão do grupo (16/11/2026):** a rodada anota o dia em que rodou (`logs/ultima-rodada.txt`,
  sem tabela nova), e o cron ganhou uma quarta linha: **de hora em hora, aos 30 minutos**,
  `rodada_diaria --se-faltar` faz a rodada só se a de hoje ainda não aconteceu (e já passou das
  03h00). Se a quinta foi perdida, a primeira rodada de sexta ou de sábado avalia o fim de semana no
  lugar dela. Os avisos que saírem de dia continuam respeitando o horário de movimento (RN12).
  **Atenção na implantação (J6):** o crontab precisa ser gerado de novo com `agenda_cron` (4 linhas).
  **Testes:** 12 novos (a rodada anota o dia mesmo com falha; recupera, não repete e espera a hora;
  as 7 combinações de dia e última rodada do fim de semana; a sexta avalia quando pedido) e 1
  ajustado (o crontab com 4 linhas). Os 13 falharam antes da correção e passam depois. **1104
  testes no total, todos aprovados.** Runbook R9 e guia de implantação atualizados.

- **X1, item 10 — Nenhuma tela mostrava a previsão (correção da revisão, gravidade média).**
  **O problema:** a previsão (em quantos dias cada produto acaba) era calculada toda madrugada, mas
  só aparecia no aviso do Telegram. A especificação pede o número em tela: o RF08 ("em quantos dias
  o produto acaba", Essencial) e a RN09 ("ainda aprendendo" nas telas de consulta). O manual do
  usuário já descrevia o "ainda aprendendo" na tela, que não existia.
  **O que foi feito (sem decisão nova: a especificação já dizia):** a Consulta de estoque ganhou a
  coluna **"Quando acaba"**, com as mesmas palavras do aviso: "Em 12 dias", "Amanhã", "Hoje",
  "Acabou", "Ainda aprendendo" (RN09, nunca "0 dias" nem "—") e "Não está vendendo". A API de
  consulta por produto ganhou os campos `previsao` e `dias_ate_acabar`, lidos de `previsao_produto`
  na mesma ida ao banco — a consulta continua sem uma ida por produto (RNF06). A tela passou pela
  UI UX Pro Max e foi conferida em captura no computador e no celular (375 px). Nenhuma tabela mudou.
  **Testes:** 1 novo de API (as quatro situações) e 1 de tela, de ponta a ponta; 1 teste de API
  ajustado para os campos novos. Os 3 falharam antes da correção e passam depois. **1092 testes no
  total, todos aprovados.** Manual atualizado.

- **X1, item 9 — Produto parado e zerado avisava "acabou" todo dia (correção da revisão,
  gravidade média).**
  **O problema:** o aviso sai quando o saldo é igual ou menor que o ponto de pedido (RN08). Um
  produto que não vende há 30 dias (o panetone depois do Natal) tem consumo zero e ponto de pedido
  zero; com saldo zero, "0 ≤ 0" gerava toda madrugada um aviso "acabou" com urgência alta, no topo
  da mensagem — o tipo de aviso repetido que faz a pessoa parar de ler os avisos de verdade.
  **Decisão do grupo (16/11/2026):** produto **sem venda no período do consumo** não gera aviso de
  "vai acabar" nem de fim de semana. Quando voltar a vender, a previsão recalcula e os avisos voltam
  sozinhos. Nenhuma tabela mudou.
  **Testes:** 2 novos (o produto parado não avisa, nem no dia a dia nem pelo fim de semana). Os 2
  falharam antes da correção e passam depois. **1090 testes no total, todos aprovados.** FAQ
  atualizado.

- **X1, item 8 — Produto sem fornecedor nunca avisava (correção da revisão, gravidade média).**
  **O problema:** o aviso de "vai acabar" (RN08) usa o prazo de entrega do fornecedor padrão. Como o
  fornecedor é opcional no cadastro, o produto sem fornecedor nunca avisava — nem quando zerava — e
  nenhuma tela mostrava isso.
  **Decisão do grupo (16/11/2026):** sem fornecedor não dá para avisar antes, mas o produto que vinha
  vendendo e **acabou** gera o aviso, com urgência alta: "Carvão 5 kg acabou — não tem mais no
  estoque. Cadastre o fornecedor para o sistema avisar antes de acabar." O cadastro continua com o
  fornecedor opcional; nenhuma tela nem tabela mudou. Produto ainda aprendendo (RN09) ou sem venda
  continua sem esse aviso.
  **Testes:** 3 novos (o aviso sai quando acaba; não sai sem venda nem ainda aprendendo) e 1
  ajustado (com estoque, continua sem aviso). O primeiro falhou antes da correção e passa depois.
  **1088 testes no total, todos aprovados.** Manual e FAQ atualizados.

- **X1, item 7 — Só "dinheiro" contava como dinheiro (correção da revisão, gravidade média).**
  **O problema:** o apurado do fechamento soma as vendas pagas em dinheiro, e o sistema só aceitava
  a palavra exata "dinheiro" na coluna Pagamento. "Espécie" não contava, e uma planilha sem a coluna
  (ela é opcional) dava apurado R$ 0,00: a gaveta inteira virava uma sobra falsa, gravada para sempre.
  **Decisão do grupo (16/11/2026):** contam como dinheiro "Dinheiro", "Espécie" e "Em espécie", sem
  diferenciar maiúscula, acento nem espaços. Se alguma venda do dia veio **sem forma de pagamento**,
  o fechamento daquele dia é recusado, explicando o motivo. Registrado em
  `docs/FORMATO-PLANILHA-CAIXA.md`. Nenhuma tabela mudou.
  **Consequência a acompanhar:** como um dia importado não entra de novo (item 1), o dia cuja
  planilha veio sem a coluna Pagamento fica sem fechamento. O caixa da loja precisa exportar sempre
  essa coluna; a planilha de exemplo do grupo já a tem em todas as linhas.
  **Testes:** 10 novos casos (as formas de escrever espécie; textos que só contêm a palavra não
  contam; venda sem pagamento recusa o fechamento, com a coluna vazia, em branco ou ausente). Os 6
  que dependiam da correção falharam antes e passam depois. **1085 testes no total, todos
  aprovados.** FAQ e glossário atualizados.

- **X1, item 6 — O caixa só podia ser fechado no dia seguinte (correção da revisão, gravidade
  média).**
  **O problema:** a tela de fechamento sempre fechava "ontem", sem poder escolher. Se ninguém abrisse
  o sistema no dia seguinte (o sábado, numa loja que não abre domingo) ou se a rodada das 03h00
  falhasse, aquele dia nunca mais podia ser fechado.
  **Decisão do grupo (16/11/2026):** a tela ganhou o campo **"Dia do caixa"**, já preenchido com
  ontem. A esposa pode escolher um dia anterior cujas vendas já entraram; hoje e o futuro continuam
  recusados, porque as vendas do dia só entram de madrugada. Na API, `?data=` no apurado e `data`
  opcional no registro; sem a data, continua sendo ontem. Nenhuma tabela mudou. A tela passou pela
  UI UX Pro Max: campo de data nativo do navegador, com rótulo, ajuda e erro embaixo do campo; se o
  dia escolhido não tem vendas, a tela explica e trava só a contagem, deixando trocar o dia.
  **Testes:** 6 novos de API (apurado e registro de um dia anterior, hoje e futuro recusados, dia sem
  vendas, data em formato errado) e 1 de tela, de ponta a ponta: o sábado fechado na quinta. Os 7
  falharam antes da correção e passam depois. Dois testes antigos mudaram de propósito: a tela agora
  digita e manda também o dia (apurado e diferença continuam fora). **1075 testes no total, todos
  aprovados.** Manual, FAQ e Guia de início rápido atualizados.

- **X1, item 5 — Depois do "Sim, pedir", o produto ficava calado para sempre (correção da revisão,
  gravidade média).**
  **O problema:** depois que o Sr. João toca em "Sim, pedir", o sistema para de avisar sobre aquele
  produto até a mercadoria chegar (decisão de 12/11). Mas não havia limite: se o fornecedor não
  entregasse, o aviso nunca mais voltava — na revisão, a carne zerada ficou 90 dias sem aviso.
  **Decisão do grupo (16/11/2026):** o silêncio dura o **prazo de entrega do fornecedor**, que já
  está no cadastro. "Sim, pedir" no dia 9 com entrega em 2 dias espera até o dia 11; sem lote novo,
  no dia 12 o aviso volta, começando por "O pedido ainda não chegou:". Nenhuma tabela nem parâmetro
  novo.
  **Testes:** 2 novos — o pedido atrasado volta a avisar (falhou antes da correção e passa depois) e
  no dia previsto para a entrega ainda não avisa (o outro lado da decisão). **1068 testes no total,
  todos aprovados.** Manual e FAQ atualizados.

- **X1, item 4 — Planilha com dois dias travava o fechamento (correção da revisão, gravidade alta).**
  **O problema:** cada planilha virava um registro de importação com uma data só, a da primeira
  linha. Numa planilha com as vendas de 10/11 e 11/11, as vendas dos dois dias entravam, mas o
  sistema achava que o dia 11 não tinha entrado: o fechamento de caixa do dia 11 era recusado, o
  balanço marcava o dia como sem vendas, e uma cópia do dia 11 podia entrar de novo. Achado junto:
  o caixa recomeça a numeração dos cupons a cada dia, e o cupom 1 de um dia se juntava ao cupom 1
  do outro numa venda só.
  **Decisão do grupo (16/11/2026):** a planilha com mais de um dia é aceita, e **cada dia ganha o
  seu registro de importação**, com as linhas e as pendências dele; os cupons são agrupados dentro
  de cada dia. A tela de importação mostra uma linha por dia. Registrado em
  `docs/FORMATO-PLANILHA-CAIXA.md`. Nenhuma tabela mudou.
  **Testes:** 3 novos (um registro por dia, com o cupom repetido virando duas vendas; o fechamento
  do segundo dia liberado; a cópia do segundo dia recusada). Os 3 falharam antes da correção e passam
  depois; os testes que esperavam um registro só passaram a receber a lista com um registro.
  **1066 testes no total, todos aprovados.** Manual do usuário atualizado.
  **Com isso, os quatro itens de gravidade alta da revisão estão corrigidos**, antes do teste de
  sábado (J4, 21/11/2026), como combinado. Os 9 de gravidade média e os 9 de baixa continuam na lista.

- **X1, item 3 — Saldo e lotes deixavam de bater (correção da revisão, gravidade alta).**
  **O problema:** o sistema guarda dois números por produto: o saldo (tudo que entrou menos tudo que
  saiu) e o que resta em cada lote. Quando o caixa vendia mais do que o sistema tinha (5 no estoque,
  venda de 8), a sobra era gravada sem lote, como decidido em 05/11. Mas a carga seguinte de 10
  entrava inteira no lote: o saldo dizia 7 e os lotes, 10. A tela de perdas confere pelos lotes, então
  aceitava uma perda de 10, e o saldo ia a −3. E não havia operação que consertasse.
  **Decisão do grupo (16/11/2026):** na entrada de mercadoria, o que foi vendido a mais é
  **descontado do lote novo** — aquelas unidades já tinham sido vendidas. No exemplo, o lote de 10
  nasce com 7 restantes; saldo e lotes batem e a perda de 10 é recusada. A movimentação de entrada
  continua com 10, e o saldo continua sendo só a soma das movimentações (RN01). Nenhuma tabela
  mudou. A operação de ajuste de estoque (lacuna L10) continua em aberto, para depois da entrega.
  **Testes:** 3 novos (a carga desconta a venda a mais; a perda maior que o saldo é recusada; uma
  carga pequena fica zerada e a seguinte desconta o resto). Os 3 falharam antes da correção e passam
  depois; **1063 testes no total, todos aprovados**. FAQ atualizado.

- **X1, item 2 — Linha com erro sumia do caixa (correção da revisão, gravidade alta).**
  **O problema:** quando uma linha da planilha não podia ser lida (por exemplo, a hora escrita
  "9h30"), o sistema importava as outras e descartava essa. A venda dela sumia do valor apurado, e
  o fechamento de caixa registrava uma sobra que não existia — um cupom de R$ 200,00 virava
  "sobra de R$ 200,00", registro que pela RN15 nunca mais se altera. Como o dia já tinha entrado
  (item 1), não havia como completar depois.
  **Decisão do grupo (16/11/2026):** uma linha que não pode ser lida **recusa a planilha inteira**.
  Ela aparece como "Não foi lida", o número da linha e o motivo ficam no registro da rodada, e o
  fechamento daquele dia continua recusado até a planilha corrigida entrar. A linha com produto
  desconhecido não muda: continua entrando e fica para conferir. Registrado em
  `docs/FORMATO-PLANILHA-CAIXA.md`, que mudava a regra da E1 (antes, linha com erro dava
  "parcial"). Nenhuma tabela mudou.
  **Testes:** 1 teste antigo trocado (a linha inválida agora recusa tudo) e 2 novos (a planilha
  corrigida entra; o fechamento com linha ilegível é recusado). Os 3 falharam antes da correção e
  passam depois; **1060 testes no total, todos aprovados**. Manual, FAQ e runbook R2 atualizados.

- **X1, item 1 — Planilha repetida ou regravada (correção da revisão, gravidade alta).**
  **O problema:** para saber se uma planilha do caixa já tinha entrado, o sistema olhava só o nome
  do arquivo. Uma cópia com outro nome (`copia.xlsx`) entrava de novo e baixava o estoque em dobro;
  e, se o caixa gravasse sempre `vendas.xlsx` por cima, a partir do segundo dia as vendas não
  entravam mais, sem nenhum aviso.
  **Decisão do grupo (16/11/2026):** as vendas são reconhecidas **pelo dia**, não pelo nome do
  arquivo. Linha de um dia que já entrou é ignorada; se a planilha inteira for de dias que já
  entraram, ela é recusada sem deixar registro, e a rodada avisa "as vendas desta planilha já
  tinham entrado". O arquivo com o nome de um já lido volta a ser lido se foi regravado depois da
  última leitura. Registrado também em `docs/FORMATO-PLANILHA-CAIXA.md`. Nenhuma tabela mudou.
  **Testes:** 5 novos (cópia com outro nome, mesmo nome com dia novo, planilha com um dia antigo e
  um novo, e os dois casos no comando da madrugada). Os 5 falharam antes da correção e passam
  depois; **1058 testes no total, todos aprovados**. Manual do usuário, FAQ e runbook R2
  atualizados.

- **J1 — Testes automatizados de todas as regras (concluída).** A J1 vinha em andamento desde
  09/10: cada regra ganhou teste junto com a sua tarefa, e a J1 é o fechamento. Hoje:
  - **As 16 regras de negócio estão construídas, testadas e aprovadas**, inclusive as da previsão
    (RN06 a RN10), que ficaram prontas em 12/11. O teste de guarda não tem mais nenhuma regra na
    lista de "ainda sem código".
  - **Os seis fluxogramas da Apostila II** têm cada losango de decisão testado pelo "sim" e pelo
    "não" — faltavam o 04 (importação), o ramo de "vai acabar" do 05 (rodada da madrugada) e a
    gravação do 06 (fechamento), que agora estão cobertos.
  - **Defeito achado ao rodar a suíte inteira:** o teste que confere a documentação do sistema
    passava sozinho e falhava junto com os outros. Causa: na primeira vez que uma tela chama a
    API, o framework acrescenta um método técnico ("HEAD") na lista daquela rota, e o documento
    gerado mudava conforme a ordem dos testes. O gerador passou a ignorar esse método, e um teste
    novo reproduz o caso sem depender da ordem. **Foi provado que o teste pega o erro:** com o
    gerador antigo, ele falha; com a correção, passa. Commit `f802807`.
  - **Relatório de testes versão 1.3** (`docs/testes/RELATORIO-DE-TESTES.pdf`, 3 páginas):
    **1053 testes, 1053 aprovados**, sobre o commit `f802807`; 14 defeitos encontrados desde
    06/10, nenhum em aberto; 130 defeitos inseridos de propósito, todos detectados. O material de
    trabalho do grupo (`docs/TESTES.md`) foi atualizado junto.
  - **O que fica para conferir à mão:** o sábado cheio simulado (J4), o aviso chegando no celular
    de verdade (J4 e J6), a facilidade de uso com as três pessoas (J5) e o computador ligado de
    madrugada com cópia de segurança (J6; o backup diário, RNF09, ainda não existe).
  Concluída em 16/11/2026 (prevista para até 18/11/2026).

- **X1 — Revisão geral do código contra a especificação (tarefa extra, fora do cronograma).**
  Antes da entrega, o grupo fez uma revisão do sistema inteiro, sem corrigir nada, só para listar.
  **O que foi revisado:** o código comparado com as 16 regras de negócio, os requisitos RF01 a
  RF17, as 14 tabelas do modelo de dados e as 10 telas; e uma procura por erros que os testes
  automáticos podem não pegar (data errada depois das 21h, perda contada como venda, saída pelo
  lote errado, saldo gravado à mão, tela sem conferir o perfil, duas pessoas mexendo no mesmo lote
  ao mesmo tempo e arredondamento de centavos). O banco deste computador também foi comparado com
  o modelo de dados entregue.
  **O que foi encontrado:** 22 problemas — **4 de gravidade alta, 9 de média e 9 de baixa**. A
  lista completa, com o arquivo, a linha e um exemplo concreto de cada um, está em
  `docs/REVISAO-FABLE.md`. Doze deles foram reproduzidos na prática.
  **As regras críticas estão corretas:** o saldo é sempre calculado pelas movimentações (RN01), a
  mercadoria sai do lote que vence primeiro (RN02), a perda não entra na conta do consumo (RN11) e
  cada pessoa só entra nas suas telas (RN14).
  **Os quatro problemas de gravidade alta** estão na importação das vendas do caixa: (1) a mesma
  planilha salva com outro nome entra duas vezes, e uma planilha nova com o nome de uma antiga não
  entra; (2) uma linha da planilha com erro fica fora do valor apurado, e o fechamento de caixa
  registra uma diferença que não existe; (3) quando o caixa vende mais do que o sistema tinha em
  estoque, o saldo do produto e a soma dos lotes deixam de bater, e não há como acertar; (4) uma
  planilha com vendas de dois dias trava o fechamento do segundo dia.
  **Combinado:** as correções dos itens 1 a 4 serão feitas **antes do teste de sábado (J4,
  21/11/2026)**. Os de gravidade média e baixa ficam para depois, na ordem da lista.
  Não muda as 51 tarefas, as 378 horas nem as porcentagens do resumo.

**Próxima tarefa:** J4 — teste em movimento real num sábado cheio (simulado, 21/11/2026).
Depois, J5 (treinamento, 23/11) e J6 (implantação, 23 a 27/11).

### 13/11/2026

- **A5 — Esteira de publicação no computador do Matheus (D05).** Um comando só, `publicar.py`,
  coloca o sistema no ar: atualiza o código, instala as dependências, sobe o banco, confere o
  padrão do código e roda **todos os testes**; **só se tudo passar** aplica as mudanças no banco e
  troca a API e o painel pelos novos, conferindo que os dois respondem. Se qualquer passo falhar,
  o sistema que está no ar continua como estava. Cada publicação fica anotada em
  `logs/publicacoes.log` (data, versão e resultado). `--parar` desliga tudo.
  **Decisão do grupo (13/11/2026):** usar o servidor do próprio Django, sem programa novo
  instalado — basta para a demonstração; um servidor de produção ficaria para outra decisão.
  **Provado de verdade neste computador:** a esteira rodou de ponta a ponta — 1046 testes
  aprovados, as tabelas da previsão criadas no banco, a tela de login respondendo e a API
  respondendo "entre no sistema" a quem não fez login —, e o `--parar` liberou as portas. Commit
  `759e62e`.
  **Foi provado que os testes pegam erro:** os 10 testes conferem a ordem (testes antes de mexer
  no que está no ar), que um passo reprovado não migra nem troca os servidores, a troca dos
  servidores antigos pelos novos, servidor que não respondeu e o `--parar`. Total do projeto:
  1046, todos passando. Concluída em 13/11/2026 (prevista para 03 e 04/11/2026).

### 12/11/2026

- **E4 — Casar o produto do caixa com o produto cadastrado (operação 04, passo 6).** Quando a
  planilha do caixa traz um produto que o sistema não reconhece pelo nome, a venda fica
  **pendente**. Agora o sobrinho consegue resolver: o sistema lista cada venda pendente e ele
  escolhe qual produto do cadastro foi vendido. Nesse momento a venda sai do estoque exatamente
  como sairia na importação: **no dia e na hora em que aconteceu**, do lote que **vence primeiro**
  (RN01, RN02), sem usar lote que já estava vencido no dia da venda (RN16) — e passa a contar no
  consumo daquele dia para a previsão (RN11). Venda já resolvida não pode ser resolvida de novo
  (não baixa duas vezes), e só o perfil de operação faz isso (RN14). Commit `c738f43`.
  **Lacuna nova, decidida pelo grupo (L26):** o modelo de dados da Apostila IV não guarda o nome
  que veio na planilha, então o sistema não tem como mostrar "o caixa escreveu *Frango
  congelado*". O grupo decidiu **não mudar o modelo**: a venda pendente aparece com data, hora,
  quantidade e preço, e o sobrinho confere na planilha dele. Para a mesma linha não ficar pendente
  todo dia, o certo é acertar o nome no cadastro igual ao do caixa.
  **Foi provado que os testes pegam erro:** cinco defeitos de propósito (resolver duas vezes a
  mesma venda, lista fora de ordem, baixa na hora de hoje em vez da hora da venda, lista mostrando
  vendas já resolvidas, resolver sem baixar o estoque) — quatro pegos de primeira; o da ordem só
  depois de um teste reforçado. 18 testes automáticos — total do projeto: 849, todos passando.
  Concluída em 12/11/2026 (prevista para 06 e 09/11/2026).

- **G1 — Consumo de cada produto em cada dia (RN11).** Primeiro passo da previsão. Toda madrugada
  o sistema soma quanto cada produto vendeu em cada dia e guarda numa tabela própria
  (`consumo_diario`, igual à Apostila IV) — é dessa tabela que sai a média de consumo (RN06, RN07)
  e o "ainda aprendendo" (RN09). **Só venda entra; perda fica de fora (RN11):** no exemplo da
  própria regra, 10 kg de frango jogados fora não aumentam o consumo do dia. A venda das 22h30
  conta no dia da loja, e não no dia seguinte do relógio do servidor. A rotina refaz **os últimos
  30 dias até ontem** (30 é a janela da média; hoje fica de fora porque as vendas de hoje só entram
  de madrugada); assim, rodar duas vezes não duplica nada, e a venda pendente que o sobrinho
  resolveu depois (E4) entra na rodada seguinte. Para refazer o histórico inteiro há o comando
  `agregar_consumo --desde`. Commit `48dba3f`.
  **Lacuna nova, adotada e a confirmar pelo grupo (L27):** a apostila não diz que número é cada
  dia da semana; adotado **0 = domingo … 6 = sábado**, como o próprio PostgreSQL numera.
  **Para a G4:** pela RN09, o histórico é contado em dias **com venda** na tabela — um produto que
  vende pouco demora mais para sair do "ainda aprendendo", o que é o comportamento pedido.
  **Foi provado que os testes pegam erro:** sete defeitos de propósito (perda entrando no consumo,
  dia contado no fuso errado, segunda como dia 0, rodar duas vezes duplicando, hoje entrando
  incompleto, janela de 31 dias, apagar dias fora da janela) — todos pegos. 19 testes automáticos
  — total do projeto: 868, todos passando. Concluída em 12/11/2026 (prevista para 06/11/2026).

- **Visual novo do painel e skill de revisão visual.** Registrados no repositório o tema novo das
  telas, feito em 21/10/2026 (fontes servidas pelo próprio painel, sem nada vindo da internet —
  RNF06) e a skill usada para revisá-lo. Os 94 testes de tela passaram com o visual novo.

- **G2 — Consumo médio e por dia da semana (RN06, RN07).** A tarefa mais difícil do projeto. O
  sistema calcula, para cada produto, **quanto vende por dia**: o total dos últimos 30 dias
  dividido por 30 — sempre 30, mesmo que o produto só tenha vendido em 5 desses dias (RN06). Calcula
  também a **média de cada dia da semana**, porque a loja não vende igual todo dia (RN07). Testado
  com os exemplos da própria apostila: arroz, 150 kg em 30 dias → 5 kg por dia; cerveja, 8 latas
  por dia na média e 26 aos sábados → na quinta, a conta dos próximos dias já usa as 26 do sábado,
  e não as 8. Como a perda nunca entra (RN11), 300 kg jogados fora não mudam nada na média.
  Commit `d6a3e45`.
  **Decisão do grupo (lacuna L02, 12/11/2026):** a apostila manda usar a média do dia da semana
  quando a diferença for "relevante", sem dizer quanto. O grupo decidiu: **quando a média do dia
  chega a 1,5 vez a média geral**. Nos outros dias vale a média geral — inclusive no dia mais
  fraco, para um domingo parado não fazer o sistema achar que o produto dura mais.
  **Foi provado que os testes pegam erro:** oito defeitos de propósito (dividir pelos dias com
  venda em vez de 30, fator 1,4 em vez de 1,5, exigir mais que 1,5 em vez de "pelo menos", média
  do dia dividida sempre por 4, usar sempre a média do dia, nunca usar a média do dia, contar o dia
  de hoje ainda incompleto, ignorar os dias sem venda na média do dia) — todos pegos; um nono
  defeito testado não mudava o resultado e foi trocado por um que muda. 15 testes automáticos —
  total do projeto: 883, todos passando. Concluída em 12/11/2026 (prevista para 09 e 10/11/2026).

- **G3 — Previsão gravada: quando acaba, quando pedir e quanto pedir (RN08, RF11).** Toda
  madrugada o sistema guarda, para cada produto, a média de venda, **em quantos dias o estoque
  acaba**, o **ponto de pedido** e **quanto comprar** (tabela `previsao_produto`, igual à Apostila
  IV). Os dias até acabar levam em conta o dia da semana: com 46 latas na quinta, a cerveja acaba
  em 3,5 dias por causa do sábado — só pela média seriam 5,8, e a loja ficaria sem cerveja no
  domingo. Conferido com os exemplos da apostila: arroz a 5 kg por dia com 20 kg acaba em 4 dias
  (RN06); carne a 8 kg por dia, fornecedor que entrega em 3 dias e 20 % de segurança → ponto de
  pedido de 28,8 kg (RN08), com os 20 % lidos da tabela de parâmetros. Commit `62b0ec5`.
  **Decisão do grupo (lacuna L15, 12/11/2026):** a apostila pede a sugestão de compra mas não diz
  a conta. Decidido: **o que o produto vai vender no prazo de entrega do fornecedor mais 7 dias,
  menos o que já tem em estoque**; nunca negativa, e sem considerar o pedido mínimo. Produto sem
  fornecedor cadastrado não tem prazo de entrega, então fica sem ponto de pedido e sem sugestão.
  **Foi provado que os testes pegam erro:** nove defeitos de propósito (esquecer o estoque de
  segurança, dias até acabar só pela média, sugestão sem os 7 dias, sugestão negativa, sugestão
  sem descontar o estoque, sem a fração do último dia, produto sem fornecedor tratado como prazo
  zero, sugestão começando amanhã, conta das semanas errada) — todos pegos. 19 testes automáticos
  — total do projeto: 902, todos passando. Concluída em 12/11/2026 (prevista para 11/11/2026).

- **G4 — "Ainda aprendendo" (RN09).** Produto com menos de **14 dias de venda** não ganha número
  de previsão: o sistema guarda a linha vazia, que é o sinal de "ainda aprendendo", e assim
  nenhuma tela nem aviso mostra "acaba em 2 dias" para um produto que acabou de chegar — o teste
  da própria apostila. Conta-se o **histórico inteiro**, não só os últimos 30 dias, e contam-se
  **dias com venda**, não quantidade: vender 500 unidades em 3 dias não encurta o aprendizado. Os
  14 dias vêm da tabela de parâmetros, então mudam sem mexer no programa. Quando o produto chega
  aos 14 dias, ganha os números na rodada seguinte. Commit `7fc505c`.
  **Foi provado que os testes pegam erro:** seis defeitos de propósito (exigir mais que 14 em vez
  de "pelo menos 14", 14 escrito no programa em vez do parâmetro, contar só os últimos 30 dias,
  contar quantidade em vez de dias, produto aprendendo com hora de cálculo, produto aprendendo com
  média) — todos pegos. 8 testes automáticos — total do projeto: 910, todos passando. Concluída em
  12/11/2026 (prevista para 11/11/2026).

- **G5 — A rodada das 03h00.** Agora existe um comando só, `rodada_diaria`, que faz todo o
  trabalho da madrugada na ordem da Apostila IV: traz as planilhas novas do caixa, soma o consumo
  de cada dia, calcula a previsão, gera os avisos de validade e manda tudo pelo Telegram. Se um
  passo falha — por exemplo, a pasta das planilhas não existe —, os outros acontecem mesmo assim
  (o aviso de validade não depende da planilha), e a rodada termina avisando qual passo falhou,
  com o motivo no log. **Achado no caminho:** a geração dos avisos de validade (H2, pronta desde
  09/10) não era chamada por nenhuma rotina; agora é, toda madrugada. Commit `1c62ea9`.
  **Decisão do grupo (12/11/2026):** quem dispara a rodada é o **cron** do computador do Matheus
  (D05), sem programa novo instalado. O comando `agenda_cron` escreve as linhas do cron com os
  horários da tabela de parâmetros — a rodada às 03h00 e o envio de novo às 13h00 e às 18h00, no
  fim dos horários de movimento, para soltar os avisos segurados (RN12). As instruções estão no
  README. O computador precisa estar ligado às 03h00.
  **Foi provado que os testes pegam erro:** seis defeitos de propósito (previsão antes do consumo,
  rodada parando no primeiro erro, rodada com falha terminando como se estivesse tudo certo, sem
  os avisos de validade, envio no começo do horário de movimento em vez do fim, hora da rodada
  escrita no programa) — todos pegos. 9 testes automáticos, um deles com a rodada inteira de
  verdade (planilha → previsão → aviso → Telegram de teste) — total do projeto: 919, todos
  passando. Concluída em 12/11/2026 (prevista para 12 e 13/11/2026). **O bloco G (previsão) está
  completo.**

- **H3 — O aviso de "vai acabar" e o de fim de semana (RN08, RN10).** É o aviso que o Sr. João
  pediu. Toda madrugada, quando o estoque de um produto chega ao ponto de pedido, o celular dele
  recebe, no vocabulário da loja: *"Frango resfriado 1 kg acaba em 2 dias — sobram 6 KG. Pedir
  30 KG — Granja Boa Vista entrega em 2 dias."*, com o botão "Sim, pedir" (H7). Nunca aparece
  "ponto de pedido" nem "ruptura" na mensagem (RNF10). Na **quinta-feira**, os produtos que não
  podem faltar no fim de semana (carne, carvão, cerveja, linguiça, asinha) são avaliados com 40 %
  de folga (RN10), para dar tempo de o fornecedor entregar antes do sábado. Produto "ainda
  aprendendo" (RN09) ou sem fornecedor cadastrado não gera aviso, e chegar mercadoria cancela o
  aviso que ainda não saiu (operação 02). O gerador entrou na rodada das 03h00. Commit `406c890`.
  **Decisão do grupo (lacuna L03, 12/11/2026):** a RN10 também fala em "véspera de feriado", mas
  a apostila não diz de onde vem a lista de feriados. Decidido: **só sábado e domingo nesta
  versão**; véspera de feriado fica **fora do escopo, declarado**.
  **Decisões da tarefa, seguindo a H2:** o aviso sai todo dia enquanto o estoque estiver baixo,
  sem repetir no mesmo dia; urgência **alta** quando o produto acabou ou vai acabar antes de a
  entrega chegar, **média** nos outros casos; produto crítico que já está abaixo do ponto de
  pedido na quinta recebe só o aviso de "vai acabar", e não dois avisos do mesmo produto.
  **Foi provado que os testes pegam erro:** doze defeitos de propósito (exigir saldo menor em vez
  de "igual ou menor", avisar produto ainda aprendendo, avaliar o fim de semana em qualquer dia,
  sem a folga, folga escrita no programa, ignorar se o produto é crítico, repetir no mesmo dia, não
  cancelar o de ontem, arredondar os dias para cima, urgência sempre média, prazo contado errado,
  dia no fuso errado) — todos pegos; um deles só depois de um teste reforçado. 29 testes
  automáticos — total do projeto: 948, todos passando. Concluída em 12/11/2026 (prevista para 12 e
  13/11/2026). **O bloco H (avisos) está completo, e as 16 regras de negócio têm código e teste.**

- **Ajuste na H3 — depois do "Sim, pedir", o sistema para de avisar.** Decisão do grupo
  (12/11/2026): quando o Sr. João responde "Sim, pedir", aquele produto não é avisado de novo
  (nem o aviso de fim de semana) até chegar mercadoria dele — o pedido está a caminho, e o aviso
  todo dia só incomodaria. Mercadoria que chega no mesmo dia do aviso respondido conta como
  chegada. Quatro defeitos de propósito, todos pegos; 5 testes novos. Commit `7bf16b8`.

- **E5 — Tela de Importação de vendas.** A tela do sobrinho para acompanhar as vendas que vêm do
  caixa. A planilha **não é enviada pela tela**: ele continua salvando na pasta de sempre, e as
  vendas entram sozinhas às 03h00 (decisão da E3). A tela tem duas partes:
  **Vendas para conferir** — as vendas da planilha com um produto que o sistema não reconheceu
  pelo nome, com data, hora, quantidade e preço; ele acha a linha na planilha, toca em "Escolher o
  produto", procura o produto e a venda sai do estoque no dia em que aconteceu (E4).
  **Planilhas lidas** — as últimas planilhas, com a situação escrita em palavras ("Lida", "Lida,
  com vendas a conferir", "Não foi lida"), nunca só pela cor. No celular, cada linha vira um
  cartão. A tela foi desenhada com a skill UI UX Pro Max, seguindo o sistema de design do painel,
  e conferida em foto no computador da loja (1024 px) e no celular (360 px); a conferência corrigiu
  três detalhes (etiqueta cortada, marca da linha cobrindo a data e "1 produtos" no plural).
  Commit `313abeb`.
  **Foi provado que os testes pegam erro:** quatro defeitos de propósito na tela (venda ligada
  continuando na lista, ligar sem escolher o produto, situação só pela cor, "Cancelar" sem devolver
  o foco) — todos pegos. 19 testes automáticos, 10 deles com a tela aberta num navegador — total
  do projeto: 975, todos passando. Concluída em 12/11/2026 (prevista para 06 e 09/11/2026).
  **Com a E5, a etapa 2 (aviso de ruptura) está completa: blocos E, G e H.**

- **I3 — Balanço da semana (RF13).** A tela da esposa que substitui a conta do caderno. Mostra,
  de segunda a domingo: **quanto a loja vendeu** (o que o caixa registrou), **quanto perdeu** (a
  preço de custo, sempre em linha separada das vendas — RN11) e o **resultado**, com as vendas de
  cada dia e as perdas produto por produto. Dá para voltar às semanas anteriores; não dá para ir a
  uma semana que ainda não começou. Commit `f1e319e`.
  **Decisão do grupo (lacuna L16, 12/11/2026):** a apostila pede o "resultado do período" sem dizer
  a conta. Decidido: **resultado = vendas − perdas**, com as perdas a preço de custo (o custo do
  lote ou, sem ele, o do produto). O custo da mercadoria vendida **não entra**, porque um lucro
  completo seria controle financeiro, que a especificação deixa de fora.
  **Adotado na tarefa, a confirmar pelo grupo:** semana de segunda a domingo, abrindo na semana de
  ontem (as vendas de hoje só entram de madrugada); o dia cuja planilha do caixa não entrou aparece
  como "não entrou", com aviso — nunca como "R$ 0,00", que diria que a loja não vendeu nada; perda
  de produto sem custo cadastrado não entra no valor e é avisada, em vez de virar zero calado.
  Conferida em foto no computador da loja e no celular; a conferência corrigiu o dia sem vendas
  aparecendo como zero e os botões de semana quebrando no celular.
  **Foi provado que os testes pegam erro:** sete defeitos de propósito (perda somada às vendas,
  custo do produto no lugar do custo do lote, semana de domingo a sábado, sem aviso de dia sem
  vendas, perda sem custo virando zero, ir para semana futura, dia sem vendas como zero) — todos
  pegos; um só depois de um teste reforçado. 29 testes automáticos, 6 com a tela aberta num
  navegador — total do projeto: 1004, todos passando. Concluída em 12/11/2026 (prevista para 09 a
  11/11/2026). **Com a I3, a etapa 3 (gestão) está completa.**

**Fim do desenvolvimento das três etapas.** Faltam as tarefas de implantação e qualidade: A5
(esteira de publicação), J1 (fecha com as regras da previsão), J2 (carga dos produtos de exemplo),
J3 (contagem de partida), J4 (teste num sábado cheio), J5 (treinamento) e J6 (implantação).

- **J2 — Carga inicial dos produtos.** Para não cadastrar produto por produto na tela, a lista
  inteira entra de uma vez por uma **planilha do Excel** com três abas — Categorias, Fornecedores e
  Produtos —, carregada pelo comando `carregar_produtos`. Cada linha passa pelas **mesmas
  conferências da tela de Produtos** (RN03, unidade de medida, nome repetido). Se alguma linha
  estiver errada, **nada é gravado** e o comando diz a aba, a linha e a coluna de cada problema,
  para corrigir tudo de uma vez; o que já está cadastrado é mantido, e rodar de novo não duplica.
  Como o mercado é fictício, o grupo montou uma **planilha de exemplo**
  (`docs/exemplos/produtos-iniciais.xlsx`): 9 categorias, 6 fornecedores e 49 produtos de um
  mercadinho de bairro, com os itens que não podem faltar no fim de semana marcados (carne,
  carvão, cerveja, linguiça, asinha — RN10). Na loja de verdade, seria esta a planilha que a esposa
  preencheria com a equipe. Formato em `docs/FORMATO-PLANILHA-PRODUTOS.md`. Commit `261ce90`.
  **Foi provado que os testes pegam erro:** seis defeitos de propósito (gravar a parte boa mesmo
  com erro, aceitar produto repetido na planilha, aceitar "talvez" em sim/não, exigir o nome da
  categoria com acento exato, duplicar produto já cadastrado, deixar a RN03 escapar) — todos
  pegos. 16 testes automáticos — total do projeto: 1020, todos passando. Concluída em 12/11/2026
  (prevista para 09/11/2026).

- **J3 — Contagem de partida.** Antes de o sistema começar a valer, alguém conta o que tem em
  cada prateleira; essa contagem é o estoque inicial. Ela entra por uma planilha (aba Contagem:
  produto, quantidade contada, validade e custo) com o comando `carregar_contagem`.
  **Decisão do grupo (12/11/2026):** a contagem entra **como entrada de mercadoria**, pelo mesmo
  caminho da tela de Entrada: cada linha contada vira um **lote**, com validade para os perecíveis
  (a da embalagem ou, se ficar em branco, a data da contagem mais a durabilidade — RN04). Assim o
  frango contado já entra no aviso de vencimento (RN05) e sai primeiro pelo lote que vence antes
  (RN02). A movimentação fica marcada como **INVENTARIO** — um valor novo numa coluna que já existe
  (`movimentacao.origem`), sem mudar o banco. Produto vencido não é aceito na contagem (sai por
  Avarias). Como na J2, é **tudo ou nada**, e rodar de novo não lança duas vezes: produto que já
  tinha estoque é mantido. Planilha de exemplo com a contagem simulada dos 49 produtos da J2
  (`docs/exemplos/contagem-de-partida.xlsx`); formato em `docs/FORMATO-PLANILHA-CONTAGEM.md`.
  Commit `d1b72b5`.
  **Foi provado que os testes pegam erro:** seis defeitos de propósito (lançar com a origem da
  tela, gravar a parte boa com erro, lançar de novo produto que já tinha estoque, escolher qualquer
  um entre dois produtos de mesmo nome, ignorar a validade da planilha, aceitar quantidade
  negativa) — todos pegos. 16 testes automáticos — total do projeto: 1036, todos passando.
  Concluída em 12/11/2026 (prevista para 17/11/2026).

**Próxima tarefa:** A5 — esteira de publicação (13/11/2026).

### 05/11/2026

- **E2 — Tabelas de venda, item de venda e importação do caixa.** As três tabelas por onde as
  vendas do caixa entram no sistema existem no banco, iguais à Apostila IV — conferidas
  automaticamente, coluna por coluna, contra o modelo de dados entregue. O banco recusa sozinho:
  venda sem data e hora ou sem valor, item sem quantidade, importação sem nome do arquivo ou com
  situação fora das quatro previstas (pendente, ok, parcial, erro). Como manda o modelo, o item da
  venda pode ficar **sem produto** quando a linha do caixa não casar com nenhum produto
  cadastrado — essa linha fica pendente e não trava as outras (fluxograma 04). Apagar uma venda
  apaga os itens dela no próprio banco, como está na Apostila IV; já um produto que tem venda não
  pode ser apagado, para o histórico não se perder. Quantidade em quilo fracionado e dinheiro com
  centavos exatos. O sistema continua **sem** tela para registrar venda: venda só vem do arquivo do
  caixa. 29 testes automáticos — total do projeto: 755, todos passando. Concluída em 05/11/2026,
  com 3 dias de atraso sobre a data prevista (02/11/2026).

- **E1 — Formato da planilha de vendas do caixa.** Decidido pelo grupo: o caixa exporta uma
  planilha do Excel (`.xlsx`) por dia, com uma linha por produto vendido e as colunas **Cupom,
  Data, Hora, Produto, Quantidade, Preço unitário e Pagamento**; as linhas do mesmo cupom formam
  uma venda, e o valor total é a soma dos itens. O sistema lê o arquivo do Excel direto (biblioteca
  `openpyxl`, dependência nova decidida pelo grupo), sem o sobrinho precisar converter nada.
  **Decisão sobre a lacuna L05:** o produto da planilha é encontrado **pelo nome do cadastro**,
  sem diferenciar maiúscula, acento ou espaço a mais — assim o modelo de dados da Apostila IV não
  muda. Linha com produto que não existe fica pendente e não trava as outras. Duas diferenças em
  relação ao texto da Apostila IV ficaram registradas, com o motivo, em
  `docs/FORMATO-PLANILHA-CAIXA.md`: a apostila fala em "arquivo de texto" e em "código do caixa".
  Criada uma planilha de exemplo com 5 vendas e 10 itens (inclui um produto escrito sem acento,
  que casa, e um que não existe no cadastro, que fica pendente). 6 testes automáticos — total do
  projeto: 761, todos passando. Concluída em 05/11/2026 (prevista para 02/11/2026).

- **E3 — Importação das vendas do caixa.** O sistema agora lê a planilha do caixa e transforma
  cada cupom numa venda, e cada produto vendido numa baixa no estoque, seguindo a operação 04 da
  Apostila IV. A baixa sai do lote que **vence primeiro** (RN02), nunca de lote que já estava
  vencido no dia da venda (RN16), e fica registrada na hora em que a venda aconteceu — assim a
  venda das 22h30 conta no dia certo para a previsão (RN11). Produto que não existe no cadastro
  fica **pendente** e não atrapalha o resto da planilha; linha com erro (quantidade zero, hora
  inválida) é apontada com o número da linha no Excel. Se a mesma planilha for colocada duas vezes,
  ela não entra de novo; se algo falhar no meio, nada fica pela metade.
  **Duas decisões do grupo (05/11/2026):** (1) se a planilha mostrar uma venda maior do que o
  estoque registrado, a venda é gravada inteira e o saldo fica negativo na consulta — a venda já
  aconteceu, e o negativo mostra que a contagem do estoque está errada; (2) o sobrinho salva a
  planilha numa pasta do computador, e a rodada das 03h00 importa as novas (como a Apostila IV
  descreve: leitura de disco, uma vez por dia). Comando: `importar_vendas`.
  **Foi provado que os testes pegam erro:** cinco defeitos de propósito (data errada no lote
  vencido, lote vencido saindo na venda, sobra da venda sumindo, hora da importação no lugar da
  hora da venda, produto com nome repetido escolhido no chute) — quatro pegos de primeira; o
  quinto só depois de um teste novo. 35 testes automáticos — total do projeto: 796, todos
  passando. Concluída em 05/11/2026, dentro da data prevista (03 a 05/11/2026).

- **I1 — Fechamento de caixa gravado no sistema (RN15).** A tela de fechamento, pronta desde
  09/10/2026, agora grava de verdade. A esposa digita só o dinheiro contado; o valor apurado vem do
  sistema e a **diferença é calculada pelo próprio banco**, nunca digitada. O registro guarda a data
  e quem registrou, e **não pode ser alterado nem apagado** — nem pela tela, nem direto no banco: se
  ela contar de novo, é um registro novo e o anterior continua lá. Testado com o exemplo da própria
  Apostila I: o sistema apura R$ 3.240,00, a contagem dá R$ 3.215,00 → registro de −R$ 25,00.
  **Duas decisões do grupo sobre a lacuna L12 (05/11/2026):** (1) o valor apurado é a soma das
  vendas do dia **pagas em dinheiro**, porque a gaveta só tem dinheiro; (2) o fechamento é **do dia
  anterior**: as vendas só entram no sistema às 03h00 do dia seguinte, então a esposa conta o
  dinheiro à noite e registra de manhã. Se as vendas daquele dia não entraram, a tela explica o
  motivo e não deixa registrar — senão o apurado sairia zero e a diferença seria falsa.
  **Foi provado que os testes pegam erro:** seis defeitos de propósito (somar PIX e cartão, fechar o
  dia errado, fechar sem as vendas importadas, aceitar importação com erro, não ignorar espaço em
  "Dinheiro", lista fora de ordem) — todos pegos. 35 testes automáticos, dois deles na tela — total
  do projeto: 831, todos passando. Concluída em 05/11/2026, dentro da data prevista (03 a 05/11/2026).

**Próxima tarefa:** E4 — casar o produto pendente da importação com o cadastro (06 e 09/11/2026).

### 04/11/2026

- **Documentação de testes (parte da J1, a pedido do professor).** O professor apontou que faltava
  documentar o que foi testado e aprovado, e o que ainda não foi testado. Criado
  `docs/TESTES.md`: resultado da execução completa de hoje — **726 testes, 726 aprovados** —, os
  testes por tarefa, por regra de negócio, por fluxograma (cada losango pelo "sim" e pelo "não") e
  por requisito; e uma seção do que **ainda não foi testado e por quê**: o que ainda não foi
  construído (RN06 a RN10, importação de vendas, fechamento I1, balanço I3), o que só dá para
  conferir à mão (aviso no celular de verdade, computador antigo, treinamento, teste do sábado
  cheio) e o que está fora do escopo. O documento passa a ser atualizado a cada execução completa.
  A J1 continua em andamento até as regras da previsão.
- **Relatório de testes em PDF (MDGS-TST-001).** O professor achou os arquivos em Markdown
  confusos e pediu um documento oficial, curto e direto. Criado `docs/testes/RELATORIO-DE-TESTES.pdf`,
  com 3 páginas: como foi testado, resultado (726 de 726 aprovados), as 16 regras de negócio com
  o exemplo verificado em cada uma, defeitos encontrados e corrigidos, o que ainda não foi testado
  (com data prevista) e conclusão. Os números são lidos da execução real dos testes, não
  digitados; o PDF é reemitido a cada execução completa.

### 30/10/2026

- **Decisão do grupo — E2 remarcada.** As tabelas de venda (E2), previstas para 26 a 28/10, não
  foram feitas e passam para **02/11**. As que dependem dela andam junto: E3 e I1 para 03 a 05/11,
  G1 para 06/11, E4 e E5 para 06 e 09/11. As demais datas e a entrega (27/11) não mudam.
- **Cronograma em uma página (fora do cronograma).** Criado `docs/CRONOGRAMA.md`, versão curta
  para o professor: o que foi feito em cada dia, com horas; o que falta, com datas; o que já
  funciona; e o que trava. A apresentação foi atualizada para a situação de 30/10.

- **Decisão do grupo — não há cliente real.** O Mercado do Sr. João é uma loja fictícia, criada
  pelo professor para o trabalho. Por isso a reunião com o cliente de 30/10 não acontece e as
  perguntas que dependiam dele foram decididas pelo grupo:
  **D01** — o caixa exporta as vendas em **Excel** (bate com a Apostila IV, que já diz que o
  sobrinho lança notas e vendas no Excel); as colunas da planilha serão definidas na E1.
  **D05** — o sistema roda **no computador do Matheus**; o professor não roda nada, assiste à
  demonstração. Como não existem dados reais, os produtos e as vendas usados nos testes e na
  apresentação serão **de exemplo**, criados pelo grupo. Com isso nenhuma tarefa espera mais
  resposta de fora: o que estava "⛔ Aguarda D01/D05" passou para "⬜ A fazer". Nada muda nas
  horas nem na entrega (27/11).

- **Nova data de entrega: 01/12/2026.** O trabalho tem de estar pronto e ser apresentado em
  01/12 (antes era 27/11). As tarefas continuam previstas até 27/11; os dias de 28 a 30/11 ficam
  de folga para ajustes. O início do projeto é 06/10/2026, o primeiro dia de código.

**Próxima tarefa:** E1 e E2 — colunas da planilha do caixa e tabelas de venda (02/11).

### 23/10/2026

- **Apresentação do andamento do cronograma (fora do cronograma).** Preparada a apresentação
  para o professor: números gerais (31 de 51 tarefas, 212 de 378 h), progresso por etapa e por
  bloco, o que foi entregue em cada dia, o que já funciona, as regras garantidas, a qualidade
  (726 testes), o que falta e por quê, e o cronograma completo tarefa por tarefa.
- **Decisão do grupo — datas no cronograma.** O professor pediu que o cronograma tenha datas. O
  da Apostila IV só tem horas e dependências; as datas das tarefas concluídas são as reais, e as
  das que faltam foram previstas e **aprovadas pelo grupo** (seção "Datas previstas", no início
  deste arquivo), contando com a reunião com o cliente em 30/10. Na apresentação, um gráfico de
  Gantt mostra os dez blocos de 06/10 a 27/11.
- **Banco de dados para a apresentação.** Configurado o DBeaver para mostrar as tabelas e o
  diagrama do banco ao professor, além do acesso pelo terminal descrito no `COMO-RODAR.md`.
  Hoje existem 8 das 14 tabelas da Apostila IV; as outras 6 dependem da D01.

**Próxima tarefa:** E2 — tabelas de venda, item de venda e importação (prevista para 26 a 28/10),
e a reunião com o cliente em 30/10 (D01, D02, D05, L12).

### 21/10/2026

- **Novo visual do painel — piloto na Consulta de estoque (a pedido do grupo, fora do
  cronograma).** O grupo achou o visual parecido com o de todo projeto e pediu algo mais
  profissional. Foi usada a skill *design-taste-frontend*, no modo de telas de trabalho, com o
  estilo "folha emoldurada": o menu fica à esquerda, sobre uma moldura no verde apagado da loja, e
  o trabalho numa folha branca, sem sombras. A cor aparece só onde há informação: vermelho e âmbar
  no que pede atenção, sempre com a palavra junto. **Novidade da tela:** ao lado do saldo, uma régua
  fina mostra quanto tem contra o estoque mínimo (o tracinho do meio é o mínimo). Ela só desenha os
  dois números que a API já mandava; quem diz se está abaixo continua sendo a API (RN01). O resumo
  virou um bloco só, sem ícones, e um zero aparece em cinza, não em vermelho.
  **Decisões do grupo:** (1) estilo "folha emoldurada", entre dois oferecidos; (2) **fonte IBM Plex
  Sans guardada no próprio projeto** (`frontend/fontes/`, uns 60 KB, licença livre OFL). Nada é
  baixado da internet, então a RNF06 continua atendida; (3) começar pela Consulta como piloto; no mesmo dia o
  grupo pediu o visual em todas as telas (só uma com o visual novo parecia defeito), e ele foi
  levado para Login, Produtos, Fornecedores, Entrada, Avarias e Fechamento de caixa.
  **No computador da loja (1024 px)** o menu lateral roubaria a largura da tabela; nessa largura ele
  volta para cima, em abas, e a folha ocupa a tela toda. Conferido em 1440, 1024, 768 e 390 px.
  Mantidos: texto de 16 px, alvos de 44 px, contraste AA (o menor par de texto dá 5,48:1). Nenhum
  dado, regra ou endereço da API mudou. 726 testes automáticos, todos passando.

- **Segunda rodada do visual: tema escuro "mercado de madrugada" (a pedido do grupo).** O grupo
  achou a primeira versão ainda "padrão" e pediu uma cara futurista. A ideia veio do próprio
  sistema: os avisos rodam às 03h00, com a loja fechada. O fundo virou verde-pinho escuro e a cor
  de destaque é o **amarelo das etiquetas de preço da gôndola** (logotipo, botão principal, régua do
  estoque, filtro ligado). Títulos e os números do resumo usam a fonte **Unbounded**, larga e
  geométrica, também guardada no projeto (uns 40 KB, licença OFL). O resumo da Consulta virou um
  painel com números grandes; o Login ganhou um campo inteiro amarelo com o nome da loja. Contraste
  conferido por cálculo: o menor par de texto dá 7,03:1, acima do mínimo AA (4,5:1). Os campos,
  listas e calendário do navegador também ficam escuros. Nada de regra, dado ou API mudou.

### 09/10/2026

- **H6 — Vincular o celular do dono ao usuário.** O sistema já sabe **para qual celular** mandar os
  avisos do Sr. João. O Telegram não deixa mandar mensagem pelo número de telefone — só para quem
  já conversou com o bot —, então a ligação é feita uma vez, na instalação, como a criação dos
  usuários: a equipe roda `vincular_telegram --login joao`, o sistema mostra um **código de 6
  números** (vale 5 minutos) e um link; o Sr. João abre o link no celular e toca em "Iniciar"; o
  sistema reconhece o código, guarda o celular dele e responde no Telegram: "Pronto, Sr. João! Os
  avisos do mercado vão chegar aqui". Trocou de celular, é só repetir.
  **Decisão do grupo:** comando com código (entre três opções: comando com código, número
  digitado à mão, ou pelo próprio bot depois da H7 — esta dependeria de o sistema estar publicado
  na internet, D05, ainda aberta). Sem tela nova e sem endereço novo na API.
  **Cuidados:** só o usuário **dono** pode ser ligado (o banco entregue diz "só o DONO recebe
  aviso"); só vale o código exato, numa conversa particular com o bot (mensagem de grupo ou com
  outro número é ignorada); o código é sorteado de forma imprevisível; se a confirmação não chegar
  ao celular, nada é gravado — assim o sistema nunca guarda um celular errado. Testado de ponta a
  ponta: liga o celular e, em seguida, o aviso de validade chega naquele mesmo chat.
  **Foi provado que os testes pegam erro:** sete defeitos de propósito; seis pegos de primeira (um
  deles — aceitar "1482913" no lugar de "482913" — só depois de um teste novo); o sétimo mostrou
  um trecho de código que não servia para nada, e ele foi retirado. 24 testes automáticos — total
  do projeto: 623, todos passando.
  **Para o aviso chegar de verdade falta só:** criar o bot no @BotFather e pôr o token no `.env`;
  depois, rodar o comando com o Sr. João do lado, com o celular na mão.

- **Análise das telas no celular (a pedido do grupo, fora do cronograma).** Conferidas as 6 telas
  em celular pequeno (360 px), médio (390 px) e tablet (768 px). **Bom:** nenhuma tela "escapa"
  para o lado, Login e formulários funcionam bem, letra dos campos no tamanho que evita o zoom
  automático do iPhone, nenhum botão abaixo do mínimo da norma de acessibilidade. **Ruim:** as
  tabelas — na Consulta de estoque, no celular só aparece o nome do produto (quantidade, validade
  e "Ver lotes" ficam escondidos à direita); o "Editar" de Produtos e Fornecedores também; o
  cabeçalho ocupa duas linhas. **Proposta:** no celular, cada linha de tabela vira um cartão, sem
  mudar dado, regra ou API. **Situação:** corrigido no mesmo dia (abaixo). Observação: a
  especificação pensa o painel para o computador da loja (R04); o celular é do Sr. João, pelo
  Telegram — por isso é melhoria, não requisito.

- **H7 — Receber e registrar a resposta dele.** Fecha a parte de avisos que não depende do caixa.
  Agora cada aviso de "vai acabar" chega no Telegram com um botão **"Sim, pedir: Frango
  resfriado"**; quando o Sr. João toca, o sistema anota no aviso que ele quer pedir e mostra
  "Anotado: pedir Frango resfriado". Vários avisos continuam numa mensagem só (RN13), cada um com
  o seu botão. Aviso de validade vai sem botão: o que se faz com ele é registrar a perda no painel.
  **Decisões do grupo:** (1) o Telegram entrega a resposta chamando um endereço do sistema
  (*webhook*), como está na Apostila IV; (2) só o botão "Sim, pedir", que é o que a especificação
  cita. **Segurança:** esse endereço é o único, além do login, que não pede usuário e senha —
  quem chama é o Telegram. Por isso ele exige uma senha combinada com o Telegram (sem ela, recusa
  tudo, até quem está logado no painel) e só aceita a resposta vinda do celular do dono que
  recebeu aquele aviso; clicar de novo não muda nada; aviso que já não vale (cancelado porque a
  mercadoria chegou) responde "Este aviso não vale mais". A exceção à regra de que toda parte do
  sistema pertence a uma tela foi aprovada pelo grupo e anotada nas regras do repositório.
  **Para funcionar de verdade** falta publicar o sistema na internet com endereço seguro (decisão
  D05) e rodar `configurar_webhook`. Os avisos de "vai acabar" em si vêm da H3, que espera o
  formato do arquivo do caixa (D01) — até lá, testado com avisos criados nos testes.
  **Foi provado que os testes pegam erro:** dez defeitos de propósito, todos pegos — dois deles
  só depois de dois testes novos (pessoa que não é dono com celular ligado; botão com número a
  mais no fim). 39 testes automáticos — total do projeto: 662, todos passando.
  **Pendência que voltou:** em 2 de 5 rodadas completas, um teste de tela (cada vez um diferente,
  de telas que a H7 não toca) falhou por demora; sozinhos, passam sempre. É a mesma falha
  intermitente registrada em 08/10 — **causa achada e corrigida na J1, no mesmo dia** (abaixo).

- **Passo a passo para Windows revisado (fora do cronograma).** O `COMO-RODAR.md` ganhou o que
  faltava para um integrante abrir o sistema sozinho: o que repetir da segunda vez em diante, como
  pegar a versão nova do grupo, o aviso do WSL 2 na instalação do Docker, regras de senha, como
  rodar os testes e mais erros comuns com a solução. Testado de novo num banco vazio: carga dos
  dados, troca de senha e login funcionando.

- **Telas no celular corrigidas (a pedido do grupo, fora do cronograma).** O que a análise do dia
  achou foi resolvido: no celular e no tablet, cada linha das tabelas virou um **cartão** com o nome
  de cada informação ao lado do valor ("Em estoque: 5,5 KG", "Validade: Perto de vencer"), e os
  botões "Editar" e "Ver lotes" ficam embaixo, em largura inteira e na altura certa para o dedo
  (44 px). Na Consulta de estoque, os lotes abrem grudados no cartão do produto; o nome da
  categoria aparece como título entre os cartões; a faixa colorida de vencido e de atenção
  continua. O cabeçalho cabe numa linha só. **No computador da loja (1024 px) nada mudou** — há
  teste conferindo isso nas cinco telas. **Nenhuma mudança de dado, regra ou API.** Para quem usa
  leitor de tela, a tabela continua sendo anunciada como tabela. Conferido: 25 testes novos em
  celular (360 px), tablet (768 px) e computador; sem a correção, 12 deles falham. Auditoria de
  acessibilidade (WCAG 2.2 AA) nas 6 telas, no celular e no computador: nenhuma falha. Total do
  projeto: 687 testes, todos passando.

**Bloco H:** feitas H1, H2, H4, H5, H6 e H7; falta só a H3, que espera a decisão D01.

- **I2 — Tela de fechamento de caixa.** A esposa já tem a tela onde, no fim do dia, confere o
  dinheiro contado na gaveta contra o que o sistema apurou (RF12). Ela digita **só o dinheiro
  contado**; o valor apurado vem do sistema e a diferença aparece **antes de confirmar**, com palavra
  e cor: "Faltam R$ 25,00 no caixa", "Sobram R$ 10,00 no caixa" ou "O caixa bateu" — o exemplo da
  Apostila I (apurado R$ 3.240,00, contado R$ 3.215,00 → −R$ 25,00) está nos testes. Ao registrar, o
  fechamento entra na lista do dia com hora, valores, diferença e quem registrou. Contou de novo?
  Registra outra vez: aparece um registro novo e **o anterior continua lá** (RN15) — a tela não tem
  como alterar nem apagar. Só o perfil da esposa abre a tela (RN14); funciona no celular.
  **Decisão do grupo:** a tela foi feita agora e será **ligada à API na I1**, como aconteceu com
  Produtos e Fornecedores (B5 e B6, ligadas na B7). A I1 (tabela e cálculo) espera as vendas do caixa
  (E2, decisão D01), e a origem exata do "valor apurado" continua aberta (lacuna L12: soma de todas as
  vendas do dia ou só do que foi pago em dinheiro?). Até a I1, a tela avisa: "O fechamento de caixa
  ainda não está disponível… continue conferindo no caderno", e não deixa registrar.
  **Contrato proposto para a I1** (a confirmar quando ela for feita): `GET
  /api/fechamentos/apurado/?data=` (o valor apurado do dia), `GET /api/fechamentos/?data=` (os
  registros do dia, o mais novo primeiro) e `POST /api/fechamentos/` só com `valor_contado` — a data
  e o apurado quem define é o servidor, e a diferença é o banco que calcula (coluna gerada).
  **Achado:** depois de registrar, a tela apagava o campo — e com isso apagava a contagem que a
  pessoa já tivesse começado a digitar enquanto o registro era gravado. Corrigido, com teste.
  **Foi provado que os testes pegam erro:** sete defeitos de propósito (diferença com sinal
  trocado, aceitar três casas de centavo, aceitar valor negativo, mandar o apurado junto, não travar
  sem a API, ler "3.215" como centavos, apagar o que foi digitado) — todos pegos. Auditoria de
  acessibilidade sem nenhuma falha, no celular e no computador. 19 testes — total do projeto: 706,
  todos passando.

- **J1 — Testes automatizados de todas as regras (em andamento).** Duas frentes:
  **(1) Cobertura das regras.** Conferido, regra por regra, que o exemplo de teste escrito na
  Apostila I para cada uma existe como teste automático: RN01 (40 kg − 12 − 3 = 25), RN03, RN04
  (21/09 + 4 dias = 25/09), RN05, RN11, RN12 (11h15 retido, sai 13h05), RN13 (6 avisos, uma
  mensagem), RN14 (a tabela inteira de perfis), RN15 (na tela) e RN16 — todos já estavam. Faltava o
  da **RN02**: "lote que vence 28/09 sai antes do de 05/10, mesmo que o de 05/10 esteja mais à mão";
  foi escrito, e foi provado que ele pega o erro de ordenar pela ordem de chegada. Também foi criado
  um **teste-guarda**: ele lê a lista das 16 regras na especificação e exige que toda regra que já
  existe no código tenha teste com o nome dela. As que ainda não existem — RN06 a RN10, da previsão,
  que esperam o arquivo do caixa (D01) — ficam numa lista com o motivo; quando alguém as programar,
  o guarda passa a cobrar o teste. **Por que a J1 continua em andamento:** ela depende de "todas as
  regras" (cronograma), e faltam a previsão (RN06–RN10), o fechamento no banco (RN15, tarefa I1) e a
  baixa por venda (RN02, tarefa E2) — tudo esperando a D01. Fecha quando elas chegarem.
  **(2) A falha intermitente dos testes de tela — causa achada e corrigida.** Desde 08/10, de vez
  em quando um teste de tela falhava porque "a tela não terminava de carregar". Investigação, passo
  a passo: os registros da API mostraram que ela respondia tudo em milissegundos (API descartada);
  uma "fotografia" tirada no meio de um travamento mostrou os dois servidores parados, esperando
  pedido (banco e servidor descartados — era o navegador que não pedia); o **rastro de rede do
  navegador** mostrou o motivo: ao abrir a tela, o navegador pede uns dez arquivos de programa
  (JavaScript) ao mesmo tempo, e **um deles teve a conexão recusada**; sem ele, nenhum roda, e a
  tela aparece sem menu. **Causa:** o servidor que entrega o painel (`servir.py`) usa o padrão do
  Python, que deixa **no máximo 5 conexões na fila**; com a máquina ocupada, a rajada passa disso.
  Reproduzido de propósito: de 64 pedidos simultâneos, 55 a 59 recusados. **Correção:** fila de 128
  no `servir.py` e no servidor da API dos testes, com teste que dispara a rajada. **Importante:**
  isso não era só problema de teste — o `servir.py` é o que o grupo usa para abrir o painel, e num
  computador mais lento uma tela poderia abrir "pela metade", sem menu. **Resultado:** antes, 4
  falhas em cerca de 9 rodadas no dia; depois da correção, 9 rodadas seguidas sem nenhuma falha.
  Total do projeto: 726 testes, todos passando.

- **Roteiro da reunião com o cliente (fora do cronograma).** Preparado o `REUNIAO-CLIENTE.md`: 24
  perguntas em linguagem da loja, em cinco blocos — o caixa (D01, a que mais trava), a validade
  (D02), o fechamento e o balanço com a esposa (L12, L16, D06), os avisos no celular do Sr. João
  (D04, L01, L03, L15, L24) e a rotina e onde o sistema vai ficar (D03, D05, D07, D08) —, o que
  pedir para separarem antes, o que muda no projeto com cada resposta, o que não prometer e uma
  folha para anotar as respostas. Também marca na agenda o cadastro dos produtos (J2) e a contagem
  do estoque de partida (J3).

**Próxima tarefa:** o que sobra depende de decisão do cliente (D01: blocos E e G, H3, I1, I3 e o
fim da J1; D05: A5, J6) ou da presença dele (J2 carga dos produtos, J3 contagem física). **É hora de
levar ao Sr. João e à esposa as decisões D01 (o caixa exporta as vendas? em que formato?), D02 e a
lacuna L12** — sem elas, o projeto não avança nas etapas 2 e 3.

### 08/10/2026

**Tarefas concluídas: B7, C5, C6, D3, D4, F3, H1 e H2** (56 h estimadas). **Os blocos B, C, D e F estão completos.**

- **B7 — Ligar as telas à API e tratar os erros na tela (inclui a tela de Login, L22).** As telas
  de Produtos e Fornecedores deixaram de usar dados de exemplo: agora leem e gravam no sistema de
  verdade. Para isso nasceu a **tela de Login** — a pessoa entra com login e senha, e o menu
  aparece conforme o seu perfil (RN14): o sobrinho vê Produtos e Fornecedores; a esposa e o
  Sr. João, cujas telas ainda vão ser feitas, veem a lista das telas do seu perfil. A entrada vale
  só enquanto a aba estiver aberta (o computador da loja é compartilhado) e há botão "Sair". Se a
  senha estiver errada, a tela não diz se o erro foi no login ou na senha — dizer ajudaria quem
  tenta adivinhar. O gerenciador de senha e o "colar" funcionam, como pede a norma de
  acessibilidade. Se o perfil não tem acesso a uma tela, ela nem abre (e a API também recusaria).
  **Os erros agora aparecem na tela, em português da loja:** "Sem conexão com o sistema. Confira se
  o computador está na rede e tente de novo."; sessão vencida leva de volta ao Login e, depois de
  entrar, à tela onde a pessoa estava; lista que não carregou diz o porquê e oferece "Tentar de
  novo" — nunca aparece vazia, o que daria a entender que não há nada cadastrado. A frase técnica
  anotada na B6 ("Este campo pode não estar em branco.") virou "Preencha o nome do fornecedor."
  **Decisão L25 — painel e sistema no mesmo endereço:** o navegador bloqueia uma página que fala com
  outro endereço. Em vez de liberar esse bloqueio (o que exigiria uma dependência que o grupo não
  aprovou), o painel e o sistema ficam atrás do mesmo endereço, que é o arranjo usual. Na máquina
  do grupo, um script de 140 linhas, só com o Python, faz esse papel; na publicação (D05), o
  servidor web.
  **Dois problemas que só apareceram ao ligar as telas no sistema de verdade:** (1) a busca "acha
  'feijão' digitando 'feijao'", prometida na B5, funcionava só com os dados de exemplo — o sistema
  diferenciava acento. Corrigido na busca de produtos e na da consulta de estoque, que a tela F3 vai
  usar, sem mexer no banco. (2) Ao digitar o prazo de entrega e clicar direto em "Salvar", o
  clique se perdia: a mensagem de erro do campo sumia nesse instante, o formulário encolhia e o
  botão saía de baixo do mouse. Agora a mensagem some enquanto a pessoa corrige o campo.
  **Limitação conhecida:** se a entrada vencer (12 h) no meio de um cadastro, a pessoa volta ao
  Login e perde o que estava digitando.
  31 testes automáticos — total do projeto: 416, todos passando. Testada num navegador de verdade,
  falando com o sistema, no tamanho do computador da loja e no de um celular: 126 verificações
  (entrar, errar a senha, cadastrar, editar, regra RN03, nome repetido, sem conexão, erro do
  sistema, sessão vencida, sair, perfil sem acesso) e auditoria de acessibilidade (WCAG 2.2, nível
  AA) sem nenhuma falha. As capturas de tela pegaram o cabeçalho ocupando três linhas e o botão
  "Sair" sem borda; os dois foram corrigidos.

**Bloco B completo (B1 a B7):** cadastro de produtos e fornecedores pronto de ponta a ponta — banco,
API, regras e telas ligadas ao sistema.

- **C5 — Tela de entrada de mercadoria (RF03, fluxograma 02).** O sobrinho já registra, na tela,
  cada carga que chega: procura o produto (digitando "frango" ou "feijao", sem precisar de acento),
  informa a quantidade — em quilo fracionado, como a carne —, o custo da nota, a validade e o
  fornecedor. A tela mostra se o produto é perecível e quanto tempo dura, e explica a regra RN04 em
  palavras da loja: "Se deixar em branco, o sistema conta 4 dias a partir de hoje". Quem calcula e
  quem recusa validade vencida é o sistema (a API da C2/C3), nunca a tela; depois de registrar, a
  tela confirma "Entrada registrada: 12,5 KG de Frango resfriado 1 kg. Agora tem 25 KG em estoque.
  Validade calculada: 12/10/2026." Como uma carga traz vários produtos do mesmo fornecedor, ele
  **continua escolhido** para o próximo produto, e o fornecedor de costume do produto já vem
  preenchido. Embaixo, as **entradas de hoje** (operação 02, passo 11); errou, a correção é por
  Avarias e quebras, para o estoque guardar o histórico (RN01). A data de entrada não aparece na
  tela: é sempre o dia da loja, decidido pelo sistema.
  **Decisão de ordem:** a tela já nasceu ligada ao sistema, e não com dados de exemplo como B5 e
  B6 — a API (C2) e a ligação (B7) já existiam, e refazer seria retrabalho. A C6 continua sendo o
  teste do fluxo completo, pela tela.
  **Dois achados das verificações, corrigidos:** o aviso flutuante de "registrado" cobria os campos
  (no celular, por 6 segundos) — virou uma confirmação fixa no topo do formulário, que fica até o
  próximo registro; e no celular a lista do dia, que rola de lado, não podia ser rolada só pelo
  teclado (norma WCAG 2.1.1).
  9 testes automáticos — total do projeto: 425, todos passando. Testada num navegador de verdade,
  falando com o sistema, no tamanho do computador da loja e no de um celular: 120 verificações
  (validade vencida recusada sem gravar nada, validade calculada, validade informada, não perecível
  sem validade, quantidade zero, custo com letras, sem conexão, outro perfil sem acesso) e
  auditoria de acessibilidade (WCAG 2.2, nível AA) sem nenhuma falha.

- **C6 — Integração e teste do fluxo completo da entrada de mercadoria.** O fluxo inteiro agora tem
  **teste automático de ponta a ponta**: um navegador de verdade, controlado pelo teste, abre a
  tela, digita como o sobrinho, clica em "Registrar entrada", e o teste confere o que apareceu na
  tela **e** o que ficou gravado no banco — o lote, a movimentação que explica o saldo (RN01),
  quem registrou e o saldo novo. Estão cobertas as **seis situações do fluxograma 02** (Apostila
  II): cada losango — "é perecível?", "a validade foi informada?", "a validade é anterior a hoje?"
  — pelo "sim" e pelo "não", como manda a Apostila IV. Mais: a lista do dia mostra o que entrou
  hoje e não o de ontem; o fornecedor fica escolhido para o resto da carga; recusa não grava nada e
  não apaga o que foi digitado; o caminho inteiro, do Login até a entrada registrada; e a esposa
  não consegue abrir a tela (RN14). **Foi provado que os testes pegam erro:** quatro defeitos
  introduzidos de propósito (a tela deixar de enviar a validade, a RN04 calcular um dia a menos, o
  fornecedor não ficar escolhido, a validade de hoje ser recusada) — cada um derrubou os testes
  certos, e o código voltou ao original.
  **Decisão do grupo:** entrou a ferramenta **Playwright** (`pytest-playwright`), só para os
  testes — ela não vai para o computador da loja. Até a C5, as verificações de tela eram feitas à
  parte e relatadas aqui; agora ficam guardadas no projeto e qualquer pessoa do grupo as roda com o
  `pytest`. Servem de base para as próximas telas (D4) e para a bateria final de testes (J1).
  Ajuste técnico registrado: com o navegador aberto, o Django passava a guardar a conexão com o
  banco num lugar diferente e o banco de teste não podia ser apagado ao fim; resolvido rodando os
  testes de tela por último. 14 testes de tela — total do projeto: 439, todos passando.

**Bloco C completo (C1 a C6):** a entrada de mercadoria funciona de ponta a ponta — banco, API,
regras de validade e saldo, tela e teste do fluxo inteiro.

- **D3 — Tela de avarias e quebras (RF04, fluxograma 03).** O caderno de avarias do sobrinho virou
  tela: ele procura o produto, diz quanto se perdeu e por quê — com botões "Venceu", "Quebrou" e
  "Estragou" para não precisar escrever —, e a perda sai do estoque. A tela mostra **os lotes do
  produto que estão na loja**, do que vence primeiro para o último, cada um com a situação em
  palavra e cor: "Vencido há 1 dia", "Vence em 2 dias", "Dentro da validade" (RN16). Se ele sabe
  qual lote estragou, escolhe; se não sabe, a opção já marcada deixa o sistema tirar pela ordem de
  validade, começando pelos vencidos (decisão L20). Depois de registrar: "Perda registrada: 4 UN de
  Iogurte natural (Estragou na geladeira). Agora tem 15 UN em estoque. Saiu de 2 lotes, pela ordem
  de validade." Embaixo, as perdas de hoje, com hora, lote, motivo e quem registrou. A perda não se
  apaga (RN01), e a tela avisa isso antes. Todas as regras continuam no sistema (API da D1): a tela
  não decide nada.
  **Achados:** (1) a frase de recusa do sistema dizia "Esse lote só tem 3,000 UN." — agora diz "3 UN",
  como a loja fala; (2) nos testes de tela, a tabela de parâmetros (o "3 dias" do aviso de
  validade) sumia depois do primeiro teste e a lista de lotes falhava — os testes agora a regravam;
  (3) ajustes de aparência vistos nas capturas de tela. As partes comuns às telas de Entrada e de
  Avarias (procurar produto, mostrar erros, confirmar) passaram a ser compartilhadas, e a tela de
  Entrada continua passando nos seus 14 testes de tela.
  15 testes automáticos (7 deles no navegador) — total do projeto: 454, todos passando. Conferida
  no tamanho do computador da loja e no de um celular: 42 verificações e auditoria de
  acessibilidade (WCAG 2.2, nível AA) sem nenhuma falha.

- **D4 — Integração e teste do fluxo de perdas.** Como a C6 fez com a entrada, o registro de perda
  agora tem **teste automático de ponta a ponta**: o navegador usa a tela de Avarias como o
  sobrinho, e o teste confere a tela e o que ficou gravado. Cada decisão do fluxograma 03 testada
  pelo "sim" e pelo "não": **tem motivo?** (sem motivo, ou só com espaços, nada é gravado);
  **escolheu o lote?** (se escolheu, sai só dele; se não, sai pela ordem de validade, o vencido
  primeiro, com uma linha no histórico para cada lote); **a quantidade cabe?** ("Esse lote só tem
  3 UN.", "Só há 19 UN de Iogurte natural no estoque."); **o lote está vencido?** (o iogurte vencido
  da Apostila I sai pela tela, como manda a RN16). E o que a perda não pode fazer: o exemplo da
  especificação — 6 kg de frango vendidos e 10 kg que foram fora: o saldo cai 16 kg e o consumo do
  dia continua 6 kg (RN11) —, e o saldo continua batendo com a soma dos lotes (RN01). Dono e esposa
  não registram perda (RN14). **Foi provado que os testes pegam erro:** quatro defeitos de
  propósito (a tela não enviar o lote escolhido, a ordem de validade pular os vencidos, o sistema
  aceitar motivo em branco, a perda ser contada como consumo) — cada um derrubou os testes certos.
  15 testes de tela — total do projeto: 469, todos passando.

**Bloco D completo (D1 a D4):** perdas e avarias de ponta a ponta — API com motivo obrigatório,
regra de que perda não é consumo, tela e teste do fluxo inteiro.

- **F3 — Tela de consulta de estoque (RF07, RN16).** A única tela que os três usam. No topo, três
  quadros dizem o que precisa de atenção — quantos produtos têm **lote vencido**, quantos estão
  **perto de vencer** e quantos estão **abaixo do mínimo** — e cada quadro, tocado, mostra só aqueles
  produtos. Embaixo, o saldo de cada produto **agrupado por categoria**, com o mínimo, a próxima
  validade e as marcações em palavra e cor ("1 lote vencido", "Perto de vencer", "Abaixo do
  mínimo", "Não pode faltar no fim de semana"). "Ver lotes" abre os lotes do produto, do que vence
  primeiro ao último, com a situação de cada um. Conferido o caso que mais importa: o carvão,
  cadastrado e nunca comprado (saldo zero), aparece como abaixo do mínimo. A tela só mostra — não
  grava nada (RN01), e um teste confere que usá-la não envia nenhuma gravação ao sistema. Todos os
  números vêm calculados pelo sistema (API da F2); para o computador antigo, a lista vem num pedido
  só e procurar e filtrar acontecem na própria tela. **Dono e esposa agora caem nesta tela ao
  entrar** — antes viam só a lista de telas em preparo.
  **Achados, corrigidos:** (1) o botão "Ver lotes" trocava o texto visível para "Esconder lotes",
  mas o leitor de tela continuava lendo "Ver lotes" (norma WCAG 2.5.3) — agora o texto fica e uma
  seta mostra se está aberto; (2) com cinco telas no menu do sobrinho, o cabeçalho quebrava
  desencontrado no computador da loja — o menu passou a ter uma linha própria, embaixo da marca e
  do nome da pessoa, o que também deixa lugar para a sexta tela (Importação de vendas).
  **Observações em aberto:** (a) no celular, a tabela rola de lado dentro do cartão, como nas
  outras telas, e o saldo fica fora da vista inicial; uma versão em "cartões" para telas estreitas
  seria melhor para a esposa consultar pelo celular — fica para o grupo decidir; (b) numa das
  execuções da bateria de testes, um teste deu erro e não se repetiu em 14 execuções seguidas; a
  causa não foi encontrada e o caso fica anotado para a J1.
  19 testes automáticos (16 deles no navegador) — total do projeto: 488, todos passando. Conferida
  com os três perfis, no tamanho do computador da loja e no de um celular: 49 verificações e
  auditoria de acessibilidade (WCAG 2.2, nível AA) sem nenhuma falha.

**Bloco F completo (F1 a F3)** e, com ele, **todas as telas da etapa 1**: Login, Produtos,
Fornecedores, Entrada de mercadoria, Avarias e quebras e Consulta de estoque. Da etapa 1 faltam a
publicação (A5, aguarda D05) e o bloco J (qualidade e implantação).

- **H1 — Tabela de aviso e controle de estado.** Primeira tarefa do bloco de avisos. O sistema já
  tem onde guardar cada aviso que vai para o celular do Sr. João — a tabela `alerta`, **igual à
  Apostila IV** (conferida coluna por coluna pelo teste automático) — e as regras de como um aviso
  muda de situação: nasce **pendente**; se for gerado na hora do movimento, fica **segurado** até a
  janela acabar (RN12); quando sai, todos os da mesma mensagem ficam **enviados** com a mesma hora
  (RN13); e pode ser **cancelado** antes de sair. Enviado e cancelado não mudam mais. Quando a
  mercadoria chega, o aviso de "vai acabar" daquele produto que ainda não saiu é cancelado
  sozinho (operação 02, passo 10) — o ponto de chamada já existia desde a C2 e agora age de
  verdade; aviso de validade e de outro produto não são tocados. As mudanças de situação são à
  prova de duas partes do sistema mexerem no mesmo aviso ao mesmo tempo (a rodada da madrugada e
  uma entrada de mercadoria): vale o que está gravado, e é tudo ou nada.
  **Decisão L11:** a urgência do aviso é **alta, média ou baixa** — a lista é conferida pelo sistema,
  sem mudar o banco entregue (como na L17). Os avisos saem nessa ordem e, empatando, o mais antigo
  primeiro (RN13). **Decisão de escopo:** nenhum endereço novo na API — nenhuma das 10 telas mostra
  avisos; eles só vão para o Telegram.
  **Achado:** a primeira versão do cancelamento automático quebraria toda entrada de mercadoria
  (pedia uma trava de banco fora de transação); foi refeita antes de qualquer teste passar.
  43 testes automáticos — total do projeto: 531, todos passando.

- **H2 — Gerador do aviso de validade (RN05).** O sistema já sabe, a cada rodada, **o que está para
  vencer** e grava o aviso para o Sr. João, com a frase da loja: "Presunto vence em 3 dias — 2,5 KG
  na prateleira.", "vence amanhã", "vence hoje". Testado com o exemplo da Apostila I: lote que vence
  em 24/09, prazo de 3 dias, gera aviso em 21/09; o que vence em 30/09, não. Só produto perecível,
  só lote com mercadoria, e o prazo vem da tabela de parâmetros — mudando para 5 dias, o sistema
  passa a avisar com 5 dias, sem mexer no código. O prazo já é lido produto a produto, para quando
  o grupo decidir a lacuna L01 (prazo por categoria). **Decisões do grupo nesta tarefa:**
  (1) o aviso se repete **todo dia** enquanto o lote estiver no prazo e com mercadoria — pela RN13,
  os do dia chegam juntos numa mensagem só, como a volta pelas gôndolas que o Sr. João faz de manhã;
  rodar duas vezes no mesmo dia não duplica; (2) o lote **já vencido também avisa**, com frase
  própria: "Iogurte natural venceu ontem — 3 UN na prateleira. Tire e registre a perda em Avarias e
  quebras." (RN16). **Decisões de implementação:** o aviso de um dia anterior que não chegou a sair é
  trocado pelo de hoje, com a contagem de dias certa; urgência **alta** para vencido e para o que
  vence hoje, **média** para o resto (L11); o aviso vai para o usuário DONO — sem dono cadastrado,
  ele é gravado mesmo assim e não se perde. **Foi provado que os testes pegam erro:** quatro defeitos
  de propósito (prazo errado por um dia, não perecível avisando, rodada dupla duplicando, aviso
  antigo não trocado) — todos pegos. 22 testes automáticos — total do projeto: 553, todos passando.
  **Falta para o aviso chegar ao celular:** a janela de silêncio e o agrupamento (H4), o envio pelo
  Telegram (H5) e ligar o celular do dono (H6). A rodada das 03h00 (G5) depende da decisão D01;
  até lá, o gerador pode ser chamado sozinho.

- **Redesenho visual do painel (fora do cronograma, a pedido do grupo).** As seis telas ganharam um
  visual mais profissional e fácil de ler, feito com a skill **UI UX Pro Max**: cabeçalho branco
  com o logotipo do mercado, menu com ícone e nome de cada tela (a tela atual destacada em verde),
  a inicial da pessoa num círculo, cartões e tabelas mais leves, marcações em "pílula" (vencido,
  perto de vencer, abaixo do mínimo), "Editar" com ícone de lápis, quadros do resumo da Consulta
  com ícone, e a tela de Login em duas partes, com a marca e o que o sistema faz. No celular, o menu
  vira uma fila que desliza para o lado. **Nada mudou no funcionamento**: mesmos campos, mensagens e
  regras. Conferido: contraste de cada cor calculado pela norma WCAG; auditoria de acessibilidade
  sem nenhuma falha nas 6 telas, no computador da loja e no celular; sem rolagem lateral.
  **Pendência registrada:** alguns testes de tela falham de vez em quando (uma tela que não termina
  de carregar dentro do tempo do teste). Já tinha acontecido uma vez na F3; nas rodadas desta
  sessão foram 4 de 36. Medido que o banco não está travado e descartada a hipótese do servidor de
  testes; a causa ainda não foi encontrada. Fica para investigar à parte (e entra na J1).
  **Resolvida em 09/10 na J1:** fila de conexões do servidor do painel (ver o diário de 09/10).

- **H4 — Janela de silêncio e agrupamento (RN12, RN13).** O sistema já sabe **quando** pode
  mandar aviso e **como** juntar tudo numa mensagem só. Nos horários de movimento (10h30 às 13h e
  16h30 às 18h, lidos da tabela de parâmetros, no horário da loja) nada é enviado: os avisos ficam
  **segurados** e saem na primeira rodada depois do pico. Fora disso, todos os avisos do Sr. João
  saem numa **única mensagem**, numerada do mais urgente para o menos urgente, e ficam marcados
  como enviados com a mesma hora. Testado com os exemplos da Apostila I: aviso das 11h15 fica
  retido e sai às 13h05; seis avisos às 13h05 viram uma mensagem com seis itens, não seis
  mensagens. **Decisões de implementação:** (1) a faixa inclui o começo e não o fim — às 10h30 já
  é silêncio, às 13h00 o aviso já pode sair ("entre 10h30 e 13h"); (2) se o envio falhar (sem
  internet), nada é marcado como enviado e a próxima rodada tenta de novo; (3) aviso sem
  destinatário (sem dono cadastrado) fica esperando, não some; (4) cada pessoa recebe só os seus
  avisos, uma mensagem por pessoa. O envio é feito por uma "porta" (`CanalDeAviso`, decisão D04):
  o Telegram de verdade entra na H5 sem mudar esta parte. **Foi provado que os testes pegam erro:**
  quatro defeitos de propósito (fim da janela incluído, relógio em UTC, ordem sem urgência, um
  envio por aviso) — todos pegos. 27 testes automáticos — total do projeto: 580, todos passando.

- **Projeto pronto para rodar em outro computador (fora do cronograma, a pedido do grupo).** O
  código foi para um repositório privado no GitHub (`MatheusLoureiro7/mercadinho`), com um passo a
  passo para Windows (`COMO-RODAR.md`): instalar, baixar, configurar, ligar e ver as tabelas do
  banco para a apresentação. Junto vai uma cópia dos dados de desenvolvimento (produtos, lotes,
  movimentações) que se carrega com um comando — testada num banco vazio. Os usuários vão **sem
  senha** (senha não vai para o GitHub); cada integrante define a sua no próprio computador.

- **H5 — Integração com o serviço de mensagens (Telegram).** O sistema já **manda a mensagem de
  verdade** para o Telegram. Um comando (`enviar_avisos`) faz a rodada inteira: respeita o horário
  de movimento (H4), junta os avisos de cada pessoa numa mensagem só e envia pelo bot. É esse
  comando que o agendador vai chamar (G5). Usa só o que já vem com o Python, sem programa novo.
  **O que acontece quando algo dá errado:** sem internet, bot sem configurar, celular da pessoa
  ainda não ligado ao sistema (H6) ou Telegram recusando — os avisos daquela pessoa **ficam
  guardados** para a próxima rodada, as outras pessoas recebem normalmente, e o comando termina
  avisando que houve falha, com o motivo no registro (log). **Segurança (RNF12):** a "senha" do
  bot (token) fica só no arquivo de configuração e nunca aparece em mensagem de erro nem no log —
  há um teste só para isso. **Decisões de implementação:** (1) a mensagem vai em texto simples,
  sem negrito, para que um símbolo no nome de um produto não faça o Telegram recusar; (2) se a
  lista de avisos passar do limite do Telegram (4096 letras), ela é dividida em mais de uma
  mensagem, sem cortar nenhuma linha e na mesma ordem — é o único caso em que a RN13 vira mais de
  uma mensagem, porque o Telegram não aceita maior. Testado contra um "Telegram de mentira" na
  própria máquina (a conversa pela internet é de verdade, só o endereço muda). **Foi provado que
  os testes pegam erro:** cinco defeitos de propósito, todos pegos — e um sexto (o token vazando
  pela exceção original) passou na primeira versão do teste, que foi reforçada até pegá-lo.
  19 testes automáticos — total do projeto: 599, todos passando.
  **Para o aviso chegar ao celular do Sr. João falta:** criar o bot no @BotFather e pôr o token
  no `.env`, e a H6 (ligar o celular dele ao usuário).

**Próxima tarefa:** H6 — vincular o celular do dono ao usuário (feita em 09/10).

### 07/10/2026

**Tarefas concluídas: C2, C3, D1, D2, F1, F2, B5 e B6** (47 h estimadas).

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

- **F1 — Visão de estoque por produto e por lote (RF07, RN16).** O sistema já sabe montar a
  "foto" do estoque que a tela de consulta vai mostrar: por produto — saldo, categoria, se está
  **abaixo do mínimo**, quantos lotes estão **vencidos** e **vencendo** e a validade mais próxima —
  e por lote — quanto resta, quantos dias faltam para vencer e a situação (vencido, vencendo, dentro
  da validade, sem validade). Testado com os exemplos da Apostila I: o iogurte vencido em 20/09
  aparece destacado em 21/09 (RN16); o lote que vence em 24/09 aparece como "vencendo" em 21/09,
  com o parâmetro de 3 dias (RN05). E foi conferido que a soma do que resta nos lotes bate com o
  saldo depois de entradas e perdas. A visão é feita com consultas sobre o que já existe — nenhum
  objeto novo foi criado no banco, que na apostila só tem a visão de saldo.
  **Decisão L21:** a tabela de parâmetros (o "3 dias" do aviso, os "14 dias" de histórico etc.)
  está no modelo de dados mas não estava em nenhuma tarefa do cronograma; foi criada aqui, igual à
  apostila, com os 7 valores iniciais. 25 testes automáticos — total do projeto: 352, todos
  passando.

- **F2 — API de consulta de estoque com filtros (RF07).** A consulta de estoque — a única tela que
  os três (dono, esposa e sobrinho) usam — já tem a sua API: saldo por produto e por lote, agrupado
  por categoria, com filtros "só o que está abaixo do mínimo", "só o que está vencendo ou vencido",
  por categoria, por produto e por nome. O lote vencido aparece destacado (RN16) e ninguém consegue
  gravar nada por ela (RN01). Pensando no computador antigo da loja (RNF06), um teste garante que a
  consulta faz no máximo 4 idas ao banco, tenha a loja 50 ou 2.000 produtos. 33 testes automáticos —
  total do projeto: 385, todos passando.

**Marco: metade da etapa 1.** Toda a parte de banco, API e regras da etapa 1 que não depende de
decisão do cliente está pronta. Faltam as telas (B5–B7, C5–C6, D3–D4, F3), a publicação (A5,
aguarda D05) e o bloco J.

- **B5 — Tela de produtos (primeira tela do painel).** Feita com a skill de design **UI UX Pro
  Max**, que gerou o sistema visual do painel inteiro (estilo limpo e funcional, cinza-ardósia com
  verde de estoque). Cada sugestão da ferramenta foi conferida contra a especificação e adaptada
  quando necessário: fonte do próprio computador, para não baixar nada da internet (computador
  antigo, RNF06), e um verde mais escuro, porque o sugerido não tinha contraste suficiente com texto
  branco — conferido por cálculo, pela norma de acessibilidade WCAG. A tela lista os produtos com
  busca (acha "feijão" digitando "feijao") e filtro por categoria, e cadastra e edita com tudo o que
  o RF01 pede, em português da loja ("Não pode faltar no fim de semana"). Quando algo é recusado,
  **nada do que foi digitado se perde** e só o campo com problema é apontado (fluxograma 01). Como
  manda o roteiro, nesta tarefa a tela usa dados de exemplo; a ligação com a API é a B7. A tela foi
  testada num navegador de verdade, no tamanho do computador da loja e no de um celular: 38
  verificações automáticas (teclado, foco, tamanho dos botões, contraste, nada cortado). As capturas
  de tela pegaram um problema que o teste não pegou — no computador da loja o botão "Editar" ficava
  fora da tela — e ele foi corrigido.
  **Lacunas novas:** L22 — a tela de Login não tem tarefa no cronograma; será feita na B7. L23 — a
  Apostila IV promete o aviso de vencimento no celular já na etapa 1, mas as horas dele estão no
  bloco H (etapa 2); o grupo precisa corrigir uma das duas coisas.

- **B6 — Tela de fornecedores (RF02).** Segunda tela do painel, no mesmo visual da tela de produtos
  e sem nenhum estilo novo. O sobrinho cadastra e edita quem entrega a mercadoria: nome, contato,
  pedido mínimo e — o que mais importa — **em quantos dias o fornecedor entrega depois do pedido**.
  A tela explica por que esse número importa, em palavras da loja: é com ele que o sistema avisa a
  tempo de o fornecedor entregar antes de o produto acabar (RN08). Na lista o prazo aparece como
  "1 dia", "3 dias" ou "No mesmo dia". Fornecedor não tem botão de excluir, porque é cadastro de
  origem e nunca é apagado (L18). Quando algo é recusado, nada do que foi digitado se perde. As
  mensagens de recusa da tela são as mesmas da API, conferidas rodando a própria API. Ainda usa
  dados de exemplo, e a ligação com a API é a B7. Testada num navegador de verdade, no tamanho do
  computador da loja e no de um celular: 47 verificações automáticas, mais a auditoria de
  acessibilidade (norma WCAG 2.2, nível AA) sem nenhuma falha. A tela de produtos continua passando
  nas 38 dela.
  **Lacuna nova:** L24 — a apostila não diz se o pedido mínimo é em reais ou em quantidade. Adotamos
  reais, pela convenção do próprio modelo de dados, e o grupo precisa confirmar.
  **Anotado para a B7:** quando o nome fica em branco, a mensagem padrão da API é "Este campo pode
  não estar em branco.", uma tradução ruim do Django REST Framework. Ela deve ser trocada por uma
  frase clara ao ligar as telas à API.

**Bloco B:** banco, API e as duas telas prontos (B1 a B6). Falta ligar as telas à API (B7).

**Próxima tarefa:** B7 — ligar as telas à API e tratar os erros na tela (inclui a tela de Login, L22).

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

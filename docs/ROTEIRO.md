# Roteiro de implementação

As **52 tarefas da Apostila IV**, seção 9, na ordem em que podem ser feitas.
Total: **378 horas**. Os códigos (A1 … J6), as horas e as dependências são os da apostila.

**Não pule tarefa.** A ordem vem de dependência real: o modelo de dados sustenta quase tudo e por
isso vem primeiro. A própria apostila diz que a pessoa de dados é o gargalo do projeto.

Marque `[x]` quando a tarefa estiver pronta **e testada**.

---

## Bloco A — Fundação · 40 h

| | ID | Tarefa | Tipo | Depende de | H |
|---|---|---|---|---|---|
| [x] | **A1** | Configurar repositório, ambiente e padrão de código | Infra | — | 6 |
| [x] | **A2** | Subir o banco de dados e a ferramenta de migração | Infra/BD | A1 | 6 |
| [x] | **A3** | Esqueleto da API: rotas, tratamento de erro e registro de log | API | A1 | 10 |
| [x] | **A4** | Autenticação e os três perfis de acesso | API/Regra | A3, B1 | 12 |
| [ ] | **A5** | Esteira de publicação em ambiente de teste | Infra | A1 | 6 |

**A4 implementa a RN14.** A verificação de papel acontece antes de qualquer operação, na camada de
autenticação — não dentro de cada regra de negócio.

---

## Bloco B — Cadastros · 46 h

| | ID | Tarefa | Tipo | Depende de | H |
|---|---|---|---|---|---|
| [x] | **B1** | Criar as tabelas de usuário, categoria, produto e fornecedor | BD | A2 | 6 |
| [x] | **B2** | API de categoria e fornecedor | API | B1, A3 | 8 |
| [x] | **B3** | API de produto, com validações | API | B1, A3 | 10 |
| [x] | **B4** | Regra: perecível exige prazo de durabilidade | Regra | B3 | 3 |
| [x] | **B5** | Tela de produtos | Tela | A3 | 8 |
| [x] | **B6** | Tela de fornecedores | Tela | A3 | 6 |
| [x] | **B7** | Ligar as telas à API e tratar os erros na tela | Tela | B2, B3, B5, B6 | 5 |

**B4 = RN03.** **B2** precisa guardar `prazo_entrega_dias`, que é o número que faz o ponto de
pedido funcionar lá no bloco G.

As telas B5 e B6 começam com dados fixos no próprio código e só em B7 passam a falar com a API.
É por isso que elas não dependem de B2/B3 — é o que permite front e back andarem em paralelo.

---

## Bloco C — Entrada de mercadoria · 40 h

| | ID | Tarefa | Tipo | Depende de | H |
|---|---|---|---|---|---|
| [x] | **C1** | Criar as tabelas de lote e movimentação | BD | A2 | 6 |
| [x] | **C2** | API de entrada de lote | API | C1, B3 | 8 |
| [x] | **C3** | Regra: validade obrigatória e cálculo automático | Regra | C2 | 4 |
| [x] | **C4** | Saldo derivado das movimentações | BD/Regra | C1 | 6 |
| [x] | **C5** | Tela de entrada de mercadoria | Tela | A3 | 10 |
| [x] | **C6** | Integração e teste do fluxo completo | Tela/Teste | C2, C5 | 6 |

**C3 = RN04.** **C4 = RN01** — é a view `vw_estoque_atual`, e é a tarefa mais importante do
projeto inteiro: tudo que vem depois consulta esse saldo.

**C2 abre transação** e grava lote + movimentação juntos (operação 02, passo 7).

---

## Bloco D — Perdas e avarias · 18 h

| | ID | Tarefa | Tipo | Depende de | H |
|---|---|---|---|---|---|
| [x] | **D1** | API de registro de perda, com motivo obrigatório | API | C1 | 6 |
| [x] | **D2** | Regra: perda não entra na base de consumo | Regra | D1 | 3 |
| [x] | **D3** | Tela de avarias e quebras | Tela | A3 | 7 |
| [x] | **D4** | Integração e teste | Tela/Teste | D1, D3 | 2 |

**D2 = RN11.** Parece pequena (3 h) e é uma das mais críticas do sistema. Se furar, quanto mais
produto estraga, mais o sistema manda comprar.

---

## Bloco E — Entrada das vendas · 44 h ⚠️ depende da decisão D01

| | ID | Tarefa | Tipo | Depende de | H |
|---|---|---|---|---|---|
| [ ] | **E1** | Levantar o formato do arquivo exportado pelo caixa | Análise | **confirmação com o cliente** | 6 |
| [ ] | **E2** | Criar as tabelas de venda, item de venda e importação | BD | A2 | 6 |
| [ ] | **E3** | Serviço que lê o arquivo e gera venda e movimentação | API | E1, E2 | 16 |
| [ ] | **E4** | Casar o produto do caixa com o produto cadastrado | API/Regra | E3 | 10 |
| [ ] | **E5** | Tela de acompanhamento da importação | Tela | E3 | 6 |

**E2 não depende de D01** e pode ser feita desde já. **E3 e E4 dependem.**

Enquanto D01 não for respondida: escreva o leitor atrás de uma interface
(`LeitorDeArquivoDoCaixa`) com uma implementação de exemplo em CSV, e deixe o parser real para
quando o formato for conhecido. **Não chute o formato e saia implementando.**

---

## Bloco F — Consulta de estoque · 22 h

| | ID | Tarefa | Tipo | Depende de | H |
|---|---|---|---|---|---|
| [x] | **F1** | Visão de estoque por produto e por lote | BD | C4 | 6 |
| [x] | **F2** | API de consulta com filtros | API | F1 | 6 |
| [x] | **F3** | Tela de estoque, com destaque para mínimo e vencidos | Tela | A3 | 10 |

**F3 implementa a parte visual da RN16**: lote vencido aparece destacado.

---

## Bloco G — Previsão · 40 h ⚠️ depende da decisão D01

| | ID | Tarefa | Tipo | Depende de | H |
|---|---|---|---|---|---|
| [ ] | **G1** | Tabela de consumo diário e rotina de agregação | BD/API | E2 | 10 |
| [ ] | **G2** | Cálculo do consumo médio e por dia da semana | Regra | G1 | 12 |
| [ ] | **G3** | Tabela de previsão e gravação do resultado | BD/API | G2 | 8 |
| [ ] | **G4** | Regra: histórico mínimo antes de projetar | Regra | G2 | 4 |
| [ ] | **G5** | Agendador das rotinas diárias | Infra | G3 | 6 |

**G1 = RN11** (filtra só VENDA) · **G2 = RN06 e RN07** · **G3 = RN08** · **G4 = RN09**.

G2 é a tarefa mais difícil do projeto. Comece pela média simples (RN06), faça passar no teste, e só
depois acrescente a média por dia da semana (RN07).

---

## Bloco H — Avisos · 52 h ⚠️ depende da decisão D01

| | ID | Tarefa | Tipo | Depende de | H |
|---|---|---|---|---|---|
| [ ] | **H1** | Tabela de aviso e controle de estado | BD/API | A2 | 8 |
| [ ] | **H2** | Gerador do aviso de validade | Regra | H1, C3 | 8 |
| [ ] | **H3** | Gerador do aviso de ruptura | Regra | H1, G3 | 10 |
| [ ] | **H4** | Janela de silêncio e agrupamento | Regra | H1 | 8 |
| [ ] | **H5** | Integração com o serviço de mensagens | API | H1 | 10 |
| [ ] | **H6** | Vincular o celular do dono ao usuário | API | H5, B1 | 4 |
| [ ] | **H7** | Receber e registrar a resposta dele | API | H5 | 4 |

**H2 = RN05** · **H3 = RN08 e RN10** · **H4 = RN12 e RN13**.

**H2 não depende de D01.** O aviso de validade só precisa de `lote.data_validade`, que vem da
entrada de mercadoria. É a parte do produto que entrega valor mais cedo e sem depender do caixa.

**H3 depende**, porque ruptura precisa de consumo, que precisa de venda.

---

## Bloco I — Fechamento e relatórios · 30 h

| | ID | Tarefa | Tipo | Depende de | H |
|---|---|---|---|---|---|
| [ ] | **I1** | Tabela de fechamento e cálculo da diferença | BD/Regra | E2 | 8 |
| [ ] | **I2** | Tela de fechamento de caixa | Tela | A3 | 10 |
| [ ] | **I3** | Relatório de balanço semanal | API/Tela | E2, D1 | 12 |

**I1 = RN15**: a diferença é calculada, nunca digitada, e o registro nunca é alterado nem apagado.
**I3**: perdas aparecem em linha separada das vendas (RN11).

---

## Bloco J — Qualidade e implantação · 46 h

| | ID | Tarefa | Tipo | Depende de | H |
|---|---|---|---|---|---|
| [ ] | **J1** | Testes automatizados de todas as regras | Teste | todas as regras | 16 |
| [ ] | **J2** | Carga inicial dos produtos, junto com o cliente | Dados | B3 | 8 |
| [ ] | **J3** | Inventário de partida: contagem física | Dados | J2 | 6 |
| [ ] | **J4** | Teste em movimento real, num sábado cheio | Teste | todos | 6 |
| [ ] | **J5** | Treinamento das três pessoas | — | J4 | 4 |
| [ ] | **J6** | Implantação e acompanhamento da primeira semana | Infra | J4 | 6 |

**J1 não é para deixar para o fim.** Escreva o teste junto com cada regra; J1 é o fechamento e a
cobertura que faltou, não o começo.

---

## Totais

| Etapa | Blocos | Esforço | O que passa a funcionar |
|---|---|---|---|
| 1 · Aviso de validade | A, B, C, D, F, J | **212 h** | Cadastro, entrada com validade, perdas, consulta de estoque e o aviso de vencimento chegando ao celular. Já ataca a maior dor do cliente. |
| 2 · Aviso de ruptura | E, G, H | **136 h** | Vendas entrando no sistema, previsão de consumo e o aviso de "vai acabar". |
| 3 · Gestão | I | **30 h** | Fechamento de caixa e balanço semanal, substituindo o caderno. |
| | | **378 h** | |

---

## Por onde começar hoje

**166 das 378 horas** — blocos **A, B, C, D e F** — não dependem de nenhuma decisão pendente.
O modelo de dados e as telas de cadastro podem começar imediatamente, porque os tipos de dados já
estão definidos.

Ordem sugerida para a primeira semana de código:

1. **A1** repositório e ambiente
2. **A2** banco e migrações
3. **A3** esqueleto da API
4. **B1** tabelas de usuário, categoria, produto e fornecedor
5. **C1** tabelas de lote e movimentação

Com isso de pé, três pessoas podem trabalhar em paralelo: API (B2, B3), telas (B5, B6) e
saldo derivado (C4).

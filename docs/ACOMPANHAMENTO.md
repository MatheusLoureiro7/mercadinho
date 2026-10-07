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

*Atualizado em 06/10/2026.*

| | Concluído | Total | % |
|---|---|---|---|
| **Tarefas** | 2 | 51 | 3,9 % |
| **Horas estimadas** | 12 h | 378 h | 3,2 % |

| Etapa | Blocos | Horas concluídas | Total | % |
|---|---|---|---|---|
| 1 · Aviso de validade | A, B, C, D, F, J | 12 h | 212 h | 5,7 % |
| 2 · Aviso de ruptura | E, G, H | 0 h | 136 h | 0,0 % |
| 3 · Gestão | I | 0 h | 30 h | 0,0 % |

As horas concluídas são as **estimadas** na apostila para cada tarefa entregue, não horas medidas.

Prazo de entrega: **27/11/2026**.

---

## Bloco A — Fundação · 40 h  ·  12 de 40 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~A1~~ | ~~Configurar repositório, ambiente e padrão de código~~ | — | 6 | ✅ Concluída | 06/10/2026 | `ca4ac9b` |
| ~~A2~~ | ~~Subir o banco de dados e a ferramenta de migração~~ | A1 | 6 | ✅ Concluída | 06/10/2026 | `02c5ae1` |
| A3 | Esqueleto da API: rotas, tratamento de erro e registro de log | A1 | 10 | ⬜ A fazer | — | — |
| A4 | Autenticação e os três perfis de acesso | A3, B1 | 12 | ⬜ A fazer | — | — |
| A5 | Esteira de publicação em ambiente de teste | A1 | 6 | ⛔ Aguarda D05 | — | — |

## Bloco B — Cadastros · 46 h  ·  0 de 46 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| B1 | Criar as tabelas de usuário, categoria, produto e fornecedor | A2 | 6 | ⬜ A fazer | — | — |
| B2 | API de categoria e fornecedor | B1, A3 | 8 | ⬜ A fazer | — | — |
| B3 | API de produto, com validações | B1, A3 | 10 | ⬜ A fazer | — | — |
| B4 | Regra: perecível exige prazo de durabilidade | B3 | 3 | ⬜ A fazer | — | — |
| B5 | Tela de produtos | A3 | 8 | ⬜ A fazer | — | — |
| B6 | Tela de fornecedores | A3 | 6 | ⬜ A fazer | — | — |
| B7 | Ligar as telas à API e tratar os erros na tela | B2, B3, B5, B6 | 5 | ⬜ A fazer | — | — |

## Bloco C — Entrada de mercadoria · 40 h  ·  0 de 40 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| C1 | Criar as tabelas de lote e movimentação | A2 | 6 | ⬜ A fazer | — | — |
| C2 | API de entrada de lote | C1, B3 | 8 | ⬜ A fazer | — | — |
| C3 | Regra: validade obrigatória e cálculo automático | C2 | 4 | ⬜ A fazer | — | — |
| C4 | Saldo derivado das movimentações | C1 | 6 | ⬜ A fazer | — | — |
| C5 | Tela de entrada de mercadoria | A3 | 10 | ⬜ A fazer | — | — |
| C6 | Integração e teste do fluxo completo | C2, C5 | 6 | ⬜ A fazer | — | — |

## Bloco D — Perdas e avarias · 18 h  ·  0 de 18 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| D1 | API de registro de perda, com motivo obrigatório | C1 | 6 | ⬜ A fazer | — | — |
| D2 | Regra: perda não entra na base de consumo | D1 | 3 | ⬜ A fazer | — | — |
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

### 06/10/2026

**Tarefas concluídas: A1 e A2** (12 h estimadas).

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

**Próxima tarefa:** A3 — esqueleto da API (rotas, tratamento de erro e registro de log).

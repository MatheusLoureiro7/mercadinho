# Cronograma — Sistema de Estoque e Compras do Mercado do Sr. João

**Grupo MDGS** · Engenharia de Software · Situação em **30/10/2026** · Entrega em **27/11/2026**

Cronograma da Apostila IV, seção 9 (entregue em 25/09/2026), com as datas: as das tarefas
feitas são as reais; as das que faltam foram previstas e aprovadas pelo grupo em 23/10/2026.
O detalhe tarefa por tarefa, com commit, está em `docs/ACOMPANHAMENTO.md`.

---

## 1. Resumo

| | Feito | Total | % |
|---|---|---|---|
| Tarefas | 31 | 51 | 60,8 % |
| Horas estimadas | 212 h | 378 h | 56,1 % |

**Faltam 166 h e 20 tarefas · 28 dias até a entrega (27/11/2026).**

As horas são as estimadas na apostila para cada tarefa entregue, não horas medidas.

### O que foi feito em cada dia

| Data | Tarefas concluídas | Horas |
|---|---|---|
| 06/10/2026 | A1, A2, A3, A4, B1, B2, B3, B4, C1, C4 — repositório, banco, API, login e perfis, cadastros, saldo | 73 h |
| 07/10/2026 | B5, B6, C2, C3, D1, D2, F1, F2 — telas de produtos e fornecedores, entrada de lote, validade, perdas, consulta | 47 h |
| 08/10/2026 | B7, C5, C6, D3, D4, F3, H1, H2, H4, H5 — telas de entrada, avarias e estoque, avisos de validade, Telegram | 74 h |
| 09/10/2026 | H6, H7, I2 — celular do dono, resposta pelo Telegram, tela de fechamento de caixa | 18 h |
| **Total** | **31 tarefas** | **212 h** |

## 2. Andamento por bloco

| Bloco | Horas feitas | Situação | Quando |
|---|---|---|---|
| A · Fundação | 34 de 40 h | Falta A5 (publicação no computador do Matheus) | 06/10 · A5 em 03–04/11 |
| B · Cadastros | 46 de 46 h | ✅ Concluído | 06 a 08/10 |
| C · Entrada de mercadoria | 40 de 40 h | ✅ Concluído | 06 a 08/10 |
| D · Perdas e avarias | 18 de 18 h | ✅ Concluído | 07 e 08/10 |
| E · Entrada das vendas | 0 de 44 h | A fazer — leitura da planilha Excel do caixa | 02 a 09/11 |
| F · Consulta de estoque | 22 de 22 h | ✅ Concluído | 07 e 08/10 |
| G · Previsão | 0 de 40 h | A fazer | 06 a 13/11 |
| H · Avisos no Telegram | 42 de 52 h | Falta H3 (aviso de "vai acabar") | 08–09/10 · H3 em 12–13/11 |
| I · Fechamento e relatórios | 10 de 30 h | Tela pronta; faltam I1 e I3 | 09/10 · resto 03 a 11/11 |
| J · Qualidade e implantação | 0 de 46 h | J1 em andamento (testes) | 09/10 a 27/11 |

## 3. O que já funciona

- **Login e três perfis** — dono, esposa e sobrinho veem só as suas telas (RN14).
- **Produtos e fornecedores** — perecível sem prazo de durabilidade é recusado (RN03).
- **Entrada de mercadoria** — validade calculada sozinha quando não vem na embalagem (RN04).
- **Avarias e quebras** — perda sempre com motivo, sai do lote que vence primeiro (RN02).
- **Consulta de estoque** — vencidos, perto de vencer e abaixo do mínimo em destaque (RN16).
- **Aviso de validade no Telegram** — "Presunto vence em 3 dias — 2,5 kg na prateleira" (RN05).

726 testes automáticos, todos passando.

## 4. O que falta, com data e horas

| Data | O que vai ser feito | Tarefas | Horas |
|---|---|---|---|
| 02/11 | Definir a planilha Excel do caixa e criar as tabelas de venda | E1, E2 | 12 h |
| 03 a 05/11 | Ler a planilha e gerar as vendas; cálculo do fechamento de caixa | E3, I1 | 24 h |
| 03 e 04/11 | Publicar o sistema no computador do Matheus | A5 | 6 h |
| 06/11 | Somar o consumo de cada dia | G1 | 10 h |
| 06 e 09/11 | Casar o produto do caixa com o cadastro; tela da importação | E4, E5 | 16 h |
| 09 a 11/11 | Carga dos produtos de exemplo; consumo médio; balanço semanal | J2, G2, I3 | 32 h |
| 11/11 | Previsão de quando cada produto acaba | G3, G4 | 12 h |
| 12 e 13/11 | Rotina das 03h00 e aviso de "vai acabar" no Telegram | G5, H3 | 16 h |
| 17/11 | Contagem de partida do estoque | J3 | 6 h |
| até 18/11 | Fim dos testes automáticos de todas as regras | J1 | 16 h |
| 21/11 (sábado) | Teste com um dia cheio de vendas | J4 | 6 h |
| 23/11 | Treinamento e demonstração | J5 | 4 h |
| 23 a 27/11 | Implantação | J6 | 6 h |
| **27/11** | **Entrega** | **20 tarefas** | **166 h** |

## 5. Decisões de 30/10/2026

O Mercado do Sr. João é uma loja **fictícia**, criada pelo professor. Não há cliente para
responder perguntas nem dados reais, então o grupo decidiu:

- **D01 — vendas:** o caixa exporta as vendas numa **planilha Excel**, que o sistema lê.
- **D05 — onde roda:** **no computador do Matheus**. O professor não roda nada; assiste à demonstração.
- **Dados:** produtos e vendas usados nos testes e na apresentação são **de exemplo**, criados pelo grupo.

Com isso, **nenhuma tarefa depende mais de resposta de fora**: as 166 h que faltam são só trabalho
do grupo.

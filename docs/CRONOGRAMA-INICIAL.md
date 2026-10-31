# Cronograma inicial (planejado) — Mercado do Sr. João

**Grupo MDGS** · Engenharia de Software · **Início: 06/10/2026** · **Entrega e apresentação final: 01/12/2026**

É o **plano**: as 51 tarefas do cronograma da Apostila IV (seção 9, entregue em 25/09/2026), na
ordem em que o grupo planejou fazer tudo, com a data prevista de início e fim de cada uma. A
apostila trazia as tarefas, as horas e as dependências, mas não as datas; as datas abaixo foram
**calculadas em 30/10/2026** com essa mesma ordem, contando cerca de **11 h de trabalho do grupo
por dia útil** a partir de 06/10.

**Não é o andamento real.** O que de fato foi feito, e em que dia, está em `docs/CRONOGRAMA.md`.

---

## Resumo por semana

| Semana | De | Até | Tarefas previstas | Horas |
|---|---|---|---|---|
| 1 | 06/10 (ter) | 09/10 (sex) | A1, A2, A3, B1, A4, B2 | 44 h |
| 2 | 12/10 (seg) | 16/10 (sex) | B2, B3, B4, B5, B6, B7, C1, C4, C2 | 55 h |
| 3 | 19/10 (seg) | 23/10 (sex) | C2, C3, C5, C6, D1, D2, D3, D4, F1, F2, F3 | 55 h |
| 4 | 26/10 (seg) | 30/10 (sex) | F3, H1, H2, H4, H5, H6, H7, J2 | 55 h |
| 5 | 02/11 (seg) | 06/11 (sex) | J2, J3, E1, E2, E3, E4, E5, G1 | 55 h |
| 6 | 09/11 (seg) | 13/11 (sex) | G1, G2, G3, G4, G5, H3, I1, I2 | 55 h |
| 7 | 16/11 (seg) | 21/11 (sáb) | I2, I3, A5, J1, J4 | 49 h |
| 8 | 23/11 (seg) | 27/11 (sex) | J5, J6 (implantação e primeira semana) | 10 h |
| | | | **51 tarefas** | **378 h** |

Folga de 28 a 30/11 · **01/12/2026 (ter): entrega e apresentação final**

---

## Etapa 1 · Aviso de validade · 216 h

| Ordem | Tarefa | O que é | Depende de | Horas | Início | Fim |
|---|---|---|---|---|---|---|
| 1 | A1 | Configurar repositório, ambiente e padrão de código | — | 6 | 06/10 (ter) | 06/10 (ter) |
| 2 | A2 | Subir o banco de dados e a ferramenta de migração | A1 | 6 | 06/10 (ter) | 07/10 (qua) |
| 3 | A3 | Esqueleto da API: rotas, tratamento de erro e registro de log | A1 | 10 | 07/10 (qua) | 07/10 (qua) |
| 4 | B1 | Criar as tabelas de usuário, categoria, produto e fornecedor | A2 | 6 | 08/10 (qui) | 08/10 (qui) |
| 5 | A4 | Autenticação e os três perfis de acesso | A3, B1 | 12 | 08/10 (qui) | 09/10 (sex) |
| 6 | B2 | API de categoria e fornecedor | B1, A3 | 8 | 09/10 (sex) | 12/10 (seg) |
| 7 | B3 | API de produto, com validações | B1, A3 | 10 | 12/10 (seg) | 13/10 (ter) |
| 8 | B4 | Regra: perecível exige prazo de durabilidade | B3 | 3 | 13/10 (ter) | 13/10 (ter) |
| 9 | B5 | Tela de produtos | A3 | 8 | 13/10 (ter) | 14/10 (qua) |
| 10 | B6 | Tela de fornecedores | A3 | 6 | 14/10 (qua) | 14/10 (qua) |
| 11 | B7 | Ligar as telas à API e tratar os erros na tela | B2, B3, B5, B6 | 5 | 14/10 (qua) | 15/10 (qui) |
| 12 | C1 | Criar as tabelas de lote e movimentação | A2 | 6 | 15/10 (qui) | 15/10 (qui) |
| 13 | C4 | Saldo derivado das movimentações | C1 | 6 | 15/10 (qui) | 16/10 (sex) |
| 14 | C2 | API de entrada de lote | C1, B3 | 8 | 16/10 (sex) | 19/10 (seg) |
| 15 | C3 | Regra: validade obrigatória e cálculo automático | C2 | 4 | 19/10 (seg) | 19/10 (seg) |
| 16 | C5 | Tela de entrada de mercadoria | A3 | 10 | 19/10 (seg) | 20/10 (ter) |
| 17 | C6 | Integração e teste do fluxo completo | C2, C5 | 6 | 20/10 (ter) | 20/10 (ter) |
| 18 | D1 | API de registro de perda, com motivo obrigatório | C1 | 6 | 20/10 (ter) | 21/10 (qua) |
| 19 | D2 | Regra: perda não entra na base de consumo | D1 | 3 | 21/10 (qua) | 21/10 (qua) |
| 20 | D3 | Tela de avarias e quebras | A3 | 7 | 21/10 (qua) | 22/10 (qui) |
| 21 | D4 | Integração e teste | D1, D3 | 2 | 22/10 (qui) | 22/10 (qui) |
| 22 | F1 | Visão de estoque por produto e por lote | C4 | 6 | 22/10 (qui) | 23/10 (sex) |
| 23 | F2 | API de consulta com filtros | F1 | 6 | 23/10 (sex) | 23/10 (sex) |
| 24 | F3 | Tela de estoque, com destaque para mínimo e vencidos | A3 | 10 | 23/10 (sex) | 26/10 (seg) |
| 25 | H1 | Tabela de aviso e controle de estado | A2 | 8 | 26/10 (seg) | 27/10 (ter) |
| 26 | H2 | Gerador do aviso de validade | H1, C3 | 8 | 27/10 (ter) | 27/10 (ter) |
| 27 | H4 | Janela de silêncio e agrupamento | H1 | 8 | 28/10 (qua) | 28/10 (qua) |
| 28 | H5 | Integração com o serviço de mensagens | H1 | 10 | 28/10 (qua) | 29/10 (qui) |
| 29 | H6 | Vincular o celular do dono ao usuário | H5, B1 | 4 | 29/10 (qui) | 29/10 (qui) |
| 30 | H7 | Receber e registrar a resposta dele | H5 | 4 | 30/10 (sex) | 30/10 (sex) |
| 31 | J2 | Carga inicial dos produtos, junto com o cliente | B3 | 8 | 30/10 (sex) | 02/11 (seg) |
| 32 | J3 | Inventário de partida: contagem física | J2 | 6 | 02/11 (seg) | 02/11 (seg) |

## Etapa 2 · Aviso de ruptura · 94 h

| Ordem | Tarefa | O que é | Depende de | Horas | Início | Fim |
|---|---|---|---|---|---|---|
| 33 | E1 | Levantar o formato do arquivo exportado pelo caixa | confirmação com o cliente | 6 | 02/11 (seg) | 03/11 (ter) |
| 34 | E2 | Criar as tabelas de venda, item de venda e importação | A2 | 6 | 03/11 (ter) | 03/11 (ter) |
| 35 | E3 | Serviço que lê o arquivo e gera venda e movimentação | E1, E2 | 16 | 03/11 (ter) | 05/11 (qui) |
| 36 | E4 | Casar o produto do caixa com o produto cadastrado | E3 | 10 | 05/11 (qui) | 06/11 (sex) |
| 37 | E5 | Tela de acompanhamento da importação | E3 | 6 | 06/11 (sex) | 06/11 (sex) |
| 38 | G1 | Tabela de consumo diário e rotina de agregação | E2 | 10 | 06/11 (sex) | 09/11 (seg) |
| 39 | G2 | Cálculo do consumo médio e por dia da semana | G1 | 12 | 09/11 (seg) | 10/11 (ter) |
| 40 | G3 | Tabela de previsão e gravação do resultado | G2 | 8 | 10/11 (ter) | 11/11 (qua) |
| 41 | G4 | Regra: histórico mínimo antes de projetar | G2 | 4 | 11/11 (qua) | 11/11 (qua) |
| 42 | G5 | Agendador das rotinas diárias | G3 | 6 | 11/11 (qua) | 12/11 (qui) |
| 43 | H3 | Gerador do aviso de ruptura | H1, G3 | 10 | 12/11 (qui) | 13/11 (sex) |

## Etapa 3 · Gestão · 30 h

| Ordem | Tarefa | O que é | Depende de | Horas | Início | Fim |
|---|---|---|---|---|---|---|
| 44 | I1 | Tabela de fechamento e cálculo da diferença | E2 | 8 | 13/11 (sex) | 13/11 (sex) |
| 45 | I2 | Tela de fechamento de caixa | A3 | 10 | 13/11 (sex) | 16/11 (seg) |
| 46 | I3 | Relatório de balanço semanal | E2, D1 | 12 | 16/11 (seg) | 17/11 (ter) |

## Fechamento · Publicação, testes e implantação · 38 h

| Ordem | Tarefa | O que é | Depende de | Horas | Início | Fim |
|---|---|---|---|---|---|---|
| 47 | A5 | Esteira de publicação em ambiente de teste | A1 | 6 | 17/11 (ter) | 18/11 (qua) |
| 48 | J1 | Testes automatizados de todas as regras | todas as regras | 16 | 18/11 (qua) | 19/11 (qui) |
| 49 | J4 | Teste em movimento real, num sábado cheio | todos | 6 | 21/11 (sáb) | 21/11 (sáb) |
| 50 | J5 | Treinamento das três pessoas | J4 | 4 | 23/11 (seg) | 23/11 (seg) |
| 51 | J6 | Implantação e acompanhamento da primeira semana | J4 | 6 | 23/11 (seg) | 27/11 (sex) |

---

## Marcos

| Data | Marco |
|---|---|
| 06/10/2026 (ter) | Início do projeto |
| 02/11/2026 (seg) | Fim da etapa 1: aviso de validade chegando ao celular e produtos carregados |
| 13/11/2026 (sex) | Fim da etapa 2: aviso de "vai acabar" |
| 17/11/2026 (ter) | Fim da etapa 3: fechamento de caixa e balanço semanal |
| 21/11/2026 (sáb) | Teste num sábado cheio |
| 23 a 27/11/2026 | Implantação e acompanhamento da primeira semana |
| **01/12/2026 (ter)** | **Entrega e apresentação final — tudo pronto** |

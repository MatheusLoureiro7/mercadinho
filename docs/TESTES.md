# Documentação de testes

Sistema de Gestão de Estoque e Compras — Mercado do Sr. João · Grupo MDGS

> **O documento para o professor é o PDF** `docs/testes/RELATORIO-DE-TESTES.pdf`
> (MDGS-TST-001, 3 páginas). Este arquivo é o material de trabalho do grupo.
>
> Para reemitir o PDF depois de uma nova execução:
> `pytest --junitxml=docs/testes/execucao.xml` e depois `python docs/testes/gerar.py`.

Este documento responde a duas perguntas:

1. **O que foi testado e aprovado** — cada teste, a regra ou tarefa que ele confere e o resultado.
2. **O que ainda não foi testado** — e por quê: ou porque a parte ainda não foi construída, ou
   porque não dá para testar de forma automática.

Ele é atualizado a cada nova execução da suíte completa. A tarefa de cronograma que fecha os testes
é a **J1** (Apostila IV, seção 9); ela continua em andamento até as regras da previsão (bloco G)
estarem prontas.

---

## 1. Resultado da última execução

| | |
|---|---|
| **Data** | 04/11/2026 |
| **Código testado** | commit `6a66cbd` mais os ajustes de tela ainda não registrados em commit |
| **Testes executados** | **726** |
| **Aprovados** | **726 (100 %)** |
| **Reprovados** | 0 |
| **Tempo** | 1 min 36 s |
| **Padrão de código** (`ruff check .`) | sem nenhum aviso |

**Ambiente:** PostgreSQL 17.11 (o mesmo banco do sistema, nunca um banco "de mentira"), Python 3.14,
Django 5.2, pytest 8.4, Playwright 1.63 com o navegador Chromium.

**Como repetir** (com o Docker ligado — ver `COMO-RODAR.md`):

```
docker compose up -d --wait
pytest                     # todos os 726
pytest -m "not tela"       # só os 634 que não abrem navegador (mais rápido)
```

---

## 2. Como os testes são feitos

| Tipo | Quantos | O que confere | Ferramenta |
|---|---|---|---|
| **Banco de dados** | parte dos 634 | As tabelas são iguais ao modelo de dados da Apostila IV, coluna por coluna; o banco recusa dado errado sozinho (quantidade negativa, perda sem motivo, saldo gravado à mão) | pytest + PostgreSQL |
| **Regra de negócio** | parte dos 634 | Cada regra RN01–RN16 com o exemplo literal da Apostila I e os casos de borda (validade de hoje, quilo fracionado, virada da meia-noite) | pytest |
| **API** | parte dos 634 | Cada endereço responde certo, recusa o que deve recusar com a mensagem da Apostila I, e só deixa entrar o perfil autorizado (RN14) | pytest + cliente HTTP do Django REST Framework |
| **Tela, de ponta a ponta** | 92 | Uma pessoa simulada abre o navegador, faz login, preenche a tela e confere **o que aparece na tela e o que ficou gravado no banco** | Playwright (Chromium) |

Regras que valem para todos os testes:

- **Nome do teste = código da regra.** Exemplo: `test_rn03_perecivel_sem_durabilidade_e_recusado`.
  Assim, qualquer pessoa acha o teste de uma regra procurando por `rn03`.
- **Cada losango de decisão dos fluxogramas da Apostila II tem pelo menos dois testes**: um pelo
  caminho "sim" e um pelo "não" (seção 5).
- **Um teste de guarda** (`test_j1_cobertura_das_regras.py`) falha sozinho se alguma regra que já
  tem código ficar sem teste com o nome dela. Ninguém precisa lembrar de conferir à mão.
- **O Telegram dos testes é local**: os testes sobem um servidor que se comporta como o Telegram, na
  própria máquina. A comunicação é HTTP de verdade; só o endereço muda. Nenhuma mensagem real sai.
- **O relógio é fixado** quando o teste depende de data ou hora (validade, janela de silêncio),
  para o resultado não mudar com o dia em que se roda.

---

## 3. O que foi testado e aprovado — por tarefa do cronograma

| Tarefa | Arquivo de teste | Testes | O que foi conferido | Resultado |
|---|---|---|---|---|
| A1 | `test_a1_configuracao.py` | 5 | Projeto configurado, fuso de São Paulo, padrão de código | ✅ 5/5 |
| A2 | `test_a2_banco.py` | 3 | Banco PostgreSQL e migrações funcionando | ✅ 3/3 |
| A3 | `test_a3_api.py` | 15 | Rotas da API, mensagens de erro em português, registro de log | ✅ 15/15 |
| A4 | `test_a4_autenticacao.py` | 50 | Login, senha guardada com hash, os três perfis (RN14), acesso negado a quem não tem perfil | ✅ 50/50 |
| B1 | `test_b1_tabelas_cadastro.py` | 36 | Tabelas de usuário, categoria, produto e fornecedor iguais à Apostila IV | ✅ 36/36 |
| B2 | `test_b2_api_categoria_fornecedor.py` | 32 | Cadastro de categoria e fornecedor, prazo de entrega obrigatório | ✅ 32/32 |
| B3 | `test_b3_api_produto.py` | 33 | Cadastro de produto com validações | ✅ 33/33 |
| B4 | `test_b4_rn03.py` | 22 | RN03 — perecível sem durabilidade é recusado | ✅ 22/22 |
| B5–B7 | `test_b7_telas_api.py` | 31 | Telas de Produtos e Fornecedores ligadas à API, erros mostrados na tela | ✅ 31/31 |
| C1 | `test_c1_tabelas_estoque.py` | 28 | Tabelas de lote e movimentação; movimentação não pode ser apagada | ✅ 28/28 |
| C2 | `test_c2_entrada_lote.py` | 27 | Entrada de lote grava lote e movimentação juntos | ✅ 27/27 |
| C3 | `test_c3_rn04.py` | 14 | RN04 — validade obrigatória, calculada quando não informada, recusada se já passou | ✅ 14/14 |
| C4 | `test_c4_saldo.py` | 16 | RN01 — saldo é sempre a soma das movimentações; ninguém grava saldo | ✅ 16/16 |
| C5 | `test_c5_tela_entrada.py` | 9 | Tela de entrada de mercadoria | ✅ 9/9 |
| C6 | `test_c6_fluxo_entrada.py` | 14 | Fluxo completo da entrada, do login ao banco — as seis situações do fluxograma 02 | ✅ 14/14 |
| D1 | `test_d1_perda.py` | 31 | Registro de perda com motivo obrigatório | ✅ 31/31 |
| D2 | `test_d2_rn11.py` | 15 | RN11 — perda não entra na base de consumo | ✅ 15/15 |
| D3 | `test_d3_tela_avarias.py` | 15 | Tela de avarias e quebras | ✅ 15/15 |
| D4 | `test_d4_fluxo_perdas.py` | 15 | Fluxo completo da perda, do login ao banco (fluxograma 03) | ✅ 15/15 |
| F1 | `test_f1_visao_estoque.py` | 25 | Visão de estoque por produto e por lote | ✅ 25/25 |
| F2 | `test_f2_api_consulta.py` | 33 | Consulta de estoque com filtros | ✅ 33/33 |
| F3 | `test_f3_tela_estoque.py` | 19 | Tela de estoque, destaque de mínimo e vencidos (RN16) | ✅ 19/19 |
| H1 | `test_h1_alerta.py` | 43 | Tabela de aviso e seus estados | ✅ 43/43 |
| H2 | `test_h2_rn05_aviso_validade.py` | 22 | RN05 — aviso de validade próxima | ✅ 22/22 |
| H4 | `test_h4_rn12_rn13_janela_e_agrupamento.py` | 27 | RN12 — nada de aviso no horário de pico · RN13 — avisos numa mensagem só | ✅ 27/27 |
| H5 | `test_h5_telegram.py` | 19 | Envio pelo Telegram; falha no envio não perde o aviso; token nunca vai para o log | ✅ 19/19 |
| H6 | `test_h6_vincular_telegram.py` | 24 | Vincular o celular do dono ao usuário | ✅ 24/24 |
| H7 | `test_h7_resposta_do_dono.py` | 39 | Receber e registrar a resposta do dono ("Sim, pedir") | ✅ 39/39 |
| I2 | `test_i2_tela_fechamento.py` | 19 | Tela de fechamento de caixa; diferença calculada, nunca digitada (RN15) | ✅ 19/19 |
| J1 | `test_j1_cobertura_das_regras.py` | 20 | Guarda: toda regra com código tem teste; exemplo literal da RN02 | ✅ 20/20 |
| — | `test_telas_no_celular.py` | 25 | Telas usáveis no celular e no tablet, sem esconder botão; no computador da loja nada muda | ✅ 25/25 |
| | **Total** | **726** | | ✅ **726/726** |

---

## 4. O que foi testado e aprovado — por regra de negócio

Conta só os testes que levam o código da regra no nome. Muitos outros conferem a mesma regra de
forma indireta (por exemplo, quase todo teste de API confere a RN14).

| Regra | Descrição (Apostila I) | Testes com o nome | Situação |
|---|---|---|---|
| RN01 | O saldo é sempre derivado das movimentações | 33 | ✅ Testada e aprovada |
| RN02 | A saída respeita a ordem de validade (FIFO) | 3 | ✅ Testada e aprovada — inclusive o exemplo do presunto de 28/09 e 05/10 |
| RN03 | Produto perecível exige prazo de durabilidade | 26 | ✅ Testada e aprovada |
| RN04 | Lote de perecível precisa de data de validade | 20 | ✅ Testada e aprovada |
| RN05 | Aviso de validade próxima | 22 | ✅ Testada e aprovada |
| RN06 | Consumo médio diário | 0 | ⬜ Não testada — ainda não construída (G2) |
| RN07 | Consumo por dia da semana | 0 | ⬜ Não testada — ainda não construída (G2) |
| RN08 | Ponto de pedido e aviso de ruptura | 0 | ⬜ Não testada — ainda não construída (G3, H3) |
| RN09 | Histórico mínimo para prever | 0 | ⬜ Não testada — ainda não construída (G4) |
| RN10 | Produtos que não podem faltar no fim de semana | 0 | ⬜ Não testada — ainda não construída (H3) |
| RN11 | Perda não conta como consumo | 18 | ✅ Testada e aprovada |
| RN12 | Janela de silêncio nos horários de pico | 15 | ✅ Testada e aprovada |
| RN13 | Avisos agrupados em uma única mensagem | 12 | ✅ Testada e aprovada |
| RN14 | Três perfis de acesso | 58 | ✅ Testada e aprovada |
| RN15 | Diferença de caixa registrada, nunca corrigida | 7 | 🟡 Testada **só na tela** — o cálculo e a gravação no banco são da I1, ainda não construída |
| RN16 | Lote vencido é bloqueado | 10 | ✅ Testada e aprovada |

**Resumo:** 10 das 16 regras testadas e aprovadas por completo, 1 testada em parte (RN15),
5 sem teste porque ainda não foram construídas (RN06 a RN10).

---

## 5. Fluxogramas da Apostila II — losangos de decisão

| # | Fluxograma | Situação | Onde |
|---|---|---|---|
| 01 | Cadastro de produto | ✅ "Perecível?" e "durabilidade informada?" pelo sim e pelo não; perfil sem permissão recusado | `test_b4_rn03.py`, `test_b3_api_produto.py` |
| 02 | Entrada de mercadoria | ✅ As **seis situações**: perecível sim/não × validade informada sim/não × validade antes de hoje sim/não | `test_c6_fluxo_entrada.py` |
| 03 | Registro de perda | ✅ Motivo informado sim/não; lote escolhido sim/não; perda maior que o estoque; lote vencido | `test_d4_fluxo_perdas.py` |
| 04 | Importação das vendas | ⬜ Não testado — bloco E ainda não construído | — |
| 05 | Rodada diária de avisos | 🟡 Testado o ramo de **validade** (RN05, RN12, RN13). O ramo de **ruptura** (RN06–RN10) ainda não foi construído | `test_h2_…`, `test_h4_…`, `test_h5_…` |
| 06 | Fechamento de caixa | 🟡 Testada a tela. A gravação e o valor apurado (I1) ainda não foram construídos | `test_i2_tela_fechamento.py` |

---

## 6. Requisitos funcionais (Apostila III)

| Requisito | Situação |
|---|---|
| RF01 Cadastrar produtos | ✅ Testado e aprovado |
| RF02 Cadastrar fornecedores | ✅ Testado e aprovado |
| RF03 Registrar entrada de mercadoria | ✅ Testado e aprovado |
| RF04 Registrar perdas | ✅ Testado e aprovado |
| RF05 Dar baixa no estoque por venda | 🟡 A ordem de saída (FIFO, RN02) está testada; a baixa pela venda depende da importação (E3) |
| RF06 Importar as vendas do caixa | ⬜ Não testado — bloco E |
| RF07 Consultar o estoque | ✅ Testado e aprovado |
| RF08 Calcular a previsão de consumo | ⬜ Não testado — bloco G |
| RF09 Avisar que um produto vai acabar | ⬜ Não testado — H3 |
| RF10 Avisar que um produto vai vencer | ✅ Testado e aprovado |
| RF11 Sugerir quanto comprar | ⬜ Não testado — depende de G3 e da lacuna L15 (fórmula) |
| RF12 Fazer o fechamento de caixa | 🟡 Tela testada; gravação depende da I1 |
| RF13 Emitir o balanço da semana | ⬜ Não testado — I3 |
| RF14 Controlar o acesso por perfil | ✅ Testado e aprovado |
| RF15 Marcar produtos críticos | ⬜ Não testado — H3 (RN10) |
| RF16 Apoiar o inventário mensal | — Fora da primeira versão (Desejável, "não coberto" na especificação) |
| RF17 Mostrar produtos vendidos juntos | — Fora da primeira versão (Desejável, "não coberto" na especificação) |

---

## 7. O que ainda não foi testado, e por quê

### 7.1 Partes que ainda não existem (o teste nasce junto com a tarefa)

| O que falta testar | Tarefa | Data prevista |
|---|---|---|
| Leitura da planilha do caixa e criação das vendas (fluxograma 04, RF06) | E3, E4 | 03 a 09/11 |
| Tela de importação de vendas | E5 | 06 e 09/11 |
| Consumo médio e por dia da semana (RN06, RN07, RF08) | G1, G2 | 06 a 10/11 |
| Ponto de pedido, histórico mínimo, produtos críticos (RN08, RN09, RN10) | G3, G4, H3 | 11 a 13/11 |
| Aviso "o produto vai acabar" (RF09) e sugestão de compra (RF11) | H3 | 12 e 13/11 |
| Agendamento da rodada das 03h00 | G5 | 12 e 13/11 |
| Cálculo e gravação do fechamento de caixa (RN15 completa) | I1 | 03 a 05/11 |
| Balanço da semana, com perdas separadas das vendas (RF13) | I3 | 09 a 11/11 |
| Publicação no computador do Matheus | A5 | 03 e 04/11 |

O teste de guarda da J1 lista RN06 a RN10 como "ainda sem código". Quando uma delas for
construída, o teste obriga a escrever o teste dela antes de passar.

### 7.2 O que não dá para testar de forma automática

Esses itens serão conferidos **à mão**, na demonstração e no teste da J4, e o resultado será
anotado aqui.

| Item | Por que não é automático | Como será conferido |
|---|---|---|
| **J4 — teste em movimento real** | Precisa de uma rodada inteira simulando um sábado cheio | 21/11, com os produtos e vendas de exemplo do grupo |
| **Aviso chegando no celular de verdade** | Os testes usam um Telegram local; não mandam mensagem real | Na J4 e na J6, com o bot real e o celular do grupo |
| **RNF02 / RNF10 — simplicidade e vocabulário do cliente** | "Fácil de usar" depende de gente | Mensagens são conferidas nos testes (ex.: "o frango acaba em 2 dias"); facilidade, na J5 (treinamento) |
| **RNF03 — treinamento** | Não é código | J5, 23/11 |
| **RNF06 — computador antigo** | Os testes rodam numa máquina atual, só no Chromium | Na J6, no computador do Matheus; telas sem framework pesado (HTML, CSS e JS puros) |
| **RNF08 — no ar no horário comercial** e **RNF09 — backup diário** | Dependem da máquina onde o sistema roda | Na A5 e na J6 |
| **Outros navegadores** (Firefox, Edge) | Os testes de tela usam só o Chromium | Conferência manual antes da apresentação |

### 7.3 O que os testes **não** cobrem por decisão de escopo

Emissão de nota fiscal, substituir o caixa, leitor de código de barras, vale-alimentação, venda
fiado, contagem por foto, controle financeiro e contábil, RF16 e RF17. Nada disso foi construído
(ver `CLAUDE.md` e Apostila III), e portanto não há o que testar.

---

## 8. Histórico de execuções

| Data | Testes | Aprovados | Reprovados | Observação |
|---|---|---|---|---|
| 04/11/2026 | 726 | 726 | 0 | Primeira execução registrada neste documento. Blocos A (menos A5), B, C, D, F, H (menos H3) e a tela I2 |

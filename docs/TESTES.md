# Documentação de testes

Sistema de Gestão de Estoque e Compras — Mercado do Sr. João · Grupo MDGS

> **O documento para o professor é o PDF** `docs/testes/RELATORIO-DE-TESTES.pdf`
> (MDGS-TST-001, versão 2.0, 6 páginas, de 25/11/2026). Este arquivo é o material de trabalho do grupo.
>
> Para reemitir o PDF depois de uma nova execução:
> `pytest --junitxml=docs/testes/execucao.xml` e depois `python docs/testes/gerar.py`.

Este documento responde a duas perguntas:

1. **O que foi testado e aprovado** — cada teste, a regra ou tarefa que ele confere e o resultado.
2. **O que ainda não foi testado** — e por quê: o que não dá para testar de forma automática e o
   que fica de fora por decisão de escopo.

Ele é atualizado a cada nova execução da suíte completa. A tarefa do cronograma que fecha os testes
é a **J1** (Apostila IV, seção 9), **concluída em 16/11/2026**: as 16 regras de negócio estão
construídas, testadas e aprovadas.

---

## 1. Resultado da última execução

| | |
|---|---|
| **Data** | 16/11/2026 |
| **Código testado** | commit `f802807` |
| **Testes executados** | **1053** |
| **Aprovados** | **1053 (100 %)** |
| **Reprovados** | 0 |
| **Tempo** | 1 min 57 s |
| **Padrão de código** (`ruff check .`) | sem nenhum aviso |

**Ambiente:** PostgreSQL 17 (o mesmo banco do sistema, nunca um banco "de mentira"), Python 3.14,
Django 5.2, pytest 8.4, Playwright com o navegador Chromium.

**Como repetir** (com o Docker ligado — ver `COMO-RODAR.md`):

```
docker compose up -d --wait
pytest                     # todos os 1053
pytest -m "not tela"       # só os 942 que não abrem navegador (mais rápido)
```

---

## 2. Como os testes são feitos

| Tipo | Quantos | O que confere | Ferramenta |
|---|---|---|---|
| **Banco de dados** | parte dos 942 | As tabelas são iguais ao modelo de dados da Apostila IV, coluna por coluna; o banco recusa dado errado sozinho (quantidade negativa, perda sem motivo, saldo gravado à mão, fechamento alterado) | pytest + PostgreSQL |
| **Regra de negócio** | parte dos 942 | Cada regra RN01–RN16 com o exemplo literal da Apostila I e os casos de borda (validade de hoje, quilo fracionado, virada da meia-noite, 13 × 14 dias de histórico) | pytest |
| **API** | parte dos 942 | Cada endereço responde certo, recusa o que deve recusar com a mensagem da Apostila I, e só deixa entrar o perfil autorizado (RN14) | pytest + cliente HTTP do Django REST Framework |
| **Tela, de ponta a ponta** | 111 | Uma pessoa simulada abre o navegador, faz login, preenche a tela e confere **o que aparece na tela e o que ficou gravado no banco** | Playwright (Chromium) |

Regras que valem para todos os testes:

- **Nome do teste = código da regra.** Exemplo: `test_rn03_perecivel_sem_durabilidade_e_recusado`.
  Assim, qualquer pessoa acha o teste de uma regra procurando por `rn03`.
- **Cada losango de decisão dos fluxogramas da Apostila II tem pelo menos dois testes**: um pelo
  caminho "sim" e um pelo "não" (seção 5).
- **Um teste de guarda** (`test_j1_cobertura_das_regras.py`) falha sozinho se alguma regra ficar
  sem teste com o nome dela. Ninguém precisa lembrar de conferir à mão.
- **Outro teste de guarda** impede que a previsão e os avisos leiam as movimentações direto: o
  consumo só se lê pelo módulo que exclui as perdas (RN11).
- **A documentação do sistema é conferida** (`test_documentacao.py`): endpoint, tabela, regra ou
  dependência nova sem regenerar os documentos faz o teste falhar.
- **O Telegram dos testes é local**: os testes sobem um servidor que se comporta como o Telegram, na
  própria máquina. A comunicação é HTTP de verdade; só o endereço muda. Nenhuma mensagem real sai.
- **O relógio é fixado** quando o teste depende de data ou hora (validade, janela de silêncio,
  quinta-feira do fim de semana), para o resultado não mudar com o dia em que se roda.
- **Prova de que os testes pegam erro:** a cada tarefa, a equipe insere defeitos de propósito no
  código e confere que algum teste falha. Foram **130** entre 08/10 e 16/11/2026, todos detectados.

---

## 3. O que foi testado e aprovado — por tarefa do cronograma

| Tarefa | Arquivo de teste | Testes | O que foi conferido | Resultado |
|---|---|---|---|---|
| A1 | `test_a1_configuracao.py` | 5 | Projeto configurado, fuso de São Paulo, padrão de código | ✅ 5/5 |
| A2 | `test_a2_banco.py` | 3 | Banco PostgreSQL e migrações funcionando | ✅ 3/3 |
| A3 | `test_a3_api.py` | 15 | Rotas da API, mensagens de erro em português, registro de log | ✅ 15/15 |
| A4 | `test_a4_autenticacao.py` | 50 | Login, senha guardada com hash, os três perfis (RN14), acesso negado a quem não tem perfil | ✅ 50/50 |
| A5 | `test_a5_publicar.py` | 10 | Publicação: testes antes de mexer no que está no ar; passo reprovado não troca nada | ✅ 10/10 |
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
| E1 | `test_e1_formato_planilha.py` | 6 | Formato da planilha do caixa e planilha de exemplo | ✅ 6/6 |
| E2 | `test_e2_tabelas_vendas.py` | 29 | Tabelas de importação, venda e item de venda iguais à Apostila IV | ✅ 29/29 |
| E3 | `test_e3_importacao.py` | 35 | Leitura da planilha; venda baixa do lote que vence primeiro (RN01, RN02); linha sem produto fica pendente e não trava as demais | ✅ 35/35 |
| E4 | `test_e4_casar_produto.py` | 18 | Ligar a venda pendente ao produto certo, baixando no dia e hora da venda | ✅ 18/18 |
| E5 | `test_e5_tela_importacao.py` | 19 | Tela de importação de vendas | ✅ 19/19 |
| F1 | `test_f1_visao_estoque.py` | 25 | Visão de estoque por produto e por lote | ✅ 25/25 |
| F2 | `test_f2_api_consulta.py` | 33 | Consulta de estoque com filtros | ✅ 33/33 |
| F3 | `test_f3_tela_estoque.py` | 19 | Tela de estoque, destaque de mínimo e vencidos (RN16) | ✅ 19/19 |
| G1 | `test_g1_consumo_diario.py` | 19 | Consumo de cada dia, só com vendas (RN11) | ✅ 19/19 |
| G2 | `test_g2_consumo_medio.py` | 15 | RN06 e RN07 — consumo médio e por dia da semana | ✅ 15/15 |
| G3 | `test_g3_previsao.py` | 20 | RN08 — ponto de pedido, dias até acabar e sugestão de compra (RF11) | ✅ 20/20 |
| G4 | `test_g4_rn09_historico_minimo.py` | 8 | RN09 — sem 14 dias de histórico, nada de número | ✅ 8/8 |
| G5 | `test_g5_rodada_diaria.py` | 9 | Rodada das 03h00 na ordem certa; passo que falha não impede os outros | ✅ 9/9 |
| H1 | `test_h1_alerta.py` | 43 | Tabela de aviso e seus estados | ✅ 43/43 |
| H2 | `test_h2_rn05_aviso_validade.py` | 22 | RN05 — aviso de validade próxima | ✅ 22/22 |
| H3 | `test_h3_ruptura.py` | 34 | RN08 e RN10 — aviso "vai acabar" e de fim de semana; depois do "Sim, pedir", silêncio até chegar mercadoria | ✅ 34/34 |
| H4 | `test_h4_rn12_rn13_janela_e_agrupamento.py` | 27 | RN12 — nada de aviso no horário de pico · RN13 — avisos numa mensagem só | ✅ 27/27 |
| H5 | `test_h5_telegram.py` | 19 | Envio pelo Telegram; falha no envio não perde o aviso; token nunca vai para o log | ✅ 19/19 |
| H6 | `test_h6_vincular_telegram.py` | 24 | Vincular o celular do dono ao usuário | ✅ 24/24 |
| H7 | `test_h7_resposta_do_dono.py` | 39 | Receber e registrar a resposta do dono ("Sim, pedir") | ✅ 39/39 |
| I1 | `test_i1_fechamento.py` | 35 | RN15 — diferença calculada pelo banco, nunca alterada; contar de novo gera registro novo | ✅ 35/35 |
| I2 | `test_i2_tela_fechamento.py` | 19 | Tela de fechamento de caixa | ✅ 19/19 |
| I3 | `test_i3_balanco.py` | 29 | Balanço da semana: vendas, perdas a preço de custo e resultado (RF13) | ✅ 29/29 |
| J1 | `test_j1_cobertura_das_regras.py` | 20 | Guarda: toda regra tem teste; exemplo literal da RN02 | ✅ 20/20 |
| J2 | `test_j2_carga_produtos.py` | 16 | Carga dos produtos por planilha, tudo ou nada | ✅ 16/16 |
| J3 | `test_j3_contagem_de_partida.py` | 16 | Contagem de partida lançada como entrada de mercadoria | ✅ 16/16 |
| — | `test_telas_no_celular.py` | 28 | Telas usáveis no celular e no tablet, sem esconder botão | ✅ 28/28 |
| — | `test_documentacao.py` | 6 | Documentação do sistema igual ao que o código gera hoje | ✅ 6/6 |
| | **Total** | **1053** | | ✅ **1053/1053** |

---

## 4. O que foi testado e aprovado — por regra de negócio

Conta só os testes que levam o código da regra no nome. Muitos outros conferem a mesma regra de
forma indireta (por exemplo, quase todo teste de API confere a RN14).

| Regra | Descrição (Apostila I) | Testes com o nome | Situação |
|---|---|---|---|
| RN01 | O saldo é sempre derivado das movimentações | 34 | ✅ Testada e aprovada |
| RN02 | A saída respeita a ordem de validade (FIFO) | 5 | ✅ Testada e aprovada — inclusive o exemplo do presunto de 28/09 e 05/10 |
| RN03 | Produto perecível exige prazo de durabilidade | 27 | ✅ Testada e aprovada |
| RN04 | Lote de perecível precisa de data de validade | 22 | ✅ Testada e aprovada |
| RN05 | Aviso de validade próxima | 23 | ✅ Testada e aprovada |
| RN06 | Consumo médio diário | 6 | ✅ Testada e aprovada |
| RN07 | Consumo por dia da semana | 9 | ✅ Testada e aprovada |
| RN08 | Ponto de pedido e aviso de ruptura | 15 | ✅ Testada e aprovada |
| RN09 | Histórico mínimo para prever | 10 | ✅ Testada e aprovada — 13 dias não projeta, 14 projeta |
| RN10 | Produtos que não podem faltar no fim de semana | 7 | ✅ Testada e aprovada |
| RN11 | Perda não conta como consumo | 23 | ✅ Testada e aprovada |
| RN12 | Janela de silêncio nos horários de pico | 15 | ✅ Testada e aprovada |
| RN13 | Avisos agrupados em uma única mensagem | 12 | ✅ Testada e aprovada |
| RN14 | Três perfis de acesso | 67 | ✅ Testada e aprovada |
| RN15 | Diferença de caixa registrada, nunca corrigida | 19 | ✅ Testada e aprovada — exemplo de R$ 3.240,00 × R$ 3.215,00 |
| RN16 | Lote vencido é bloqueado | 14 | ✅ Testada e aprovada |

**Resumo:** as 16 regras testadas e aprovadas.

---

## 5. Fluxogramas da Apostila II — losangos de decisão

| # | Fluxograma | Situação | Onde |
|---|---|---|---|
| 01 | Cadastro de produto | ✅ "Perecível?" e "durabilidade informada?" pelo sim e pelo não; perfil sem permissão recusado | `test_b4_rn03.py`, `test_b3_api_produto.py` |
| 02 | Entrada de mercadoria | ✅ As **seis situações**: perecível sim/não × validade informada sim/não × validade antes de hoje sim/não | `test_c6_fluxo_entrada.py` |
| 03 | Registro de perda | ✅ Motivo informado sim/não; lote escolhido sim/não; perda maior que o estoque; lote vencido | `test_d4_fluxo_perdas.py` |
| 04 | Importação das vendas | ✅ Produto casou sim/não (pendente não trava as demais); linha válida sim/não; arquivo legível sim/não; tudo certo → OK, com pendência → PARCIAL | `test_e3_importacao.py`, `test_e4_casar_produto.py` |
| 05 | Rodada diária de avisos | ✅ Validade dentro do prazo sim/não; histórico de 14 dias sim/não; saldo no ponto de pedido sim/não; quinta e crítico sim/não; horário de pico sim/não | `test_h2_…`, `test_g4_…`, `test_h3_…`, `test_h4_…`, `test_g5_…` |
| 06 | Fechamento de caixa | ✅ Vendas do dia importadas sim/não; diferença zero, negativa e positiva | `test_i1_fechamento.py`, `test_i2_tela_fechamento.py` |

---

## 6. Requisitos funcionais (Apostila III)

| Requisito | Situação |
|---|---|
| RF01 Cadastrar produtos | ✅ Testado e aprovado |
| RF02 Cadastrar fornecedores | ✅ Testado e aprovado |
| RF03 Registrar entrada de mercadoria | ✅ Testado e aprovado |
| RF04 Registrar perdas | ✅ Testado e aprovado |
| RF05 Dar baixa no estoque por venda | ✅ Testado e aprovado (E3, E4) |
| RF06 Importar as vendas do caixa | ✅ Testado e aprovado (E3 a E5) |
| RF07 Consultar o estoque | ✅ Testado e aprovado |
| RF08 Calcular a previsão de consumo | ✅ Testado e aprovado (G1 a G4) |
| RF09 Avisar que um produto vai acabar | ✅ Testado e aprovado (H3) |
| RF10 Avisar que um produto vai vencer | ✅ Testado e aprovado |
| RF11 Sugerir quanto comprar | ✅ Testado e aprovado (G3; fórmula da L15) |
| RF12 Fazer o fechamento de caixa | ✅ Testado e aprovado (I1, I2) |
| RF13 Emitir o balanço da semana | ✅ Testado e aprovado (I3) |
| RF14 Controlar o acesso por perfil | ✅ Testado e aprovado |
| RF15 Marcar produtos críticos | ✅ Testado e aprovado (B3, H3) |
| RF16 Apoiar o inventário mensal | — Fora da primeira versão (Desejável, "não coberto" na especificação) |
| RF17 Mostrar produtos vendidos juntos | — Fora da primeira versão (Desejável, "não coberto" na especificação) |

---

## 7. O que ainda não foi testado, e por quê

### 7.1 Partes que ainda não existem

Nenhuma. Todo o código da primeira versão está construído e testado de forma automática.

### 7.2 O que não dá para testar de forma automática

Esses itens serão conferidos **à mão**, no teste da J4 e nas tarefas seguintes, e o resultado será
anotado aqui.

| Item | Por que não é automático | Como será conferido |
|---|---|---|
| **J4 — teste em movimento real** | Precisa de uma rodada inteira simulando um sábado cheio | 21/11, com os produtos e vendas de exemplo do grupo — roteiro e casos em `docs/testes/ROTEIRO-J4.md` |
| **Aviso chegando no celular de verdade** | Os testes usam um Telegram local; não mandam mensagem real | Na J4 e na J6, com o bot real e o celular do grupo |
| **RNF02 / RNF10 — simplicidade e vocabulário do cliente** | "Fácil de usar" depende de gente | Mensagens são conferidas nos testes (ex.: "o frango acaba em 2 dias"); facilidade, na J5 (treinamento) |
| **RNF03 — treinamento** | Não é código | J5, 23/11 |
| **RNF06 — computador antigo** | Os testes rodam numa máquina atual, só no Chromium | Na J6, no computador do Matheus; telas sem framework pesado (HTML, CSS e JS puros) |
| **RNF08 — no ar no horário comercial** e **RNF09 — backup diário** | Dependem da máquina onde o sistema roda; o backup automático ainda não existe | Na J6 |
| **Outros navegadores** (Firefox, Edge) | Os testes de tela usam só o Chromium | Conferência manual antes da apresentação |

### 7.3 O que os testes **não** cobrem por decisão de escopo

Emissão de nota fiscal, substituir o caixa, leitor de código de barras, vale-alimentação, venda
fiado, contagem por foto, controle financeiro e contábil, RF16 e RF17. Nada disso foi construído
(ver `CLAUDE.md` e Apostila III), e portanto não há o que testar.

---

## 8. Defeitos encontrados desde a versão 1.2 do relatório

| Encontrado em | Defeito | Corrigido em |
|---|---|---|
| 12/11/2026 | O aviso de validade estava pronto, mas nenhuma rotina da madrugada o chamava (achado na G5) | 12/11/2026 |
| 13/11/2026 | Sugestão de compra quebrada em produto vendido por pacote ("pedir 14,531 PCT"), achado na demonstração | 13/11/2026, commit `756a65f` |
| 16/11/2026 | O documento da API mudava conforme a ordem em que os testes rodavam; `test_documentacao` falhava só na suíte inteira (achado na J1) | 16/11/2026, commit `f802807` |

A lista completa, desde 06/10/2026, está no PDF (14 defeitos, nenhum em aberto).

---

## 9. Histórico de execuções

| Data | Testes | Aprovados | Reprovados | Observação |
|---|---|---|---|---|
| 16/11/2026 | 1053 | 1053 | 0 | Relatório 1.3. Fechamento da J1: as 16 regras, todos os blocos de A a J (menos J4 a J6, que são manuais) |
| 13/11/2026 | 1046 | 1046 | 0 | Execução da esteira de publicação (A5) |
| 05/11/2026 | 831 | 831 | 0 | Relatório 1.2: E1 a E3 e I1; RN15 aprovada por inteiro |
| 05/11/2026 | 796 | 796 | 0 | Relatório 1.1 |
| 04/11/2026 | 726 | 726 | 0 | Primeira execução registrada neste documento. Blocos A (menos A5), B, C, D, F, H (menos H3) e a tela I2 |

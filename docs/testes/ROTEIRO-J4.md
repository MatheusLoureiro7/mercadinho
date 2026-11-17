# Roteiro do teste em movimento real — J4

Tarefa **J4** do cronograma · **sábado, 21/11/2026** · 6 horas · todo o grupo MDGS
Preparado em 17/11/2026.

## Para que serve

Os 1.144 testes automáticos conferem cada regra separada, com o relógio parado. A J4 confere o
**sistema inteiro rodando como na loja**, durante um dia de movimento: a rodada da madrugada de
verdade, o aviso chegando no celular de verdade e as três pessoas usando as telas ao mesmo tempo.
É o primeiro item da seção 7.2 do `docs/TESTES.md` ("o que não dá para testar de forma automática").

O mercado é fictício: o "sábado cheio" é **simulado** pelo grupo, com produtos e vendas de exemplo.
O sistema roda no computador do Matheus (decisão D05), na versão publicada pelo `publicar.py`.

**O que a J4 não é:** não é treinamento (J5, 23/11) nem implantação (J6). Não se testa nada fora
de escopo (nota fiscal, caixa, código de barras etc.) nem RF16/RF17.

---

## 1. Papéis

Cada integrante faz um papel o dia inteiro. Quem faz um papel entra **só** com o login dele.

| Papel | Login | Faz |
|---|---|---|
| **Sobrinho** (operação) | `sobrinho` | Entrada de mercadoria, avarias, produtos, conferência das vendas |
| **Esposa** (gestão) | `esposa` | Fechamento de caixa e balanço da semana |
| **Sr. João** (dono) | `joao` | Só o celular com o Telegram e, se quiser, a consulta de estoque |
| **Caixa e anotador** | — | Monta a planilha de vendas do dia e anota cada resultado na seção 6 |

Se o grupo tiver só três pessoas, o anotador acumula com o Sr. João, que quase não usa o sistema.

---

## 2. Preparação — até sexta, 20/11/2026

Sem estes itens o sábado não funciona. P1, P2 e P3 vêm da conferência de 17/11/2026.

| # | O que | Por que | Como | Feito |
|---|---|---|---|---|
| P1 | **Configurar a pasta das planilhas do caixa** | `PASTA_VENDAS_CAIXA` está vazio no `.env` do computador do Matheus: a rodada não importaria nada | Criar a pasta e preencher `PASTA_VENDAS_CAIXA=` no `.env`; republicar | ☐ |
| P2 | **Instalar o agendador** | Não há crontab no computador: a rodada das 03h00 não roda sozinha | `python backend/manage.py agenda_cron` e colar as linhas com `crontab -e`; conferir que o fuso do computador é São Paulo | ☐ |
| P3 | **Repor o estoque antes das vendas de exemplo** | O estoque de hoje não cobre os dias de 13/11 a 21/11 (há 3 sacos de carvão e 5 refrigerantes) | Duas rodadas de **Entrada de mercadoria**, pela tela, com as quantidades da seção 3 | ☐ |
| P4 | **Salvar as vendas de 13/11 a 20/11 na pasta** | O banco tem vendas de 24/10 a 12/11. Sem os dias seguintes, o balanço mostra "não entrou" e a previsão perde a última semana | Planilhas prontas em `docs/exemplos/j4/`, copiadas para a pasta do P1 **no ritmo da seção 3**, nunca antes do dia delas | ☐ |
| P5 | **Celular do Sr. João ligado ao bot** | O usuário `joao` já está vinculado; conferir que é o celular que estará no sábado | Se for outro celular: `python backend/manage.py vincular_telegram --login joao` | ☐ |
| P6 | **Mercadoria para chegar no sábado** | Entradas reais durante o dia (fluxograma 02) | Separar 4 entregas no papel: produto, quantidade, fornecedor, custo, validade | ☐ |
| P7 | **Publicar a versão final** | Testar o que será apresentado | `python publicar.py` na sexta à noite: todos os testes passam e o sistema sobe | ☐ |
| P8 | **Computador ligado de sexta para sábado** | A rodada das 03h00 de 21/11 importa as vendas de sexta | Desligar a suspensão automática | ☐ |

---

## 3. As planilhas e a reposição

Todas as planilhas estão prontas em `docs/exemplos/j4/`, no formato do `docs/FORMATO-PLANILHA-CAIXA.md`,
e foram conferidas com o leitor do próprio sistema em 17/11/2026: as nove entram sem erro.
As vendas são de exemplo, calculadas pela média do histórico do banco (24/10 a 12/11): de 12 a 17
cupons por dia, com o mesmo peso de cada produto e a mesma divisão entre Dinheiro, PIX e Cartão.

| Arquivo | Cupons | Linhas | Para quê |
|---|---|---|---|
| `vendas-2026-11-13.xlsx` a `vendas-2026-11-20.xlsx` | 12 a 17 por dia | 18 a 32 | Fechar o buraco de 13/11 a 20/11 (P4) |
| `vendas-2026-11-21.xlsx` | 70 | 117 | O sábado cheio: uns 5 dias comuns, com picos de 10h30 a 13h00 e de 16h30 a 18h00 |
| `teste-hora-errada.xlsx` | 3 | 4 | Só para o caso C14 |

**No sábado, de propósito**, para testar os caminhos do "não":

| Erro colocado | Onde | Esperado |
|---|---|---|
| Produto com nome que não existe no cadastro: `Frango 1kg` | 3 linhas | Aparece em "Vendas para conferir" (fluxograma 04) |
| Pagamento escrito `espécie` | 2 cupons | Conta como dinheiro no fechamento |

A hora errada (`9h30`) fica fora da planilha do sábado, porque recusaria o dia inteiro.

### Em que ordem

A venda tem de encontrar estoque. Por isso a reposição vem antes de cada lote de planilhas, e
nenhuma planilha entra antes do dia dela (vender amanhã não existe):

| Quando | O que |
|---|---|
| **Quarta, 18/11** | 1ª reposição (tabela abaixo). Depois, copiar para a pasta as planilhas de **13/11 a 17/11**; a rodada das 03h00 de quinta importa |
| **Quinta, 19/11, à noite** | Copiar `vendas-2026-11-18.xlsx` e `vendas-2026-11-19.xlsx` |
| **Sexta, 20/11** | 2ª reposição. À noite, copiar `vendas-2026-11-20.xlsx`; a rodada das 03h00 de sábado importa |
| **Sábado, 21/11, à noite** | Copiar `vendas-2026-11-21.xlsx`; a rodada das 03h00 de domingo importa |

### Quanto repor

Calculado pelas planilhas, com folga de 20%. As entregas do próprio sábado (P6) são além disto.

| Produto | Quarta, 18/11 | Sexta, 20/11 |
|---|---|---|
| Alcatra | 14 kg | 32 kg |
| Arroz 5 kg | 1 pct | 10 pct |
| Carvão 3 kg | 30 pct | 11 pct |
| Cerveja lata 350 ml | 171 un | 222 un |
| Feijão carioca 1 kg | — | 11 pct |
| Frango resfriado 1 kg | 16 kg | 24 kg |
| Iogurte natural | 2 un | 7 un |
| Linguiça toscana | 19 kg | 27 kg |
| Presunto | 1 kg | 3,5 kg |
| Refrigerante 2 L | 51 un | 24 un |

---

## 4. O dia, hora a hora

| Hora | Quem | O que acontece |
|---|---|---|
| **03h00** | (sozinho) | A rodada importa as vendas de sexta, calcula a previsão e manda os avisos |
| **08h00** | todos | Conferir a rodada da madrugada (casos C01 a C04) |
| **08h30** | Esposa | Fechamento de caixa de sexta, 20/11 (C10 a C12) |
| **09h00–10h30** | Sobrinho | Chegam 2 entregas; uma avaria (C05 a C09) |
| **10h30–13h00** | todos | **Horário de movimento:** nada pode chegar no celular (C15) |
| **10h45** | Sobrinho | Duas avarias grandes, em dois produtos que não tiveram aviso hoje (C15) |
| **11h00** | Matheus | Roda `rodada_diaria` no terminal: os avisos novos ficam segurados |
| **11h30** | Sobrinho | Chega a 3ª entrega, de um dos dois produtos (C08) |
| **13h00** | Sr. João | Chega o aviso só do outro produto (C08, C15) |
| **13h00–14h00** | todos | Casos de erro e acesso (C13, C14, C16, C17); preencher a seção 6 |

O sábado termina às 14h00, mas o teste continua em dois momentos curtos:

| Quando | Quem | O que |
|---|---|---|
| **Domingo, 22/11, de manhã** | Matheus | A planilha do sábado é salva na pasta no sábado à noite; às 03h00 de domingo a rodada importa. Conferir C18 e C19 |
| **Segunda, 23/11** (antes da J5) | Esposa | Fechamento de caixa do sábado (C20) e balanço da semana (C21) |

---

## 5. Casos de teste

Cada caso tem o resultado esperado tirado da especificação. O resultado de verdade vai na seção 6.

### Rodada da madrugada (fluxograma 05, operação 03)

| Caso | O que fazer | Esperado | Regra |
|---|---|---|---|
| C01 | Abrir **Importação de vendas** | Planilha de 20/11 com situação *Lida* | RN01 |
| C02 | Olhar o celular do Sr. João | **Uma** mensagem só, do mais urgente para o menos | RN13 |
| C03 | Ler a mensagem | Vocabulário da loja ("acaba em 2 dias", "vence em 3 dias"), nunca termo técnico | RNF10 |
| C04 | **Consulta de estoque**, coluna **Quando acaba** | Previsão para todos os produtos com mais de 14 dias de venda | RN06, RN09 |

### Entrada e perda (fluxogramas 02 e 03)

| Caso | O que fazer | Esperado | Regra |
|---|---|---|---|
| C05 | Entrada de perecível **com** validade da embalagem | Lote criado com aquela validade; saldo sobe | RN01, RN04 |
| C06 | Entrada de perecível **sem** validade | Validade calculada: hoje + durabilidade | RN04 |
| C07 | Entrada com validade **de ontem** | Recusada, com a mensagem da RN04 | RN04 |
| C08 | Às 11h30, entrada do produto B (ver C15), cujo aviso ainda está segurado | O aviso dele é cancelado: não vem na mensagem das 13h00 | Operação 02, passo 10 |
| C09 | Avaria: "Quebrou", sem escolher o lote | Sai do lote que vence primeiro; não conta como venda | RN02, RN11 |

### Fechamento de caixa (fluxograma 06)

| Caso | O que fazer | Esperado | Regra |
|---|---|---|---|
| C10 | Fechar sexta, 20/11, com o dinheiro certo | Diferença R$ 0,00, registrado | RN15 |
| C11 | Registrar de novo com outro valor | O registro anterior continua; aparece o novo | RN15 |
| C12 | Tentar fechar **hoje** (21/11) | A tela não deixa | RN15 |

### Erros e acesso

| Caso | O que fazer | Esperado | Regra |
|---|---|---|---|
| C13 | Salvar na pasta uma **cópia** da planilha de 20/11 com outro nome e rodar `importar_vendas` | Nada entra de novo; saldo não cai | X1, item 1 |
| C14 | Copiar `teste-hora-errada.xlsx` para a pasta e rodar `importar_vendas`. **Depois, tirar o arquivo da pasta** | *Não foi lida*; nenhuma venda dela entra | X1, item 2 |
| C15 | 10h45: avaria que leva quase todo o estoque de dois produtos (A e B) sem aviso hoje. 11h00: `rodada_diaria` | Nada chega antes das 13h00; logo depois chega o aviso de A | RN12 |
| C16 | Sobrinho digita o endereço `fechamento-caixa.html` | A API recusa: a tela não mostra nada do caixa | RN14 |
| C17 | Esposa digita o endereço `entrada-mercadoria.html` | A API recusa: não dá para registrar entrada | RN14 |

### Depois do sábado

| Caso | O que fazer | Esperado | Regra |
|---|---|---|---|
| C18 | Domingo: **Importação de vendas** | Sábado *Lida, com vendas a conferir* (as 3 linhas com nome errado) | Fluxograma 04 |
| C19 | Ligar as vendas de `Frango 1kg` ao **Frango resfriado 1 kg** | Saldo do frango cai pela quantidade, do lote que vence primeiro | RN01, RN02 |
| C20 | Segunda: fechar o sábado | Apurado inclui os cupons em "espécie" | RN15 |
| C21 | Balanço da semana de 16/11 a 22/11 | Vendas − perdas; perdas em linha separada; nenhum dia "não entrou" | RF13, RN11 |

Os comandos dos casos C13 a C15 são rodados pelo Matheus, no terminal do computador do sistema.
A rodada das 11h00 não repete aviso que já foi gerado no dia: por isso A e B são produtos que não
apareceram na mensagem da madrugada.

---

## 6. Resultado

Preencher no dia. **Falhou** é qualquer diferença do esperado, mesmo pequena.

| Caso | Passou / Falhou | Hora | O que aconteceu (se falhou) |
|---|---|---|---|
| C01 | | | |
| C02 | | | |
| C03 | | | |
| C04 | | | |
| C05 | | | |
| C06 | | | |
| C07 | | | |
| C08 | | | |
| C09 | | | |
| C10 | | | |
| C11 | | | |
| C12 | | | |
| C13 | | | |
| C14 | | | |
| C15 | | | |
| C16 | | | |
| C17 | | | |
| C18 | | | |
| C19 | | | |
| C20 | | | |
| C21 | | | |

Também anotar: lentidão (tela que demora mais de 3 segundos), mensagem confusa e qualquer coisa
que alguém no papel de usuário não entendeu. Isso vai para a J5.

## 7. Depois do teste

1. Cada falha vira um item de correção, com teste automático antes da correção, um commit por item.
2. O resultado vai para a seção 7.2 do `docs/TESTES.md` e para o Diário do `docs/ACOMPANHAMENTO.md`.
3. A J4 é riscada no roteiro e no acompanhamento só quando C01 a C21 passarem, ou quando o grupo
   decidir, por escrito no Diário, conviver com uma falha.

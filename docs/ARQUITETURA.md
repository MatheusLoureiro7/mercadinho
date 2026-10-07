# Arquitetura

Transcrição da **Apostila IV**, seções 2 a 7.

---

## Fronteira do sistema

```
Sr. João   (celular, Telegram)  ──┐
Esposa     (navegador)          ──┤──▶  Sistema de Gestão de Estoque e Compras
Sobrinho   (navegador)          ──┘            (escopo deste projeto)
                                                  ▲            │
                                      arquivo de  │            │ avisos
                                      vendas      │            ▼
                                   Caixa / PDV atual        Telegram
                                   sistema de terceiro      serviço externo
                                   NÃO será substituído     canal de aviso
```

**O caixa da loja não é chamado por nós.** Nós lemos um arquivo que ele deixou — o caixa nem sabe
que o nosso sistema existe.

**A única conversa com sistema de terceiro é o envio de mensagens, e ela é de saída.**

**Só uma porta fica aberta para a internet.** Banco de dados e processos automáticos não têm
endereço público.

---

## As quatro camadas

```
1 · APRESENTAÇÃO — o que o usuário vê
    Painel Web (sobrinho e esposa)        Bot do Telegram (Sr. João — só recebe e responde)

2 · APLICAÇÃO — a API REST, porta única de entrada
    Autenticação · Cadastros · Movimentação · Relatórios · Recebimento do bot

3 · PROCESSAMENTO — roda sozinho, em horário agendado
    Importador do PDV · Motor de previsão · Motor de regras · Serviço de notificação

4 · DADOS
    PostgreSQL — única fonte da verdade
```

**Quem está numa camada só conversa com a camada vizinha — nunca pula.**

**O painel web nunca acessa o banco diretamente.** Toda leitura e toda escrita passam pela API. Se
um dia existir um aplicativo, ele usa a mesma API e as regras não precisam ser escritas duas vezes.

**Por que o processamento é separado da API:** previsão e avisos não podem rodar no clique do
usuário. São pesados, percorrem todo o histórico e precisam acontecer mesmo sem ninguém usando o
sistema. Por isso são processos agendados, e não telas.

---

## Comunicação entre os componentes

| # | Quem chama | Quem responde | Por onde | Formato | Quando |
|---|---|---|---|---|---|
| 1 | Navegador do painel | Ponto de entrada | HTTPS, porta 443 | JSON | A cada ação do usuário |
| 2 | Ponto de entrada | API do sistema | HTTP interno, porta 8000 | JSON | Encaminhamento imediato |
| 3 | API do sistema | Banco de dados | TCP, porta 5432 | SQL | A cada requisição |
| 4 | Agendador | Processos automáticos | Chamada local | — | 03h00, diariamente |
| 5 | Importador de vendas | Arquivo do caixa | Leitura de disco | Arquivo de texto | 1× por dia |
| 6 | Motor de previsão | Banco de dados | TCP, porta 5432 | SQL | 1× por dia, após a importação |
| 7 | Motor de regras | Banco de dados | TCP, porta 5432 | SQL | 1× por dia, após a previsão |
| 8 | Serviço de aviso | Serviço de mensagens | HTTPS de saída | JSON | Nas janelas permitidas |
| 9 | Serviço de mensagens | API do sistema | HTTPS, porta 443 | JSON | Quando o dono responde |
| 10 | Rotina de backup | Armazenamento externo | HTTPS de saída | Arquivo comprimido | 1× por dia |

**A ordem da rodada diária importa:** importação → previsão → regras → notificação. Cada uma
depende do resultado da anterior.

---

## Os dois caminhos do dado

**Caminho 1 — dado bruto: valida e grava direto.**
Entrada pelo painel (produto, fornecedor, lote, validade, perda, contagem) → validação na API
(tipo, obrigatoriedade, RN03, RN04, RN16) → tabelas de origem (`produto`, `fornecedor`, `lote`,
`movimentacao`, `venda`).

**Caminho 2 — dado derivado: lê o bruto, calcula, grava o resultado.**
Tabelas de origem → motor de previsão (RN06, RN07, RN09 · 1× por dia) → motor de regras (RN05,
RN08, RN10) → tabelas derivadas (`consumo_diario`, `previsao_produto`, `alerta`) → serviço de
notificação (RN12, RN13) → Telegram.

**Por que a separação importa:** se a previsão fosse calculada na hora de exibir a tela, cada
consulta percorreria meses de histórico e o sistema ficaria lento justamente no horário de pico.

**O dado calculado pode ser apagado.** `consumo_diario`, `previsao_produto` e `alerta` podem ser
recalculados a qualquer momento a partir das tabelas de origem, sem perda. As de origem, não — elas
são o registro do que de fato aconteceu na loja.

---

## Operações passo a passo

### Operação 01 — Cadastro de produto (10 passos, 5 componentes)

1. Navegador envia o formulário preenchido
2. Ponto de entrada encaminha com o token da sessão
3. API valida o token e lê o papel do usuário
   → **RN14**: só OPERACAO cadastra produto. DONO e GESTAO recebem recusa **aqui, antes de tocar
   no banco**.
4. Libera a requisição já identificada
5. Valida tipo e obrigatoriedade dos campos
   → **RN03**: perecível marcado e durabilidade vazia → para aqui e devolve o campo que falta.
   Nada é gravado.
6. Verifica se o nome já existe na categoria
7. Banco devolve que o nome está livre
8. `INSERT` em `produto`
9. Banco devolve o id gerado
10. Responde `201` com o produto criado

### Operação 02 — Entrada de mercadoria (11 passos)

1. Navegador envia o lote: produto, quantidade, validade, custo
2. API lê o produto para saber se é perecível
3. Pede a validação das regras do lote
4. Motor de regras aplica as regras de validade
   → **RN04**: perecível sem validade recebe `data_entrada + durabilidade`. Validade no passado é
   recusada.
5. Devolve o lote já validado
6. **ABRE TRANSAÇÃO** · `INSERT` em `lote`
7. `INSERT` em `movimentacao` com `tipo = ENTRADA`
   → **RN01**: as duas gravações acontecem juntas. Se a segunda falhar, a primeira é desfeita.
   **Nunca existe lote sem a movimentação que explica o saldo.**
8. Confirma a transação
9. Avisa que o saldo mudou
10. Cancela alerta de ruptura pendente, se houver
11. Responde `201` e atualiza a lista do dia

### Operação 03 — Aviso no Telegram (14 passos, sem nenhuma tela)

1. Agendador dispara a rodada às 03h00
2. Motor de previsão lê as vendas do dia anterior
3. Grava `consumo_diario`
   → **RN11**: movimentações `PERDA` ficam de fora da soma.
4. Calcula média, média por dia da semana e ponto de pedido
   → **RN06, RN07, RN08, RN09**: produto com menos de 14 dias não gera número.
5. Grava `previsao_produto`
6. Motor de regras lê estoque, lotes e previsão
7. Decide o que vira aviso
   → **RN05, RN10, RN16**
8. `INSERT` em `alerta` com `status = PENDENTE`
9. Serviço de notificação lê os alertas pendentes e o chat do Sr. João
10. Aplica a janela de silêncio e agrupa
    → **RN12, RN13**
11. Envia a mensagem
12. `UPDATE alerta: status = ENVIADO`
13. Webhook recebe a resposta "Sim, pedir"
14. `UPDATE alerta.resposta_usuario`

**Nenhum passo desta operação tem tela.** É o produto inteiro funcionando de madrugada, sem
ninguém abrir o sistema — e é aqui que o cliente recebe o valor que pediu.

### Operação 04 — Importação das vendas

1. Arquivo de vendas do dia fica disponível
2. Registra a importação com `status = PENDENTE`
3. Lê o arquivo linha a linha
4. Pede a conciliação de cada linha
5. Procura o produto pelo código do caixa
6. Separa o que casou do que não casou
   → **Linha sem produto correspondente fica pendente de revisão e NÃO trava as demais.** O
   sobrinho resolve depois, na tela de importação.
7. `INSERT` em `venda` e `item_venda`
8. `INSERT` em `movimentacao` com `tipo = VENDA`
   → **RN01, RN02**: a baixa sai do lote de validade mais próxima.
9. `UPDATE importacao_pdv`: `OK` ou `PARCIAL`

**Esta operação supõe que o caixa consegue exportar as vendas em arquivo — premissa ainda não
confirmada (decisão D01).**

---

## Cobertura das atividades da loja

| Quem | O que faz hoje | Quem do sistema atende | Coberto? |
|---|---|---|---|
| Sr. João | Passa pelas gôndolas de manhã | Motor de regras e serviço de aviso | Sim |
| Sr. João | Decide o que comprar e quando | Motor de previsão | Sim |
| Sr. João | Tira da prateleira o que está ruim | Aviso de validade | Sim |
| Sr. João | Sai para comprar às pressas | Aviso antecipado pelo prazo do fornecedor | Sim |
| Sr. João | Compra mais no Natal, e às vezes sobra | Previsão por período | **Parcial** |
| Esposa | Confere o caixa no fim do dia | Tela de fechamento de caixa | Sim |
| Esposa | Faz o balanço da semana no caderno | Relatório de balanço | Sim |
| Sobrinho | Lança notas e vendas no Excel | Importador de vendas | Sim |
| Sobrinho | Arruma a mercadoria, o mais velho na frente | Cadastro de lote com validade e ordem de saída | Sim |
| Sobrinho | Anota no caderno o que estragou | Tela de avarias e quebras | Sim |
| Funcionários | Repõem a gôndola e avisam quando falta | Nenhum componente | **Fora de escopo** |
| Sr. João | Faz inventário uma vez por mês | Apoio ao inventário | **Não coberto** |
| Sr. João | Percebe que leite e café saem juntos | Relatório de produtos vendidos juntos | **Não coberto** |

As três últimas linhas são escolhas declaradas, não esquecimentos. **Não as implemente.**

---

## As 10 telas

| Tela | Quem usa | Para que serve |
|---|---|---|
| Login | Todos | Identifica a pessoa e monta o menu conforme o papel (RN14). |
| Produtos | Sobrinho | Cadastra o que a loja vende: categoria, unidade, preços, estoque mínimo. |
| Fornecedores | Sobrinho | Cadastra quem entrega e em quantos dias — número que alimenta o ponto de pedido. |
| Entrada de mercadoria | Sobrinho | Registra o lote que chegou: quantidade, custo e data de validade. |
| Avarias e quebras | Sobrinho | Registra o que venceu, quebrou ou estragou, sempre com o motivo. |
| Importação de vendas | Sobrinho | Traz as vendas registradas no caixa da loja. |
| Consulta de estoque | Todos | Saldo atual, o que está abaixo do mínimo e o que está perto de vencer. |
| Fechamento de caixa | Esposa | Confere o dinheiro contado contra o apurado no dia. |
| Balanço da semana | Esposa | Vendas, perdas e resultado do período. |
| Telegram | Sr. João | Não é tela: é o canal por onde os avisos chegam ao celular. |

**São dez e só dez.** Não crie tela de inventário, de pedido ao fornecedor nem de relatório que não
esteja nesta lista.

**O dono é o usuário que menos abre o sistema.** Isso não é falha do desenho: é consequência direta
do que ele disse — que não dá para ficar no computador porque precisa vender.

---

## Fluxograma × tela × regra

| # | Fluxograma | Tela | Regras | Tabelas |
|---|---|---|---|---|
| 1 | Cadastro de produto | Produtos | RN03, RN14 | produto, categoria |
| 2 | Entrada de mercadoria | Entrada de mercadoria | RN01, RN02, RN04 | lote, movimentacao |
| 3 | Registro de perda | Avarias e quebras | RN01, RN02, RN11 | movimentacao, lote |
| 4 | Importação das vendas | Importação de vendas | RN01, RN02 | importacao_pdv, venda, item_venda, movimentacao |
| 5 | Rodada diária de avisos | Sem tela | RN05 a RN13 | consumo_diario, previsao_produto, alerta |
| 6 | Fechamento de caixa | Fechamento de caixa | RN15 | venda, fechamento_caixa |

**Cada losango de decisão dos fluxogramas vira pelo menos dois testes:** um pelo "sim" e um pelo
"não". O fluxograma 02, sozinho, define seis situações a testar.

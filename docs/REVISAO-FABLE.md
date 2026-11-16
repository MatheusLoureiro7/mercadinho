# Revisão geral do código contra a especificação

Tarefa extra **X1** (fora do cronograma da Apostila IV) · feita em **16/11/2026** · Grupo MDGS

Revisão do projeto inteiro antes da entrega de 01/12/2026, sobre o commit `32c7f7c`. **Nada foi
corrigido nesta tarefa:** este documento é só a lista, em ordem de gravidade.

## O que foi revisado e como

- **Conformidade:** o código comparado com as 16 regras de negócio (`docs/REGRAS-NEGOCIO.md`), os
  requisitos RF01 a RF17 (`docs/ESPECIFICACAO.md`), as 14 tabelas do `schema.sql` e as 10 telas da
  Apostila II.
- **Defeitos que os testes podem não pegar:** data com `date.today()`, perda entrando no consumo
  (RN11), saída pelo lote errado (RN02), saldo gravado fora de `movimentacao` (RN01), view sem `tela`
  (RN14), duas operações ao mesmo tempo no mesmo lote e arredondamento de `Decimal`.
- **Método:** leitura das cerca de 5.400 linhas do backend, do painel e dos documentos; comparação
  do banco deste computador com o `schema.sql` carregado num banco temporário (apagado em seguida).
  Os itens marcados **[reproduzido]** foram confirmados com um teste rodado fora do repositório; os
  outros vêm da leitura do código.

## Resumo

| Gravidade | Problemas |
|---|---|
| Alta | 4 |
| Média | 9 |
| Baixa | 9 |
| **Total** | **22** |

**As regras críticas estão corretas:** o saldo é sempre derivado das movimentações e ninguém o grava
(RN01), a saída segue a ordem de validade (RN02), a perda não entra no consumo (RN11) e toda view
confere o perfil antes de qualquer operação (RN14). Os quatro problemas de gravidade alta estão na
importação das vendas e no que depende dela.

**Combinado:** os itens 1 a 4 serão corrigidos antes do teste de sábado (J4, 21/11/2026).

**Situação em 16/11/2026:** os itens 1 a 4 foram corrigidos (commits `fa2866e`, `b16f38d`, `1b710f5`
e o do item 4), cada um com teste e anotação no Diário do `docs/ACOMPANHAMENTO.md`.

---

## Gravidade alta

### 1. Planilha com outro nome entra duas vezes; com o mesmo nome, não entra [reproduzido]

- **Onde:** `backend/vendas/importacao.py:122`
- **Causa:** a única proteção contra importar duas vezes é o nome do arquivo.
- **Cenário A:** o sobrinho salva `copia.xlsx` com as vendas de um dia já importado. Tudo entra de
  novo: o saldo cai em dobro (ficou −2 no teste), o consumo dobra e a previsão manda comprar mais.
- **Cenário B:** o caixa exporta sempre `vendas.xlsx`. No segundo dia a rodada responde "Nenhuma
  planilha nova" e as vendas nunca entram, sem erro.

### 2. Linha com erro some do valor apurado e o fechamento grava uma diferença falsa [reproduzido]

- **Onde:** `backend/caixa/fechamento.py:33` e `backend/vendas/importacao.py:148`
- **Causa:** importação PARCIAL conta como "vendas importadas", mas a linha recusada não vira venda.
- **Cenário:** cupom de R$ 200,00 com a hora escrita "9h30". O caixa tem R$ 220,00, o sistema apura
  R$ 20,00 e a esposa registra uma sobra de R$ 200,00. Pela RN15 esse registro nunca mais se altera,
  e a tela não avisa que a planilha veio incompleta.

### 3. Saldo e lotes se separam para sempre, e a perda piora [reproduzido]

- **Onde:** `backend/vendas/importacao.py:75` e `backend/estoque/perda.py:55`
- **Causa:** venda maior que o estoque grava a sobra sem lote (decisão do grupo de 05/11/2026); a
  entrada seguinte soma a quantidade inteira no lote. A perda confere a soma dos lotes, não o saldo.
- **Cenário:** 5 em estoque, venda de 8, entrada de 10. O saldo fica 7 e os lotes somam 10. Uma perda
  de 10 foi aceita e o saldo ficou −3.
- **Agravante:** não existe operação que conserte. Nenhum código cria movimentação `AJUSTE` (a
  lacuna L10 continua aberta).

### 4. Planilha com vendas de dois dias trava o fechamento do segundo [reproduzido]

- **Onde:** `backend/vendas/importacao.py:138`
- **Causa:** `data_referencia` é a data da primeira linha da planilha.
- **Cenário:** planilha com vendas de 10/11 e 11/11. O dia 11 aparece como "ainda não entrou no
  sistema" e o fechamento é recusado, embora as vendas estejam gravadas. O balanço também marca o
  dia como sem vendas.

---

## Gravidade média

### 5. Depois do "Sim, pedir", o produto fica calado sem prazo [reproduzido]

- **Onde:** `backend/alertas/ruptura.py:75`
- **Cenário:** o Sr. João toca em "Sim, pedir" e o fornecedor não entrega. A carne zerada não gerou
  aviso em +1, +30 nem +90 dias.
- **Observação:** é a decisão do grupo de 12/11/2026, mas sem limite de dias. Hoje está adormecido,
  porque sem endereço `https` público o toque não chega ao sistema.

### 6. Fechamento só existe para ontem

- **Onde:** `backend/caixa/fechamento.py:28`
- **Cenário:** o caixa de sábado só pode ser registrado no domingo. Se ninguém abrir o sistema no
  domingo, ou a rodada das 03h00 falhar, o sábado nunca mais pode ser fechado.

### 7. Só conta como dinheiro o texto exato "dinheiro" [reproduzido]

- **Onde:** `backend/caixa/fechamento.py:44`
- **Cenário:** planilha sem a coluna Pagamento (ela é opcional), ou com "Espécie". O apurado sai
  R$ 0,00 e a gaveta inteira vira "sobra".

### 8. Produto sem fornecedor padrão nunca avisa que vai acabar

- **Onde:** `backend/previsao/projecao.py:82` e `backend/alertas/ruptura.py:110`
- **Cenário:** o fornecedor é opcional no cadastro. Sem ele não há ponto de pedido, e o carvão pode
  zerar sem aviso. Nenhuma tela mostra que o produto está nessa situação.

### 9. Produto parado e zerado avisa "acabou" todo dia, com urgência alta [reproduzido]

- **Onde:** `backend/alertas/ruptura.py:122`
- **Cenário:** panetone sem venda há 30 dias e saldo 0. O ponto de pedido é 0, e 0 ≤ 0 gera aviso
  toda madrugada, no topo da mensagem.

### 10. Nenhuma tela mostra a previsão nem "ainda aprendendo"

- **Onde:** `backend/estoque/serializers.py:169`
- **Divergência:** a RN09 pede isso nas "telas de consulta", e o RF08 pede "em quantos dias o produto
  acaba". Não há endpoint que leia `previsao_produto`; o número só aparece no Telegram.

### 11. Rodada perdida não é recuperada

- **Onde:** `backend/comum/management/commands/agenda_cron.py:39` e `backend/alertas/ruptura.py:100`
- **Cenário:** notebook fechado às 03h00 de quinta. Não há importação nem avisos, o fechamento fica
  travado, e a avaliação de fim de semana (RN10) não acontece naquela semana, porque sexta não
  avalia.

### 12. Dois produtos com nome igual, mudando só maiúscula ou acento [reproduzido]

- **Onde:** `backend/cadastro/serializers.py:177` e `backend/vendas/importacao.py:58`
- **Cenário:** o cadastro aceita "Arroz 5 kg" e "arroz 5 KG" na mesma categoria. A importação trata o
  nome como ambíguo e toda venda desse produto fica pendente.

### 13. "1.000" digitado na quantidade vira 1

- **Onde:** `frontend/js/formatos.js:25`
- **Cenário:** sem vírgula, o ponto é lido como decimal. Uma entrada de 1.000 latas grava um lote de
  1 UN, sem aviso.

---

## Gravidade baixa

| # | Problema | Onde | Cenário |
|---|---|---|---|
| 14 | Erro 500 com número fora do esperado [reproduzido] | `backend/vendas/views.py:50`; `backend/cadastro/serializers.py:126` e `backend/estoque/regras.py:34` | `/api/itens-pendentes/abc/casar/` responde erro interno; durabilidade de 2.000.000.000 dias é aceita no cadastro e quebra a entrada de mercadoria |
| 15 | Total do cupom arredondado só no fim [reproduzido] | `backend/vendas/importacao.py:104` | 2 × 0,333 kg a R$ 19,99 dá 13,31; o caixa, arredondando por item, dá 13,32 |
| 16 | Duas rodadas ao mesmo tempo | `backend/vendas/importacao.py:121` e `backend/alertas/ruptura.py:106` | Confere e depois grava, sem trava: cron mais comando manual duplicam a importação ou os avisos |
| 17 | Envio é tudo ou nada | `backend/alertas/notificacao.py:90` | Se o Telegram recusar a mensagem agrupada, nenhum aviso sai; em mensagem dividida, a primeira parte pode repetir |
| 18 | Venda casada com o produto errado não tem desfazer | `backend/vendas/conciliacao.py` | O sobrinho escolhe o produto errado na tela de importação e a baixa fica no estoque errado |
| 19 | Banco deste computador diferente do `schema.sql` | `backend/estoque/models.py:87` | O padrão de `movimentacao.data_hora` está como `statement_timestamp()` e a migração diz `NOW()`; as chaves são `IDENTITY`, não `SERIAL`; as chaves estrangeiras são `DEFERRABLE`; há 17 índices a mais. Colunas, tipos, restrições e a view das 14 tabelas conferem |
| 20 | `DJANGO_DEBUG=true` na publicação | `.env.example:5` e o `.env` desta máquina | Endereço errado mostra a página de depuração do Django em vez da resposta em JSON |
| 21 | Uma consulta ao parâmetro por lote | `backend/alertas/validade.py:54` | Com centenas de lotes perecíveis, a rodada faz centenas de leituras iguais |
| 22 | Comentários desatualizados | `backend/comum/management/commands/rodada_diaria.py:6` e `backend/estoque/views.py:10` | O primeiro não cita o aviso de "vai acabar"; o segundo fala em "ajuste", que não existe |

---

## Divergências já decididas pelo grupo

Não são defeitos novos, mas podem ser perguntadas:

- RN05 com prazo global, não por categoria (L01).
- RN10 sem véspera de feriado (L03).
- Produto casado pelo nome, não pelo código do caixa (L05).
- RN16 pelo dia da venda, não por hoje (decisão de 05/11/2026).
- Cinco tabelas internas do Django além das 14 (L09).
- Backup diário inexistente (RNF09).

## O que foi conferido e está certo

- Nenhum `date.today()` nem `float` em dinheiro ou quantidade; o painel também calcula o dia no fuso
  da loja.
- RN11: só `backend/previsao/consumo.py` lê movimentação, sempre filtrando VENDA.
- RN02: ordem por validade, lote vencido fora da venda, lotes travados na perda, na importação e ao
  casar o produto.
- RN14: toda view declara `tela`, e a tabela de acesso é igual à da regra.
- As 10 telas existem (9 páginas mais o Telegram).
- As 14 tabelas têm as mesmas colunas, tipos, restrições e a mesma view de saldo do `schema.sql`.

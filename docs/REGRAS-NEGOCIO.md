# Regras de negócio — forma testável

Transcrição da **Apostila I** para a forma que o código precisa: condição, o que acontece,
mensagem de erro e teste.

**O enunciado de cada regra é o da apostila, palavra por palavra.** O que foi acrescentado aqui
é só a tradução para condição programável e a mensagem ao usuário — e isso está marcado.

Regra de ouro das mensagens (RNF10): o texto usa o vocabulário da loja. É "o frango acaba em 2
dias", nunca "estoque abaixo do ponto de reposição".

---

## Quadro geral

| ID | Regra | Grupo | Criticidade |
|---|---|---|---|
| RN01 | O saldo é sempre derivado das movimentações | Integridade do estoque | Alta |
| RN02 | A saída respeita a ordem de validade (FIFO) | Integridade do estoque | Alta |
| RN03 | Produto perecível exige prazo de durabilidade | Cadastro | Alta |
| RN04 | Lote de perecível precisa de data de validade | Entrada de mercadoria | Alta |
| RN05 | Aviso de validade próxima | Alertas | Alta |
| RN06 | Consumo médio diário | Previsão | Média |
| RN07 | Consumo por dia da semana | Previsão | Média |
| RN08 | Ponto de pedido e aviso de ruptura | Previsão | Alta |
| RN09 | Histórico mínimo para prever | Previsão | Média |
| RN10 | Produtos que não podem faltar no fim de semana | Previsão | Alta |
| RN11 | Perda não conta como consumo | Integridade do estoque | Alta |
| RN12 | Janela de silêncio nos horários de pico | Alertas | Alta |
| RN13 | Avisos agrupados em uma única mensagem | Alertas | Alta |
| RN14 | Três perfis de acesso | Acesso | Média |
| RN15 | Diferença de caixa registrada, nunca corrigida | Conferência | Média |
| RN16 | Lote vencido é bloqueado | Integridade do estoque | Alta |

---

## RN01 — O saldo é sempre derivado das movimentações · ALTA

> O saldo em estoque de um produto é sempre o resultado da soma das suas movimentações. Nenhuma
> tela, nenhum processo e nenhum usuário pode escrever um valor de saldo diretamente.

**Onde:** banco de dados (view `vw_estoque_atual`) e API de movimentação.
**Dados:** `movimentacao` (tipo, quantidade) · `lote` · view de saldo.

**Em código:**

- Não existe coluna de saldo em `produto`. Se você sentir vontade de criar uma, pare.
- `saldo = Σ(ENTRADA) + Σ(AJUSTE) − Σ(VENDA) − Σ(PERDA)`
- Toda operação que muda o estoque grava **uma linha** em `movimentacao` explicando o porquê.
- Operações que gravam em duas tabelas (lote + movimentação) rodam **numa transação só**.
  Se a segunda falhar, a primeira é desfeita. Nunca existe lote sem a movimentação que explica o
  saldo. *(Apostila IV, operação 02, passo 7.)*

**Teste:** entrada de 40 kg, venda de 12 kg, perda de 3 kg → saldo 25 kg, e as três linhas no
histórico. *(Exemplo literal da apostila — já validado contra o `schema.sql`.)*

**Se falhar:** o estoque passa a mentir sem deixar rastro.

---

## RN02 — A saída respeita a ordem de validade (FIFO) · ALTA

> Na baixa por venda, a quantidade sai do lote com a data de validade mais próxima entre os lotes
> disponíveis daquele produto.

**Onde:** serviço de movimentação, na baixa por venda.
**Dados:** `lote` (data_validade, quantidade_atual) · `movimentacao`.

**Em código:**

```sql
SELECT * FROM lote
 WHERE produto_id = :produto AND quantidade_atual > 0
 ORDER BY data_validade ASC         -- nunca por id, nunca por data_entrada
```

- Se a quantidade da venda for maior que o lote mais antigo, consome o lote inteiro e continua no
  próximo, sempre em ordem de validade.
- Lotes vencidos ficam fora desta seleção (RN16).

**Teste:** dois lotes de presunto, um vence 28/09 e outro 05/10. Venda de 2 kg baixa do lote de
28/09, mesmo que o de 05/10 esteja mais à mão.

---

## RN03 — Produto perecível exige prazo de durabilidade · ALTA

> Um produto marcado como perecível só pode ser salvo com o campo de durabilidade em dias
> preenchido e maior que zero.

**Onde:** API de cadastro de produto, **antes de gravar**.
**Dados:** `produto` (perecivel, durabilidade_dias).

**Condição:** `perecivel = true AND (durabilidade_dias IS NULL OR durabilidade_dias <= 0)` → recusa.

**Mensagem** *[acrescentada aqui — não está na apostila]*:
"Produto perecível precisa do prazo de durabilidade em dias. Sem ele o sistema não consegue avisar
quando o produto vai vencer."

O fluxograma 01 manda **manter o que já foi digitado** e apontar só o campo que falta.

**Teste:** marcar "Frango resfriado 1 kg" como perecível sem durabilidade → recusado.
Com 4 dias → salvo.

---

## RN04 — Lote de perecível precisa de data de validade · ALTA

> Ao registrar a entrada de um lote de produto perecível, a data de validade é obrigatória. Se não
> for informada, o sistema calcula automaticamente somando a durabilidade do produto à data de
> entrada. Validade anterior à data de hoje é recusada.

**Onde:** API de entrada de lote.
**Dados:** `lote` (data_entrada, data_validade) · `produto` (durabilidade_dias).

**Em código, nesta ordem:**

1. produto não é perecível → validade opcional, segue.
2. produto é perecível e validade veio preenchida → usa ela.
3. produto é perecível e validade veio vazia → `data_validade = data_entrada + durabilidade_dias`.
4. validade (informada ou calculada) `< CURRENT_DATE` → **recusa**.

**Mensagem** *[acrescentada]*: "Essa validade já passou. Confira a data na embalagem."

**Teste:** entrada de frango em 21/09 sem validade, durabilidade 4 dias → sistema grava 25/09.

---

## RN05 — Aviso de validade próxima · ALTA

> Gera um aviso quando um lote de produto perecível está a N dias ou menos do vencimento. O valor
> de N é configurável e vale por categoria.

**Onde:** motor de regras, na rodada diária (03h00).
**Dados:** `lote` · `alerta` · `parametro (dias_aviso_validade)`.

**Condição:** `lote.data_validade - CURRENT_DATE <= dias_aviso_validade AND quantidade_atual > 0`
→ `INSERT INTO alerta` com `tipo='VALIDADE'`, `status='PENDENTE'`.

**Atenção:** a apostila diz que N **vale por categoria**, mas a tabela `parametro` tem uma chave
única `dias_aviso_validade`. Isso é uma lacuna real da especificação — está listada em
`docs/LACUNAS.md`. Até ser resolvida, implemente o parâmetro global e deixe o ponto de extensão
pronto.

**Mensagem** *[acrescentada, no vocabulário da loja]*: "O presunto vence em 3 dias — 2,5 kg na
prateleira."

**Teste:** lote vence 24/09, parâmetro em 3 dias → aviso gerado em 21/09.

---

## RN06 — Consumo médio diário · MÉDIA

> O consumo médio diário de um produto é o total vendido nos últimos 30 dias dividido por 30. Só
> entram movimentações do tipo VENDA.

**Onde:** motor de previsão, na rodada diária.
**Dados:** `consumo_diario` · `previsao_produto (consumo_medio_diario)`.

**Em código:** divide sempre por **30**, não pelo número de dias com venda. Produto que vendeu em 5
dos 30 dias tem média baixa — e está certo.

**Teste:** arroz, 150 kg em 30 dias → 5 kg/dia. Com 20 kg em estoque, acaba em 4 dias.

---

## RN07 — Consumo por dia da semana · MÉDIA

> Além da média geral, o sistema calcula a média de consumo separada por dia da semana, e usa a
> maior das duas na projeção quando a diferença entre elas for relevante.

**Onde:** motor de previsão.
**Dados:** `consumo_diario (dia_semana)` · `previsao_produto (consumo_por_dia_semana)`.

**Lacuna:** a apostila não define o que é "diferença relevante". Está em `docs/LACUNAS.md`.
Sugestão a confirmar com o grupo: relevante = média do dia da semana ≥ 1,5 × média geral.

**Teste:** cerveja, média geral 8 un/dia, 26 aos sábados. Na quinta a projeção usa o número do fim
de semana, não a média.

---

## RN08 — Ponto de pedido e aviso de ruptura · ALTA

> Ponto de pedido = consumo médio diário × prazo de entrega do fornecedor + estoque de segurança.
> Quando o saldo cai igual ou abaixo desse ponto, gera aviso de ruptura.

**Onde:** motor de previsão (cálculo) e motor de regras (decisão de avisar).
**Dados:** `fornecedor (prazo_entrega_dias)` · `previsao_produto (ponto_pedido)`.

**Fórmula, conferida contra o exemplo da apostila:**

```
estoque_seguranca = consumo_medio_diario × prazo_entrega_dias × (estoque_seguranca_pct / 100)
ponto_pedido      = consumo_medio_diario × prazo_entrega_dias + estoque_seguranca
```

Verificação com o exemplo da apostila: carne a 8 kg/dia, prazo 3 dias, parâmetro 20 %.
`8 × 3 = 24`, segurança `24 × 0,20 = 4,8`, ponto de pedido `28,8 ≈ 29 kg`. **Bate com os 29 kg do
exemplo** — é essa a leitura correta do parâmetro.

**Condição do aviso:** `saldo <= ponto_pedido` → `alerta` com `tipo='RUPTURA'`.

---

## RN09 — Histórico mínimo para prever · MÉDIA

> Com menos de 14 dias de histórico de vendas, o sistema não apresenta número de previsão. Em vez
> disso, informa que ainda está aprendendo aquele produto.

**Onde:** motor de previsão e telas de consulta.
**Dados:** `consumo_diario` · `previsao_produto (calculado_em)`.

**Em código:** `COUNT(DISTINCT data) FROM consumo_diario WHERE produto_id = :p` menor que
`historico_minimo_dias` → **não grava número**, deixa `calculado_em` nulo. A tela mostra
"ainda aprendendo", nunca "0 dias" nem "—".

**Teste:** produto cadastrado há 6 dias mostra "ainda aprendendo", não "acaba em 2 dias".

---

## RN10 — Produtos que não podem faltar no fim de semana · ALTA

> Produtos marcados como críticos de fim de semana são avaliados já na quinta-feira, com acréscimo
> de folga no ponto de pedido, para garantir presença no sábado, domingo e vésperas de feriado.

**Onde:** motor de regras, avaliação de quinta-feira.
**Dados:** `produto (critico_fim_semana)` · `previsao_produto`.

**Em código:** se hoje é quinta e `produto.critico_fim_semana` → compara o saldo com
`ponto_pedido × (1 + folga_fim_semana_pct/100)` e gera `alerta` com `tipo='FIM_SEMANA'`.

Itens que o cliente nomeou um a um: carne, carvão, cerveja, linguiça, asinha de frango.

**Lacuna:** "véspera de feriado" exige um calendário de feriados que a apostila não define.
Está em `docs/LACUNAS.md`.

---

## RN11 — Perda não conta como consumo · ALTA

> Movimentações do tipo PERDA reduzem o estoque, mas são excluídas da base de cálculo de consumo e
> de previsão.

**Onde:** motor de previsão (filtro) e relatório de balanço.
**Dados:** `movimentacao (tipo=PERDA)` · `consumo_diario`.

**Em código:** todo `WHERE` que alimenta `consumo_diario` filtra `tipo = 'VENDA'`. O relatório de
balanço mostra perdas em linha **separada** das vendas.

**Esta é a regra mais fácil de quebrar sem perceber.** Se falhar, quanto mais produto estraga, mais
o sistema manda comprar — o erro se alimenta sozinho.

**Teste:** 10 kg de frango vão fora. O saldo cai 10 kg; o consumo do dia continua sendo só o
vendido.

---

## RN12 — Janela de silêncio nos horários de pico · ALTA

> Nenhum aviso é enviado entre 10h30 e 13h, nem entre 16h30 e 18h. Avisos gerados nessas faixas
> ficam retidos e saem na primeira janela livre.

**Onde:** serviço de notificação, **antes do envio**.
**Dados:** `alerta (status=SEGURADO)` · `parametro (janela_silencio)`.

**Em código:** a verificação é na hora do **envio**, não da geração. Dentro da janela, o alerta vai
para `status='SEGURADO'` e o serviço tenta de novo na próxima execução. Horário local da loja
(`America/Sao_Paulo`).

**Teste:** aviso gerado às 11h15 fica retido e sai às 13h05.

---

## RN13 — Avisos agrupados em uma única mensagem · ALTA

> Todos os avisos pendentes de uma mesma janela de envio são reunidos em uma única mensagem,
> ordenados por urgência.

**Onde:** serviço de notificação.
**Dados:** `alerta (status, severidade, gerado_em)`.

**Em código:** seleciona todos os `PENDENTE` e `SEGURADO`, ordena por severidade e depois por
`gerado_em`, monta **um** texto e faz **uma** chamada ao Telegram. Marca todos como `ENVIADO` com
o mesmo `enviado_em`.

**Teste:** 6 avisos pendentes às 13h05 → uma mensagem com 6 itens, começando pelo que vence
primeiro. Não seis mensagens.

---

## RN14 — Três perfis de acesso · MÉDIA

> Existem três perfis: DONO, GESTAO e OPERACAO. Cada um enxerga e pode fazer apenas o que
> corresponde à sua função. Os dois funcionários da loja não têm acesso ao sistema.

**Onde:** API de autenticação, **antes de qualquer operação**.
**Dados:** `usuario (papel)` · todas as rotas da API.

| Tela | DONO | GESTAO | OPERACAO |
|---|---|---|---|
| Produtos | — | — | ✔ |
| Fornecedores | — | — | ✔ |
| Entrada de mercadoria | — | — | ✔ |
| Avarias e quebras | — | — | ✔ |
| Importação de vendas | — | — | ✔ |
| Consulta de estoque | ✔ | ✔ | ✔ |
| Fechamento de caixa | — | ✔ | — |
| Balanço da semana | — | ✔ | — |
| Telegram (sem tela) | ✔ | — | — |

*Tabela montada a partir do mapa de navegação da Apostila II, seção 3.*

A recusa acontece **antes de tocar no banco** (Apostila IV, operação 01, passo 3).

---

## RN15 — Diferença de caixa registrada, nunca corrigida · MÉDIA

> A diferença de caixa é o valor contado menos o valor apurado pelo sistema. Ela é registrada com
> data e responsável. Correções geram um novo registro; o anterior nunca é apagado.

**Onde:** API de fechamento de caixa.
**Dados:** `fechamento_caixa (valor_sistema, valor_contado, diferenca)`.

**Em código:** `diferenca` é coluna gerada no banco (`valor_contado - valor_sistema`). **Não existe
UPDATE nem DELETE** nesta tabela. A API só aceita INSERT.

**Teste:** sistema apura R$ 3.240,00, contagem dá R$ 3.215,00 → registro com −R$ 25,00, data e
responsável.

---

## RN16 — Lote vencido é bloqueado · ALTA

> Lote com data de validade anterior à data atual fica bloqueado para saída por venda e é destacado
> na tela de estoque. A saída só é possível registrando perda.

**Onde:** API de movimentação e tela de consulta de estoque.
**Dados:** `lote (data_validade)` · `movimentacao`.

**Em código:** na seleção FIFO da RN02, `AND (data_validade IS NULL OR data_validade >= CURRENT_DATE)`.
Movimentação `tipo='PERDA'` **ignora** esse bloqueio — é justamente por ela que o lote vencido sai.

**Teste:** lote de iogurte vencido em 20/09 aparece destacado em 21/09, não pode ser baixado por
venda, e sai pela tela de avarias com motivo.

---

## Parâmetros

Ficam na tabela `parametro`, nunca fixos no código. **Nenhum valor abaixo foi confirmado pelo
cliente** — são propostas da equipe e o primeiro assunto da próxima conversa.

| Chave | Proposto | Para que serve | Regra |
|---|---|---|---|
| `dias_aviso_validade` | 3 dias | Antecedência do aviso de vencimento | RN05 |
| `estoque_seguranca_pct` | 20 % | Folga somada ao ponto de pedido | RN08 |
| `janela_silencio_manha` | 10h30–13h00 | Primeiro pico de venda | RN12 |
| `janela_silencio_tarde` | 16h30–18h00 | Segundo pico de venda | RN12 |
| `historico_minimo_dias` | 14 dias | Mínimo para projetar | RN09 |
| `folga_fim_semana_pct` | 40 % | Acréscimo nos itens críticos | RN10 |
| `hora_rodada_diaria` | 03h00 | Quando os cálculos rodam | — |

# Lacunas e divergências da especificação

Pontos em que a documentação entregue **não é suficiente para programar sem escolher por conta
própria**. Nenhum deles foi resolvido aqui: estão listados para o grupo decidir, e alguns para
perguntar ao professor ou ao cliente.

**Enquanto uma lacuna estiver aberta, não invente a resposta no código.** Implemente o mínimo que
não fecha porta e deixe o ponto de extensão pronto.

---

## 1. Lacunas que afetam o código

### L01 — `dias_aviso_validade` é global ou por categoria?

A **RN05** diz: *"O valor de N é configurável e vale por categoria."*
Mas a tabela `parametro` da Apostila IV tem chave única (`dias_aviso_validade`), que só comporta um
valor global.

A própria Apostila I reconhece o problema: *"3 dias serve para carne, mas é pouco para um produto
de giro lento."*

**Impacto:** tarefa H2 (gerador do aviso de validade, 8 h).
**O que fazer agora:** implementar o parâmetro global, mas ler o valor por uma função
`dias_aviso_validade(produto)` — assim, quando a decisão sair, muda um lugar só.
**Quem decide:** o grupo, e vale confirmar com o cliente.

---

### L02 — O que é "diferença relevante" na RN07?

A **RN07** diz que o sistema usa a maior entre a média geral e a média do dia da semana *"quando a
diferença entre elas for relevante"*. Relevante não está definido em lugar nenhum.

**Impacto:** tarefa G2 (12 h), a mais difícil do projeto.
**Proposta para o grupo decidir:** usar a média do dia da semana quando ela for **≥ 1,5 ×** a média
geral. O exemplo da apostila (cerveja: 8/dia na média, 26 aos sábados) passaria com folga nesse
critério.
**Quem decide:** o grupo. É uma escolha técnica, não precisa do cliente.

---

### L03 — Qual calendário de feriados a RN10 usa?

A **RN10** manda avaliar os itens críticos também em **véspera de feriado**. A especificação não
diz de onde vem a lista de feriados.

**Impacto:** tarefa H3 (10 h).
**Opções:** tabela de feriados cadastrada à mão pela esposa; biblioteca de feriados nacionais;
ignorar feriado na primeira versão e tratar só sábado e domingo.
**Quem decide:** o grupo. Se escolher ignorar, **declare isso** — vira um item de escopo, não um
esquecimento.

---

### L04 — O que é a "previsão por período" do Natal?

A Apostila IV, seção 8, marca como **Parcial** a atividade *"Compra mais no Natal, e às vezes
sobra"*, atendida por "Previsão por período". Nenhuma RF e nenhuma RN descrevem esse cálculo.

**Impacto:** nenhuma tarefa do cronograma implementa isso. A linha "Parcial" fica sem código.
**O que fazer:** não implementar. Se o professor perguntar, a resposta honesta é que a cobertura é
parcial justamente porque a regra de sazonalidade não foi especificada.

---

### L05 — Como o `item_venda` casa com o `produto`?

A operação 04 fala em *"procura o produto pelo código do caixa"*, e a tarefa E4 (10 h) se chama
"casar o produto do caixa com o produto cadastrado". Mas a tabela `produto` **não tem uma coluna
para o código do caixa**.

**Impacto:** tarefa E4. Sem esse campo, o casamento teria de ser por nome, que é frágil.
**Proposta:** acrescentar `produto.codigo_pdv VARCHAR(40) UNIQUE`.
**Atenção:** isso é uma alteração no modelo de dados da Apostila IV. **Não faça sem o grupo
decidir e sem registrar a mudança numa versão 1.1 da apostila.** Depende também de D01, porque o
formato do arquivo é que diz qual é o código.

---

## 2. Divergências internas da documentação entregue

São erros pequenos nas apostilas, de contagem. Não impedem programar, mas é melhor corrigir numa
versão 1.1 do que o professor encontrar.

### L06 — "13 tabelas" na capa, 14 nas figuras

A capa da Apostila IV diz *"13 tabelas · 52 tarefas · 378 horas estimadas"*.
As figuras 5 e 6 desenham **14 tabelas**:

- Figura 5 (7): categoria, produto, fornecedor, lote, movimentacao, item_venda, venda
- Figura 6 (7): usuario, importacao_pdv, consumo_diario, alerta, parametro, fechamento_caixa, previsao_produto

**O desenho está certo e a contagem da capa está errada.** O `schema.sql` segue as figuras.

### L07 — "52 tarefas" na capa, 51 nas tabelas

Somando as tarefas listadas na seção 9: A 5 + B 7 + C 6 + D 4 + E 5 + F 3 + G 5 + H 7 + I 3 + J 6 =
**51**.

As **horas** estão todas corretas: os totais por bloco somam 378 h, e as etapas batem em 212 / 136
/ 30. O erro é só na contagem de tarefas da capa.

### L08 — A Apostila V contradiz as Apostilas I a IV

O cronograma datado (Apostila V) foi montado com uma lista de tarefas diferente da seção 9 da
Apostila IV, e por isso:

- cita **tela e API de inventário**, que a Apostila IV marca como **"não coberto"** e a Apostila II
  não lista entre as 10 telas;
- cita **"API de pedido ao fornecedor"**, que não corresponde a nenhum RF (o RF11 é *sugerir quanto
  comprar*, não emitir pedido);
- **não contém** o importador do PDV, o motor de previsão, os avisos no Telegram nem o fechamento
  de caixa — que são o núcleo do produto;
- usa os **códigos de RN trocados** (por exemplo, trata RN13–RN14 como regras de inventário, quando
  RN13 é agrupamento de avisos e RN14 é perfis de acesso);
- totaliza **362 h**, contra as **378 h** da Apostila IV.

**Este pacote segue as Apostilas I a IV.** A Apostila V precisa ser refeita em cima da seção 9 da
Apostila IV antes de ser entregue ao professor.

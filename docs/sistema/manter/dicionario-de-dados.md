# Modelo e dicionário de dados

> Gerado automaticamente por `docs/sistema/gerar.py` a partir do código. Não edite à mão: a suíte de testes falha se este arquivo ficar diferente do código.

Fonte: `schema.sql`, a transcrição da Apostila IV, seção 6 — e conferido contra o banco criado
pelas migrações em `backend/tests/` (cada tabela tem um teste `divergencias_do_schema`).
Saldo de estoque não é coluna: é a view `vw_estoque_atual`, derivada das movimentações (RN01).

## `categoria`

Agrupamento de produtos. Usa o vocabulário da loja: "Secos e molhados", "Açougue", "Frios". RNF10.

Model no código: `cadastro.Categoria`

| Coluna | Tipo | Regras | Observação |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | — |
| `nome` | VARCHAR(80) | NOT NULL UNIQUE | — |
| `perecivel_padrao` | BOOLEAN | NOT NULL DEFAULT FALSE | — |

## `fornecedor`

Model no código: `cadastro.Fornecedor`

| Coluna | Tipo | Regras | Observação |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | — |
| `nome` | VARCHAR(120) | NOT NULL | — |
| `prazo_entrega_dias` | INTEGER | NOT NULL | Dias entre o pedido e a entrega. É o número que faz o aviso de ruptura sair com antecedência (RN08). |
| `pedido_minimo` | NUMERIC(12,2) | — | — |
| `contato` | VARCHAR(160) | — | — |

Restrições: `CONSTRAINT ck_fornecedor_prazo CHECK (prazo_entrega_dias >= 0)`

## `produto`

ATENÇÃO: não existe coluna de saldo aqui. O saldo é derivado das movimentações (RN01).

Model no código: `cadastro.Produto`

| Coluna | Tipo | Regras | Observação |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | — |
| `categoria_id` | INTEGER | NOT NULL REFERENCES categoria(id) | — |
| `fornecedor_padrao_id` | INTEGER | REFERENCES fornecedor(id) | — |
| `nome` | VARCHAR(160) | NOT NULL | — |
| `unidade_medida` | VARCHAR(10) | NOT NULL | 'KG', 'UN', 'L', 'PCT' |
| `perecivel` | BOOLEAN | NOT NULL DEFAULT FALSE | — |
| `durabilidade_dias` | INTEGER | — | obrigatório se perecivel (RN03) |
| `preco_custo` | NUMERIC(12,2) | — | — |
| `preco_venda` | NUMERIC(12,2) | — | — |
| `estoque_minimo` | NUMERIC(12,3) | — | — |
| `critico_fim_semana` | BOOLEAN | NOT NULL DEFAULT FALSE | Itens que o cliente nomeou como intocáveis no fim de semana: carne, carvão, cerveja, linguiça, asinha de frango. RN10. |

Restrições: `CONSTRAINT ck_produto_rn03 CHECK (` · `CONSTRAINT uq_produto_nome_categoria UNIQUE (categoria_id, nome)`

## `lote`

Model no código: `estoque.Lote`

| Coluna | Tipo | Regras | Observação |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | — |
| `produto_id` | INTEGER | NOT NULL REFERENCES produto(id) | — |
| `fornecedor_id` | INTEGER | REFERENCES fornecedor(id) | — |
| `quantidade_inicial` | NUMERIC(12,3) | NOT NULL | — |
| `quantidade_atual` | NUMERIC(12,3) | NOT NULL | Saldo DO LOTE, usado pelo FIFO (RN02). Não confundir com o saldo do produto, que é derivado das movimentações (RN01). |
| `custo_unitario` | NUMERIC(12,2) | — | — |
| `data_entrada` | DATE | NOT NULL DEFAULT CURRENT_DATE | — |
| `data_validade` | DATE | — | RN04: se não informada num produto perecível, o sistema grava data_entrada + produto.durabilidade_dias. Validade no passado é recusada. |

Restrições: `CONSTRAINT ck_lote_qtd CHECK (quantidade_atual >= 0)`

## `usuario`

Model no código: `cadastro.Usuario`

| Coluna | Tipo | Regras | Observação |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | — |
| `nome` | VARCHAR(120) | NOT NULL | — |
| `papel` | VARCHAR(10) | NOT NULL | RN14 |
| `login` | VARCHAR(60) | NOT NULL UNIQUE | — |
| `senha_hash` | VARCHAR(255) | NOT NULL | RNF12: nunca em texto puro |
| `telegram_chat_id` | VARCHAR(40) | — | só o DONO recebe aviso |
| `ativo` | BOOLEAN | NOT NULL DEFAULT TRUE | — |

Restrições: `CONSTRAINT ck_usuario_papel CHECK (papel IN ('DONO', 'GESTAO', 'OPERACAO'))`

## `movimentacao`

A ÚNICA coisa que altera o estoque. Toda linha explica uma mudança de saldo (RN01). Nada é apagado.

Model no código: `estoque.Movimentacao`

| Coluna | Tipo | Regras | Observação |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | — |
| `produto_id` | INTEGER | NOT NULL REFERENCES produto(id) | — |
| `lote_id` | INTEGER | REFERENCES lote(id) | nulo: a apostila marca "(nulo)" |
| `usuario_id` | INTEGER | REFERENCES usuario(id) | — |
| `tipo` | VARCHAR(10) | NOT NULL | ENTRADA e AJUSTE somam, VENDA e PERDA subtraem. PERDA é excluída da base de consumo (RN11). |
| `quantidade` | NUMERIC(12,3) | NOT NULL | — |
| `preco_unitario` | NUMERIC(12,2) | — | — |
| `data_hora` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | — |
| `motivo` | VARCHAR(200) | — | obrigatório quando tipo = 'PERDA' (tarefa D1) |
| `origem` | VARCHAR(20) | — | 'TELA', 'IMPORTACAO_PDV', 'AJUSTE' |

Restrições: `CONSTRAINT ck_mov_tipo CHECK (tipo IN ('ENTRADA', 'VENDA', 'PERDA', 'AJUSTE'))` · `CONSTRAINT ck_mov_qtd CHECK (quantidade > 0)` · `CONSTRAINT ck_mov_perda_motivo CHECK (`

## `venda`

Vem do arquivo exportado pelo caixa da loja (importador, fluxograma 04). O sistema NÃO registra venda pela tela.

Model no código: `vendas.Venda`

| Coluna | Tipo | Regras | Observação |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | — |
| `data_hora` | TIMESTAMPTZ | NOT NULL | — |
| `valor_total` | NUMERIC(12,2) | NOT NULL | — |
| `forma_pagamento` | VARCHAR(30) | — | — |

## `item_venda`

Model no código: `vendas.ItemVenda`

| Coluna | Tipo | Regras | Observação |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | — |
| `venda_id` | INTEGER | NOT NULL REFERENCES venda(id) ON DELETE CASCADE | — |
| `produto_id` | INTEGER | REFERENCES produto(id) | Fica nulo quando a linha do arquivo não casou com nenhum produto cadastrado. Linha pendente NÃO trava as demais (fluxograma 04). |
| `quantidade` | NUMERIC(12,3) | NOT NULL | — |
| `preco` | NUMERIC(12,2) | — | — |

## `parametro`

Números das regras que NÃO ficam fixos no código. Apostila I, seção 7. Os valores iniciais ainda não foram validados com o cliente.

Model no código: `comum.Parametro`

| Coluna | Tipo | Regras | Observação |
|---|---|---|---|
| `chave` | VARCHAR(60) | PRIMARY KEY | — |
| `valor` | VARCHAR(80) | NOT NULL | — |
| `descricao` | VARCHAR(200) | — | — |
| `atualizado_em` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | — |

## `importacao_pdv`

ATENÇÃO — decisão D01 em aberto: ainda não foi confirmado que o caixa exporta arquivo, nem em que formato.

Model no código: `vendas.ImportacaoPdv`

| Coluna | Tipo | Regras | Observação |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | — |
| `arquivo_nome` | VARCHAR(200) | NOT NULL | — |
| `data_referencia` | DATE | NOT NULL | — |
| `linhas_lidas` | INTEGER | NOT NULL DEFAULT 0 | — |
| `linhas_erro` | INTEGER | NOT NULL DEFAULT 0 | — |
| `status` | VARCHAR(12) | NOT NULL DEFAULT 'PENDENTE' | — |
| `processado_em` | TIMESTAMPTZ | — | — |

Restrições: `CONSTRAINT ck_imp_status CHECK (status IN ('PENDENTE', 'OK', 'PARCIAL', 'ERRO'))`

## `fechamento_caixa`

RN15: correção gera NOVO registro. O anterior nunca é apagado nem sobrescrito — o padrão ao longo das semanas é o que revela o problema.

Model no código: `caixa.FechamentoCaixa`

| Coluna | Tipo | Regras | Observação |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | — |
| `data` | DATE | NOT NULL | — |
| `valor_sistema` | NUMERIC(12,2) | NOT NULL | — |
| `valor_contado` | NUMERIC(12,2) | NOT NULL | — |
| `diferenca` | NUMERIC(12,2) | GENERATED ALWAYS AS (valor_contado - valor_sistema) STORED | — |
| `registrado_por` | INTEGER | REFERENCES usuario(id) | RN15: "com data e responsável" |
| `registrado_em` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | — |

## `consumo_diario`

RN11: só entram movimentações tipo VENDA. PERDA fica de fora — se entrasse, o sistema acharia que o produto vendeu.

Model no código: `previsao.ConsumoDiario`

| Coluna | Tipo | Regras | Observação |
|---|---|---|---|
| `produto_id` | INTEGER | NOT NULL REFERENCES produto(id) | — |
| `data` | DATE | NOT NULL | — |
| `quantidade_vendida` | NUMERIC(12,3) | NOT NULL DEFAULT 0 | — |
| `dia_semana` | SMALLINT | NOT NULL | RN07 |

Restrições: `PRIMARY KEY (produto_id, data)` · `CONSTRAINT ck_consumo_dia CHECK (dia_semana BETWEEN 0 AND 6)`

## `previsao_produto`

Model no código: `previsao.PrevisaoProduto`

| Coluna | Tipo | Regras | Observação |
|---|---|---|---|
| `produto_id` | INTEGER | PRIMARY KEY REFERENCES produto(id) | — |
| `consumo_medio_diario` | NUMERIC(12,3) | — | RN06 |
| `consumo_por_dia_semana` | JSONB | — | RN07 — [derivado: a apostila não fixa o formato] |
| `dias_ate_acabar` | NUMERIC(8,1) | — | — |
| `ponto_pedido` | NUMERIC(12,3) | — | RN08 |
| `sugestao_compra` | NUMERIC(12,3) | — | RF11 |
| `calculado_em` | TIMESTAMPTZ | — | RN09: com menos de 14 dias de histórico o sistema NÃO apresenta número. Mostra "ainda aprendendo". |

## `alerta`

Model no código: `alertas.Alerta`

| Coluna | Tipo | Regras | Observação |
|---|---|---|---|
| `id` | SERIAL | PRIMARY KEY | — |
| `produto_id` | INTEGER | NOT NULL REFERENCES produto(id) | — |
| `lote_id` | INTEGER | REFERENCES lote(id) | nulo em aviso de ruptura |
| `tipo` | VARCHAR(20) | NOT NULL | — |
| `severidade` | VARCHAR(10) | NOT NULL | — |
| `mensagem` | TEXT | NOT NULL | RNF10: vocabulário da loja |
| `gerado_em` | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | — |
| `enviado_em` | TIMESTAMPTZ | — | — |
| `canal` | VARCHAR(20) | NOT NULL DEFAULT 'TELEGRAM' | — |
| `status` | VARCHAR(12) | NOT NULL DEFAULT 'PENDENTE' | — |
| `resposta_usuario` | VARCHAR(40) | — | "Sim, pedir" (fluxograma 05, passo 13) |
| `destinatario_id` | INTEGER | REFERENCES usuario(id) | — |

Restrições: `CONSTRAINT ck_alerta_tipo CHECK (tipo IN ('VALIDADE', 'RUPTURA', 'FIM_SEMANA'))` · `CONSTRAINT ck_alerta_status CHECK (status IN ('PENDENTE', 'SEGURADO', 'ENVIADO', 'CANCELADO'))`

-- =====================================================================
-- Sistema de Gestão de Estoque e Compras — Mercado do Sr. João
-- Grupo MDGS · PostgreSQL
--
-- Transcrição literal do modelo de dados da Apostila IV, seção 6
-- (figuras 5 e 6). Nenhuma tabela e nenhuma coluna foi acrescentada.
--
-- Os tipos, tamanhos, chaves estrangeiras, restrições CHECK e índices
-- NÃO estão desenhados na apostila: foram derivados do uso descrito nas
-- regras de negócio. Estão marcados com [derivado] e podem ser
-- discutidos — a estrutura de tabelas e colunas, não.
--
-- OBSERVAÇÃO: a capa da Apostila IV diz "13 tabelas", mas as figuras 5
-- e 6 desenham 14. Este arquivo segue as figuras, que são o desenho
-- normativo. Vale corrigir a contagem da capa numa próxima versão.
-- =====================================================================

-- ---------------------------------------------------------------------
-- GRUPO 1 · TABELAS DE ORIGEM — registram o que aconteceu na loja.
-- Nunca podem ser apagadas ou recalculadas (Apostila IV, seção 5).
-- ---------------------------------------------------------------------

CREATE TABLE categoria (
    id                    SERIAL       PRIMARY KEY,
    nome                  VARCHAR(80)  NOT NULL UNIQUE,
    perecivel_padrao      BOOLEAN      NOT NULL DEFAULT FALSE
);

COMMENT ON TABLE categoria IS
    'Agrupamento de produtos. Usa o vocabulário da loja: "Secos e molhados", "Açougue", "Frios". RNF10.';


CREATE TABLE fornecedor (
    id                    SERIAL       PRIMARY KEY,
    nome                  VARCHAR(120) NOT NULL,
    prazo_entrega_dias    INTEGER      NOT NULL,     -- alimenta o ponto de pedido (RN08)
    pedido_minimo         NUMERIC(12,2),
    contato               VARCHAR(160),

    CONSTRAINT ck_fornecedor_prazo CHECK (prazo_entrega_dias >= 0)   -- [derivado]
);

COMMENT ON COLUMN fornecedor.prazo_entrega_dias IS
    'Dias entre o pedido e a entrega. É o número que faz o aviso de ruptura sair com antecedência (RN08).';


CREATE TABLE produto (
    id                    SERIAL       PRIMARY KEY,
    categoria_id          INTEGER      NOT NULL REFERENCES categoria(id),
    fornecedor_padrao_id  INTEGER               REFERENCES fornecedor(id),
    nome                  VARCHAR(160) NOT NULL,
    unidade_medida        VARCHAR(10)  NOT NULL,     -- 'KG', 'UN', 'L', 'PCT'
    perecivel             BOOLEAN      NOT NULL DEFAULT FALSE,
    durabilidade_dias     INTEGER,                   -- obrigatório se perecivel (RN03)
    preco_custo           NUMERIC(12,2),
    preco_venda           NUMERIC(12,2),
    estoque_minimo        NUMERIC(12,3),
    critico_fim_semana    BOOLEAN      NOT NULL DEFAULT FALSE,  -- RN10

    -- RN03: produto perecível só pode ser salvo com durabilidade preenchida e maior que zero.
    -- A validação também existe na API (fluxograma 01), mas o banco é a última linha de defesa.
    CONSTRAINT ck_produto_rn03 CHECK (
        perecivel = FALSE OR (durabilidade_dias IS NOT NULL AND durabilidade_dias > 0)
    ),
    -- Fluxograma 01: "já existe produto com este nome na categoria?"
    CONSTRAINT uq_produto_nome_categoria UNIQUE (categoria_id, nome)   -- [derivado]
);

COMMENT ON TABLE produto IS
    'ATENÇÃO: não existe coluna de saldo aqui. O saldo é derivado das movimentações (RN01).';
COMMENT ON COLUMN produto.critico_fim_semana IS
    'Itens que o cliente nomeou como intocáveis no fim de semana: carne, carvão, cerveja, linguiça, asinha de frango. RN10.';


CREATE TABLE lote (
    id                    SERIAL       PRIMARY KEY,
    produto_id            INTEGER      NOT NULL REFERENCES produto(id),
    fornecedor_id         INTEGER               REFERENCES fornecedor(id),
    quantidade_inicial    NUMERIC(12,3) NOT NULL,
    quantidade_atual      NUMERIC(12,3) NOT NULL,
    custo_unitario        NUMERIC(12,2),
    data_entrada          DATE         NOT NULL DEFAULT CURRENT_DATE,
    data_validade         DATE,                      -- obrigatória se o produto é perecível (RN04)

    CONSTRAINT ck_lote_qtd CHECK (quantidade_atual >= 0)               -- [derivado]
);

-- RN02 (FIFO): a baixa por venda procura o lote de validade mais próxima.
CREATE INDEX ix_lote_fifo ON lote (produto_id, data_validade)          -- [derivado]
    WHERE quantidade_atual > 0;

COMMENT ON COLUMN lote.data_validade IS
    'RN04: se não informada num produto perecível, o sistema grava data_entrada + produto.durabilidade_dias. Validade no passado é recusada.';
COMMENT ON COLUMN lote.quantidade_atual IS
    'Saldo DO LOTE, usado pelo FIFO (RN02). Não confundir com o saldo do produto, que é derivado das movimentações (RN01).';


CREATE TABLE usuario (
    id                    SERIAL       PRIMARY KEY,
    nome                  VARCHAR(120) NOT NULL,
    papel                 VARCHAR(10)  NOT NULL,     -- RN14
    login                 VARCHAR(60)  NOT NULL UNIQUE,
    senha_hash            VARCHAR(255) NOT NULL,     -- RNF12: nunca em texto puro
    telegram_chat_id      VARCHAR(40),               -- só o DONO recebe aviso
    ativo                 BOOLEAN      NOT NULL DEFAULT TRUE,

    -- RN14: existem exatamente três perfis. Os dois funcionários da loja não acessam.
    CONSTRAINT ck_usuario_papel CHECK (papel IN ('DONO', 'GESTAO', 'OPERACAO'))
);


CREATE TABLE movimentacao (
    id                    SERIAL       PRIMARY KEY,
    produto_id            INTEGER      NOT NULL REFERENCES produto(id),
    lote_id               INTEGER               REFERENCES lote(id),   -- nulo: a apostila marca "(nulo)"
    usuario_id            INTEGER               REFERENCES usuario(id),
    tipo                  VARCHAR(10)  NOT NULL,
    quantidade            NUMERIC(12,3) NOT NULL,
    preco_unitario        NUMERIC(12,2),
    data_hora             TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    motivo                VARCHAR(200),              -- obrigatório quando tipo = 'PERDA' (tarefa D1)
    origem                VARCHAR(20),               -- 'TELA', 'IMPORTACAO_PDV', 'AJUSTE'

    CONSTRAINT ck_mov_tipo CHECK (tipo IN ('ENTRADA', 'VENDA', 'PERDA', 'AJUSTE')),
    CONSTRAINT ck_mov_qtd  CHECK (quantidade > 0),                     -- [derivado]
    -- Tarefa D1: "API de registro de perda, com motivo obrigatório"
    CONSTRAINT ck_mov_perda_motivo CHECK (                             -- [derivado]
        tipo <> 'PERDA' OR (motivo IS NOT NULL AND length(trim(motivo)) > 0)
    )
);

CREATE INDEX ix_mov_produto_data ON movimentacao (produto_id, data_hora);  -- [derivado]
CREATE INDEX ix_mov_tipo_data    ON movimentacao (tipo, data_hora);        -- [derivado] RN11

COMMENT ON TABLE movimentacao IS
    'A ÚNICA coisa que altera o estoque. Toda linha explica uma mudança de saldo (RN01). Nada é apagado.';
COMMENT ON COLUMN movimentacao.tipo IS
    'ENTRADA e AJUSTE somam, VENDA e PERDA subtraem. PERDA é excluída da base de consumo (RN11).';


CREATE TABLE venda (
    id                    SERIAL       PRIMARY KEY,
    data_hora             TIMESTAMPTZ  NOT NULL,
    valor_total           NUMERIC(12,2) NOT NULL,
    forma_pagamento       VARCHAR(30)
);

COMMENT ON TABLE venda IS
    'Vem do arquivo exportado pelo caixa da loja (importador, fluxograma 04). O sistema NÃO registra venda pela tela.';


CREATE TABLE item_venda (
    id                    SERIAL       PRIMARY KEY,
    venda_id              INTEGER      NOT NULL REFERENCES venda(id) ON DELETE CASCADE,
    produto_id            INTEGER               REFERENCES produto(id),  -- nulo enquanto não casar
    quantidade            NUMERIC(12,3) NOT NULL,
    preco                 NUMERIC(12,2)
);

COMMENT ON COLUMN item_venda.produto_id IS
    'Fica nulo quando a linha do arquivo não casou com nenhum produto cadastrado. Linha pendente NÃO trava as demais (fluxograma 04).';


-- ---------------------------------------------------------------------
-- GRUPO 2 · APOIO
-- ---------------------------------------------------------------------

CREATE TABLE parametro (
    chave                 VARCHAR(60)  PRIMARY KEY,
    valor                 VARCHAR(80)  NOT NULL,
    descricao             VARCHAR(200),
    atualizado_em         TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE parametro IS
    'Números das regras que NÃO ficam fixos no código. Apostila I, seção 7. Os valores iniciais ainda não foram validados com o cliente.';


CREATE TABLE importacao_pdv (
    id                    SERIAL       PRIMARY KEY,
    arquivo_nome          VARCHAR(200) NOT NULL,
    data_referencia       DATE         NOT NULL,
    linhas_lidas          INTEGER      NOT NULL DEFAULT 0,
    linhas_erro           INTEGER      NOT NULL DEFAULT 0,
    status                VARCHAR(12)  NOT NULL DEFAULT 'PENDENTE',
    processado_em         TIMESTAMPTZ,

    CONSTRAINT ck_imp_status CHECK (status IN ('PENDENTE', 'OK', 'PARCIAL', 'ERRO'))
);

COMMENT ON TABLE importacao_pdv IS
    'ATENÇÃO — decisão D01 em aberto: ainda não foi confirmado que o caixa exporta arquivo, nem em que formato.';


CREATE TABLE fechamento_caixa (
    id                    SERIAL       PRIMARY KEY,
    data                  DATE         NOT NULL,
    valor_sistema         NUMERIC(12,2) NOT NULL,
    valor_contado         NUMERIC(12,2) NOT NULL,
    diferenca             NUMERIC(12,2) GENERATED ALWAYS AS (valor_contado - valor_sistema) STORED,
    registrado_por        INTEGER               REFERENCES usuario(id),   -- RN15: "com data e responsável"
    registrado_em         TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE fechamento_caixa IS
    'RN15: correção gera NOVO registro. O anterior nunca é apagado nem sobrescrito — o padrão ao longo das semanas é o que revela o problema.';


-- ---------------------------------------------------------------------
-- GRUPO 3 · TABELAS DERIVADAS — resultado de cálculo.
-- Podem ser recalculadas a qualquer momento a partir das de origem,
-- sem perda (Apostila IV, seção 5).
-- ---------------------------------------------------------------------

CREATE TABLE consumo_diario (
    produto_id            INTEGER      NOT NULL REFERENCES produto(id),
    data                  DATE         NOT NULL,
    quantidade_vendida    NUMERIC(12,3) NOT NULL DEFAULT 0,
    dia_semana            SMALLINT     NOT NULL,     -- RN07

    PRIMARY KEY (produto_id, data),
    CONSTRAINT ck_consumo_dia CHECK (dia_semana BETWEEN 0 AND 6)       -- [derivado]
);

COMMENT ON TABLE consumo_diario IS
    'RN11: só entram movimentações tipo VENDA. PERDA fica de fora — se entrasse, o sistema acharia que o produto vendeu.';


CREATE TABLE previsao_produto (
    produto_id            INTEGER      PRIMARY KEY REFERENCES produto(id),
    consumo_medio_diario  NUMERIC(12,3),             -- RN06
    consumo_por_dia_semana JSONB,                    -- RN07 — [derivado: a apostila não fixa o formato]
    dias_ate_acabar       NUMERIC(8,1),
    ponto_pedido          NUMERIC(12,3),             -- RN08
    sugestao_compra       NUMERIC(12,3),             -- RF11
    calculado_em          TIMESTAMPTZ                -- RN09: nulo = ainda aprendendo
);

COMMENT ON COLUMN previsao_produto.calculado_em IS
    'RN09: com menos de 14 dias de histórico o sistema NÃO apresenta número. Mostra "ainda aprendendo".';


CREATE TABLE alerta (
    id                    SERIAL       PRIMARY KEY,
    produto_id            INTEGER      NOT NULL REFERENCES produto(id),
    lote_id               INTEGER               REFERENCES lote(id),   -- nulo em aviso de ruptura
    tipo                  VARCHAR(20)  NOT NULL,
    severidade            VARCHAR(10)  NOT NULL,
    mensagem              TEXT         NOT NULL,     -- RNF10: vocabulário da loja
    gerado_em             TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    enviado_em            TIMESTAMPTZ,
    canal                 VARCHAR(20)  NOT NULL DEFAULT 'TELEGRAM',
    status                VARCHAR(12)  NOT NULL DEFAULT 'PENDENTE',
    resposta_usuario      VARCHAR(40),               -- "Sim, pedir" (fluxograma 05, passo 13)
    destinatario_id       INTEGER               REFERENCES usuario(id),

    CONSTRAINT ck_alerta_tipo   CHECK (tipo IN ('VALIDADE', 'RUPTURA', 'FIM_SEMANA')),
    -- RN12: SEGURADO é o aviso retido na janela de silêncio
    CONSTRAINT ck_alerta_status CHECK (status IN ('PENDENTE', 'SEGURADO', 'ENVIADO', 'CANCELADO'))
);

CREATE INDEX ix_alerta_pendente ON alerta (status, gerado_em);         -- [derivado] RN13


-- ---------------------------------------------------------------------
-- VISÃO DE SALDO — RN01
-- A apostila cita esta view pelo nome na ficha da RN01.
-- O saldo NUNCA é uma coluna: é sempre a soma das movimentações.
-- ---------------------------------------------------------------------

CREATE VIEW vw_estoque_atual AS
SELECT
    p.id                AS produto_id,
    p.nome              AS produto_nome,
    p.unidade_medida,
    p.estoque_minimo,
    COALESCE(SUM(
        CASE m.tipo
            WHEN 'ENTRADA' THEN  m.quantidade
            WHEN 'AJUSTE'  THEN  m.quantidade
            WHEN 'VENDA'   THEN -m.quantidade
            WHEN 'PERDA'   THEN -m.quantidade
        END
    ), 0)               AS saldo
FROM produto p
LEFT JOIN movimentacao m ON m.produto_id = p.id
GROUP BY p.id, p.nome, p.unidade_medida, p.estoque_minimo;

COMMENT ON VIEW vw_estoque_atual IS
    'RN01. Todo número desta view pode ser explicado linha a linha pelas movimentações que o geraram.';


-- ---------------------------------------------------------------------
-- PARÂMETROS INICIAIS — Apostila I, seção 7
--
-- ATENÇÃO: nenhum destes valores foi confirmado pelo cliente. São
-- propostas da equipe e o primeiro assunto da próxima conversa com ele.
-- ---------------------------------------------------------------------

INSERT INTO parametro (chave, valor, descricao) VALUES
  ('dias_aviso_validade',   '3',     'Antecedência do aviso de vencimento, em dias (RN05)'),
  ('estoque_seguranca_pct', '20',    'Folga percentual somada ao ponto de pedido (RN08)'),
  ('janela_silencio_manha', '10:30-13:00', 'Primeiro pico de venda — nada é enviado (RN12)'),
  ('janela_silencio_tarde', '16:30-18:00', 'Segundo pico de venda — nada é enviado (RN12)'),
  ('historico_minimo_dias', '14',    'Mínimo de histórico para o sistema projetar (RN09)'),
  ('folga_fim_semana_pct',  '40',    'Acréscimo nos itens críticos de fim de semana (RN10)'),
  ('hora_rodada_diaria',    '03:00', 'Horário em que os cálculos rodam');

# Arquitetura (modelo C4)

*Atualizado em 13/11/2026.* Base: Apostila IV, seções 3 a 5 (`docs/ARQUITETURA.md`). Aqui, em três
níveis de zoom: o sistema no mundo, as peças que rodam e os módulos de dentro da API.

## Nível 1 — Contexto

```
   Sobrinho, Esposa ──(navegador)──▶ ┌─────────────────────────────┐ ──(HTTPS de saída)──▶ Telegram ──▶ celular
   Sr. João (consulta)               │  Sistema de Gestão de       │ ◀─(webhook "Sim, pedir")──         do Sr. João
                                     │  Estoque e Compras          │
   Caixa da loja ──(planilha .xlsx   │                             │
     numa pasta, 1× por dia)──────▶  └─────────────────────────────┘
```

- **O caixa não é chamado nem alterado** (R05): o sistema só lê a planilha que ele exporta.
- O Sr. João quase não usa tela: os avisos chegam no Telegram (RNF01).

## Nível 2 — Contêineres

| Peça | Tecnologia | Onde roda | Conversa com |
|---|---|---|---|
| Painel | HTML, CSS e JavaScript puros (`frontend/`), servido por `frontend/servir.py` | 127.0.0.1:8090 | Só com a API, por `fetch` em `/api/...` (mesma origem, L25) |
| API REST | Django 5.2 + Django REST Framework (`backend/`) | 127.0.0.1:8000 | Banco; Telegram (saída) |
| Rodada da madrugada | Comandos `manage.py` disparados pelo cron (`rodada_diaria`) | Mesmo computador, 03h00, 13h00, 18h00 | Pasta das planilhas; banco; Telegram |
| Banco de dados | PostgreSQL 17 em contêiner Docker | 127.0.0.1:5432, sem acesso externo | — |

**A regra das camadas (Apostila IV, seção 3):** apresentação (painel e Telegram) → aplicação (API)
→ processamento (importador, previsão, regras, notificação) → dados (PostgreSQL). Quem está numa
camada só conversa com a vizinha: **o painel nunca acessa o banco**, e **previsão e avisos nunca
rodam no clique** — rodam de madrugada, mesmo sem ninguém usando o sistema.

## Nível 3 — Componentes da API

| Módulo | Responsabilidade | Regras |
|---|---|---|
| `comum` | Autenticação por token, permissão por tela (RN14), formato de erro, parâmetros, rodada diária e cron | RN14 |
| `cadastro` | Categoria, fornecedor, produto, usuário; carga por planilha (J2) | RN03 |
| `estoque` | Lote, movimentação, saldo derivado (view `vw_estoque_atual`), FIFO, entrada, perda, consulta, contagem de partida (J3) | RN01, RN02, RN04, RN16 |
| `vendas` | Venda, item, importação da planilha (leitor atrás da interface `LeitorDeArquivoDoCaixa`), conciliação das pendentes | RN01, RN02 |
| `previsao` | Consumo diário, médias, previsão gravada. Lê vendas **só** por `previsao/consumo.py` | RN06–RN09, RN11 |
| `alertas` | Avisos de validade e de ruptura, estados do aviso, envio agrupado pelo Telegram (atrás de `CanalDeAviso`), webhook | RN05, RN08, RN10, RN12, RN13 |
| `caixa` | Fechamento de caixa e balanço da semana | RN15, RF13 |

**Regra de negócio não mora na view nem na tela:** mora nos módulos de serviço (`entrada.py`,
`perda.py`, `importacao.py`, `projecao.py`, `ruptura.py`…), chamados tanto pela API quanto pela rodada.

## Integrações

| Integração | Sentido | Formato | Quando | Onde no código |
|---|---|---|---|---|
| Planilha do caixa | Entrada (leitura de disco) | Excel `.xlsx`, colunas em `docs/FORMATO-PLANILHA-CAIXA.md` | 03h00 | `vendas/leitor.py`, `vendas/importacao.py` |
| Telegram — envio | Saída (HTTPS) | Bot API, JSON | 03h00, 13h00, 18h00 | `alertas/telegram.py`, `alertas/notificacao.py` |
| Telegram — resposta | Entrada (webhook HTTPS) | JSON, com segredo no cabeçalho | Quando o dono toca "Sim, pedir" | `alertas/views.py`, `alertas/respostas.py` |
| Planilhas de carga | Entrada (comando) | Excel `.xlsx` | Uma vez, na implantação | `cadastro/carga.py`, `estoque/inventario.py` |

## A rodada da madrugada

```
03h00  importar_vendas → agregar_consumo → calcular_previsao → avisos de validade → avisos de ruptura → enviar_avisos
13h00 e 18h00                                                                                       enviar_avisos (solta os segurados)
```

A ordem importa: cada passo usa o resultado do anterior. Um passo que falha não impede os outros
(`comum/rodada.py`). Os dados calculados (`consumo_diario`, `previsao_produto`, `alerta`) podem ser
apagados e recalculados a partir das tabelas de origem, que nunca se apagam.

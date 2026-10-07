# Sistema de Gestão de Estoque e Compras — Mercado do Sr. João

Trabalho de Engenharia de Software · 2º semestre de Sistemas de Informação · **Grupo MDGS**
Prazo de entrega: **27/11/2026**.

---

## A regra mais importante deste repositório

**A especificação já existe e não se inventa nada por cima dela.**

Quatro documentos foram entregues ao professor em 25/09/2026 e são a fonte da verdade:

| Documento | O que define | Arquivo aqui |
|---|---|---|
| Apostila I — Regras de Negócio | As 16 regras RN01–RN16 | `docs/REGRAS-NEGOCIO.md` |
| Apostila II — Fluxogramas e Navegação | As 10 telas e os 6 fluxos | `docs/ARQUITETURA.md` (seções finais) |
| Apostila III — Requisitos e Recursos | RF01–RF17, RNF01–RNF12, R01–R08 | `docs/ESPECIFICACAO.md` |
| Apostila IV — Arquitetura e Modelo de Dados | As camadas e as 14 tabelas | `docs/ARQUITETURA.md` · `schema.sql` |

Antes de escrever qualquer código, leia o documento correspondente.

**Se algo que você precisa não estiver escrito em nenhum deles, pare e pergunte.** Não invente
tabela, coluna, campo de tela, regra ou endpoint. Um sistema que não confere com a documentação
entregue é um trabalho reprovado, mesmo que funcione.

**Nunca mude a especificação para facilitar o código.** Se a especificação estiver errada ou
incompleta, aponte isso em texto e espere a decisão — não corrija por conta própria.

---

## O que o sistema é (e o que não é)

É um **sistema de gestão de estoque e compras**. Controla o que entra, o que sai e o que está
vencendo, e avisa o dono no celular antes do problema acontecer.

**Não é um sistema de caixa.** O caixa eletrônico da loja continua funcionando como está, emitindo
nota fiscal (restrição R05). O nosso sistema apenas **lê um arquivo** que o caixa exporta. Nunca
chame o caixa, nunca escreva nele, nunca tente substituí-lo.

### Fora de escopo — não implemente, nem "só por garantia"

- Emissão de nota fiscal
- Substituir o caixa / PDV
- Leitor de código de barras (a loja não tem)
- Vale-alimentação
- Venda fiado
- Contagem de estoque por foto
- Controle financeiro e contábil

RF16 (apoio ao inventário mensal) e RF17 (produtos vendidos juntos) são prioridade **Desejável** e
estão marcados como **não cobertos** na primeira versão. Não implemente sem autorização explícita.

---

## Stack

Decidida pelo grupo. A Apostila IV fixa o banco e a arquitetura; o resto o grupo escolheu.

| Camada | Escolha | De onde veio |
|---|---|---|
| Banco de dados | **PostgreSQL** | Apostila IV, figura 2 e seção 3 — **fixado pela especificação** |
| Linguagem | **Python 3.11+** | escolha do grupo |
| API REST | **Django 5 + Django REST Framework** | escolha do grupo |
| Migrações | Django migrations | Apostila IV, tarefa A2 pede ferramenta de migração |
| Painel web | **HTML + CSS + JavaScript puro**, arquivos estáticos | Apostila IV, figura 2 lista "Arquivos estáticos" separado do servidor da API |
| Agendador | comando `manage.py` disparado por cron/APScheduler às 03h00 | Apostila IV, comunicação nº 4 |
| Canal de aviso | **Telegram** (bot) | Apostila I RN13, Apostila IV figura 1 |
| Testes | `pytest` + `pytest-django` | Apostila IV, tarefa J1 |

### Por que Django e não Flask/FastAPI

As tarefas A2 (migração), A4 (autenticação e três perfis, 12 h) e J2 (carga inicial dos produtos)
vêm quase prontas no Django. São cerca de 25 das 378 horas que a equipe não precisa gastar. A
especificação não proíbe nenhum framework — ela só fixa PostgreSQL e a separação em camadas.

---

## A separação de camadas é obrigatória

A Apostila IV, seção 3, define quatro camadas e uma regra: **quem está numa camada só conversa com
a camada vizinha, nunca pula.**

```
1 · APRESENTAÇÃO   painel web (estático)  +  bot do Telegram
2 · APLICAÇÃO      a API REST  —  porta única de entrada
3 · PROCESSAMENTO  importador do PDV · motor de previsão · motor de regras · serviço de notificação
4 · DADOS          PostgreSQL
```

Consequências diretas no código, e nenhuma delas é negociável:

- **O painel web NUNCA acessa o banco.** Toda leitura e toda escrita passam pela API via HTTP.
  Não gere `template` Django que consulta o ORM e renderiza tabela. O frontend é estático e chama
  a API com `fetch`.
- **Previsão e avisos NUNCA rodam no clique do usuário.** São processos agendados, pesados,
  que precisam acontecer mesmo sem ninguém usando o sistema. Rodam às 03h00.
- **Regra de negócio não mora na view nem na tela.** Mora em módulos de serviço, chamados tanto
  pela API quanto pelos processos em lote.

Estrutura de pastas que respeita isso:

```
backend/
  core/            configuração Django, settings, urls
  cadastro/        categoria, produto, fornecedor, usuario      (RN03, RN14)
  estoque/         lote, movimentacao, saldo derivado           (RN01, RN02, RN04, RN16)
  vendas/          venda, item_venda, importacao_pdv            (RN01, RN02)
  previsao/        consumo_diario, previsao_produto             (RN06–RN09, RN11)
  alertas/         alerta, motor de regras, notificação         (RN05, RN08, RN10, RN12, RN13)
  caixa/           fechamento_caixa                             (RN15)
  comum/           parametros, erros, autenticação
frontend/          HTML/CSS/JS estático — consome a API
docs/              a especificação (não editar sem decisão do grupo)
schema.sql         referência do modelo de dados
```

---

## Convenções

**Idioma do código: português.** Tabelas, colunas, models, campos e endpoints usam exatamente os
nomes da Apostila IV (`produto`, `lote`, `movimentacao`, `previsao_produto`, `durabilidade_dias`).
Não traduza para inglês. Comentários e mensagens de erro também em português.

**Vocabulário do cliente nas telas e mensagens (RNF10).** A mensagem é "o frango acaba em 2 dias",
nunca "estoque abaixo do ponto de reposição". A categoria se chama "Secos e molhados". O cliente
disse na reunião: *"eu não sei o que é histórico de volante, o que você está falando"*.

**Nomes:** tabelas e colunas em `snake_case` singular, como na Apostila IV. Endpoints em plural:
`/api/produtos/`, `/api/lotes/`, `/api/movimentacoes/`.

**Dinheiro e quantidade:** `DECIMAL`, nunca `float`. Quantidade em `DECIMAL(12,3)` porque carne é
vendida em quilos fracionados.

**Datas e horas:** `TIMESTAMP WITH TIME ZONE`, fuso `America/Sao_Paulo`. As janelas de silêncio da
RN12 são em horário local da loja. **"Hoje" é sempre `timezone.localdate()`**, nunca `date.today()`
nem o `CURRENT_DATE` do banco: o Django conversa com o PostgreSQL em UTC, e depois das 21h de São
Paulo o `CURRENT_DATE` já é amanhã. Vale para `lote.data_entrada` (C2), validade no passado (RN04),
lote vencido (RN16) e aviso de validade (RN05).

**Commits:** uma tarefa do cronograma por commit, começando pelo código da tarefa.
Exemplo: `C3: regra de validade obrigatória e cálculo automático (RN04)`.

---

## Regras que o código tem de obedecer sempre

Estas quatro são as que mais aparecem e as mais fáceis de quebrar sem perceber:

**RN01 — saldo é sempre derivado.** Não existe coluna de saldo em `produto`. O saldo é
`SUM(movimentacao.quantidade)` com sinal pelo tipo. Nenhuma tela, processo ou usuário escreve saldo
diretamente. Toda operação que mexe no estoque grava uma linha em `movimentacao` explicando o
porquê.

**RN02 — FIFO na saída.** A baixa por venda sai do lote com `data_validade` mais próxima entre os
lotes disponíveis daquele produto. Nunca do mais recente, nunca do primeiro que a consulta
devolver.

**RN11 — perda não é consumo.** Movimentação `tipo = 'PERDA'` reduz o estoque mas é **excluída** da
base de cálculo de consumo e previsão. Todo `WHERE` do motor de previsão filtra `tipo = 'VENDA'`.
Se isso falhar, quanto mais produto estraga, mais o sistema manda comprar.

**RN14 — três perfis.** `DONO`, `GESTAO`, `OPERACAO`. A verificação acontece **antes** de qualquer
operação, na camada de autenticação da API, não dentro da regra de negócio. Os dois funcionários da
loja não têm acesso. **No código:** toda view declara `tela = "..."` (uma das chaves de
`ACESSO_POR_TELA` em `backend/comum/permissoes.py`); view sem `tela` é recusada para todos. Nunca
use `AllowAny` fora do login.

As 16 regras completas, com condição testável e mensagem de erro, estão em
`docs/REGRAS-NEGOCIO.md`. Leia a regra antes de implementar o trecho que ela governa.

---

## Testes

Cada regra de negócio precisa de teste automatizado (tarefa J1 do cronograma, 16 h).

Cada losango de decisão dos fluxogramas da Apostila II vira **no mínimo dois testes**: um pelo
caminho "sim" e um pelo "não". O fluxograma 02 (entrada de mercadoria), sozinho, define seis
situações a testar.

Nomeie o teste pelo código da regra: `test_rn03_perecivel_sem_durabilidade_e_recusado`.

---

## Skills do projeto — quando usar

As skills ficam em `.claude/skills/` (origem e versão em `skills-lock.json`). Carregue a skill
indicada **antes** de começar a tarefa correspondente, sem esperar pedido.

**A especificação tem prioridade sobre qualquer skill.** Skill é fonte de boas práticas, não de
decisão: os exemplos delas foram escritos para outros projetos. Quando um exemplo contrariar este
arquivo, os `docs/` ou o `schema.sql`, adapte o exemplo — nunca o projeto. Nenhuma skill autoriza
trocar banco de testes, ferramenta, dependência, arquitetura, modelo de usuário, `Decimal` ou
`schema.sql`. Dependência nova só com decisão do grupo.

### Por tipo de tarefa

| Tarefa | Skills | Para quê |
|---|---|---|
| **Toda tarefa com código** | `superpowers:test-driven-development` + `django-tdd` + `python-testing-patterns` | Teste antes do código; testes de API do DRF, mocks de serviço externo, padrão AAA |
| **Tabelas e migrações** — B1, C1, C4, E2, F1, G1, G3, H1, I1 | `django-expert` (`references/models-and-orm.md`) · `postgresql-table-design` · `postgres-patterns` · `supabase-postgres-best-practices` | Model fiel ao `schema.sql`; conferir constraints, índices e tipos. As três de PostgreSQL servem para **revisar**, não para redesenhar |
| **API** — B2, B3, C2, D1, E3, E4, F2, H7, I1, I3 | `django-expert` (`references/drf-guidelines.md`) · `django-patterns` (Service Layer, ViewSet, N+1) | Serializer, viewset, regra no módulo de serviço com `transaction.atomic` |
| **Autenticação e perfis** — A4, H6 | `django-security` (Authorization, Password Hashing, API Security) · `django-expert` (`references/security-checklist.md`) | Verificação do papel (RN14) antes de qualquer operação, hash de senha, segurança da API |
| **Consultas pesadas** — F2, G1, G2, H2, H3 | `django-expert` (`references/performance-optimization.md`) · `postgres-patterns` | `select_related`, agregação no banco, índice certo, `EXPLAIN` |
| **Telegram** — H5, H6, H7 | `telegram-bot-builder` · `telegram-bot` | Conceitos de bot, webhook, botões de resposta ("Sim, pedir"), notificação agrupada |
| **Telas** — B5, B6, B7, C5, D3, E5, F3, I2 e login | **`ui-ux-pro-max` sempre** · `accessibility` | Desenho de toda tela passa pela UI UX Pro Max; depois, auditoria WCAG 2.2 |
| **Revisão ao fim de cada tarefa** | `django-reviewer` (só relata) · `/code-review` | Revisar o diff antes do commit |
| **Antes de publicar** — A5, J4, J6 | `django-verification` · `django-security` (Production Settings, checklist) · `django-expert` (`references/production-deployment.md`) | Verificação completa antes de subir um ambiente |

### Adaptações obrigatórias

| A skill sugere | Neste projeto |
|---|---|
| SQLite nos testes (`django-tdd`, `python-testing-patterns`, `django-verification`) | **PostgreSQL sempre**, inclusive nos testes |
| `factory_boy` | Fixtures do pytest e funções auxiliares em `conftest.py`, com nomes em português |
| Celery, Redis, cache | Comando `manage.py` disparado às 03h00 (Apostila IV). Sem cache: o sistema é pequeno |
| `AbstractUser`, login por e-mail, JWT/simplejwt, sessão | Decisão da **L09**: `AbstractBaseUser` sobre a tabela `usuario`, `login` como identificador, `senha_hash`, sem `last_login`, token assinado sem tabela |
| RBAC com `is_admin()`/grupos/`is_superuser` | O `papel` (`DONO`, `GESTAO`, `OPERACAO`) checado numa permission do DRF, conforme a tabela da RN14 |
| Templates, `render()`, `TemplateView`, fragment caching | Painel estático em HTML/CSS/JS puro chamando a API com `fetch` |
| `FloatField`, `DOUBLE PRECISION` | `DecimalField` / `NUMERIC`, como no `schema.sql` |
| `BIGINT IDENTITY`, `TEXT`, `UUID` como chave | `SERIAL` e `VARCHAR(n)` **exatamente** como no `schema.sql` |
| RLS, Supabase | Não se aplica. Acesso controlado pela API (RN14); banco sem acesso externo |
| `config/settings/` dividido, `django-environ` | `backend/core/settings.py` lendo o `.env` com `python-dotenv` |
| `black`, `isort`, `mypy` | `ruff check` e `ruff format` |
| `django-filter`, `corsheaders`, `whitenoise`, `sentry`, `gunicorn`, `pip-audit`, `bandit` | Só com decisão do grupo. Até lá, filtros escritos à mão na view |
| `signals` para efeitos colaterais | Chamada explícita no serviço (ex.: operação 02, passo 10, cancela o aviso de ruptura) |
| Soft delete, `DELETE` de registros | `movimentacao` e `fechamento_caixa` nunca são apagadas (RN01, RN15) |
| n8n, Telegraf, grammY, aiogram | Python, atrás da interface `CanalDeAviso.enviar(destinatario, mensagem)` (D04) |
| `freezegun` para fixar o relógio | `unittest.mock.patch` em `django.utils.timezone.now`, sem dependência nova |
| Tailwind, shadcn, React nas sugestões da UI UX Pro Max | HTML, CSS e JS puros e leves — computador antigo (RNF06, R04) |
| Nomes em inglês nos exemplos (`Order`, `User`, `price`) | Nomes em português, exatamente os da Apostila IV |

---

## O que ainda não foi decidido

Oito decisões dependem do cliente e estão em `docs/DECISOES-PENDENTES.md`. Duas são **bloqueantes**:

- **D01** — o caixa da loja exporta as vendas em arquivo? Em que formato?
  Trava os blocos E, G e H — 136 das 378 horas.
- **D02** — como o sistema fica sabendo da validade?

**166 horas não dependem de nenhuma decisão** (blocos A, B, C, D e F). É por aí que o trabalho
começa. Não tente adivinhar o formato do arquivo do caixa: implemente a leitura atrás de uma
interface e deixe o parser real para quando a resposta chegar.

---

## Ao começar uma tarefa

1. Localize a tarefa em `docs/ROTEIRO.md` (códigos A1 a J6).
2. Confirme que as dependências dela já estão prontas.
3. Leia as regras de negócio que ela cita.
4. Implemente.
5. Escreva o teste.
6. Marque a tarefa no roteiro.
7. Atualize `docs/ACOMPANHAMENTO.md` — é o andamento do cronograma que foi entregue ao professor:
   risque a tarefa (`~~A3~~`), preencha situação, data de conclusão e commit, recalcule o resumo
   (tarefas, horas e % por etapa) e escreva no **Diário** o que foi feito no dia, em linguagem
   que o professor entenda. Decisões tomadas e lacunas novas também entram no diário.
8. Ao responder, diga sempre o que foi feito, em que data, e qual é a próxima tarefa.

Não pule para uma tarefa adiante porque parece mais fácil. A ordem existe por dependência real:
o modelo de dados sustenta quase tudo e por isso vem primeiro.

# Sistema de Gestão de Estoque e Compras — Mercado do Sr. João

Trabalho de Engenharia de Software · Sistemas de Informação · **Grupo MDGS** · entrega 01/12/2026.

Controla o que entra, o que sai e o que está vencendo no estoque, e avisa o dono no celular
(Telegram) antes do problema acontecer. **Não é sistema de caixa**: só lê o arquivo que o caixa
exporta.

| Leia antes de programar | |
|---|---|
| `CLAUDE.md` | Regras do repositório, stack e convenções |
| `docs/ROTEIRO.md` | As tarefas A1–J6, na ordem — marque `[x]` ao terminar |
| `docs/ACOMPANHAMENTO.md` | **Andamento do cronograma**: o que já foi feito, quando, e o diário |
| `docs/REGRAS-NEGOCIO.md` | RN01–RN16 em forma testável |
| `docs/ESPECIFICACAO.md` | RF, RNF, restrições e fora de escopo |
| `docs/ARQUITETURA.md` | Camadas, operações, as 10 telas |
| `schema.sql` | As 14 tabelas — nenhuma coluna a mais |
| `docs/LACUNAS.md` | Lacunas da especificação e como o grupo decidiu cada uma |

---

## Estrutura

```
backend/
  core/        configuração Django (settings, urls)
  comum/       parâmetros, erros, autenticação        (RN14)
  cadastro/    categoria, produto, fornecedor, usuário (RN03, RN14)
  estoque/     lote, movimentação, saldo derivado     (RN01, RN02, RN04, RN16)
  vendas/      venda, item de venda, importação PDV   (RN01, RN02)
  previsao/    consumo diário, previsão               (RN06–RN09, RN11)
  alertas/     aviso, motor de regras, notificação    (RN05, RN08, RN10, RN12, RN13)
  caixa/       fechamento de caixa                    (RN15)
  tests/       testes (pytest)
frontend/      HTML + CSS + JS puro — só conversa com a API
docs/          especificação (não editar sem decisão do grupo)
schema.sql     modelo de dados de referência
```

---

## Subir o ambiente

> **Primeira vez, no Windows, sozinho?** Siga o [COMO-RODAR.md](COMO-RODAR.md): passo a passo
> do zero até as telas abertas com os dados da apresentação.

Pré-requisitos: **Python 3.11 ou mais novo**, **Git** e **Docker** (Docker Desktop no Windows e no
macOS). O Docker só serve para rodar o PostgreSQL na máquina de desenvolvimento.

### Linux e macOS

```bash
git clone https://github.com/MatheusLoureiro7/mercadinho.git mercadinho
cd mercadinho

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
playwright install chromium   # uma vez: navegador dos testes de tela

cp .env.example .env          # edite: DJANGO_SECRET_KEY e POSTGRES_PASSWORD
docker compose up -d --wait   # sobe o PostgreSQL
python backend/manage.py migrate
pytest
```

### Windows (PowerShell)

```powershell
git clone https://github.com/MatheusLoureiro7/mercadinho.git mercadinho
cd mercadinho

py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
playwright install chromium   # uma vez: navegador dos testes de tela

Copy-Item .env.example .env   # edite: DJANGO_SECRET_KEY e POSTGRES_PASSWORD
docker compose up -d --wait   # sobe o PostgreSQL
python backend\manage.py migrate
pytest
```

Se o PowerShell recusar o `Activate.ps1`, rode uma vez:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

No **Prompt de Comando (cmd)**, a ativação é `.venv\Scripts\activate.bat` e a cópia é
`copy .env.example .env`.

### O banco de dados

PostgreSQL 17 em contêiner, definido em `docker-compose.yml`. A porta só aceita conexão da própria
máquina (`127.0.0.1`) — o banco não tem acesso externo (RNF12).

| Comando | O que faz |
|---|---|
| `docker compose up -d --wait` | Sobe o banco e espera ele ficar pronto |
| `docker compose down` | Para o banco (os dados ficam guardados) |
| `docker compose down -v` | Para o banco **e apaga todos os dados** |
| `docker compose exec banco psql -U mercadinho` | Abre o terminal SQL do banco |
| `python backend/manage.py migrate` | Aplica as migrações pendentes |
| `python backend/manage.py makemigrations` | Gera a migração depois de mudar um model |

Os testes criam e apagam um banco próprio (`test_mercadinho`); o banco de desenvolvimento não é
tocado. Se preferir PostgreSQL instalado direto na máquina, sem Docker, basta apontar as
variáveis `POSTGRES_*` do `.env` para ele.

### O arquivo `.env`

| Variável | Para quê |
|---|---|
| `DJANGO_SECRET_KEY` | Obrigatória quando `DJANGO_DEBUG=false` |
| `DJANGO_DEBUG` | `true` só na máquina de desenvolvimento; o `publicar.py` sempre sobe a API com `false` |
| `POSTGRES_*` | Conexão com o banco — o `docker compose` usa as mesmas variáveis para criar o banco |
| `TELEGRAM_BOT_TOKEN` | Bot de avisos (H5). Vazio: os avisos ficam guardados e não saem |
| `TELEGRAM_WEBHOOK_SEGREDO` | Segredo do webhook que recebe a resposta do dono (H7). Vazio: nada é aceito |

O `.env` nunca vai para o git (RNF12).

---

## O painel

O painel (`frontend/`) e a API ficam no **mesmo endereço**: o painel chama sempre `/api/...`, sem
CORS (decisão L25). Na máquina do grupo, com a API rodando em outro terminal:

```bash
python backend/manage.py runserver      # terminal 1 — a API, em 127.0.0.1:8000
python frontend/servir.py               # terminal 2 — o painel, em http://127.0.0.1:8090/
```

O `servir.py` entrega os arquivos do painel e repassa o que começa com `/api/` para a API. Usa só
a biblioteca padrão do Python e aceita conexão só da própria máquina. Na publicação (D05), o
servidor web faz o mesmo papel. Para entrar, crie os usuários (abaixo).

---

## Publicar no computador da loja (A5)

O sistema roda no computador do Matheus (decisão D05). Com o `.venv` ativado, um comando faz a
esteira inteira:

```bash
python publicar.py                  # atualiza, confere, testa e, se tudo passar, publica
python publicar.py --sem-atualizar  # publica o que está na pasta, sem git pull
python publicar.py --parar          # para a API e o painel publicados
```

A ordem protege o que está no ar: `git pull`, dependências, banco, `ruff` e **todos os testes**
vêm antes; só se tudo passar o script aplica as migrações e troca a API (`127.0.0.1:8000`) e o
painel (`127.0.0.1:8090`), conferindo que os dois respondem. Se um passo falhar, nada muda no
sistema publicado. Cada publicação fica em `logs/publicacoes.log`; a saída dos servidores, em
`logs/api.log` e `logs/painel.log`. Usa o servidor do próprio Django, sem dependência nova
(decisão do grupo, 13/11/2026): basta para a demonstração; um servidor de produção ficaria para
outra decisão.

---

## Rodada diária (03h00)

A previsão e os avisos não rodam no clique de ninguém: rodam de madrugada (Apostila IV,
comunicação nº 4). Um comando faz a rodada inteira, na ordem da apostila — importa as planilhas
novas do caixa, soma o consumo de cada dia, calcula a previsão, gera os avisos de validade e
envia pelo Telegram:

```bash
python backend/manage.py rodada_diaria
```

Se um passo falha (por exemplo, a pasta das planilhas não existe), os outros acontecem mesmo
assim; o comando termina com erro dizendo qual falhou, e o motivo fica no log.

**Quem dispara é o cron do computador da loja** (decisão do grupo, 12/11/2026 — sem dependência
nova). Os horários vêm da tabela de parâmetros: a rodada às 03h00 e o envio de novo no fim de cada
horário de movimento (13h00 e 18h00), para soltar os avisos segurados (RN12). Para instalar:

```bash
python backend/manage.py agenda_cron    # mostra as linhas, com os caminhos deste computador
crontab -e                              # cole as linhas no fim do arquivo e salve
```

O computador precisa estar **ligado às 03h00** e no **horário de São Paulo**. A saída de cada
rodada vai para `logs/rodada.log`. Mudou um horário na tabela de parâmetros? Gere as linhas de
novo e troque no crontab. No macOS, se o cron não conseguir ler a pasta do projeto, dê a ele
acesso em *Ajustes do Sistema → Privacidade e Segurança → Acesso Total ao Disco* (`/usr/sbin/cron`).

---

## Avisos no Telegram

O Sr. João não usa o painel: os avisos chegam no celular dele (operação 03). Quem envia é o
comando abaixo, que o cron chama (G5, seção anterior) — às 03h00, dentro da rodada diária, e de
novo depois de cada horário de movimento, para soltar os avisos segurados (RN12):

```bash
python backend/manage.py enviar_avisos
```

Ele junta os avisos de cada pessoa numa mensagem só, do mais urgente para o menos (RN13). Se a
mensagem de alguém não sair (sem internet, bot sem token, celular ainda não ligado — H6), os
avisos ficam guardados para a próxima rodada e o comando termina com erro, com o motivo no log.

**Criar o bot (uma vez):** no Telegram, abra o **@BotFather**, mande `/newbot`, escolha o nome e
o usuário (termina em `bot`) e cole o token que ele devolve em `TELEGRAM_BOT_TOKEN` no `.env`.
O token é segredo: nunca no git, nunca no log (RNF12).

**Ligar o celular do Sr. João (uma vez, ou ao trocar de celular — H6):**

```bash
python backend/manage.py vincular_telegram --login joao
```

O comando mostra um código de 6 dígitos (vale 5 minutos) e um link `t.me/...`. No celular dele,
abra o link e toque em **Iniciar** — ou mande `/start <código>` ao bot. O sistema grava o chat e
manda "Pronto, Sr. João! Os avisos do mercado vão chegar aqui". Só o usuário `DONO` recebe aviso.

**A resposta dele (H7):** cada aviso de "vai acabar" chega com o botão **"Sim, pedir: <produto>"**.
O toque vai para `POST /api/telegram/` (webhook), que grava `alerta.resposta_usuario`. Esse endereço
não usa login: só aceita quem traz o segredo `TELEGRAM_WEBHOOK_SEGREDO` (o Telegram o manda em todo
chamado), e só grava resposta vinda do chat do DONO que recebeu o aviso. Para ligar — só com o
sistema publicado em `https://` (decisão D05):

```bash
python backend/manage.py configurar_webhook --url https://<endereço do sistema>/api/telegram/
python backend/manage.py configurar_webhook --remover      # para vincular outro celular (H6)
```

---

## A API

Tudo fica sob `/api/`, sempre em JSON. Rodar localmente:

```bash
python backend/manage.py runserver      # http://127.0.0.1:8000/api/
```

### Usuários e login

Só três pessoas usam o sistema (RN14). Os usuários são criados pela equipe, no terminal — a senha
é pedida duas vezes e nunca aparece na tela:

```bash
python backend/manage.py criar_usuario --login joao     --nome "Sr. João" --papel DONO
python backend/manage.py criar_usuario --login esposa   --nome "Esposa"   --papel GESTAO
python backend/manage.py criar_usuario --login sobrinho --nome "Sobrinho" --papel OPERACAO
python backend/manage.py changepassword sobrinho      # trocar a senha depois
```

### Carga inicial dos produtos e contagem de partida (J2, J3)

Categorias, fornecedores e produtos entram de uma vez por uma planilha do Excel, com as mesmas
conferências da tela de Produtos. Se uma linha estiver errada, nada é gravado e o comando diz a
aba, a linha e a coluna. Formato em `docs/FORMATO-PLANILHA-PRODUTOS.md`:

```bash
python backend/manage.py carregar_produtos docs/exemplos/produtos-iniciais.xlsx
```

Depois, a **contagem de partida (J3)**: o saldo inicial de cada produto entra como entrada de
mercadoria (um lote por linha, com validade), uma vez só. Formato em
`docs/FORMATO-PLANILHA-CONTAGEM.md`:

```bash
python backend/manage.py carregar_contagem docs/exemplos/contagem-de-partida.xlsx
```

### Sessão

O painel entra com `POST /api/sessoes/` (`{"login", "senha"}`) e recebe um `token`, que manda em
toda requisição no cabeçalho `Authorization: Bearer <token>`. O token vale `SESSAO_VALIDADE_HORAS`
(12 h) e cai antes disso se a senha for trocada ou o usuário desativado. `GET /api/sessoes/atual/`
devolve quem está usando e as `telas` do menu daquele papel.

**Todo endpoint declara a sua tela** — é assim que a RN14 é verificada antes de qualquer operação:

```python
class ProdutoViewSet(ModelViewSet):
    tela = "produtos"  # só OPERACAO entra (comum/permissoes.py, ACESSO_POR_TELA)
```

Endpoint sem `tela` é recusado para todos.

### Endereços da API

| Endereço | Métodos | Quem (RN14) | Tarefa |
|---|---|---|---|
| `/api/sessoes/` | POST | qualquer um (é o login) | A4 |
| `/api/sessoes/atual/` | GET | os três perfis | A4 |
| `/api/categorias/` · `/api/categorias/{id}/` | GET | os três perfis (Consulta de estoque) | B2 |
| | POST, PUT, PATCH | OPERACAO (tela de Produtos) | B2 |
| `/api/fornecedores/` · `/api/fornecedores/{id}/` | GET, POST, PUT, PATCH | OPERACAO | B2 |
| `/api/produtos/` · `/api/produtos/{id}/` | GET, POST, PUT, PATCH | OPERACAO | B3 |
| `/api/lotes/` · `/api/lotes/{id}/` | GET, POST (sem editar) | OPERACAO (Entrada de mercadoria) | C2 |
| `/api/perdas/` · `/api/perdas/{id}/` | GET, POST (sem editar) | OPERACAO (Avarias e quebras) | D1 |
| `/api/estoque/` | GET | os três perfis (Consulta de estoque) | F2 |
| `/api/estoque/lotes/` | GET | os três perfis (Consulta de estoque) | F2 |
| `/api/telegram/` | POST | o Telegram (segredo do webhook, sem login) — resposta do DONO | H7 |

`POST /api/lotes/` registra a carga que chegou: grava o lote e a movimentação de ENTRADA numa
transação só (operação 02) e devolve o `saldo_produto` novo. A data de entrada é sempre hoje, no
horário da loja. Lista do dia: `GET /api/lotes/?data_entrada=AAAA-MM-DD` (também `?produto=<id>`).

`POST /api/perdas/` registra o que venceu, quebrou ou estragou: `{"produto", "quantidade",
"motivo", "lote"?}`. Motivo obrigatório. Sem lote, sai pela ordem de validade (L20). Caderno de
avarias: `GET /api/perdas/?data=AAAA-MM-DD` (também `?produto=<id>`).

Consulta de estoque (só leitura): `GET /api/estoque/` por produto — `?categoria=<id>`,
`?busca=`, `?abaixo_do_minimo=1`, `?validade_proxima=1`; `GET /api/estoque/lotes/` por lote —
`?categoria=`, `?produto=`, `?busca=`, `?situacao=VENCIDO,VENCENDO` (também `OK`, `SEM_VALIDADE`).
"Vencendo" usa o parâmetro `dias_aviso_validade` (3 dias).

Filtros de `/api/produtos/`: `?busca=<parte do nome>` e `?categoria=<id>`. Unidades aceitas:
`KG`, `UN`, `L`, `PCT` (L17).

Nada de origem é apagado (Apostila IV, seção 5): `DELETE` responde 405.

**Formato de erro** — igual em toda a API, para o painel só precisar mostrar `mensagem`:

```json
{"erro": {"codigo": "validacao",
          "mensagem": "Confira os campos destacados.",
          "campos": {"durabilidade_dias": ["Este campo é obrigatório."]}}}
```

| `codigo` | HTTP | Quando |
|---|---|---|
| `validacao` | 400 | Campo faltando ou inválido — `campos` diz quais (fluxograma 01: a tela mantém o resto) |
| `regra_de_negocio` | 400 | Uma regra recusou — vem também `regra` (ex.: `"RN03"`) |
| `requisicao_invalida` | 400 | O corpo não é um JSON válido |
| `nao_autenticado` | 401 | Precisa entrar no sistema (tarefa A4) |
| `sem_permissao` | 403 | O papel não permite (RN14, tarefa A4) |
| `muitas_tentativas` | 429 | Mais de 10 tentativas de login por minuto do mesmo endereço |
| `nao_encontrado` | 404 | Endereço ou registro inexistente |
| `metodo_nao_permitido` | 405 | Operação que não existe naquele endereço |
| `erro_interno` | 500 | Falha inesperada — vem `id`, o mesmo código gravado no log |

Nos serviços, regra de negócio recusa a operação com
`raise ErroDeRegraDeNegocio("RN03", "mensagem para a tela", campo="durabilidade_dias")`
(`backend/comum/erros.py`). A view não testa regra.

**Log:** uma linha por requisição (método, endereço, situação, tempo, usuário) no console e em
`logs/mercadinho.log`. Erro inesperado grava o detalhe técnico com o mesmo `id` mostrado na tela.
O corpo da requisição nunca vai para o log (RNF12).

---

## Padrão de código

- **Idioma:** português — tabelas, colunas, models e endpoints com os nomes exatos do `schema.sql`.
- **Formatação e lint:** [Ruff](https://docs.astral.sh/ruff/), configurado em `pyproject.toml`.

  ```bash
  ruff check .
  ruff format .
  ```

- **Dinheiro e quantidade:** `Decimal`, nunca `float`.
- **Testes:** nome pela regra — `test_rn03_perecivel_sem_durabilidade_e_recusado`.
- **Commits:** uma tarefa por commit, começando pelo código —
  `C3: regra de validade obrigatória e cálculo automático (RN04)`.

Antes de cada commit: `ruff check . && ruff format --check . && pytest`.

### Testes de tela

Os testes marcados `@pytest.mark.tela` abrem o painel num navegador de verdade (Chromium, pelo
`pytest-playwright`) e percorrem o fluxo inteiro: tela → `servir.py` → API → banco de teste. Cada
um confere o que aparece na tela **e** o que ficou gravado. Rodam junto com o `pytest`, sempre por
último. Para rodar só os rápidos: `pytest -m "not tela"`. Para ver o navegador trabalhando:
`pytest -m tela --headed --slowmo 300`.

As fixtures ficam em `backend/tests/conftest.py`: `painel` (sobe a API e o painel), `abrir_tela`
(abre uma tela já com sessão) e `entrar_pelo_login`. Exemplos: `backend/tests/test_c6_fluxo_entrada.py` e `test_d4_fluxo_perdas.py`.

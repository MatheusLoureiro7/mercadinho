# Sistema de Gestão de Estoque e Compras — Mercado do Sr. João

Trabalho de Engenharia de Software · Sistemas de Informação · **Grupo MDGS** · entrega 27/11/2026.

Controla o que entra, o que sai e o que está vencendo no estoque, e avisa o dono no celular
(Telegram) antes do problema acontecer. **Não é sistema de caixa**: só lê o arquivo que o caixa
exporta.

| Leia antes de programar | |
|---|---|
| `CLAUDE.md` | Regras do repositório, stack e convenções |
| `docs/ROTEIRO.md` | As tarefas A1–J6, na ordem — marque `[x]` ao terminar |
| `docs/REGRAS-NEGOCIO.md` | RN01–RN16 em forma testável |
| `docs/ESPECIFICACAO.md` | RF, RNF, restrições e fora de escopo |
| `docs/ARQUITETURA.md` | Camadas, operações, as 10 telas |
| `schema.sql` | As 14 tabelas — nenhuma coluna a mais |
| `docs/DECISOES-PENDENTES.md` · `docs/LACUNAS.md` | O que ainda não foi decidido |
| `openspec/` | Especificação no formato OpenSpec (specs por capacidade e propostas de mudança) |

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
openspec/      especificação OpenSpec
schema.sql     modelo de dados de referência
```

---

## Subir o ambiente

Pré-requisitos: **Python 3.11 ou mais novo** e **Git**. O PostgreSQL entra na tarefa A2 — até lá,
os comandos abaixo funcionam sem banco.

### Linux e macOS

```bash
git clone <url-do-repositorio> mercadinho
cd mercadinho

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env          # depois edite o .env
python backend/manage.py check
pytest
```

### Windows (PowerShell)

```powershell
git clone <url-do-repositorio> mercadinho
cd mercadinho

py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

Copy-Item .env.example .env   # depois edite o .env
python backend\manage.py check
pytest
```

Se o PowerShell recusar o `Activate.ps1`, rode uma vez:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

No **Prompt de Comando (cmd)**, a ativação é `.venv\Scripts\activate.bat` e a cópia é
`copy .env.example .env`.

### O arquivo `.env`

| Variável | Para quê |
|---|---|
| `DJANGO_SECRET_KEY` | Obrigatória quando `DJANGO_DEBUG=false` |
| `DJANGO_DEBUG` | `true` só na máquina de desenvolvimento |
| `POSTGRES_*` | Conexão com o banco (tarefa A2) |
| `TELEGRAM_BOT_TOKEN` | Bot de avisos (tarefa H5) — pode ficar vazio até lá |

O `.env` nunca vai para o git (RNF12).

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

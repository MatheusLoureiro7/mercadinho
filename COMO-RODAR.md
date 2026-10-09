# Como rodar o projeto no seu computador (Windows)

Passo a passo para quem vai abrir o sistema pela primeira vez, sem ajuda. Leva uns 30 minutos,
quase tudo esperando instalação. No fim você terá as telas abertas no navegador **com os mesmos
produtos, lotes e movimentações que o grupo usa na apresentação**.

Todos os comandos são digitados no **PowerShell** (menu Iniciar → digite "PowerShell").

---

## 1. Instalar os programas (só na primeira vez)

| Programa | Onde baixar | Atenção |
|---|---|---|
| **Python 3.11 ou mais novo** | https://www.python.org/downloads/ | Na primeira tela do instalador, marque **"Add python.exe to PATH"** |
| **Git** | https://git-scm.com/download/win | Pode aceitar tudo como vem |
| **Docker Desktop** | https://www.docker.com/products/docker-desktop/ | Pede para reiniciar o computador. Depois, abra o Docker Desktop e espere aparecer "Engine running" |

Feche e abra o PowerShell de novo depois de instalar, e confira:

```powershell
py --version        # Python 3.11 ou mais novo
git --version
docker --version
```

> **O Docker não abre?** Ele precisa da virtualização ligada no computador. Se não der certo, veja
> "Sem Docker" no fim deste arquivo.

## 2. Baixar o projeto

O repositório é privado: aceite antes o convite que chegou no seu e-mail do GitHub.

```powershell
cd $HOME\Documents
git clone https://github.com/MatheusLoureiro7/mercadinho.git
cd mercadinho
```

Na primeira vez o Git abre uma janela para entrar na sua conta do GitHub.

## 3. Preparar o Python

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

Se o PowerShell disser que a execução de scripts está desabilitada, rode uma vez
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, responda `S` e repita a segunda linha.

Deu certo quando o começo da linha do PowerShell mostra `(.venv)`. **Toda vez** que abrir um
PowerShell novo para o projeto, entre na pasta e rode `.\.venv\Scripts\Activate.ps1` de novo.

## 4. Criar o arquivo de configuração

```powershell
Copy-Item .env.example .env
notepad .env
```

No Bloco de Notas, troque só estas duas linhas (invente qualquer texto) e salve:

```
DJANGO_SECRET_KEY=qualquer-texto-comprido-aqui-1234567890
POSTGRES_PASSWORD=uma-senha-qualquer
```

## 5. Subir o banco e carregar os dados da apresentação

Com o Docker Desktop aberto:

```powershell
docker compose up -d --wait
python backend\manage.py migrate
python backend\manage.py loaddata demonstracao
```

O último comando deve responder `Installed 48 object(s)`. Ele cria as categorias, os fornecedores,
os 10 produtos, os lotes e as movimentações, e os três usuários do sistema.

## 6. Escolher as senhas dos três usuários

O arquivo de dados **não traz senha nenhuma** (senha não vai para o GitHub). Defina a sua, uma
para cada usuário (o comando pede duas vezes e não mostra o que você digita):

```powershell
python backend\manage.py changepassword joao       # Sr. João — DONO
python backend\manage.py changepassword esposa     # Esposa — GESTAO
python backend\manage.py changepassword sobrinho   # Sobrinho — OPERACAO
```

## 7. Ligar o sistema

São **dois PowerShell abertos ao mesmo tempo**, os dois na pasta do projeto e com o
`.\.venv\Scripts\Activate.ps1` rodado.

```powershell
# PowerShell 1 — a API
python backend\manage.py runserver
```

```powershell
# PowerShell 2 — o painel
python frontend\servir.py
```

Abra no navegador: **http://127.0.0.1:8090/**

Cada perfil vê telas diferentes (RN14):

| Entrar como | Vê |
|---|---|
| `sobrinho` | Produtos, Fornecedores, Entrada de mercadoria, Avarias e quebras, Consulta de estoque |
| `esposa` | Consulta de estoque (e Fechamento de caixa e Balanço da semana, quando ficarem prontas) |
| `joao` | Consulta de estoque — os avisos dele chegam pelo Telegram |

Para desligar: `Ctrl+C` em cada PowerShell. O banco continua guardado no Docker.

---

## Ver as tabelas do banco (para a apresentação)

**Pelo terminal**, sem instalar nada:

```powershell
docker compose exec banco psql -U mercadinho
```

Dentro dele:

| Digite | Mostra |
|---|---|
| `\dt` | As tabelas |
| `\d produto` | As colunas da tabela `produto` |
| `SELECT * FROM produto;` | Os produtos cadastrados |
| `SELECT * FROM vw_estoque_atual;` | O saldo de cada produto (somado das movimentações, RN01) |
| `SELECT * FROM movimentacao ORDER BY id;` | Toda entrada e perda, com o motivo |
| `\q` | Sair |

**Com janela e tabelas visíveis**: instale o **pgAdmin 4** (https://www.pgadmin.org/download/) ou
o **DBeaver Community** (https://dbeaver.io/download/) e crie uma conexão PostgreSQL com:

| Campo | Valor |
|---|---|
| Host | `localhost` |
| Porta | `5432` |
| Banco (database) | `mercadinho` |
| Usuário | `mercadinho` |
| Senha | a `POSTGRES_PASSWORD` que você pôs no `.env` |

As tabelas ficam em *mercadinho → Schemas → public → Tables*.

---

## Deu errado?

| Mensagem | O que fazer |
|---|---|
| `py` não é reconhecido | Reinstale o Python marcando "Add python.exe to PATH" |
| `docker` … `cannot connect` / `pipe` | Abra o Docker Desktop e espere "Engine running" |
| `port is already allocated` (5432) | Já existe um PostgreSQL instalado no computador. No `.env`, mude `POSTGRES_PORT=5433` e rode `docker compose up -d --wait` de novo |
| `password authentication failed` | A senha do `.env` mudou depois de criar o banco. Rode `docker compose down -v` (apaga o banco) e refaça o passo 5 |
| `loaddata` … `duplicate key` | Os dados já foram carregados antes. Para recomeçar do zero: `docker compose down -v` e refaça os passos 5 e 6 |
| A tela diz "O sistema não está respondendo" | O PowerShell 1 (a API) está desligado ou com erro — olhe o que ele mostra |
| Login recusado | Refaça o passo 6 para aquele usuário |

## Sem Docker

Instale o PostgreSQL direto no Windows (https://www.postgresql.org/download/windows/ — o
instalador já traz o pgAdmin). No pgAdmin, crie o usuário `mercadinho` com uma senha e o banco
`mercadinho` com esse dono. No `.env`, coloque essa senha em `POSTGRES_PASSWORD`. Depois siga do
passo 5 pulando o `docker compose`, e troque o acesso pelo terminal por `psql -U mercadinho`.

## Sobre os dados de demonstração

São uma cópia do banco de desenvolvimento do grupo em 08/10/2026, em
`backend/comum/fixtures/demonstracao.json`. **Não são** a carga real dos produtos da loja (tarefa
J2, feita com o cliente). As validades são datas fixas: com o passar dos dias, mais lotes aparecem
como vencidos na Consulta de estoque — é a RN16 funcionando, não erro.

# Como rodar o projeto no seu computador (Windows)

Passo a passo para quem vai abrir o sistema **pela primeira vez, sozinho**. Leva uns 30 a 40
minutos, quase tudo esperando download e instalação. No fim você terá as telas abertas no navegador
**com os mesmos produtos, lotes e movimentações que o grupo usa na apresentação**.

**Como ler:** faça os passos 1 a 8 **uma vez só**. Depois, sempre que for usar o sistema de novo,
siga só a seção **"Toda vez que for usar"**.

Todos os comandos são digitados no **PowerShell**: menu Iniciar → digite `PowerShell` → Enter.
Copie e cole um bloco de cada vez (no PowerShell, colar é o **botão direito do mouse**).

---

## 1. Instalar os programas

Instale os três, nesta ordem. Só precisa fazer isso uma vez no computador.

| Programa | Onde baixar | Atenção na instalação |
|---|---|---|
| **Python 3.12, 3.13 ou 3.14** | https://www.python.org/downloads/windows/ | Na **primeira tela** do instalador, marque **"Add python.exe to PATH"** antes de clicar em *Install Now*. O grupo usa a 3.14. |
| **Git** | https://git-scm.com/download/win | Pode clicar em *Next* em tudo, como vem. |
| **Docker Desktop** | https://www.docker.com/products/docker-desktop/ | Se pedir para instalar ou atualizar o **WSL 2**, aceite. No fim pede para **reiniciar** o computador. Depois de reiniciar, abra o Docker Desktop, aceite os termos (pode pular o cadastro) e espere aparecer **"Engine running"** embaixo, à esquerda. |

Depois de instalar tudo, **feche e abra o PowerShell de novo** e confira:

```powershell
py --version
git --version
docker --version
```

Os três têm de responder com um número de versão. Se algum disser "não é reconhecido", veja
**"Deu errado?"** no fim.

> **O Docker não liga?** Ele precisa da virtualização ligada no computador (no Windows Home, vem
> pelo WSL 2). Se mesmo assim não der, veja **"Sem Docker"** no fim deste arquivo.

## 2. Aceitar o convite e baixar o projeto

O repositório é **privado**. Antes, abra o e-mail da sua conta do GitHub e **aceite o convite**
para `MatheusLoureiro7/mercadinho` (ou entre em https://github.com/notifications).

```powershell
cd $HOME\Documents
git clone https://github.com/MatheusLoureiro7/mercadinho.git
cd mercadinho
```

Na primeira vez o Git abre uma janela para entrar na sua conta do GitHub: entre com o navegador.
O projeto fica em **Documentos\mercadinho**.

## 3. Preparar o Python do projeto

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

- Se o PowerShell disser que **a execução de scripts está desabilitada**, rode uma vez
  `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, responda `S` e repita a segunda linha.
- Deu certo quando o começo da linha do PowerShell mostra **`(.venv)`**.
- O `pip install` demora alguns minutos e mostra muito texto. No fim deve aparecer
  `Successfully installed ...`.

## 4. Criar o arquivo de configuração

```powershell
Copy-Item .env.example .env
notepad .env
```

No Bloco de Notas, troque **só estas duas linhas** (invente qualquer texto, sem espaço) e salve
com `Ctrl+S`:

```
DJANGO_SECRET_KEY=qualquer-texto-comprido-aqui-1234567890
POSTGRES_PASSWORD=uma-senha-qualquer
```

O resto fica como está. As linhas `TELEGRAM_...` **ficam vazias**: elas só servem para mandar os
avisos ao celular do Sr. João, e o sistema funciona sem elas.

## 5. Subir o banco de dados

**Abra o Docker Desktop** e espere o "Engine running". Depois:

```powershell
docker compose up -d --wait
python backend\manage.py migrate
```

- O primeiro comando baixa o PostgreSQL (só na primeira vez, uns 150 MB) e termina com
  `Container mercadinho-banco Healthy`.
- O segundo cria as 14 tabelas e mostra uma lista de linhas terminando em `OK`.

## 6. Carregar os dados da apresentação

```powershell
python backend\manage.py loaddata demonstracao
```

Deve responder **`Installed 48 object(s) from 1 fixture(s)`**. Ele cria as 4 categorias, os 3
fornecedores, os 10 produtos, os lotes, as movimentações e os três usuários do sistema.

## 7. Escolher as senhas dos três usuários

O arquivo de dados **não traz senha nenhuma** (senha não vai para o GitHub). Escolha uma para
cada usuário. O comando pede a senha **duas vezes** e **não mostra nada enquanto você digita** —
é normal, digite e aperte Enter:

```powershell
python backend\manage.py changepassword sobrinho   # Sobrinho — OPERACAO (vê quase tudo)
python backend\manage.py changepassword esposa     # Esposa — GESTAO
python backend\manage.py changepassword joao       # Sr. João — DONO
```

Use pelo menos 8 caracteres, misturando letras e números (ex.: `Mercado2026`). Senha fácil
demais é recusada; aí é só tentar outra.

## 8. Ligar o sistema

São **dois PowerShell abertos ao mesmo tempo**. No que você já está usando:

```powershell
# PowerShell 1 — a API (deixe esta janela aberta)
python backend\manage.py runserver
```

Deve aparecer `Starting development server at http://127.0.0.1:8000/`. **Não feche essa janela.**

Abra **outro** PowerShell e rode:

```powershell
# PowerShell 2 — o painel (deixe esta janela aberta também)
cd $HOME\Documents\mercadinho
.\.venv\Scripts\Activate.ps1
python frontend\servir.py
```

Agora abra no navegador: **http://127.0.0.1:8090/** — aparece a tela de Login.

Cada perfil vê telas diferentes (RN14):

| Entrar como | Vê |
|---|---|
| `sobrinho` | Produtos, Fornecedores, Entrada de mercadoria, Avarias e quebras, Consulta de estoque |
| `esposa` | Consulta de estoque (e Fechamento de caixa e Balanço da semana, quando ficarem prontas) |
| `joao` | Consulta de estoque — os avisos dele chegam pelo Telegram |

**Para desligar:** clique em cada PowerShell e aperte `Ctrl+C`. Os dados continuam guardados.

---

## Toda vez que for usar (da segunda vez em diante)

1. Abra o **Docker Desktop** e espere "Engine running".
2. PowerShell 1:

   ```powershell
   cd $HOME\Documents\mercadinho
   .\.venv\Scripts\Activate.ps1
   docker compose up -d --wait
   python backend\manage.py runserver
   ```

3. PowerShell 2:

   ```powershell
   cd $HOME\Documents\mercadinho
   .\.venv\Scripts\Activate.ps1
   python frontend\servir.py
   ```

4. Navegador: **http://127.0.0.1:8090/**

## Pegar a versão mais nova do grupo

Quando alguém do grupo avisar que subiu coisa nova, com o sistema **desligado**:

```powershell
cd $HOME\Documents\mercadinho
.\.venv\Scripts\Activate.ps1
git pull
pip install -r requirements-dev.txt
python backend\manage.py migrate
```

Depois ligue de novo (seção acima). Se o `git pull` reclamar de arquivo alterado, você mexeu em
algum arquivo do projeto: peça ajuda ao grupo antes de apagar qualquer coisa.

---

## Ver as tabelas do banco (para a apresentação)

**Pelo terminal**, sem instalar nada (com o Docker ligado):

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

Se a lista for maior que a tela, aparece `-- More --` ou `:` embaixo: aperte **espaço** para
continuar e **`q`** para voltar.

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

## Rodar os testes (opcional)

Para conferir que tudo funciona na sua máquina. Uma vez só, baixe o navegador dos testes de tela:

```powershell
playwright install chromium
```

Depois, com o Docker ligado (não precisa ligar a API nem o painel):

```powershell
pytest
```

Leva cerca de 1 minuto e deve terminar com `... passed`. Os testes usam um banco separado e
**não mexem** nos dados da apresentação.

---

## Deu errado?

| Mensagem | O que fazer |
|---|---|
| `py` não é reconhecido | Reinstale o Python marcando **"Add python.exe to PATH"**. Feche e abra o PowerShell. |
| `git` ou `docker` não é reconhecido | Feche e abra o PowerShell (ou reinicie o computador) depois de instalar. |
| `docker` … `cannot connect`, `pipe` ou `daemon` | O Docker Desktop está fechado. Abra e espere "Engine running". |
| `execução de scripts foi desabilitada` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, responda `S`. |
| `No module named django` (ou parecido) | Faltou ativar o Python do projeto: `.\.venv\Scripts\Activate.ps1` (a linha tem de começar com `(.venv)`). |
| `port is already allocated` (5432) | Já existe um PostgreSQL instalado no computador. No `.env`, mude `POSTGRES_PORT=5433` e rode `docker compose up -d --wait` de novo. |
| `password authentication failed` | A senha do `.env` mudou depois de criar o banco. Rode `docker compose down -v` (**apaga** o banco) e refaça os passos 5, 6 e 7. |
| `loaddata` … `duplicate key` | Os dados já foram carregados antes. Para recomeçar do zero: `docker compose down -v` e refaça os passos 5, 6 e 7. |
| `Error: That port is already in use` (8000 ou 8090) | O sistema já está ligado em outra janela do PowerShell. Use aquela, ou feche-a com `Ctrl+C`. |
| A tela diz **"O sistema não está respondendo"** | O PowerShell 1 (a API) está desligado ou com erro — olhe o que ele mostra. |
| Login recusado | Refaça o passo 7 para aquele usuário. |
| A página não abre no navegador | Confira se o PowerShell 2 (o painel) está ligado e se o endereço é `http://127.0.0.1:8090/`. |

Se nada disso resolver, mande ao grupo **um print do PowerShell** com a mensagem de erro inteira.

## Sem Docker

Se o Docker não funcionar no seu computador, instale o PostgreSQL direto no Windows:

1. Baixe em https://www.postgresql.org/download/windows/ (versão 17). O instalador já traz o
   **pgAdmin**. Anote a senha que ele pedir para o usuário `postgres`.
2. Abra o pgAdmin, entre com essa senha e crie:
   - em *Login/Group Roles*: o usuário **`mercadinho`**, com uma senha e a opção *Can login?* ligada;
   - em *Databases*: o banco **`mercadinho`**, com *Owner* = `mercadinho`.
3. No `.env`, coloque a senha do usuário `mercadinho` em `POSTGRES_PASSWORD`.
4. Siga do passo 5 **pulando** o `docker compose up -d --wait` (e na seção "Toda vez que for usar"
   também). Para ver as tabelas pelo terminal, use o pgAdmin no lugar do `docker compose exec`.

## Sobre os dados de demonstração

São uma cópia do banco de desenvolvimento do grupo em 08/10/2026, em
`backend/comum/fixtures/demonstracao.json`. **Não são** a carga real dos produtos da loja (tarefa
J2, feita com o cliente). As validades são datas fixas: com o passar dos dias, mais lotes aparecem
como vencidos na Consulta de estoque — é a RN16 funcionando, não erro.

---

## Conferência rápida

- [ ] `py --version`, `git --version` e `docker --version` respondem
- [ ] Convite do GitHub aceito e projeto em `Documentos\mercadinho`
- [ ] Linha do PowerShell começando com `(.venv)`
- [ ] `.env` criado, com `DJANGO_SECRET_KEY` e `POSTGRES_PASSWORD` preenchidos
- [ ] `loaddata demonstracao` respondeu `Installed 48 object(s)`
- [ ] Senhas dos três usuários escolhidas
- [ ] Dois PowerShell ligados (API e painel) e o Login abrindo em http://127.0.0.1:8090/

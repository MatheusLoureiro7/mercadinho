# Como usar este pacote com o Claude Code

---

## Passo 1 — Montar a pasta do projeto

Crie uma pasta vazia para o sistema e copie este pacote para dentro dela:

```
sistema-mercado/
  CLAUDE.md
  schema.sql
  PRIMEIRO-PROMPT.md
  docs/
    ESPECIFICACAO.md
    REGRAS-NEGOCIO.md
    ARQUITETURA.md
    ROTEIRO.md
    DECISOES-PENDENTES.md
    LACUNAS.md
```

Inicialize o git antes de qualquer coisa — é a tarefa **A1** do cronograma:

```bash
cd sistema-mercado
git init
git add .
git commit -m "A1: especificação do projeto (apostilas I a IV)"
```

Depois abra o Claude Code dentro dessa pasta:

```bash
claude
```

Ele lê o `CLAUDE.md` sozinho, toda vez. Não precisa colar o conteúdo dele em prompt nenhum.

---

## Passo 2 — A primeira conversa

Cole exatamente isto:

> Leia `CLAUDE.md` e todos os arquivos de `docs/`. Depois leia `schema.sql`.
>
> Antes de escrever qualquer código, me responda em texto:
>
> 1. Qual é o objetivo do sistema em duas frases.
> 2. Quantas tabelas existem, e quais são as três que o resto depende.
> 3. Quais regras de negócio a tarefa **C4** (saldo derivado das movimentações) precisa respeitar.
> 4. Quais tarefas do `docs/ROTEIRO.md` podem começar hoje sem depender de nenhuma decisão
>    pendente.
> 5. Alguma coisa que você precisaria saber para programar e que não está em nenhum documento.
>
> Não crie nenhum arquivo ainda.

**Isto é um teste, e é o passo mais importante.** Se as respostas estiverem erradas ou vagas, o
problema está nos documentos, não nele — e é muito mais barato corrigir agora do que depois de
2.000 linhas de código escritas em cima de um mal-entendido.

Confira em especial a pergunta 3. A resposta certa menciona **RN01** (saldo é sempre derivado,
nunca uma coluna) e, de perto, **RN11** (perda reduz estoque mas não conta como consumo).

---

## Passo 3 — Começar pelo bloco A

Uma tarefa por conversa. Nunca peça "faça o sistema".

> Vamos fazer a tarefa **A1** do `docs/ROTEIRO.md`.
>
> Stack confirmada no `CLAUDE.md`: Python 3.11, Django 5 + Django REST Framework, PostgreSQL,
> frontend em HTML/CSS/JS estático.
>
> Monte a estrutura inicial do repositório conforme a seção "Estrutura de pastas" do `CLAUDE.md`:
> apps `cadastro`, `estoque`, `vendas`, `previsao`, `alertas`, `caixa` e `comum`, mais a pasta
> `frontend/`. Inclua `requirements.txt`, `.gitignore`, `.env.example` e um `README.md` com o
> passo a passo para subir o ambiente em máquina Windows e Linux.
>
> Não crie model nenhum ainda — isso é a tarefa B1.

Depois, uma de cada vez: **A2**, **A3**, **B1**, **C1**…

---

## Passo 4 — O formato de pedido que funciona

Para toda tarefa daqui em diante, use este molde:

> Tarefa **[código]** do `docs/ROTEIRO.md`: **[nome da tarefa]**.
>
> Regras que se aplicam: **[RNxx, RNyy]** — leia em `docs/REGRAS-NEGOCIO.md` antes.
> Tabelas envolvidas: **[nomes]** — os campos estão em `schema.sql`.
>
> Escreva o código e os testes na mesma conversa. Cada losango de decisão do fluxograma vira pelo
> menos dois testes.
>
> Se faltar alguma informação que não esteja nos documentos, pare e pergunte em vez de decidir.

Exemplo real, para a tarefa que mais importa acertar:

> Tarefa **C4** do `docs/ROTEIRO.md`: saldo derivado das movimentações.
>
> Regras: **RN01** (o saldo é sempre a soma das movimentações — não existe coluna de saldo em
> `produto`) e **RN11** (movimentação tipo PERDA reduz o estoque mas fica fora da base de consumo).
>
> Tabelas: `movimentacao`, `lote`, e a view `vw_estoque_atual` do `schema.sql`.
>
> Escreva a migração, a função de consulta de saldo e os testes. Um dos testes precisa reproduzir
> o exemplo da Apostila I: entrada 40 kg, venda 12 kg, perda 3 kg, saldo 25 kg.

---

## As cinco frases que você vai precisar repetir

Guarde estas. Elas resolvem quase todo desvio:

1. **"Isso não está na especificação. Me mostre onde está, ou pare e pergunte."**
2. **"Não crie tabela nem coluna que não esteja no `schema.sql`."**
3. **"Essa tela não existe. As 10 telas estão em `docs/ARQUITETURA.md`."**
4. **"Releia a RN[xx] em `docs/REGRAS-NEGOCIO.md` e me diga se o seu código obedece."**
5. **"Qual tarefa do `docs/ROTEIRO.md` é essa? Se não for nenhuma, não é para fazer agora."**

---

## O que esperar — e o que não

**Ele vai acertar bem:** estrutura de pastas, models a partir do `schema.sql`, serializers, CRUD,
testes das regras simples (RN03, RN14, RN15), telas HTML básicas.

**Ele vai precisar de revisão de perto:**

- **RN02 (FIFO)** — tem muitas formas de escrever errado, e todas parecem funcionar com um lote só.
  Teste com dois lotes e validades diferentes.
- **RN11 (perda ≠ consumo)** — é um `WHERE` que se esquece com facilidade. Confira todas as
  consultas do motor de previsão.
- **A transação da entrada de mercadoria** (operação 02, passo 7) — lote e movimentação têm de
  gravar juntos ou nenhum.
- **RN12 (janela de silêncio)** — a verificação é na hora do **envio**, não da geração. É fácil
  implementar no lugar errado.

**Ele vai tentar fazer, e você precisa barrar:** criar tela de inventário, criar coluna `saldo` em
`produto`, acessar o banco direto do frontend, usar SQLite "só para testar", traduzir os nomes das
tabelas para inglês.

---

## Se ele inventar alguma coisa

Acontece. A resposta é sempre a mesma:

> Isso não está em nenhuma apostila. Remova e me diga qual decisão precisa ser tomada para isso
> existir.

E registre o ponto em `docs/LACUNAS.md`. Lacuna anotada é assunto de reunião de sexta; lacuna
resolvida sozinha no código é retrabalho na frente do professor.

---

## Lembrete

**O código serve à documentação, não o contrário.** O trabalho entregue ao professor foram as
apostilas. O sistema precisa ser aquilo que elas descrevem — se o código e o documento discordarem,
quem está errado é o código, até que o grupo decida mudar o documento **e registre a mudança numa
nova versão**.

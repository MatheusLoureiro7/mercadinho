# Roteiro da reunião com o cliente — Mercado do Sr. João

Preparado em 09/10/2026 pelo Grupo MDGS. Entrega do trabalho: **27/11/2026**.

**Para que serve:** tirar as dúvidas que só o Sr. João, a esposa e o sobrinho podem responder.
Sem elas o sistema não avança: **a resposta da primeira pergunta sozinha libera 136 das 378 horas
do cronograma** (vendas, previsão e o aviso de "vai acabar").

**Tempo:** 40 minutos. **Fora do horário de movimento** — de preferência entre 14h e 16h, ou depois
das 18h (o próprio sistema evita 10h30–13h e 16h30–18h).

**Quem precisa estar:**

| Pessoa | Por quê | Blocos |
|---|---|---|
| **Sr. João** | Decide compras e recebe os avisos no celular | 1, 4, 5 |
| **Esposa** | Confere o caixa e faz o balanço da semana | 1, 3 |
| **Sobrinho** | Registra mercadoria e lança as vendas | 1, 2, 5 |

**O que pedir para separarem antes** (mandar a mensagem uns dias antes):

- [ ] Acesso ao **computador do caixa**, com alguém que saiba mexer nele
- [ ] Um **pen drive** — para tentar trazer um arquivo de vendas de um dia
- [ ] O **caderno do balanço da semana** (da esposa) e o **caderno de avarias**
- [ ] O **celular do Sr. João**

**Como conduzir:** falar a língua da loja ("o que vendeu no dia", "vai acabar", "o que venceu"),
nunca termos técnicos — o Sr. João já disse: *"eu não sei o que é histórico de volante, o que você
está falando"*. Uma pessoa pergunta, outra **anota as respostas na folha de respostas (última página)**. Tirar **foto da
tela do caixa** e das páginas dos cadernos (com permissão).

---

## Bloco 1 — O caixa da loja · **O MAIS IMPORTANTE** (15 min)

> **Decisão D01** (bloqueante) e **lacuna L05**. Trava os blocos E, G, H3, I1, I3 e o fim da J1.

Ir **até o caixa**, com o sobrinho ou quem mexe nele.

1. **"Qual é a marca e o modelo do caixa? Que programa ele usa?"**
   *Anotar e fotografar a tela inicial e a etiqueta do aparelho.*
2. **"O caixa consegue tirar um relatório do que foi vendido no dia — produto por produto, com a
   quantidade?"** Pedir para mostrar onde fica.
3. **"Esse relatório sai só no papel, ou dá para salvar num arquivo — no pen drive ou no
   computador?"**
4. Se der para salvar: **"Podemos levar o arquivo de um dia para testar?"** (Copiar no pen drive.)
   *Anotar o tipo do arquivo: termina em `.csv`, `.txt`, `.xls`, `.xml`, `.pdf`?*
5. **"Cada produto tem um código no caixa?"** (Aquele número que aparece ao lado do nome.)
   *Isso decide como o sistema reconhece "o mesmo frango" no arquivo do caixa e no cadastro (L05).*
6. **"Quem tira esse relatório hoje, e quando?"** (Fim do dia? Fim da semana?)
7. **"O sobrinho hoje passa as vendas para o Excel — ele copia de onde?"**

**O que muda com cada resposta:**

| Resposta | O que a equipe faz |
|---|---|
| Sai arquivo (`.csv`, `.txt`, `.xls`…) e trouxemos um exemplo | Escrever o leitor desse formato (bloco E) e destravar previsão e avisos (G, H3). **Melhor caso.** |
| Sai arquivo, mas não conseguimos trazer | Marcar nova visita só para buscar o arquivo. Não programar no escuro. |
| Só sai no papel / não sai nada | **Mudança de escopo**: 136 h mudam de desenho. Levar ao professor antes de programar — não se resolve no código. |
| O caixa tem código por produto | Pedir ao grupo a coluna `codigo_pdv` em `produto` (L05) e registrar numa versão 1.1 da Apostila IV. |

---

## Bloco 2 — A validade dos produtos (5 min)

> **Decisão D02** (bloqueante). O sistema já está pronto para a recomendação da equipe.

Com o **sobrinho**:

8. **"Quando chega frango, carne, frios, iogurte… dá para você digitar a data da embalagem na
   hora de registrar?"** E para os outros produtos (arroz, enlatado), **não precisa**.
9. **"Se a embalagem não tiver data, ou se você esquecer, tudo bem o sistema calcular sozinho pelo
   prazo de cada produto?"** (Ex.: frango dura 4 dias → chegou dia 21, vale até dia 25.)

**O que muda:** se ele concordar, **nada muda** — é assim que o sistema já funciona (RN04). Se ele
disser que não consegue digitar, levar ao grupo.

---

## Bloco 3 — O caixa do fim do dia e o balanço (10 min)

> **Lacunas L12 e L16**, **decisão D06**. Trava as tarefas I1 (fechamento) e I3 (balanço).

Com a **esposa**, com o caderno do balanço aberto:

10. **"No fim do dia, a senhora confere só o dinheiro da gaveta, ou também cartão e Pix?"**
    *Decide o "valor apurado pelo sistema" na tela de fechamento: soma de **todas** as vendas, ou
    só das pagas em **dinheiro** (L12).*
11. **"Quando o caixa não bate, o que a senhora anota no caderno?"** (Só a diferença? O motivo?)
12. **"Como a senhora faz a conta do balanço da semana?"** Pedir para mostrar uma página.
    *Anotar: soma as vendas? Tira as perdas? A perda entra pelo preço que pagou ou pelo preço que
    vende? Tira o que pagou nas mercadorias? (L16)*
13. **"Mais ou menos quanto a loja vende por mês? E quanto se perdeu de mercadoria no último
    balanço?"** *Só para a apresentação do trabalho (D06) — se preferirem não dizer, tudo bem.*

**O que muda:** com a 10, a equipe fecha a I1 e liga a tela de fechamento (que já está pronta) à
API. Com a 12, define a conta do balanço (I3).

---

## Bloco 4 — Os avisos no celular do Sr. João (7 min)

> **Decisão D04**, **lacunas L01, L03, L15 e L24**. O envio pelo Telegram (H4–H7) já está pronto.

Com o **Sr. João**, com o celular dele na mão:

14. **"O senhor usa o Telegram?"** Se usa só o WhatsApp: **"Tudo bem instalar o Telegram só para
    os avisos da loja?"** *O sistema foi feito com o Telegram (Apostila IV). Se ele não aceitar,
    levar ao grupo — trocar o canal é possível (D04), mas custa horas.*
15. **"Os avisos podem chegar de madrugada e ficar esperando o senhor acordar?"** E confirmar: **"Nada
    entre 10h30 e 13h, nem entre 16h30 e 18h — continua assim?"** (RN12)
16. **"Avisar 3 dias antes de vencer está bom para tudo? Ou para alguma coisa precisa avisar com mais
    tempo?"** (Ex.: queijo, embutido, que vende mais devagar.) *(L01)*
17. **"Quando o senhor vai comprar, como decide quanto pedir?"** (Para quantos dias? Respeita o
    mínimo do fornecedor?) *(L15)*
18. **"Além do fim de semana, tem algum feriado em que a carne, o carvão e a cerveja não podem
    faltar?"** *(L03 — se não fizer diferença, a primeira versão trata só sábado e domingo.)*
19. **"O pedido mínimo do fornecedor é em reais (ex.: R$ 500) ou em quantidade?"** *(L24 — a tela
    hoje mostra em reais.)*

**Ligar o celular dele ao sistema já nesta visita**, se o bot estiver criado: rodar
`vincular_telegram --login joao` (README) e ele toca no link — leva 1 minuto.

---

## Bloco 5 — Rotina e onde o sistema vai ficar (3 min)

> **Decisões D03, D05, D07, D08**, e **agendar a J2 e a J3**.

20. **"O pedido da semana chega na segunda de manhã, e o sobrinho só chega à tarde. Tudo bem ele
    registrar a mercadoria à tarde?"** *(D08 — os avisos só rodam de madrugada, então não atrapalha.)*
21. **"O computador da loja fica ligado o tempo todo? Tem nobreak?"** *(D05 — a equipe registrou que
    a loja não tem espaço nem nobreak (R03), e os avisos de madrugada precisam de um computador
    ligado. Se não tiver, o sistema fica num servidor na internet, que pode ter um custo mensal
    pequeno — perguntar se aceitam.)*
22. **"Podemos começar pelos produtos que estragam (carne, frios, laticínios) e depois o resto?"**
    *(D03 — recomendação da equipe.)*
23. **"A loja vende fiado?"** *(D07 — só para registrar. **Não entra nesta versão**: está fora de
    escopo na Apostila III. Não prometer.)*
24. **Agendar duas datas:**
    - **Cadastro dos produtos junto com o sobrinho** (J2 — 8 h, pode ser em duas tardes);
    - **Contagem do estoque de partida** (J3 — 6 h, de preferência num dia mais calmo).

---

## Não prometer

O que o cliente pode pedir e **não está nesta versão** (Apostila III — fora de escopo):
nota fiscal, substituir o caixa, leitor de código de barras, vale-alimentação, fiado, contagem do
estoque por foto, controle financeiro. Resposta: *"Anotamos, mas não entra nesta primeira versão."*

---

## Depois da reunião (no mesmo dia)

1. Passar as respostas para `docs/DECISOES-PENDENTES.md` e `docs/LACUNAS.md` **como decisão do
   grupo** (a especificação só muda com decisão do grupo — CLAUDE.md).
2. Registrar no **Diário** de `docs/ACOMPANHAMENTO.md` o que foi decidido, em linguagem que o
   professor entenda.
3. Guardar o arquivo do caixa (se trouxemos) **fora do git** se tiver dado de cliente da loja; para
   os testes, fazer uma cópia com produtos e valores trocados.
4. Se a resposta do bloco 1 for "não sai arquivo": escrever ao professor **antes** de mudar o plano.

## Folha de respostas

| # | Pergunta | Resposta | Quem respondeu |
|---|---|---|---|
| 1 | Marca e modelo do caixa / programa | | |
| 2 | Tira relatório do que vendeu no dia? | | |
| 3 | Sai em arquivo? Onde salva? | | |
| 4 | Tipo do arquivo / trouxemos exemplo? | | |
| 5 | Cada produto tem código no caixa? | | |
| 6 | Quem tira o relatório, quando | | |
| 7 | De onde o sobrinho copia para o Excel | | |
| 8 | Digitar validade só nos perecíveis? | | |
| 9 | Sistema calcular quando não houver data? | | |
| 10 | Confere só dinheiro, ou cartão e Pix também? | | |
| 11 | O que anota quando o caixa não bate | | |
| 12 | Como faz a conta do balanço | | |
| 13 | Faturamento mensal / perda do último balanço | | |
| 14 | Usa Telegram? Aceita instalar? | | |
| 15 | Avisos de madrugada; silêncio 10h30–13h e 16h30–18h | | |
| 16 | 3 dias antes serve para tudo? | | |
| 17 | Como decide quanto pedir | | |
| 18 | Feriados em que não pode faltar | | |
| 19 | Pedido mínimo: reais ou quantidade | | |
| 20 | Registrar a mercadoria de segunda à tarde | | |
| 21 | Computador ligado sempre? Nobreak? Custo mensal? | | |
| 22 | Começar pelos perecíveis | | |
| 23 | Vende fiado? (só registrar) | | |
| 24 | Datas da J2 (cadastro) e da J3 (contagem) | | |

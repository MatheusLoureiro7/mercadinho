# Manual do usuário

*Atualizado em 16/11/2026.* Quem lê: o Sr. João, a esposa e o sobrinho. Base: Apostila II (as 10
telas) e RN14 (três perfis).

O sistema controla o que entra, o que sai e o que está vencendo, e avisa o Sr. João no celular
antes do problema acontecer. **Ele não é o caixa:** o caixa da loja continua vendendo e emitindo
nota; o sistema só lê a planilha que o caixa exporta (R05). Se a internet cair, a venda não para.

## Quem usa o quê

Cada pessoa vê no menu só as telas dela (RN14). Os dois funcionários não têm acesso.

| Tela | Sr. João (dono) | Esposa (gestão) | Sobrinho (operação) |
|---|---|---|---|
| Produtos | | | ✔ |
| Fornecedores | | | ✔ |
| Entrada de mercadoria | | | ✔ |
| Avarias e quebras | | | ✔ |
| Importação de vendas | | | ✔ |
| Consulta de estoque | ✔ | ✔ | ✔ |
| Fechamento de caixa | | ✔ | |
| Balanço da semana | | ✔ | |
| Avisos no Telegram (sem tela) | ✔ | | |

## Entrar no sistema

Abra o painel no navegador (`http://127.0.0.1:8090/` no computador da loja), escreva o **login** e
a **senha** e toque em **Entrar**. A sessão dura 12 horas; depois disso, ou se a senha for trocada,
o sistema pede para entrar de novo. **Sair** fica no canto de cima.

## Telas do sobrinho

### Produtos (RF01, RF15)
Cadastra e altera produtos: nome, categoria, unidade (KG, UN, L ou PCT), se é perecível e **quantos
dias dura**, preços, estoque mínimo, fornecedor e se **não pode faltar no fim de semana**.
- Produto perecível só é salvo com a durabilidade em dias (RN03).
- A categoria nova é criada dali mesmo. Produto, categoria e fornecedor não se apagam.

### Fornecedores (RF02)
Nome, contato, **em quantos dias entrega** depois do pedido e pedido mínimo. O prazo de entrega é o
que o sistema usa para saber quando pedir.

### Entrada de mercadoria (RF03, operação 02)
Quando a mercadoria chega: procure o produto, informe a quantidade, o fornecedor, o custo e a
**validade da embalagem**. Cada entrada vira um **lote**.
- Perecível sem validade: o sistema calcula (data de hoje + durabilidade). Validade que já passou é
  recusada (RN04).
- Ao chegar mercadoria, o aviso de "vai acabar" daquele produto que ainda não saiu é cancelado.
- A lista do dia fica embaixo do formulário. Lote não se edita: erro se corrige com perda ou nova entrada.

### Avarias e quebras (RF04)
O que venceu, quebrou ou estragou sai do estoque **sempre com o motivo** (botões "Venceu",
"Quebrou", "Estragou" ou texto livre). Escolha o lote, ou deixe o sistema tirar do que vence
primeiro. **Perda não conta como venda**: não faz o sistema mandar comprar mais (RN11).

### Importação de vendas (RF06, operação 04)
As vendas **entram sozinhas**: salve a planilha do caixa (Excel, uma por dia) na pasta combinada e a
rodada das 03h00 importa. Nesta tela:
- **Vendas para conferir** — venda cujo produto o sistema não reconheceu pelo nome. Aparece com
  data, hora, quantidade e preço; ache a linha na planilha, toque em **Escolher o produto**,
  procure e toque em **Ligar a este produto**. A venda sai do estoque no dia em que aconteceu.
- **Planilhas lidas** — as últimas 30, com a situação: *Lida*, *Lida, com vendas a conferir* ou
  *Não foi lida* (essa é tentada de novo na madrugada seguinte). Basta uma linha fora do formato —
  hora "9h30" em vez de "09:30", por exemplo — para a planilha inteira não entrar: corrija a linha
  no Excel e salve de novo na pasta. Assim nenhuma venda some do fechamento de caixa.
- Se uma planilha trouxer vendas de mais de um dia (a de ontem esquecida junto com a de hoje), ela
  entra normalmente e aparece em **Planilhas lidas** uma vez para cada dia.
- O nome do arquivo não importa: o sistema reconhece as vendas pelo dia. Um dia que já entrou não
  entra de novo, nem salvo com outro nome; e o caixa pode gravar sempre por cima do mesmo arquivo.
- Para a mesma venda não ficar pendente todo dia, deixe o nome do produto no cadastro igual ao do caixa.

## Tela de todos

### Consulta de estoque (RF07, RN16)
Saldo de cada produto, com três quadros no alto: **com lote vencido**, **perto de vencer** e
**abaixo do mínimo** (toque para filtrar). Procure pelo nome ou pela categoria; **Ver lotes** mostra
cada lote, do que vence primeiro ao último. Lote vencido aparece destacado e **não sai por venda**:
só por Avarias e quebras. Produto novo aparece como "ainda aprendendo" até ter 14 dias de venda (RN09).

## Telas da esposa

### Fechamento de caixa (RF12, RN15)
De manhã, confira o caixa **do dia anterior** (as vendas de ontem entram de madrugada). O **Dia do
caixa** já vem com ontem; para fechar um dia que ficou para trás (o sábado, fechado na segunda), troque
a data. Hoje e os dias que ainda não chegaram não podem ser fechados. Digite o **dinheiro contado**: o
sistema mostra o apurado (vendas em dinheiro daquele dia) e a diferença antes de registrar. Registro
não se altera nem se apaga: contou de novo, registra de novo, e o anterior fica. Se as vendas do dia
escolhido ainda não entraram, a tela explica e não deixa registrar.

### Balanço da semana (RF13)
Vendas, perdas e resultado de **segunda a domingo**, no lugar do caderno:
- **Resultado = vendas − perdas**, com as perdas a preço de custo e sempre em linha separada (L16, RN11).
- Embaixo, as vendas de cada dia e as perdas produto por produto.
- Dia cuja planilha não entrou aparece como "não entrou", com aviso — nunca como R$ 0,00.
- Perda de produto sem custo cadastrado fica de fora do valor e é avisada.
- Use **Semana anterior** para voltar.

## Avisos no celular do Sr. João (RN05, RN08, RN10, RN12, RN13)

O Sr. João não precisa abrir o sistema (RNF01). Toda madrugada o sistema calcula e manda pelo
Telegram, **numa mensagem só**, do mais urgente para o menos:
- **Validade:** "Presunto vence em 3 dias — 2,5 KG na prateleira."
- **Vai acabar:** "Frango resfriado 1 kg acaba em 2 dias — sobram 6 KG. Pedir 30 KG — Granja Boa
  Vista entrega em 2 dias.", com o botão **Sim, pedir**.
- **Fim de semana** (na quinta-feira): carne, carvão, cerveja, linguiça e asinha avaliados com folga.

Nada é enviado nos horários de movimento (10h30–13h00 e 16h30–18h00): o aviso espera e sai no fim do
horário. Depois do "Sim, pedir", aquele produto não é avisado de novo até a mercadoria chegar —
mas só pelo prazo de entrega do fornecedor: se ele entrega em 2 dias e nada chegou, no terceiro dia
o aviso volta começando por **"O pedido ainda não chegou"**.
Para ligar o celular, ver o Guia de início rápido.

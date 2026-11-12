# Lacunas e divergências da especificação

Pontos em que a documentação entregue **não é suficiente para programar sem escolher por conta
própria**. Nenhum deles foi resolvido aqui: estão listados para o grupo decidir, e alguns para
perguntar ao professor ou ao cliente.

**Enquanto uma lacuna estiver aberta, não invente a resposta no código.** Implemente o mínimo que
não fecha porta e deixe o ponto de extensão pronto.

---

## 1. Lacunas que afetam o código

### L01 — `dias_aviso_validade` é global ou por categoria?

A **RN05** diz: *"O valor de N é configurável e vale por categoria."*
Mas a tabela `parametro` da Apostila IV tem chave única (`dias_aviso_validade`), que só comporta um
valor global.

A própria Apostila I reconhece o problema: *"3 dias serve para carne, mas é pouco para um produto
de giro lento."*

**Impacto:** tarefa H2 (gerador do aviso de validade, 8 h).
**O que fazer agora:** implementar o parâmetro global, mas ler o valor por uma função
`dias_aviso_validade(produto)` — assim, quando a decisão sair, muda um lugar só.
**Quem decide:** o grupo, e vale confirmar com o cliente.

---

### L02 — O que é "diferença relevante" na RN07?

A **RN07** diz que o sistema usa a maior entre a média geral e a média do dia da semana *"quando a
diferença entre elas for relevante"*. Relevante não está definido em lugar nenhum.

**Impacto:** tarefa G2 (12 h), a mais difícil do projeto.
**Proposta para o grupo decidir:** usar a média do dia da semana quando ela for **≥ 1,5 ×** a média
geral. O exemplo da apostila (cerveja: 8/dia na média, 26 aos sábados) passaria com folga nesse
critério.
**Quem decide:** o grupo. É uma escolha técnica, não precisa do cliente.

> **✅ DECIDIDA em 12/11/2026 (tarefa G2):** **≥ 1,5 × a média geral**, como proposto. Quando a
> média de um dia da semana chega a 1,5 vez a média geral, a projeção daquele dia usa a média do
> dia (a maior das duas); nos outros dias, a média geral — inclusive no dia mais fraco, para o
> domingo parado não derrubar a projeção. A média do dia usa os mesmos 30 dias da RN06 e divide
> pelas vezes que o dia aparece neles (4 ou 5), contando dia sem venda como zero. O fator fica em
> `previsao.calculo.FATOR_DIA_RELEVANTE`.

---

### L03 — Qual calendário de feriados a RN10 usa?

A **RN10** manda avaliar os itens críticos também em **véspera de feriado**. A especificação não
diz de onde vem a lista de feriados.

**Impacto:** tarefa H3 (10 h).
**Opções:** tabela de feriados cadastrada à mão pela esposa; biblioteca de feriados nacionais;
ignorar feriado na primeira versão e tratar só sábado e domingo.
**Quem decide:** o grupo. Se escolher ignorar, **declare isso** — vira um item de escopo, não um
esquecimento.

> **✅ DECIDIDA em 12/11/2026 (tarefa H3):** **sem calendário de feriados nesta versão — só sábado e
> domingo.** Os itens críticos são avaliados na quinta-feira (RN10), para garantir o fim de
> semana. **Véspera de feriado fica fora do escopo da primeira versão, declarado:** não há tabela
> de feriados (seria tabela nova no modelo de dados) nem biblioteca de feriados (dependência nova).

---

### L04 — O que é a "previsão por período" do Natal?

A Apostila IV, seção 8, marca como **Parcial** a atividade *"Compra mais no Natal, e às vezes
sobra"*, atendida por "Previsão por período". Nenhuma RF e nenhuma RN descrevem esse cálculo.

**Impacto:** nenhuma tarefa do cronograma implementa isso. A linha "Parcial" fica sem código.
**O que fazer:** não implementar. Se o professor perguntar, a resposta honesta é que a cobertura é
parcial justamente porque a regra de sazonalidade não foi especificada.

---

### L05 — Como o `item_venda` casa com o `produto`?

A operação 04 fala em *"procura o produto pelo código do caixa"*, e a tarefa E4 (10 h) se chama
"casar o produto do caixa com o produto cadastrado". Mas a tabela `produto` **não tem uma coluna
para o código do caixa**.

**Impacto:** tarefa E4. Sem esse campo, o casamento teria de ser por nome, que é frágil.
**Proposta:** acrescentar `produto.codigo_pdv VARCHAR(40) UNIQUE`.
**Atenção:** isso é uma alteração no modelo de dados da Apostila IV. **Não faça sem o grupo
decidir e sem registrar a mudança numa versão 1.1 da apostila.** Depende também de D01, porque o
formato do arquivo é que diz qual é o código.
**Decisão do grupo (05/11/2026, tarefa E1):** o produto é encontrado **pelo nome**, comparado sem
diferenciar maiúscula, acento nem espaços a mais. **Nenhuma coluna nova**: o modelo de dados da
Apostila IV não muda. Linha que não casa fica pendente (operação 04, passo 6). Ver
`docs/FORMATO-PLANILHA-CAIXA.md`.

---

### L09 — A autenticação do Django não cabe na tabela `usuario`

A Apostila IV define `usuario` com `senha_hash`, `papel`, `login`, `telegram_chat_id` e `ativo`.
O modelo de usuário do Django (`AbstractBaseUser`) exige as colunas `password` e `last_login`, e a
autenticação por token do DRF exige a tabela `authtoken_token`. O próprio Django também cria
tabelas internas (`django_migrations`, `django_content_type`, `auth_permission`, `django_session`).
Nenhuma delas está nas 14 tabelas.

**Impacto:** tarefas B1 (6 h) e A4 (12 h). Precisa ser decidido **antes da B1**.
**Opções:**
- (a) autenticação própria sobre a tabela `usuario` exatamente como está, sem o modelo de usuário
  do Django — por exemplo, token assinado (sem tabela) e hash de senha do próprio Django;
- (b) usar o modelo de usuário do Django com `db_table = 'usuario'`, aceitando `last_login` e
  registrando isso numa versão 1.1 da Apostila IV.

**Atenção (desde a A2):** a primeira migração já criou as tabelas `auth_*` do Django no banco de
desenvolvimento. O Django só permite trocar o modelo de usuário antes da primeira migração; se o
grupo escolher (b), cada pessoa precisa recriar o banco local (`docker compose down -v`). Enquanto
não há dado real isso não custa nada — mas a decisão tem de sair antes da B1.

Nas duas opções as tabelas internas do Django existem. Vale declarar que elas são infraestrutura do
framework, não parte do modelo de dados do negócio.
**Quem decide:** o grupo.

> **✅ DECIDIDA em 06/10/2026 — opção (c), surgida na análise:** usar a autenticação do Django
> apontada para a tabela `usuario` **exatamente como está na Apostila IV**, sem coluna a mais:
>
> - modelo próprio sobre `AbstractBaseUser`, com `db_table = 'usuario'`;
> - o hash da senha vai na coluna `senha_hash` (`db_column`), com o hash padrão do Django (RNF12);
> - a coluna `last_login` é removida do modelo (`last_login = None`);
> - `login` é o identificador (`USERNAME_FIELD`) e `ativo` faz o papel de "usuário ativo";
> - sem `PermissionsMixin` e sem `django.contrib.admin`: o controle de acesso é o `papel` da
>   RN14, verificado na camada de autenticação da API (tarefa A4);
> - token de acesso **assinado** (`django.core.signing`), que não precisa de tabela.
>
> **Por quê:** o modelo de dados entregue ao professor fica intacto, e o grupo continua
> aproveitando o hash de senha e o login prontos do Django — o motivo de ter escolhido Django.
> **Custo:** recriar o banco local uma vez, na B1 (`docker compose down -v`). Ainda não há dado real.
> **Onde entra no código:** B1 (model `usuario`) e A4 (token e verificação de papel).

---

### L10 — Não há como registrar ajuste para menos

A `movimentacao` aceita só `quantidade > 0` (restrição `[derivado]` do `schema.sql`), e a view
`vw_estoque_atual` sempre **soma** o tipo `AJUSTE`. Se uma contagem física encontrar menos do que o
sistema mostra, não existe forma de lançar a diferença — só como `PERDA`, o que tem outro sentido.

**Impacto:** tarefa C4 (6 h).
**Opções:** permitir quantidade negativa só no `AJUSTE`; ou declarar que diferença para menos é
sempre registrada como `PERDA` com motivo. A primeira muda uma restrição `[derivado]`, não uma
coluna — mas ainda assim é decisão do grupo.
**Quem decide:** o grupo.

---

### L11 — Os valores de `alerta.severidade` não estão definidos

A coluna existe e a **RN13** manda ordenar os avisos "por urgência" (severidade, depois
`gerado_em`). Nenhum documento lista os valores possíveis nem a ordem entre eles.

**Impacto:** tarefas H1 (8 h) e H4 (8 h).
**Proposta para o grupo decidir:** `ALTA`, `MEDIA`, `BAIXA`, com uma restrição CHECK.
**Quem decide:** o grupo.

> **✅ DECIDIDA em 08/10/2026 (tarefa H1):** `ALTA`, `MEDIA`, `BAIXA`, nessa ordem de urgência,
> **validadas no código** (`alertas.servicos.criar_aviso`), sem restrição CHECK nova — o banco fica
> igual ao `schema.sql`, como na L17 (unidade de medida). Qual tipo de aviso recebe qual
> severidade fica para os geradores (H2, H3). Vale registrar numa versão 1.1 da Apostila IV.

---

### L12 — De onde vem `fechamento_caixa.valor_sistema`?

A **RN15** fala em "valor apurado pelo sistema", e o fluxograma 06 liga o fechamento à tabela
`venda`. Presume-se que seja `SUM(venda.valor_total)` do dia — mas isso não está escrito, e não
se sabe se considera a forma de pagamento (só dinheiro é contado na gaveta?).

**Impacto:** tarefa I1 (8 h). Depende também da D01.
**Quem decide:** o grupo, confirmando com a esposa do Sr. João.
**Decisão do grupo (05/11/2026, tarefa I1):** o apurado é a soma das vendas do dia **pagas em
dinheiro** (a gaveta só tem dinheiro). O fechamento é do **dia anterior**, porque as vendas entram às
03h00 do dia seguinte (E3); sem as vendas daquele dia importadas, o fechamento é recusado.

---

### L13 — Desempate do FIFO e lotes sem validade

A **RN02** ordena por `data_validade ASC`. Não diz:
- o que fazer quando dois lotes vencem no mesmo dia;
- onde ficam os lotes sem validade (produto não perecível). No PostgreSQL, `NULL` vai para o fim
  da ordenação crescente.

**Impacto:** tarefas C4 e E3.
**Proposta para o grupo decidir:** desempatar por `data_entrada` e depois `id`; lote sem validade
sai por último.
**Quem decide:** o grupo. É escolha técnica.

> **✅ DECIDIDA em 07/10/2026 (tarefa D1):** como proposto. Ordem: `data_validade` (critério da
> RN02), depois `data_entrada`, depois `id`; lote sem validade sai por último. Implementado uma
> vez só em `backend/estoque/fifo.py`, usado pela perda (D1) e pela venda (E3).

---

### L14 — Nenhuma tela cuida de usuários e parâmetros

As 10 telas da Apostila II não incluem cadastro de usuário, troca de senha, nem edição da tabela
`parametro`. Os parâmetros, porém, "nunca ficam fixos no código" e ainda serão ajustados com o
cliente.

**Impacto:** operação e implantação (J2, J6). Não trava nenhuma tarefa de código.
**Proposta para o grupo decidir:** administrar usuários e parâmetros por comando `manage.py` (ou
pelo admin do Django), operado pela equipe — sem criar uma 11ª tela.
**Quem decide:** o grupo.

> **◐ DECIDIDA EM PARTE em 06/10/2026 (tarefa A4) — usuários:** criados pela equipe com
> `manage.py criar_usuario --login --nome --papel` (senha pedida no terminal, validada pelas
> regras de senha do Django) e trocados com `manage.py changepassword`. Sem tela nova e sem o
> admin do Django.
> **Parâmetros: ainda em aberto.** Precisa ser decidido antes da primeira tarefa que lê a tabela
> `parametro` (H2, aviso de validade).

---

### L15 — Qual é a fórmula da sugestão de compra?

O **RF11** pede para "indicar a quantidade a pedir de cada produto, considerando o prazo do
fornecedor", e a tabela `previsao_produto` tem a coluna `sugestao_compra`. Nenhuma RN diz como esse
número é calculado: até quantos dias de cobertura comprar, se desconta o saldo atual, se respeita
`fornecedor.pedido_minimo`.

**Impacto:** tarefa G3 (8 h).
**Quem decide:** o grupo. Vale confirmar com o Sr. João como ele decide hoje quanto pedir.

> **✅ DECIDIDA em 12/11/2026 (tarefa G3):** sugestão = **o que o produto vai vender durante o prazo
> de entrega do fornecedor + 7 dias**, contados de hoje e com o consumo de cada dia (RN07: o
> sábado da cerveja conta 26), **menos o saldo atual**; nunca negativa. O pedido mínimo do
> fornecedor **não entra**. Produto sem fornecedor padrão não tem prazo, então fica sem sugestão
> (e sem ponto de pedido). Os 7 dias ficam em `previsao.projecao.DIAS_ALEM_DO_PRAZO`.

---

### L16 — O que é o "resultado do período" no balanço?

O **RF13** pede "vendas, perdas e resultado do período". Não está definido se o resultado é
vendas menos perdas, se as perdas entram a preço de custo ou de venda, nem se o custo da mercadoria
vendida entra na conta.

**Impacto:** tarefa I3 (12 h).
**Quem decide:** o grupo, confirmando com a esposa do Sr. João como ela faz a conta no caderno.

---

### L17 — `unidade_medida` aceita só KG, UN, L e PCT?

O `schema.sql` cita `'KG', 'UN', 'L', 'PCT'` apenas num comentário da coluna
`produto.unidade_medida`. Não há restrição no banco, e o **RF01** só diz "unidade de medida".
Não está definido se a lista é fechada nem se existem outras unidades na loja (dúzia, bandeja,
caixa, fardo).

**Impacto:** tarefa B3 (validações do produto) e B5 (campo da tela: lista ou texto livre).
**Situação na B1:** a coluna foi criada como no `schema.sql`, sem restrição — nada foi inventado.
**Proposta para o grupo decidir:** lista fechada validada na API (não no banco), conferida com o
sobrinho na carga inicial (J2).
**Quem decide:** o grupo, confirmando com o sobrinho.

> **✅ DECIDIDA em 06/10/2026 (tarefa B3):** lista fechada **KG, UN, L, PCT** — a que o
> `schema.sql` cita —, validada só na API (`UNIDADES_DE_MEDIDA` em
> `backend/cadastro/serializers.py`). O banco continua sem restrição, como no `schema.sql`.
> Minúsculas são aceitas e gravadas em maiúsculas. **Por quê:** evita o mesmo produto cadastrado
> como "kg", "Kg" e "quilo", o que estragaria a previsão de consumo. Se a carga inicial (J2) mostrar
> outra unidade, acrescentar é mudar uma linha.

---

### L18 — A categoria não tem tela própria: quem lê e quem cadastra?

As 10 telas da Apostila II não incluem uma tela de categorias, mas a tarefa **B2** cria a "API de
categoria". A categoria aparece em duas telas com perfis diferentes na RN14: **Produtos** (onde se
escolhe a categoria — só OPERACAO) e **Consulta de estoque** (o RF07 pede o saldo "por
categoria" — os três perfis).

**Impacto:** tarefa B2 (8 h).

> **✅ DECIDIDA em 06/10/2026 (tarefa B2):** **ler** as categorias pertence à Consulta de estoque
> (DONO, GESTAO e OPERACAO); **criar e editar** pertence à tela de Produtos (só OPERACAO). Nenhuma
> tela nova: o cadastro de categoria é feito de dentro da tela de Produtos (B5).
> Como categoria e fornecedor são tabelas de origem ("nunca podem ser apagadas", Apostila IV,
> seção 5), a API **não tem exclusão** para nenhum dos dois.

---

### L19 — Para que serve `categoria.perecivel_padrao`?

A coluna existe na Apostila IV (`categoria.perecivel_padrao BOOLEAN NOT NULL DEFAULT FALSE`), mas
nenhum documento diz como ela é usada.

**Impacto:** tarefa B3 (cadastro de produto).

> **✅ DECIDIDA em 06/10/2026 (tarefa B3):** quando o produto é cadastrado **sem dizer** se é
> perecível, ele herda o `perecivel_padrao` da categoria. Quem diz explicitamente prevalece (o
> carvão pode ficar no Açougue sem ser perecível). **Por quê:** é a única função que justifica a
> coluna, e poupa o sobrinho de marcar um por um os produtos do açougue e dos frios (RNF05).

---

### L20 — De qual lote sai a perda?

O fluxograma 03 (registro de perda) usa a **RN02** (ordem de validade) e a tabela `lote`, e a
**RN16** diz que o lote vencido "só sai registrando perda". Não está escrito se a tela de avarias
pede o lote ou se a perda sai sozinha pela ordem de validade.

**Impacto:** tarefas D1 (API) e D3 (tela).

> **✅ DECIDIDA em 07/10/2026 (tarefa D1):** os dois. **Com lote informado** (o sobrinho sabe qual
> estragou), a perda sai dele. **Sem lote**, sai pela ordem de validade da RN02, **vencidos
> incluídos** (RN16), uma linha de movimentação por lote afetado (RN01). Perda maior do que o que
> existe é recusada, e nada é gravado.

---

### L21 — A tabela `parametro` não está em nenhuma tarefa do cronograma

A tabela `parametro` está no `schema.sql` (com os 7 valores iniciais da Apostila I, seção 7), mas
nenhuma das tarefas da seção 9 da Apostila IV a cria: B1 cria cadastros, C1 lote e movimentação,
E2 vendas, G1/G3 consumo e previsão, H1 avisos, I1 fechamento.

**Impacto:** F1 (o que está "vencendo" usa `dias_aviso_validade`) e todas as regras com número
configurável (RN05, RN08, RN09, RN10, RN12).

> **✅ DECIDIDA em 07/10/2026 (tarefa F1):** a tabela é criada na F1, a primeira tarefa que precisa
> dela — igual ao `schema.sql`, com os 7 valores iniciais copiados literalmente. Vale registrar
> numa versão 1.1 da Apostila IV que a F1 também cria a tabela de parâmetros. A forma de **alterar**
> os valores continua aberta (L14).

---

### L22 — A tela de Login não tem tarefa no cronograma

A Apostila II lista o **Login** entre as 10 telas ("Identifica a pessoa e monta o menu conforme o
papel"), e a A4 entregou a API dela. Mas nenhuma tarefa de tela da seção 9 da Apostila IV a
constrói (B5 Produtos, B6 Fornecedores, C5 Entrada, D3 Avarias, E5 Importação, F3 Consulta, I2
Fechamento).

**Impacto:** sem ela, as telas não conseguem falar com a API (que exige login desde a A4).

> **✅ DECIDIDA em 07/10/2026 (tarefa B5):** a tela de Login é feita na **B7** ("Ligar as telas à
> API"), que é quando as telas passam a precisar do token. Vale registrar numa versão 1.1 da
> Apostila IV.

---

### L23 — Divergência: a etapa 1 promete o aviso de vencimento no celular, mas não tem as horas dele

A Apostila IV, "Totais e o que cada etapa entrega", diz que a etapa 1 (blocos A, B, C, D, F, J —
212 h) entrega "o aviso de vencimento chegando ao celular". Mas o aviso de validade (H2) e o
envio pelo Telegram (H5) estão no bloco H, contado na etapa 2.

**Impacto:** o que se promete ao cliente ao fim da etapa 1.
**O que fazer:** corrigir numa versão 1.1 — ou tirar o aviso da descrição da etapa 1, ou mover H1,
H2, H4 e H5 (34 h) para ela. **Quem decide:** o grupo.

---

### L24 — O pedido mínimo do fornecedor é em reais ou em quantidade?

A Apostila IV tem a coluna `fornecedor.pedido_minimo NUMERIC(12,2)`, mas nenhum documento diz o que
ela mede. O RF02 cita só "nome, contato e, principalmente, em quantos dias o fornecedor entrega".

**Impacto:** tarefa B6 (rótulo do campo na tela) e G3 (L15, se a sugestão de compra respeitar o
pedido mínimo).

> **Adotado na B6 (07/10/2026), a confirmar pelo grupo:** **reais**. É a convenção do próprio
> modelo — dinheiro em `NUMERIC(12,2)`, quantidade em `NUMERIC(12,3)` (carne em quilos
> fracionados) —, e quantidade não teria unidade, porque o fornecedor entrega vários produtos. A
> tela mostra "Pedido mínimo · R$". Nada muda no banco nem na API; se o grupo decidir diferente,
> muda só o rótulo.

### L25 — Como o painel estático chega à API?

A Apostila IV, figura 2, separa os "arquivos estáticos" (o painel) do servidor da API, mas não diz
em que endereço cada um fica. Em endereços diferentes (porta 8090 e 8000, por exemplo), o
navegador bloqueia a chamada (CORS), e liberar exigiria configuração a mais — ou a dependência
`corsheaders`, que o CLAUDE.md só permite com decisão do grupo.

**Impacto:** tarefa B7 em diante (toda tela) e a publicação (A5, J6, decisão D05).

> **✅ DECIDIDA em 08/10/2026 (tarefa B7):** **mesma origem**. O painel chama sempre `/api/...`,
> caminho relativo; quem serve o painel repassa `/api/` para a API. Em desenvolvimento isso é o
> `frontend/servir.py` (só biblioteca padrão do Python); na publicação, o servidor web faz o mesmo
> papel. É o arranjo usual de painel + API: sem CORS, sem dependência nova, nenhuma linha a mais no
> Django, e o painel continua separado do servidor da API, como na figura 2.

### L26 — Como o sobrinho sabe qual produto era a linha pendente?

A operação 04, passo 6, diz que a linha sem produto correspondente "fica pendente de revisão" e
que "o sobrinho resolve depois, na tela de importação". Mas `item_venda` guarda só venda,
quantidade e preço — **não guarda o nome escrito na planilha**, e `venda` não guarda o número do
cupom. Na revisão, o sistema não tem como mostrar qual produto o caixa registrou.

**Impacto:** tarefas E4 (casar o item pendente) e E5 (tela de acompanhamento da importação).

> **✅ DECIDIDA em 12/11/2026 (tarefa E4):** **o modelo de dados não muda.** O item pendente
> aparece com **data, hora, quantidade e preço** da venda; o sobrinho confere na planilha dele e
> escolhe o produto. Ao escolher, o sistema grava o produto no item e faz a baixa do estoque como
> se tivesse casado na importação: na hora da venda, do lote que vence primeiro (RN01, RN02), sem
> lote vencido no dia da venda (RN16). A importação continua com a situação que teve na leitura
> (`PARCIAL`): ela é o registro do que aconteceu, e não tem ligação com a venda no modelo.
> Alternativas descartadas: coluna nova `item_venda.nome_no_caixa` (mudaria o modelo de dados
> entregue) e reler a planilha guardada na pasta (frágil se o arquivo sumir ou houver duas linhas
> iguais). Para a mesma linha não ficar pendente todo dia, o caminho é acertar o nome no cadastro
> igual ao do caixa.

### L27 — Qual número é cada dia da semana em `consumo_diario.dia_semana`?

O `schema.sql` tem `dia_semana SMALLINT` com `CHECK (dia_semana BETWEEN 0 AND 6)`, marcado como
`[derivado]`, mas nenhum documento diz se 0 é domingo ou segunda-feira. O Python numera segunda = 0;
o PostgreSQL (`EXTRACT(DOW)`) numera domingo = 0.

**Impacto:** tarefas G1 (gravar), G2 (média por dia da semana, RN07) e o formato de
`previsao_produto.consumo_por_dia_semana` (G3).

> **Adotado na G1 (12/11/2026), a confirmar pelo grupo:** **0 = domingo … 6 = sábado**, como o
> `EXTRACT(DOW)` do PostgreSQL — o banco que a Apostila IV fixa, e a única numeração comum que cabe
> no `CHECK 0 a 6` sem conversão (a ISO vai de 1 a 7). O banco não muda; se o grupo decidir
> diferente, muda uma função (`previsao.agregacao.dia_da_semana`) e a tabela é recalculada com
> `agregar_consumo --desde`, porque é dado derivado.

---

## 2. Divergências internas da documentação entregue

São erros pequenos nas apostilas, de contagem. Não impedem programar, mas é melhor corrigir numa
versão 1.1 do que o professor encontrar.

### L06 — "13 tabelas" na capa, 14 nas figuras

A capa da Apostila IV diz *"13 tabelas · 52 tarefas · 378 horas estimadas"*.
As figuras 5 e 6 desenham **14 tabelas**:

- Figura 5 (7): categoria, produto, fornecedor, lote, movimentacao, item_venda, venda
- Figura 6 (7): usuario, importacao_pdv, consumo_diario, alerta, parametro, fechamento_caixa, previsao_produto

**O desenho está certo e a contagem da capa está errada.** O `schema.sql` segue as figuras.

### L07 — "52 tarefas" na capa, 51 nas tabelas

Somando as tarefas listadas na seção 9: A 5 + B 7 + C 6 + D 4 + E 5 + F 3 + G 5 + H 7 + I 3 + J 6 =
**51**.

As **horas** estão todas corretas: os totais por bloco somam 378 h, e as etapas batem em 212 / 136
/ 30. O erro é só na contagem de tarefas da capa.

### L08 — A Apostila V contradiz as Apostilas I a IV

O cronograma datado (Apostila V) foi montado com uma lista de tarefas diferente da seção 9 da
Apostila IV, e por isso:

- cita **tela e API de inventário**, que a Apostila IV marca como **"não coberto"** e a Apostila II
  não lista entre as 10 telas;
- cita **"API de pedido ao fornecedor"**, que não corresponde a nenhum RF (o RF11 é *sugerir quanto
  comprar*, não emitir pedido);
- **não contém** o importador do PDV, o motor de previsão, os avisos no Telegram nem o fechamento
  de caixa — que são o núcleo do produto;
- usa os **códigos de RN trocados** (por exemplo, trata RN13–RN14 como regras de inventário, quando
  RN13 é agrupamento de avisos e RN14 é perfis de acesso);
- totaliza **362 h**, contra as **378 h** da Apostila IV.

**Este pacote segue as Apostilas I a IV.** A Apostila V precisa ser refeita em cima da seção 9 da
Apostila IV antes de ser entregue ao professor.

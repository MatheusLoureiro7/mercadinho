# Acompanhamento do cronograma

Andamento das tarefas do **cronograma da Apostila IV, seção 9** — o mesmo que foi entregue ao
professor em 25/09/2026. Os códigos, as horas e as dependências são os da apostila.

**Como ler:** tarefa concluída aparece ~~riscada~~, com a data e o commit em que foi entregue.
O diário, no fim do arquivo, conta o que foi feito em cada dia.

| Situação | Significado |
|---|---|
| ✅ Concluída | Pronta **e testada** |
| 🔄 Em andamento | Começou e ainda não terminou |
| ⬜ A fazer | Não começou; não depende de decisão do cliente |
| ⛔ Aguarda Dxx | Depende de uma decisão pendente (`docs/DECISOES-PENDENTES.md`) |

---

## Resumo

*Atualizado em 09/10/2026.*

| | Concluído | Total | % |
|---|---|---|---|
| **Tarefas** | 30 | 51 | 58,8 % |
| **Horas estimadas** | 202 h | 378 h | 53,4 % |

| Etapa | Blocos | Horas concluídas | Total | % |
|---|---|---|---|---|
| 1 · Aviso de validade | A, B, C, D, F, J | 160 h | 212 h | 75,5 % |
| 2 · Aviso de ruptura | E, G, H | 42 h | 136 h | 30,9 % |
| 3 · Gestão | I | 0 h | 30 h | 0,0 % |

As horas concluídas são as **estimadas** na apostila para cada tarefa entregue, não horas medidas.

Prazo de entrega: **27/11/2026**.

---

## Bloco A — Fundação · 40 h  ·  34 de 40 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~A1~~ | ~~Configurar repositório, ambiente e padrão de código~~ | — | 6 | ✅ Concluída | 06/10/2026 | `ca4ac9b` |
| ~~A2~~ | ~~Subir o banco de dados e a ferramenta de migração~~ | A1 | 6 | ✅ Concluída | 06/10/2026 | `02c5ae1` |
| ~~A3~~ | ~~Esqueleto da API: rotas, tratamento de erro e registro de log~~ | A1 | 10 | ✅ Concluída | 06/10/2026 | `ebea081` |
| ~~A4~~ | ~~Autenticação e os três perfis de acesso~~ | A3, B1 | 12 | ✅ Concluída | 06/10/2026 | `ec49325` |
| A5 | Esteira de publicação em ambiente de teste | A1 | 6 | ⛔ Aguarda D05 | — | — |

## Bloco B — Cadastros · 46 h  ·  46 de 46 h concluídas ✅

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~B1~~ | ~~Criar as tabelas de usuário, categoria, produto e fornecedor~~ | A2 | 6 | ✅ Concluída | 06/10/2026 | `a3923e2` |
| ~~B2~~ | ~~API de categoria e fornecedor~~ | B1, A3 | 8 | ✅ Concluída | 06/10/2026 | `3f93ef1` |
| ~~B3~~ | ~~API de produto, com validações~~ | B1, A3 | 10 | ✅ Concluída | 06/10/2026 | `0172832` |
| ~~B4~~ | ~~Regra: perecível exige prazo de durabilidade~~ | B3 | 3 | ✅ Concluída | 06/10/2026 | `a7d6512` |
| ~~B5~~ | ~~Tela de produtos~~ | A3 | 8 | ✅ Concluída | 07/10/2026 | `7f32893` |
| ~~B6~~ | ~~Tela de fornecedores~~ | A3 | 6 | ✅ Concluída | 07/10/2026 | `e6c031e` |
| ~~B7~~ | ~~Ligar as telas à API e tratar os erros na tela~~ | B2, B3, B5, B6 | 5 | ✅ Concluída | 08/10/2026 | `71a8811` |

## Bloco C — Entrada de mercadoria · 40 h  ·  40 de 40 h concluídas ✅

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~C1~~ | ~~Criar as tabelas de lote e movimentação~~ | A2 | 6 | ✅ Concluída | 06/10/2026 | `251d78d` |
| ~~C2~~ | ~~API de entrada de lote~~ | C1, B3 | 8 | ✅ Concluída | 07/10/2026 | `92bf7de` |
| ~~C3~~ | ~~Regra: validade obrigatória e cálculo automático~~ | C2 | 4 | ✅ Concluída | 07/10/2026 | `43dc95d` |
| ~~C4~~ | ~~Saldo derivado das movimentações~~ | C1 | 6 | ✅ Concluída | 06/10/2026 | `48451c5` |
| ~~C5~~ | ~~Tela de entrada de mercadoria~~ | A3 | 10 | ✅ Concluída | 08/10/2026 | `30e51b1` |
| ~~C6~~ | ~~Integração e teste do fluxo completo~~ | C2, C5 | 6 | ✅ Concluída | 08/10/2026 | `defb4a9` |

## Bloco D — Perdas e avarias · 18 h  ·  18 de 18 h concluídas ✅

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~D1~~ | ~~API de registro de perda, com motivo obrigatório~~ | C1 | 6 | ✅ Concluída | 07/10/2026 | `18285b3` |
| ~~D2~~ | ~~Regra: perda não entra na base de consumo~~ | D1 | 3 | ✅ Concluída | 07/10/2026 | `83dbc5f` |
| ~~D3~~ | ~~Tela de avarias e quebras~~ | A3 | 7 | ✅ Concluída | 08/10/2026 | `c8c4252` |
| ~~D4~~ | ~~Integração e teste~~ | D1, D3 | 2 | ✅ Concluída | 08/10/2026 | `9fe0d21` |

## Bloco E — Entrada das vendas · 44 h ⚠️ depende da decisão D01  ·  0 de 44 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| E1 | Levantar o formato do arquivo exportado pelo caixa | **confirmação com o cliente** | 6 | ⛔ Aguarda D01 | — | — |
| E2 | Criar as tabelas de venda, item de venda e importação | A2 | 6 | ⬜ A fazer | — | — |
| E3 | Serviço que lê o arquivo e gera venda e movimentação | E1, E2 | 16 | ⛔ Aguarda D01 | — | — |
| E4 | Casar o produto do caixa com o produto cadastrado | E3 | 10 | ⛔ Aguarda D01 | — | — |
| E5 | Tela de acompanhamento da importação | E3 | 6 | ⛔ Aguarda D01 | — | — |

## Bloco F — Consulta de estoque · 22 h  ·  22 de 22 h concluídas ✅

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~F1~~ | ~~Visão de estoque por produto e por lote~~ | C4 | 6 | ✅ Concluída | 07/10/2026 | `01b84a8` |
| ~~F2~~ | ~~API de consulta com filtros~~ | F1 | 6 | ✅ Concluída | 07/10/2026 | `2365139` |
| ~~F3~~ | ~~Tela de estoque, com destaque para mínimo e vencidos~~ | A3 | 10 | ✅ Concluída | 08/10/2026 | `6a6321e` |

## Bloco G — Previsão · 40 h ⚠️ depende da decisão D01  ·  0 de 40 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| G1 | Tabela de consumo diário e rotina de agregação | E2 | 10 | ⛔ Aguarda D01 | — | — |
| G2 | Cálculo do consumo médio e por dia da semana | G1 | 12 | ⛔ Aguarda D01 | — | — |
| G3 | Tabela de previsão e gravação do resultado | G2 | 8 | ⛔ Aguarda D01 | — | — |
| G4 | Regra: histórico mínimo antes de projetar | G2 | 4 | ⛔ Aguarda D01 | — | — |
| G5 | Agendador das rotinas diárias | G3 | 6 | ⛔ Aguarda D01 | — | — |

## Bloco H — Avisos · 52 h ⚠️ depende da decisão D01  ·  42 de 52 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| ~~H1~~ | ~~Tabela de aviso e controle de estado~~ | A2 | 8 | ✅ Concluída | 08/10/2026 | `eae1d23` |
| ~~H2~~ | ~~Gerador do aviso de validade~~ | H1, C3 | 8 | ✅ Concluída | 08/10/2026 | `a3627f3` |
| H3 | Gerador do aviso de ruptura | H1, G3 | 10 | ⛔ Aguarda D01 | — | — |
| ~~H4~~ | ~~Janela de silêncio e agrupamento~~ | H1 | 8 | ✅ Concluída | 08/10/2026 | `5a7be53` |
| ~~H5~~ | ~~Integração com o serviço de mensagens~~ | H1 | 10 | ✅ Concluída | 08/10/2026 | `075a5de` |
| ~~H6~~ | ~~Vincular o celular do dono ao usuário~~ | H5, B1 | 4 | ✅ Concluída | 09/10/2026 | `094a2ee` |
| ~~H7~~ | ~~Receber e registrar a resposta dele~~ | H5 | 4 | ✅ Concluída | 09/10/2026 | `606e94f` |

## Bloco I — Fechamento e relatórios · 30 h  ·  0 de 30 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| I1 | Tabela de fechamento e cálculo da diferença | E2 | 8 | ⬜ A fazer | — | — |
| I2 | Tela de fechamento de caixa | A3 | 10 | ⬜ A fazer | — | — |
| I3 | Relatório de balanço semanal | E2, D1 | 12 | ⬜ A fazer | — | — |

## Bloco J — Qualidade e implantação · 46 h  ·  0 de 46 h concluídas

| ID | TAREFA | DEPENDE DE | H | SITUAÇÃO | CONCLUÍDA EM | COMMIT |
|---|---|---|---|---|---|---|
| J1 | Testes automatizados de todas as regras | todas as regras | 16 | ⬜ A fazer | — | — |
| J2 | Carga inicial dos produtos, junto com o cliente | B3 | 8 | ⬜ A fazer | — | — |
| J3 | Inventário de partida: contagem física | J2 | 6 | ⬜ A fazer | — | — |
| J4 | Teste em movimento real, num sábado cheio | todos | 6 | ⬜ A fazer | — | — |
| J5 | Treinamento das três pessoas | J4 | 4 | ⬜ A fazer | — | — |
| J6 | Implantação e acompanhamento da primeira semana | J4 | 6 | ⛔ Aguarda D05 | — | — |

---

## Diário

O que foi feito em cada dia, do mais recente para o mais antigo. Cada linha aponta a tarefa do
cronograma, a regra de negócio (quando houver) e o commit.

### 09/10/2026

- **H6 — Vincular o celular do dono ao usuário.** O sistema já sabe **para qual celular** mandar os
  avisos do Sr. João. O Telegram não deixa mandar mensagem pelo número de telefone — só para quem
  já conversou com o bot —, então a ligação é feita uma vez, na instalação, como a criação dos
  usuários: a equipe roda `vincular_telegram --login joao`, o sistema mostra um **código de 6
  números** (vale 5 minutos) e um link; o Sr. João abre o link no celular e toca em "Iniciar"; o
  sistema reconhece o código, guarda o celular dele e responde no Telegram: "Pronto, Sr. João! Os
  avisos do mercado vão chegar aqui". Trocou de celular, é só repetir.
  **Decisão do grupo:** comando com código (entre três opções: comando com código, número
  digitado à mão, ou pelo próprio bot depois da H7 — esta dependeria de o sistema estar publicado
  na internet, D05, ainda aberta). Sem tela nova e sem endereço novo na API.
  **Cuidados:** só o usuário **dono** pode ser ligado (o banco entregue diz "só o DONO recebe
  aviso"); só vale o código exato, numa conversa particular com o bot (mensagem de grupo ou com
  outro número é ignorada); o código é sorteado de forma imprevisível; se a confirmação não chegar
  ao celular, nada é gravado — assim o sistema nunca guarda um celular errado. Testado de ponta a
  ponta: liga o celular e, em seguida, o aviso de validade chega naquele mesmo chat.
  **Foi provado que os testes pegam erro:** sete defeitos de propósito; seis pegos de primeira (um
  deles — aceitar "1482913" no lugar de "482913" — só depois de um teste novo); o sétimo mostrou
  um trecho de código que não servia para nada, e ele foi retirado. 24 testes automáticos — total
  do projeto: 623, todos passando.
  **Para o aviso chegar de verdade falta só:** criar o bot no @BotFather e pôr o token no `.env`;
  depois, rodar o comando com o Sr. João do lado, com o celular na mão.

- **Análise das telas no celular (a pedido do grupo, fora do cronograma).** Conferidas as 6 telas
  em celular pequeno (360 px), médio (390 px) e tablet (768 px). **Bom:** nenhuma tela "escapa"
  para o lado, Login e formulários funcionam bem, letra dos campos no tamanho que evita o zoom
  automático do iPhone, nenhum botão abaixo do mínimo da norma de acessibilidade. **Ruim:** as
  tabelas — na Consulta de estoque, no celular só aparece o nome do produto (quantidade, validade
  e "Ver lotes" ficam escondidos à direita); o "Editar" de Produtos e Fornecedores também; o
  cabeçalho ocupa duas linhas. **Proposta:** no celular, cada linha de tabela vira um cartão, sem
  mudar dado, regra ou API. **Situação:** aguardando o grupo pedir a correção. Observação: a
  especificação pensa o painel para o computador da loja (R04); o celular é do Sr. João, pelo
  Telegram — por isso é melhoria, não requisito.

- **H7 — Receber e registrar a resposta dele.** Fecha a parte de avisos que não depende do caixa.
  Agora cada aviso de "vai acabar" chega no Telegram com um botão **"Sim, pedir: Frango
  resfriado"**; quando o Sr. João toca, o sistema anota no aviso que ele quer pedir e mostra
  "Anotado: pedir Frango resfriado". Vários avisos continuam numa mensagem só (RN13), cada um com
  o seu botão. Aviso de validade vai sem botão: o que se faz com ele é registrar a perda no painel.
  **Decisões do grupo:** (1) o Telegram entrega a resposta chamando um endereço do sistema
  (*webhook*), como está na Apostila IV; (2) só o botão "Sim, pedir", que é o que a especificação
  cita. **Segurança:** esse endereço é o único, além do login, que não pede usuário e senha —
  quem chama é o Telegram. Por isso ele exige uma senha combinada com o Telegram (sem ela, recusa
  tudo, até quem está logado no painel) e só aceita a resposta vinda do celular do dono que
  recebeu aquele aviso; clicar de novo não muda nada; aviso que já não vale (cancelado porque a
  mercadoria chegou) responde "Este aviso não vale mais". A exceção à regra de que toda parte do
  sistema pertence a uma tela foi aprovada pelo grupo e anotada nas regras do repositório.
  **Para funcionar de verdade** falta publicar o sistema na internet com endereço seguro (decisão
  D05) e rodar `configurar_webhook`. Os avisos de "vai acabar" em si vêm da H3, que espera o
  formato do arquivo do caixa (D01) — até lá, testado com avisos criados nos testes.
  **Foi provado que os testes pegam erro:** dez defeitos de propósito, todos pegos — dois deles
  só depois de dois testes novos (pessoa que não é dono com celular ligado; botão com número a
  mais no fim). 39 testes automáticos — total do projeto: 662, todos passando.
  **Pendência que voltou:** em 2 de 5 rodadas completas, um teste de tela (cada vez um diferente,
  de telas que a H7 não toca) falhou por demora; sozinhos, passam sempre. É a mesma falha
  intermitente registrada em 08/10, que continua sem causa encontrada e entra na J1.

**Bloco H:** feitas H1, H2, H4, H5, H6 e H7; falta só a H3, que espera a decisão D01.

**Próxima tarefa:** I2 — tela de fechamento de caixa (não depende de decisão pendente). A correção
das telas no celular fica à espera do grupo.

### 08/10/2026

**Tarefas concluídas: B7, C5, C6, D3, D4, F3, H1 e H2** (56 h estimadas). **Os blocos B, C, D e F estão completos.**

- **B7 — Ligar as telas à API e tratar os erros na tela (inclui a tela de Login, L22).** As telas
  de Produtos e Fornecedores deixaram de usar dados de exemplo: agora leem e gravam no sistema de
  verdade. Para isso nasceu a **tela de Login** — a pessoa entra com login e senha, e o menu
  aparece conforme o seu perfil (RN14): o sobrinho vê Produtos e Fornecedores; a esposa e o
  Sr. João, cujas telas ainda vão ser feitas, veem a lista das telas do seu perfil. A entrada vale
  só enquanto a aba estiver aberta (o computador da loja é compartilhado) e há botão "Sair". Se a
  senha estiver errada, a tela não diz se o erro foi no login ou na senha — dizer ajudaria quem
  tenta adivinhar. O gerenciador de senha e o "colar" funcionam, como pede a norma de
  acessibilidade. Se o perfil não tem acesso a uma tela, ela nem abre (e a API também recusaria).
  **Os erros agora aparecem na tela, em português da loja:** "Sem conexão com o sistema. Confira se
  o computador está na rede e tente de novo."; sessão vencida leva de volta ao Login e, depois de
  entrar, à tela onde a pessoa estava; lista que não carregou diz o porquê e oferece "Tentar de
  novo" — nunca aparece vazia, o que daria a entender que não há nada cadastrado. A frase técnica
  anotada na B6 ("Este campo pode não estar em branco.") virou "Preencha o nome do fornecedor."
  **Decisão L25 — painel e sistema no mesmo endereço:** o navegador bloqueia uma página que fala com
  outro endereço. Em vez de liberar esse bloqueio (o que exigiria uma dependência que o grupo não
  aprovou), o painel e o sistema ficam atrás do mesmo endereço, que é o arranjo usual. Na máquina
  do grupo, um script de 140 linhas, só com o Python, faz esse papel; na publicação (D05), o
  servidor web.
  **Dois problemas que só apareceram ao ligar as telas no sistema de verdade:** (1) a busca "acha
  'feijão' digitando 'feijao'", prometida na B5, funcionava só com os dados de exemplo — o sistema
  diferenciava acento. Corrigido na busca de produtos e na da consulta de estoque, que a tela F3 vai
  usar, sem mexer no banco. (2) Ao digitar o prazo de entrega e clicar direto em "Salvar", o
  clique se perdia: a mensagem de erro do campo sumia nesse instante, o formulário encolhia e o
  botão saía de baixo do mouse. Agora a mensagem some enquanto a pessoa corrige o campo.
  **Limitação conhecida:** se a entrada vencer (12 h) no meio de um cadastro, a pessoa volta ao
  Login e perde o que estava digitando.
  31 testes automáticos — total do projeto: 416, todos passando. Testada num navegador de verdade,
  falando com o sistema, no tamanho do computador da loja e no de um celular: 126 verificações
  (entrar, errar a senha, cadastrar, editar, regra RN03, nome repetido, sem conexão, erro do
  sistema, sessão vencida, sair, perfil sem acesso) e auditoria de acessibilidade (WCAG 2.2, nível
  AA) sem nenhuma falha. As capturas de tela pegaram o cabeçalho ocupando três linhas e o botão
  "Sair" sem borda; os dois foram corrigidos.

**Bloco B completo (B1 a B7):** cadastro de produtos e fornecedores pronto de ponta a ponta — banco,
API, regras e telas ligadas ao sistema.

- **C5 — Tela de entrada de mercadoria (RF03, fluxograma 02).** O sobrinho já registra, na tela,
  cada carga que chega: procura o produto (digitando "frango" ou "feijao", sem precisar de acento),
  informa a quantidade — em quilo fracionado, como a carne —, o custo da nota, a validade e o
  fornecedor. A tela mostra se o produto é perecível e quanto tempo dura, e explica a regra RN04 em
  palavras da loja: "Se deixar em branco, o sistema conta 4 dias a partir de hoje". Quem calcula e
  quem recusa validade vencida é o sistema (a API da C2/C3), nunca a tela; depois de registrar, a
  tela confirma "Entrada registrada: 12,5 KG de Frango resfriado 1 kg. Agora tem 25 KG em estoque.
  Validade calculada: 12/10/2026." Como uma carga traz vários produtos do mesmo fornecedor, ele
  **continua escolhido** para o próximo produto, e o fornecedor de costume do produto já vem
  preenchido. Embaixo, as **entradas de hoje** (operação 02, passo 11); errou, a correção é por
  Avarias e quebras, para o estoque guardar o histórico (RN01). A data de entrada não aparece na
  tela: é sempre o dia da loja, decidido pelo sistema.
  **Decisão de ordem:** a tela já nasceu ligada ao sistema, e não com dados de exemplo como B5 e
  B6 — a API (C2) e a ligação (B7) já existiam, e refazer seria retrabalho. A C6 continua sendo o
  teste do fluxo completo, pela tela.
  **Dois achados das verificações, corrigidos:** o aviso flutuante de "registrado" cobria os campos
  (no celular, por 6 segundos) — virou uma confirmação fixa no topo do formulário, que fica até o
  próximo registro; e no celular a lista do dia, que rola de lado, não podia ser rolada só pelo
  teclado (norma WCAG 2.1.1).
  9 testes automáticos — total do projeto: 425, todos passando. Testada num navegador de verdade,
  falando com o sistema, no tamanho do computador da loja e no de um celular: 120 verificações
  (validade vencida recusada sem gravar nada, validade calculada, validade informada, não perecível
  sem validade, quantidade zero, custo com letras, sem conexão, outro perfil sem acesso) e
  auditoria de acessibilidade (WCAG 2.2, nível AA) sem nenhuma falha.

- **C6 — Integração e teste do fluxo completo da entrada de mercadoria.** O fluxo inteiro agora tem
  **teste automático de ponta a ponta**: um navegador de verdade, controlado pelo teste, abre a
  tela, digita como o sobrinho, clica em "Registrar entrada", e o teste confere o que apareceu na
  tela **e** o que ficou gravado no banco — o lote, a movimentação que explica o saldo (RN01),
  quem registrou e o saldo novo. Estão cobertas as **seis situações do fluxograma 02** (Apostila
  II): cada losango — "é perecível?", "a validade foi informada?", "a validade é anterior a hoje?"
  — pelo "sim" e pelo "não", como manda a Apostila IV. Mais: a lista do dia mostra o que entrou
  hoje e não o de ontem; o fornecedor fica escolhido para o resto da carga; recusa não grava nada e
  não apaga o que foi digitado; o caminho inteiro, do Login até a entrada registrada; e a esposa
  não consegue abrir a tela (RN14). **Foi provado que os testes pegam erro:** quatro defeitos
  introduzidos de propósito (a tela deixar de enviar a validade, a RN04 calcular um dia a menos, o
  fornecedor não ficar escolhido, a validade de hoje ser recusada) — cada um derrubou os testes
  certos, e o código voltou ao original.
  **Decisão do grupo:** entrou a ferramenta **Playwright** (`pytest-playwright`), só para os
  testes — ela não vai para o computador da loja. Até a C5, as verificações de tela eram feitas à
  parte e relatadas aqui; agora ficam guardadas no projeto e qualquer pessoa do grupo as roda com o
  `pytest`. Servem de base para as próximas telas (D4) e para a bateria final de testes (J1).
  Ajuste técnico registrado: com o navegador aberto, o Django passava a guardar a conexão com o
  banco num lugar diferente e o banco de teste não podia ser apagado ao fim; resolvido rodando os
  testes de tela por último. 14 testes de tela — total do projeto: 439, todos passando.

**Bloco C completo (C1 a C6):** a entrada de mercadoria funciona de ponta a ponta — banco, API,
regras de validade e saldo, tela e teste do fluxo inteiro.

- **D3 — Tela de avarias e quebras (RF04, fluxograma 03).** O caderno de avarias do sobrinho virou
  tela: ele procura o produto, diz quanto se perdeu e por quê — com botões "Venceu", "Quebrou" e
  "Estragou" para não precisar escrever —, e a perda sai do estoque. A tela mostra **os lotes do
  produto que estão na loja**, do que vence primeiro para o último, cada um com a situação em
  palavra e cor: "Vencido há 1 dia", "Vence em 2 dias", "Dentro da validade" (RN16). Se ele sabe
  qual lote estragou, escolhe; se não sabe, a opção já marcada deixa o sistema tirar pela ordem de
  validade, começando pelos vencidos (decisão L20). Depois de registrar: "Perda registrada: 4 UN de
  Iogurte natural (Estragou na geladeira). Agora tem 15 UN em estoque. Saiu de 2 lotes, pela ordem
  de validade." Embaixo, as perdas de hoje, com hora, lote, motivo e quem registrou. A perda não se
  apaga (RN01), e a tela avisa isso antes. Todas as regras continuam no sistema (API da D1): a tela
  não decide nada.
  **Achados:** (1) a frase de recusa do sistema dizia "Esse lote só tem 3,000 UN." — agora diz "3 UN",
  como a loja fala; (2) nos testes de tela, a tabela de parâmetros (o "3 dias" do aviso de
  validade) sumia depois do primeiro teste e a lista de lotes falhava — os testes agora a regravam;
  (3) ajustes de aparência vistos nas capturas de tela. As partes comuns às telas de Entrada e de
  Avarias (procurar produto, mostrar erros, confirmar) passaram a ser compartilhadas, e a tela de
  Entrada continua passando nos seus 14 testes de tela.
  15 testes automáticos (7 deles no navegador) — total do projeto: 454, todos passando. Conferida
  no tamanho do computador da loja e no de um celular: 42 verificações e auditoria de
  acessibilidade (WCAG 2.2, nível AA) sem nenhuma falha.

- **D4 — Integração e teste do fluxo de perdas.** Como a C6 fez com a entrada, o registro de perda
  agora tem **teste automático de ponta a ponta**: o navegador usa a tela de Avarias como o
  sobrinho, e o teste confere a tela e o que ficou gravado. Cada decisão do fluxograma 03 testada
  pelo "sim" e pelo "não": **tem motivo?** (sem motivo, ou só com espaços, nada é gravado);
  **escolheu o lote?** (se escolheu, sai só dele; se não, sai pela ordem de validade, o vencido
  primeiro, com uma linha no histórico para cada lote); **a quantidade cabe?** ("Esse lote só tem
  3 UN.", "Só há 19 UN de Iogurte natural no estoque."); **o lote está vencido?** (o iogurte vencido
  da Apostila I sai pela tela, como manda a RN16). E o que a perda não pode fazer: o exemplo da
  especificação — 6 kg de frango vendidos e 10 kg que foram fora: o saldo cai 16 kg e o consumo do
  dia continua 6 kg (RN11) —, e o saldo continua batendo com a soma dos lotes (RN01). Dono e esposa
  não registram perda (RN14). **Foi provado que os testes pegam erro:** quatro defeitos de
  propósito (a tela não enviar o lote escolhido, a ordem de validade pular os vencidos, o sistema
  aceitar motivo em branco, a perda ser contada como consumo) — cada um derrubou os testes certos.
  15 testes de tela — total do projeto: 469, todos passando.

**Bloco D completo (D1 a D4):** perdas e avarias de ponta a ponta — API com motivo obrigatório,
regra de que perda não é consumo, tela e teste do fluxo inteiro.

- **F3 — Tela de consulta de estoque (RF07, RN16).** A única tela que os três usam. No topo, três
  quadros dizem o que precisa de atenção — quantos produtos têm **lote vencido**, quantos estão
  **perto de vencer** e quantos estão **abaixo do mínimo** — e cada quadro, tocado, mostra só aqueles
  produtos. Embaixo, o saldo de cada produto **agrupado por categoria**, com o mínimo, a próxima
  validade e as marcações em palavra e cor ("1 lote vencido", "Perto de vencer", "Abaixo do
  mínimo", "Não pode faltar no fim de semana"). "Ver lotes" abre os lotes do produto, do que vence
  primeiro ao último, com a situação de cada um. Conferido o caso que mais importa: o carvão,
  cadastrado e nunca comprado (saldo zero), aparece como abaixo do mínimo. A tela só mostra — não
  grava nada (RN01), e um teste confere que usá-la não envia nenhuma gravação ao sistema. Todos os
  números vêm calculados pelo sistema (API da F2); para o computador antigo, a lista vem num pedido
  só e procurar e filtrar acontecem na própria tela. **Dono e esposa agora caem nesta tela ao
  entrar** — antes viam só a lista de telas em preparo.
  **Achados, corrigidos:** (1) o botão "Ver lotes" trocava o texto visível para "Esconder lotes",
  mas o leitor de tela continuava lendo "Ver lotes" (norma WCAG 2.5.3) — agora o texto fica e uma
  seta mostra se está aberto; (2) com cinco telas no menu do sobrinho, o cabeçalho quebrava
  desencontrado no computador da loja — o menu passou a ter uma linha própria, embaixo da marca e
  do nome da pessoa, o que também deixa lugar para a sexta tela (Importação de vendas).
  **Observações em aberto:** (a) no celular, a tabela rola de lado dentro do cartão, como nas
  outras telas, e o saldo fica fora da vista inicial; uma versão em "cartões" para telas estreitas
  seria melhor para a esposa consultar pelo celular — fica para o grupo decidir; (b) numa das
  execuções da bateria de testes, um teste deu erro e não se repetiu em 14 execuções seguidas; a
  causa não foi encontrada e o caso fica anotado para a J1.
  19 testes automáticos (16 deles no navegador) — total do projeto: 488, todos passando. Conferida
  com os três perfis, no tamanho do computador da loja e no de um celular: 49 verificações e
  auditoria de acessibilidade (WCAG 2.2, nível AA) sem nenhuma falha.

**Bloco F completo (F1 a F3)** e, com ele, **todas as telas da etapa 1**: Login, Produtos,
Fornecedores, Entrada de mercadoria, Avarias e quebras e Consulta de estoque. Da etapa 1 faltam a
publicação (A5, aguarda D05) e o bloco J (qualidade e implantação).

- **H1 — Tabela de aviso e controle de estado.** Primeira tarefa do bloco de avisos. O sistema já
  tem onde guardar cada aviso que vai para o celular do Sr. João — a tabela `alerta`, **igual à
  Apostila IV** (conferida coluna por coluna pelo teste automático) — e as regras de como um aviso
  muda de situação: nasce **pendente**; se for gerado na hora do movimento, fica **segurado** até a
  janela acabar (RN12); quando sai, todos os da mesma mensagem ficam **enviados** com a mesma hora
  (RN13); e pode ser **cancelado** antes de sair. Enviado e cancelado não mudam mais. Quando a
  mercadoria chega, o aviso de "vai acabar" daquele produto que ainda não saiu é cancelado
  sozinho (operação 02, passo 10) — o ponto de chamada já existia desde a C2 e agora age de
  verdade; aviso de validade e de outro produto não são tocados. As mudanças de situação são à
  prova de duas partes do sistema mexerem no mesmo aviso ao mesmo tempo (a rodada da madrugada e
  uma entrada de mercadoria): vale o que está gravado, e é tudo ou nada.
  **Decisão L11:** a urgência do aviso é **alta, média ou baixa** — a lista é conferida pelo sistema,
  sem mudar o banco entregue (como na L17). Os avisos saem nessa ordem e, empatando, o mais antigo
  primeiro (RN13). **Decisão de escopo:** nenhum endereço novo na API — nenhuma das 10 telas mostra
  avisos; eles só vão para o Telegram.
  **Achado:** a primeira versão do cancelamento automático quebraria toda entrada de mercadoria
  (pedia uma trava de banco fora de transação); foi refeita antes de qualquer teste passar.
  43 testes automáticos — total do projeto: 531, todos passando.

- **H2 — Gerador do aviso de validade (RN05).** O sistema já sabe, a cada rodada, **o que está para
  vencer** e grava o aviso para o Sr. João, com a frase da loja: "Presunto vence em 3 dias — 2,5 KG
  na prateleira.", "vence amanhã", "vence hoje". Testado com o exemplo da Apostila I: lote que vence
  em 24/09, prazo de 3 dias, gera aviso em 21/09; o que vence em 30/09, não. Só produto perecível,
  só lote com mercadoria, e o prazo vem da tabela de parâmetros — mudando para 5 dias, o sistema
  passa a avisar com 5 dias, sem mexer no código. O prazo já é lido produto a produto, para quando
  o grupo decidir a lacuna L01 (prazo por categoria). **Decisões do grupo nesta tarefa:**
  (1) o aviso se repete **todo dia** enquanto o lote estiver no prazo e com mercadoria — pela RN13,
  os do dia chegam juntos numa mensagem só, como a volta pelas gôndolas que o Sr. João faz de manhã;
  rodar duas vezes no mesmo dia não duplica; (2) o lote **já vencido também avisa**, com frase
  própria: "Iogurte natural venceu ontem — 3 UN na prateleira. Tire e registre a perda em Avarias e
  quebras." (RN16). **Decisões de implementação:** o aviso de um dia anterior que não chegou a sair é
  trocado pelo de hoje, com a contagem de dias certa; urgência **alta** para vencido e para o que
  vence hoje, **média** para o resto (L11); o aviso vai para o usuário DONO — sem dono cadastrado,
  ele é gravado mesmo assim e não se perde. **Foi provado que os testes pegam erro:** quatro defeitos
  de propósito (prazo errado por um dia, não perecível avisando, rodada dupla duplicando, aviso
  antigo não trocado) — todos pegos. 22 testes automáticos — total do projeto: 553, todos passando.
  **Falta para o aviso chegar ao celular:** a janela de silêncio e o agrupamento (H4), o envio pelo
  Telegram (H5) e ligar o celular do dono (H6). A rodada das 03h00 (G5) depende da decisão D01;
  até lá, o gerador pode ser chamado sozinho.

- **Redesenho visual do painel (fora do cronograma, a pedido do grupo).** As seis telas ganharam um
  visual mais profissional e fácil de ler, feito com a skill **UI UX Pro Max**: cabeçalho branco
  com o logotipo do mercado, menu com ícone e nome de cada tela (a tela atual destacada em verde),
  a inicial da pessoa num círculo, cartões e tabelas mais leves, marcações em "pílula" (vencido,
  perto de vencer, abaixo do mínimo), "Editar" com ícone de lápis, quadros do resumo da Consulta
  com ícone, e a tela de Login em duas partes, com a marca e o que o sistema faz. No celular, o menu
  vira uma fila que desliza para o lado. **Nada mudou no funcionamento**: mesmos campos, mensagens e
  regras. Conferido: contraste de cada cor calculado pela norma WCAG; auditoria de acessibilidade
  sem nenhuma falha nas 6 telas, no computador da loja e no celular; sem rolagem lateral.
  **Pendência registrada:** alguns testes de tela falham de vez em quando (uma tela que não termina
  de carregar dentro do tempo do teste). Já tinha acontecido uma vez na F3; nas rodadas desta
  sessão foram 4 de 36. Medido que o banco não está travado e descartada a hipótese do servidor de
  testes; a causa ainda não foi encontrada. Fica para investigar à parte (e entra na J1).

- **H4 — Janela de silêncio e agrupamento (RN12, RN13).** O sistema já sabe **quando** pode
  mandar aviso e **como** juntar tudo numa mensagem só. Nos horários de movimento (10h30 às 13h e
  16h30 às 18h, lidos da tabela de parâmetros, no horário da loja) nada é enviado: os avisos ficam
  **segurados** e saem na primeira rodada depois do pico. Fora disso, todos os avisos do Sr. João
  saem numa **única mensagem**, numerada do mais urgente para o menos urgente, e ficam marcados
  como enviados com a mesma hora. Testado com os exemplos da Apostila I: aviso das 11h15 fica
  retido e sai às 13h05; seis avisos às 13h05 viram uma mensagem com seis itens, não seis
  mensagens. **Decisões de implementação:** (1) a faixa inclui o começo e não o fim — às 10h30 já
  é silêncio, às 13h00 o aviso já pode sair ("entre 10h30 e 13h"); (2) se o envio falhar (sem
  internet), nada é marcado como enviado e a próxima rodada tenta de novo; (3) aviso sem
  destinatário (sem dono cadastrado) fica esperando, não some; (4) cada pessoa recebe só os seus
  avisos, uma mensagem por pessoa. O envio é feito por uma "porta" (`CanalDeAviso`, decisão D04):
  o Telegram de verdade entra na H5 sem mudar esta parte. **Foi provado que os testes pegam erro:**
  quatro defeitos de propósito (fim da janela incluído, relógio em UTC, ordem sem urgência, um
  envio por aviso) — todos pegos. 27 testes automáticos — total do projeto: 580, todos passando.

- **Projeto pronto para rodar em outro computador (fora do cronograma, a pedido do grupo).** O
  código foi para um repositório privado no GitHub (`MatheusLoureiro7/mercadinho`), com um passo a
  passo para Windows (`COMO-RODAR.md`): instalar, baixar, configurar, ligar e ver as tabelas do
  banco para a apresentação. Junto vai uma cópia dos dados de desenvolvimento (produtos, lotes,
  movimentações) que se carrega com um comando — testada num banco vazio. Os usuários vão **sem
  senha** (senha não vai para o GitHub); cada integrante define a sua no próprio computador.

- **H5 — Integração com o serviço de mensagens (Telegram).** O sistema já **manda a mensagem de
  verdade** para o Telegram. Um comando (`enviar_avisos`) faz a rodada inteira: respeita o horário
  de movimento (H4), junta os avisos de cada pessoa numa mensagem só e envia pelo bot. É esse
  comando que o agendador vai chamar (G5). Usa só o que já vem com o Python, sem programa novo.
  **O que acontece quando algo dá errado:** sem internet, bot sem configurar, celular da pessoa
  ainda não ligado ao sistema (H6) ou Telegram recusando — os avisos daquela pessoa **ficam
  guardados** para a próxima rodada, as outras pessoas recebem normalmente, e o comando termina
  avisando que houve falha, com o motivo no registro (log). **Segurança (RNF12):** a "senha" do
  bot (token) fica só no arquivo de configuração e nunca aparece em mensagem de erro nem no log —
  há um teste só para isso. **Decisões de implementação:** (1) a mensagem vai em texto simples,
  sem negrito, para que um símbolo no nome de um produto não faça o Telegram recusar; (2) se a
  lista de avisos passar do limite do Telegram (4096 letras), ela é dividida em mais de uma
  mensagem, sem cortar nenhuma linha e na mesma ordem — é o único caso em que a RN13 vira mais de
  uma mensagem, porque o Telegram não aceita maior. Testado contra um "Telegram de mentira" na
  própria máquina (a conversa pela internet é de verdade, só o endereço muda). **Foi provado que
  os testes pegam erro:** cinco defeitos de propósito, todos pegos — e um sexto (o token vazando
  pela exceção original) passou na primeira versão do teste, que foi reforçada até pegá-lo.
  19 testes automáticos — total do projeto: 599, todos passando.
  **Para o aviso chegar ao celular do Sr. João falta:** criar o bot no @BotFather e pôr o token
  no `.env`, e a H6 (ligar o celular dele ao usuário).

**Próxima tarefa:** H6 — vincular o celular do dono ao usuário (feita em 09/10).

### 07/10/2026

**Tarefas concluídas: C2, C3, D1, D2, F1, F2, B5 e B6** (47 h estimadas).

- **C2 — API de entrada de mercadoria (RF03, operação 02).** O sobrinho já registra, pela API,
  cada carga que chega: produto, quantidade, custo, fornecedor e validade. Como manda a operação 02
  da Apostila IV, o lote e a movimentação de entrada são gravados **juntos, numa transação só** — se
  qualquer parte falhar, nada fica gravado, e nunca existe lote sem a movimentação que explica o
  saldo (RN01); um teste simula a falha e prova isso. A resposta já traz o saldo novo do produto
  (passo 9), e a "lista do dia" mostra o que entrou hoje (passo 11). A data de entrada é sempre o
  dia da loja — inclusive à noite, quando o banco (que trabalha em UTC) já está "amanhã". Lote não
  pode ser editado nem apagado; correção de estoque é por perda ou ajuste, que deixam rastro.
  O passo 10 (cancelar o aviso de "vai acabar" quando a mercadoria chega) já é chamado, e passa a
  agir quando a tabela de avisos existir (tarefa H1). As regras de validade (RN04) são a próxima
  tarefa, C3. 27 testes automáticos — total do projeto: 267, todos passando.

- **C3 — Regra: validade obrigatória e cálculo automático (RN04).** Ao registrar a entrada de um
  perecível, a validade agora é garantida: se o sobrinho não informar, o sistema calcula sozinho
  somando a durabilidade do produto ao dia da entrada — o exemplo da própria Apostila I, frango que
  entra em 21/09 com 4 dias de durabilidade, é gravado com validade 25/09. Validade já vencida é
  recusada com "Essa validade já passou. Confira a data na embalagem.", e nesse caso nada é gravado.
  A regra segue a ordem exata da especificação, fica num módulo próprio (vale para qualquer caminho
  de entrada, não só a tela) e usa o "hoje" da loja, também à noite. **Leitura registrada:** o
  passo 1 da RN04 diz que o não perecível "segue" — então validade informada e já vencida é recusada
  também nele, como diz a frase da regra ("Validade anterior à data de hoje é recusada"). Com a C2,
  estão testadas as seis situações do fluxograma 02. 14 testes automáticos — total do projeto: 281,
  todos passando.

**Bloco C:** banco, API e regras completos (C1 a C4). Faltam a tela (C5) e a integração (C6).

- **D1 — API de registro de perda, com motivo obrigatório (RF04).** O caderno de avarias do
  sobrinho já tem a sua API: o que venceu, quebrou ou estragou sai do estoque **sempre com o
  motivo anotado** — sem motivo, é recusado. Cada perda baixa o saldo e a quantidade do lote,
  numa transação só (RN01), e fica registrada como PERDA, separada das vendas (RN11). Não dá para
  registrar perda maior do que o que existe. O lote vencido sai por aqui, como manda a RN16 — o
  exemplo da Apostila I, iogurte vencido em 20/09 e retirado em 21/09 com motivo, está testado.
  **Decisão L20:** se o sobrinho informa o lote que estragou, a perda sai dele; se não informa,
  sai pela ordem de validade (RN02), começando pelos vencidos. **Decisão L13:** desempate da ordem
  de validade — mesma validade, sai antes o que entrou antes; sem validade, sai por último. Essa
  ordem já fica pronta para a baixa por venda (E3), que deixa os vencidos de fora. 31 testes
  automáticos — total do projeto: 312, todos passando.

- **D2 — Regra: perda não entra na base de consumo (RN11).** A regra que o roteiro chama de "uma
  das mais críticas do sistema": se a perda contasse como consumo, quanto mais produto estragasse,
  mais o sistema mandaria comprar. Agora existe **um único lugar** no sistema que responde "quanto
  se vendeu", e ele conta só vendas — perdas, entradas e ajustes ficam de fora. É dele que a
  previsão (bloco G) vai ler, e um teste automático impede que alguém do grupo calcule consumo por
  fora. Testado com o exemplo da Apostila I: 10 kg de frango vão fora, o saldo cai 10 kg, o consumo
  do dia continua sendo só o vendido. A conta é feita pelo dia da loja — a venda das 22h30 não vira
  "dia seguinte". Foi provado que os testes pegam o erro: colocando a perda na conta, 5 testes
  falham. 15 testes automáticos — total do projeto: 327, todos passando.

**Bloco D:** banco, API e regra completos (D1 e D2). Faltam a tela (D3) e a integração (D4).

- **F1 — Visão de estoque por produto e por lote (RF07, RN16).** O sistema já sabe montar a
  "foto" do estoque que a tela de consulta vai mostrar: por produto — saldo, categoria, se está
  **abaixo do mínimo**, quantos lotes estão **vencidos** e **vencendo** e a validade mais próxima —
  e por lote — quanto resta, quantos dias faltam para vencer e a situação (vencido, vencendo, dentro
  da validade, sem validade). Testado com os exemplos da Apostila I: o iogurte vencido em 20/09
  aparece destacado em 21/09 (RN16); o lote que vence em 24/09 aparece como "vencendo" em 21/09,
  com o parâmetro de 3 dias (RN05). E foi conferido que a soma do que resta nos lotes bate com o
  saldo depois de entradas e perdas. A visão é feita com consultas sobre o que já existe — nenhum
  objeto novo foi criado no banco, que na apostila só tem a visão de saldo.
  **Decisão L21:** a tabela de parâmetros (o "3 dias" do aviso, os "14 dias" de histórico etc.)
  está no modelo de dados mas não estava em nenhuma tarefa do cronograma; foi criada aqui, igual à
  apostila, com os 7 valores iniciais. 25 testes automáticos — total do projeto: 352, todos
  passando.

- **F2 — API de consulta de estoque com filtros (RF07).** A consulta de estoque — a única tela que
  os três (dono, esposa e sobrinho) usam — já tem a sua API: saldo por produto e por lote, agrupado
  por categoria, com filtros "só o que está abaixo do mínimo", "só o que está vencendo ou vencido",
  por categoria, por produto e por nome. O lote vencido aparece destacado (RN16) e ninguém consegue
  gravar nada por ela (RN01). Pensando no computador antigo da loja (RNF06), um teste garante que a
  consulta faz no máximo 4 idas ao banco, tenha a loja 50 ou 2.000 produtos. 33 testes automáticos —
  total do projeto: 385, todos passando.

**Marco: metade da etapa 1.** Toda a parte de banco, API e regras da etapa 1 que não depende de
decisão do cliente está pronta. Faltam as telas (B5–B7, C5–C6, D3–D4, F3), a publicação (A5,
aguarda D05) e o bloco J.

- **B5 — Tela de produtos (primeira tela do painel).** Feita com a skill de design **UI UX Pro
  Max**, que gerou o sistema visual do painel inteiro (estilo limpo e funcional, cinza-ardósia com
  verde de estoque). Cada sugestão da ferramenta foi conferida contra a especificação e adaptada
  quando necessário: fonte do próprio computador, para não baixar nada da internet (computador
  antigo, RNF06), e um verde mais escuro, porque o sugerido não tinha contraste suficiente com texto
  branco — conferido por cálculo, pela norma de acessibilidade WCAG. A tela lista os produtos com
  busca (acha "feijão" digitando "feijao") e filtro por categoria, e cadastra e edita com tudo o que
  o RF01 pede, em português da loja ("Não pode faltar no fim de semana"). Quando algo é recusado,
  **nada do que foi digitado se perde** e só o campo com problema é apontado (fluxograma 01). Como
  manda o roteiro, nesta tarefa a tela usa dados de exemplo; a ligação com a API é a B7. A tela foi
  testada num navegador de verdade, no tamanho do computador da loja e no de um celular: 38
  verificações automáticas (teclado, foco, tamanho dos botões, contraste, nada cortado). As capturas
  de tela pegaram um problema que o teste não pegou — no computador da loja o botão "Editar" ficava
  fora da tela — e ele foi corrigido.
  **Lacunas novas:** L22 — a tela de Login não tem tarefa no cronograma; será feita na B7. L23 — a
  Apostila IV promete o aviso de vencimento no celular já na etapa 1, mas as horas dele estão no
  bloco H (etapa 2); o grupo precisa corrigir uma das duas coisas.

- **B6 — Tela de fornecedores (RF02).** Segunda tela do painel, no mesmo visual da tela de produtos
  e sem nenhum estilo novo. O sobrinho cadastra e edita quem entrega a mercadoria: nome, contato,
  pedido mínimo e — o que mais importa — **em quantos dias o fornecedor entrega depois do pedido**.
  A tela explica por que esse número importa, em palavras da loja: é com ele que o sistema avisa a
  tempo de o fornecedor entregar antes de o produto acabar (RN08). Na lista o prazo aparece como
  "1 dia", "3 dias" ou "No mesmo dia". Fornecedor não tem botão de excluir, porque é cadastro de
  origem e nunca é apagado (L18). Quando algo é recusado, nada do que foi digitado se perde. As
  mensagens de recusa da tela são as mesmas da API, conferidas rodando a própria API. Ainda usa
  dados de exemplo, e a ligação com a API é a B7. Testada num navegador de verdade, no tamanho do
  computador da loja e no de um celular: 47 verificações automáticas, mais a auditoria de
  acessibilidade (norma WCAG 2.2, nível AA) sem nenhuma falha. A tela de produtos continua passando
  nas 38 dela.
  **Lacuna nova:** L24 — a apostila não diz se o pedido mínimo é em reais ou em quantidade. Adotamos
  reais, pela convenção do próprio modelo de dados, e o grupo precisa confirmar.
  **Anotado para a B7:** quando o nome fica em branco, a mensagem padrão da API é "Este campo pode
  não estar em branco.", uma tradução ruim do Django REST Framework. Ela deve ser trocada por uma
  frase clara ao ligar as telas à API.

**Bloco B:** banco, API e as duas telas prontos (B1 a B6). Falta ligar as telas à API (B7).

**Próxima tarefa:** B7 — ligar as telas à API e tratar os erros na tela (inclui a tela de Login, L22).

### 06/10/2026

**Tarefas concluídas: A1, A2, A3, B1, A4, B2, B3, B4, C1 e C4** (73 h estimadas).

- **A1 — Repositório, ambiente e padrão de código.** Repositório git criado, com a especificação
  (Apostilas I a IV) no primeiro commit. Projeto Django com os sete módulos do sistema
  (`comum`, `cadastro`, `estoque`, `vendas`, `previsao`, `alertas`, `caixa`) e a pasta do painel
  web estático. Padrão de código com Ruff, testes com pytest e README com o passo a passo para
  Windows, Linux e macOS. 5 testes automáticos.
- **A2 — Banco de dados e ferramenta de migração.** PostgreSQL 17 rodando em Docker, aceitando
  conexão só da própria máquina (RNF12), no fuso de São Paulo. Migrações do Django funcionando.
  3 testes automáticos — total do projeto: 8, todos passando.
- **Leitura crítica da especificação.** Oito lacunas novas registradas em `docs/LACUNAS.md`
  (L09 a L16) — pontos que as apostilas não definem e que o grupo precisa decidir. Nenhuma foi
  resolvida por conta própria no código.
- **Decisão da L09** (autenticação × tabela `usuario`): opção (c) — a autenticação do Django
  usa a tabela `usuario` exatamente como está na Apostila IV, sem nenhuma coluna a mais.
- **OpenSpec.** A especificação foi passada também para o formato OpenSpec (`openspec/specs/`):
  10 capacidades, cada requisito apontando a regra de origem e usando os exemplos das apostilas.

- **A3 — Esqueleto da API.** A API REST — a "porta única de entrada" da Apostila IV — está de
  pé em `/api/`, respondendo sempre em JSON. Toda recusa volta no mesmo formato, com a mensagem
  em português no vocabulário da loja (RNF10) e apontando só o campo com problema, como pede o
  fluxograma 01. As regras de negócio têm um jeito padrão de recusar uma operação, informando
  qual regra recusou (ex.: RN03). Erro inesperado não mostra detalhe técnico na tela: mostra um
  código, e o detalhe vai para o log com o mesmo código. Toda requisição é registrada em log,
  sem nunca gravar senha (RNF12). 15 testes automáticos — total do projeto: 23, todos passando.

- **Skills de apoio.** Instaladas no projeto 13 skills (guias de boas práticas para o assistente
  de programação) de Django, PostgreSQL, testes, Telegram e acessibilidade. O `CLAUDE.md` registra
  qual usar em cada tarefa e, principalmente, o que **não** seguir delas: onde um exemplo contraria
  a especificação (banco de testes, modelo de usuário, tipos do `schema.sql`), vale a especificação.
- **B1 — Tabelas de usuário, categoria, produto e fornecedor.** As quatro primeiras tabelas da
  Apostila IV existem no banco, criadas por migração. Um teste automático compara o banco com o
  modelo de dados entregue, coluna por coluna (nome, tipo, tamanho, obrigatoriedade, valor
  padrão) — se alguém acrescentar uma coluna fora da apostila, o teste quebra (foi provado
  criando de propósito uma coluna `saldo`, proibida pela RN01). O banco já recusa sozinho:
  produto perecível sem prazo de durabilidade (RN03), produto com nome repetido na mesma
  categoria (fluxograma 01), fornecedor sem prazo de entrega e usuário com perfil diferente de
  DONO, GESTAO e OPERACAO (RN14). A senha é gravada só como hash (RNF12). O login usa a tabela
  `usuario` exatamente como na apostila (decisão da L09). 36 testes automáticos — total do
  projeto: 59, todos passando.
- **Lacuna nova: L17** — a apostila não diz se a unidade de medida é uma lista fechada
  (KG, UN, L, PCT). Fica para o grupo decidir antes da B3.

- **A4 — Autenticação e os três perfis de acesso (RN14).** A tela de Login já tem a sua API: a
  pessoa entra com login e senha e recebe uma chave de acesso que vale por um dia de loja (12 h) —
  e deixa de valer na hora se a senha for trocada ou o usuário desativado. Junto, recebe o menu do
  seu perfil, como pede a Apostila II. A tabela de acesso da RN14 está no código exatamente como na
  especificação, e um teste confere todas as 24 combinações (8 telas × 3 perfis). A recusa
  acontece antes de qualquer gravação no banco (Apostila IV, operação 01, passo 3), e uma parte do
  sistema que esqueça de dizer a que tela pertence fica fechada para todos. Contra adivinhação de
  senha, no máximo 10 tentativas por minuto (RNF12) — e um teste prova que não dá para burlar o
  limite fingindo outro endereço. Os três usuários são criados pela equipe com um comando no
  terminal (decisão parcial da L14). 50 testes automáticos — total do projeto: 109, todos
  passando.

**Bloco A:** só falta a A5 (esteira de publicação), que aguarda a decisão D05 — onde o sistema vai
rodar.

- **B2 — API de categoria e fornecedor.** O sobrinho já pode, pela API, cadastrar e corrigir
  fornecedores com o prazo de entrega — obrigatório, porque é o número que faz o aviso de "vai
  acabar" sair a tempo (RF02, RN08) — e as categorias da loja ("Secos e molhados", "Açougue",
  "Frios"). Nada é apagado: categoria e fornecedor são registros de origem, que a Apostila IV
  manda nunca apagar. Os outros dois perfis não mexem em fornecedor (RN14).
  **Decisão L18:** a categoria não tem tela própria entre as 10; ler as categorias ficou com a
  Consulta de estoque (os três perfis, que veem o saldo por categoria) e cadastrar ficou com a tela
  de Produtos (só o sobrinho). Nenhuma tela nova foi criada. 32 testes automáticos — total do
  projeto: 141, todos passando.

- **B3 — API de produto, com validações.** O sobrinho já pode, pela API, cadastrar e corrigir os
  produtos com tudo o que o RF01 pede — nome, categoria, unidade, se é perecível e quantos dias
  dura, preços, estoque mínimo — e marcar os que não podem faltar no fim de semana (RF15). Segue a
  operação 01 da Apostila IV: aponta só o campo que falta e recusa produto com nome repetido na
  mesma categoria, inclusive ao editar. O produto não tem saldo (RN01) e não pode ser apagado.
  Busca por nome e filtro por categoria, para a tela de Produtos dar conta de até 2.000 itens.
  **Decisão L17:** unidade de medida em lista fechada — KG, UN, L ou PCT. **Decisão L19:** produto
  cadastrado sem dizer se é perecível herda o padrão da categoria (ex.: tudo do Açougue já nasce
  perecível). 33 testes automáticos — total do projeto: 174, todos passando.

- **B4 — Regra: perecível exige prazo de durabilidade (RN03).** Produto perecível sem a
  durabilidade em dias — ou com zero — é recusado antes de gravar, com a mensagem "Produto
  perecível precisa do prazo de durabilidade em dias. Sem ele o sistema não consegue avisar quando
  o produto vai vencer." A resposta aponta só esse campo, para a tela manter o resto do que foi
  digitado (fluxograma 01). A regra vale também ao editar (marcar como perecível, apagar a
  durabilidade) e para o produto que herdou o "perecível" da categoria. Testado com o exemplo da
  própria Apostila I: "Frango resfriado 1 kg" sem durabilidade é recusado; com 4 dias, é salvo.
  A regra fica num módulo próprio, não na tela, como manda a Apostila IV. 22 testes automáticos —
  total do projeto: 196, todos passando.

**Bloco B:** a parte de banco e API está completa (B1 a B4). Faltam as telas — B5, B6 e B7.

- **C1 — Tabelas de lote e movimentação.** As duas tabelas que sustentam o estoque existem no banco,
  iguais à Apostila IV — conferidas automaticamente, coluna por coluna, contra o modelo de dados
  entregue. O teste pegou uma diferença sutil e ela foi corrigida: o horário padrão da
  movimentação agora é o `NOW()` da apostila (o horário da transação), para que um lote e a
  movimentação que o explica fiquem com a mesma hora. O banco já recusa sozinho: lote com
  quantidade negativa, movimentação de tipo desconhecido, quantidade zero ou negativa, e perda sem
  motivo. O índice que acelera a saída pela validade mais próxima (RN02) está criado. Produto ou
  lote que já tem movimentação não pode ser apagado — o histórico do estoque fica intacto (RN01).
  Ficou registrado um cuidado para as próximas tarefas: o "hoje" do sistema é sempre o horário de
  São Paulo, nunca o do banco (que trabalha em UTC). 28 testes automáticos — total do projeto: 224,
  todos passando.

- **C4 — Saldo derivado das movimentações (RN01).** "A tarefa mais importante do projeto inteiro",
  segundo o roteiro. O saldo de cada produto nunca é um número guardado: é sempre a soma das
  movimentações — entradas e ajustes somam, vendas e perdas subtraem —, calculada pela visão
  `vw_estoque_atual` **copiada literalmente** do modelo de dados da Apostila IV. Um teste prova que
  a visão do sistema é idêntica à da apostila (e que uma alteração, como trocar o sinal do ajuste,
  seria pega). Testado com o exemplo da própria Apostila I: entram 40 kg, vendem-se 12 kg, perdem-se
  3 kg → saldo de 25 kg, com as três linhas no histórico. Ninguém consegue gravar um saldo — nem o
  sistema, nem direto no banco. Quilo fracionado sem erro de arredondamento. 16 testes automáticos —
  total do projeto: 240, todos passando.

**Próxima tarefa:** C2 — API de entrada de lote.

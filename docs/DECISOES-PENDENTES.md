# Decisões pendentes

Transcrição do **Apêndice A da Apostila IV**, com o que cada uma significa na prática para quem
está programando.

| # | Decisão | Situação | O que trava |
|---|---|---|---|
| D01 | De onde vêm os dados de venda | ✅ Decidida em 30/10: **Excel** | Blocos E, G e H · 136 h |
| D02 | Como o sistema fica sabendo da validade | **Bloqueante** | Parte do bloco C e todo o aviso de validade |
| D03 | Tamanho da primeira entrega | Aberta | Define ordem, não bloqueia |
| D04 | Por onde o aviso chega ao dono | Aberta | Bloco H · 52 h |
| D05 | Onde o sistema vai rodar | ✅ Decidida em 30/10: **computador do Matheus** | Blocos A5 e J6 · 12 h |
| D06 | Faturamento mensal da loja | Aberta | Nenhum bloco técnico |
| D07 | A loja vende fiado | Aberta | Nenhum bloco atual |
| D08 | Quem registra a mercadoria da segunda de manhã | Aberta | Afeta a operação, não o cronograma |

---

## D01 — De onde vêm os dados de venda · ✅ DECIDIDA EM 30/10/2026

**Decisão do grupo:** o Mercado do Sr. João é uma loja fictícia, criada pelo professor; não há
cliente para responder. O grupo decidiu que **o caixa exporta as vendas em Excel** (a Apostila IV,
quadro de usuários, já diz que o sobrinho lança notas e vendas no Excel). As colunas da planilha
são definidas na tarefa E1. Como não há dados reais, as planilhas usadas nos testes e na
demonstração são de exemplo, criadas pelo grupo.

**Formato decidido na E1 (05/11/2026):** planilha `.xlsx`, um arquivo por dia, uma linha por
produto vendido, colunas Cupom, Data, Hora, Produto, Quantidade, Preço unitário e Pagamento; lida
direto pelo sistema com a biblioteca `openpyxl`. Detalhes em `docs/FORMATO-PLANILHA-CAIXA.md`.

**Pergunta:** o caixa da loja exporta as vendas em arquivo? Em que formato?

**Recomendação da equipe:** confirmar com o cliente antes da primeira linha de código. Sem isso,
não existe previsão nem aviso de ruptura.

**Como programar enquanto não há resposta:**
Crie a interface `LeitorDeArquivoDoCaixa` com um método `ler(caminho) -> list[LinhaDeVenda]` e uma
implementação de exemplo em CSV, usada só nos testes. A tabela `importacao_pdv` e a tela E5 podem
ser feitas normalmente. **O que não se faz é escrever o parser do formato real sem saber qual é.**

Se a resposta for "o caixa não exporta nada", 136 das 378 horas mudam de desenho e isso precisa
voltar ao professor como mudança de escopo, não ser resolvido no código.

---

## D02 — Como o sistema fica sabendo da validade · BLOQUEANTE

**Pergunta:** a validade será digitada na entrada, estimada pelo tipo de produto, ou digitada só
nos perecíveis?

**Recomendação da equipe:** digitar só nos perecíveis. Concentra o esforço onde está a dor e não
pesa na operação.

**Como programar enquanto não há resposta:** a RN04 já cobre as três hipóteses — campo obrigatório
para perecível, cálculo automático por `durabilidade_dias` quando vem vazio, recusa de data
passada. Implemente a RN04 como está escrita e a decisão vira só uma mudança de qual campo é
obrigatório na tela.

**Na prática esta é a menos arriscada das duas bloqueantes.**

---

## D03 — Tamanho da primeira entrega · ABERTA

**Pergunta:** começar só pelo perecível, pela loja inteira, ou entregar tudo?

**Recomendação:** começar pelo perecível — entrega valor rápido e não depende de nenhuma decisão em
aberto.

**No código:** não muda nada estruturalmente. Muda qual carga de dados entra em J2 e qual conjunto
de produtos é testado em J4.

---

## D04 — Por onde o aviso chega ao dono · ABERTA

**Pergunta:** aplicativo de mensagens, aplicativo próprio ou e-mail?

**Recomendação:** aplicativo de mensagens que ele já usa — custo praticamente zero e não exige
instalar nada.

**No código:** a coluna `alerta.canal` já existe justamente para isso. Mantenha o serviço de
notificação atrás de uma interface `CanalDeAviso.enviar(destinatario, mensagem)`. Trocar Telegram
por e-mail depois vira uma classe nova, não uma reescrita.

---

## D05 — Onde o sistema vai rodar · ✅ DECIDIDA EM 30/10/2026

**Decisão do grupo:** o sistema roda **no computador do Matheus**. O professor não instala nem roda
nada; ele assiste à demonstração.

**Pergunta:** na própria loja, num servidor na nuvem, ou em nuvem gerenciada?

**Recomendação da equipe:** não fecha. Registra que a loja não tem espaço nem nobreak para
equipamento (restrição R03), e que o aviso no celular fica consideravelmente mais complicado
rodando dentro da loja.

**No código:** nada muda. As três opções usam o mesmo modelo de dados e o mesmo código. Afeta as
tarefas A5 (esteira de publicação) e J6 (implantação), 12 h ao todo. **Isso não é desculpa para
atrasar o desenvolvimento.**

---

## D06 — Faturamento mensal da loja · ABERTA

**Pergunta:** qual o faturamento médio e quanto foi anotado de perda no último balanço?

**No código:** nada. São duas perguntas rápidas que transformam a estimativa de retorno do projeto
em número real — valem para a apresentação, não para o sistema.

---

## D07 — A loja vende fiado · ABERTA

**Pergunta:** existe caderneta? Se existe, o cliente quer controlar isso no sistema?

**Recomendação:** manter fora do escopo enquanto não houver requisito confirmado.

**No código:** não implemente. Está declarado em "fora de escopo" na Apostila III.

---

## D08 — Quem registra a mercadoria da segunda de manhã · ABERTA

**Pergunta:** o sobrinho só chega à tarde, e o pedido semanal chega pela manhã.

**Recomendação:** registrar à tarde. A rotina de avisos roda de madrugada, então a defasagem não
gera prejuízo.

**No código:** nada muda. É decisão de rotina da loja.

---

## O que não está travado

**166 das 378 horas** — blocos **A, B, C, D e F** — não dependem de nenhuma destas decisões.
O modelo de dados e as telas de cadastro podem começar imediatamente, porque os tipos de dados já
estão definidos.

Some-se a isso a tarefa **H2** (aviso de validade, 8 h), que depende só de `lote.data_validade` —
ou seja, do bloco C, não do caixa. É a parte do produto que entrega valor mais cedo.

# Registros de decisão de arquitetura (ADR)

*Atualizado em 16/11/2026.* O porquê de cada decisão. Cada uma tem contexto, decisão, consequência,
data e situação. As decisões de regra de negócio (as lacunas da especificação) estão, com o
detalhe, em `docs/LACUNAS.md`; as do cliente, em `docs/DECISOES-PENDENTES.md`. Decisão nova vira um
ADR novo no fim da lista; decisão substituída fica, marcada como *substituída*.

| ADR | Decisão | Data | Situação |
|---|---|---|---|
| 001 | PostgreSQL como banco | 25/09/2026 | Aceita (fixada pela Apostila IV) |
| 002 | Django 5 + Django REST Framework na API | 06/10/2026 | Aceita |
| 003 | Painel estático em HTML/CSS/JS puros, na mesma origem da API | 08/10/2026 | Aceita |
| 004 | Autenticação própria sobre a tabela `usuario`, com token assinado | 06/10/2026 | Aceita |
| 005 | Permissão por tela declarada em cada endpoint | 06/10/2026 | Aceita |
| 006 | Saldo derivado por view; consumo lido por um módulo só | 06/10/2026 | Aceita |
| 007 | Planilha Excel do caixa, produto casado pelo nome | 05/11/2026 | Aceita |
| 008 | Rodada diária por cron, num comando só | 12/11/2026 | Aceita |
| 009 | Telegram atrás da interface `CanalDeAviso` | 08/10/2026 | Aceita |
| 010 | Contagem de partida como entrada de mercadoria | 12/11/2026 | Aceita |
| 011 | Publicação com o servidor do próprio Django | 13/11/2026 | Aceita (para a demonstração) |
| 012 | Documentação versionada com o código ("docs as code") | 13/11/2026 | Aceita |

### ADR-001 — PostgreSQL como banco
**Contexto:** a Apostila IV, figura 2 e seção 3, fixa o banco. **Decisão:** PostgreSQL 17, também
nos testes (nada de SQLite). **Consequência:** tipos `NUMERIC`, `TIMESTAMPTZ` e restrições do
`schema.sql` valem do jeito que foram entregues; o banco roda em Docker na máquina de desenvolvimento.

### ADR-002 — Django 5 + Django REST Framework
**Contexto:** a especificação não fixa a linguagem; a equipe é pequena. **Decisão:** Python e
Django, porque migração (A2), autenticação com perfis (A4) e carga inicial (J2) vêm quase prontas —
cerca de 25 das 378 horas. **Consequência:** Django 5.2 é LTS, com suporte até abril de 2028.

### ADR-003 — Painel estático na mesma origem
**Contexto:** RNF06 e R04 (computador antigo); a figura 2 separa os arquivos estáticos do servidor
da API; endereços diferentes exigiriam CORS (L25). **Decisão:** HTML/CSS/JS puros, sem framework, e
o painel chama sempre `/api/...`; quem serve o painel repassa para a API. **Consequência:** nenhuma
dependência no navegador; template Django que lê o banco é proibido.

### ADR-004 — Autenticação própria sobre `usuario`
**Contexto:** o modelo de usuário do Django exige colunas que a tabela `usuario` da Apostila IV não
tem (L09). **Decisão:** `AbstractBaseUser` sobre a tabela como está, login como identificador, senha
com o hash do Django e token assinado sem tabela, válido por 12 horas. **Consequência:** a tabela
continua igual à apostila; trocar a senha derruba as sessões abertas.

### ADR-005 — Permissão por tela
**Contexto:** RN14 manda verificar o perfil antes de qualquer operação, fora da regra de negócio.
**Decisão:** todo endpoint declara `tela = "..."`, conferida contra `ACESSO_POR_TELA`; endpoint sem
tela é recusado para todos. Exceções: a entrada no sistema e o webhook do Telegram (segredo).
**Consequência:** um teste prova o acesso de cada perfil a cada tela.

### ADR-006 — Saldo derivado; consumo por um módulo só
**Contexto:** RN01 (saldo nunca escrito) e RN11 (perda não é consumo — "a regra mais fácil de
quebrar"). **Decisão:** o saldo é a view `vw_estoque_atual`; a previsão e os avisos leem vendas só
por `previsao/consumo.py`. **Consequência:** um teste de guarda falha se `previsao/` ou `alertas/`
tocarem a tabela de movimentação diretamente.

### ADR-007 — Planilha Excel, casada pelo nome
**Contexto:** D01 (o caixa exporta em Excel); a tabela `produto` não tem código do caixa (L05).
**Decisão:** ler o `.xlsx` (biblioteca `openpyxl`) e achar o produto pelo nome, sem diferenciar
maiúscula nem acento; linha que não casa fica para conferir (L26). O leitor fica atrás da
interface `LeitorDeArquivoDoCaixa`. **Consequência:** o modelo de dados não muda; trocar o formato
do caixa é trocar o leitor.

### ADR-008 — Rodada por cron
**Contexto:** previsão e avisos rodam às 03h00, mesmo sem ninguém usando (Apostila IV, comunicação
nº 4); dependência nova só com decisão do grupo. **Decisão:** um comando `rodada_diaria` com os
passos na ordem da apostila, disparado pelo cron; as linhas saem dos parâmetros (`agenda_cron`).
**Consequência:** o computador precisa estar ligado às 03h00; um passo que falha não para os outros.

### ADR-009 — Telegram atrás de `CanalDeAviso`
**Contexto:** RN13 e a figura 1 escolhem o Telegram, mas o canal pode mudar (D04). **Decisão:** o
envio conversa com a interface `CanalDeAviso.enviar(destinatario, mensagem)`; o Telegram é uma
implementação, só com a biblioteca padrão. **Consequência:** outro canal entra sem mexer nas regras.

### ADR-010 — Contagem de partida como entrada
**Contexto:** RN01 — saldo só nasce de movimentação; perecível precisa de validade (RN04).
**Decisão:** cada linha contada vira um lote pela operação 02, com origem `INVENTARIO`.
**Consequência:** o estoque inicial já entra no aviso de validade e na saída pelo lote que vence primeiro.

### ADR-011 — Publicação com o servidor do Django
**Contexto:** D05 (computador do Matheus); o uso previsto é a demonstração. **Decisão:** `publicar.py`
roda tudo (testes antes) e sobe `runserver --noreload` e `servir.py`. **Consequência:** não serve para
uso real com muitos acessos; servidor de produção fica no roadmap.

### ADR-012 — Docs as code
**Contexto:** critério de aceite dos slides do professor (13/11/2026). **Decisão:** a documentação
fica em `docs/sistema/`, versionada com o código; quatro documentos são gerados do código e um teste
falha se ficarem desatualizados; toda tarefa atualiza o que mudou. **Consequência:** o PDF entregue
sai sempre dos mesmos arquivos.

### ADR-013 — Trava do PostgreSQL contra duas rodadas ao mesmo tempo
**Contexto:** revisão X1, item 16 (16/11/2026): a importação e os avisos conferem ("o dia já
entrou?", "já avisei hoje?") e depois gravam; duas rodadas juntas (o cron e o comando à mão, ou a
verificação de hora em hora do item 11) gravavam em dobro. **Decisão:** a conferência e a gravação
acontecem numa transação só, depois de `pg_advisory_xact_lock` (`comum/trava.py`), sem tabela nem
dependência nova. **Consequência:** quem chega depois espera e encontra o que o primeiro gravou; a
trava se solta sozinha no fim da transação, mesmo se o processo cair.

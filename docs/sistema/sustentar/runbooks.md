# Runbooks — o que fazer quando algo dá errado

*Atualizado em 16/11/2026.* Incidentes conhecidos, com sintoma, causa provável e passos. Todos os
comandos rodam na raiz do projeto com o `.venv` ativado. **Lembrete: o caixa da loja nunca para por
causa do sistema (RNF07)** — o pior caso é o aviso atrasar.

## R1 — A rodada da madrugada falhou
**Sintoma:** avisos não chegaram de manhã; `logs/rodada.log` termina com "com falha em: …".
1. Ler a última rodada em `logs/rodada.log` e o motivo em `logs/mercadinho.log`.
2. Corrigir a causa (ver R2, R3, R5) e rodar de novo: `python backend/manage.py rodada_diaria`.
   Pode rodar quantas vezes precisar: nada é duplicado (consumo e previsão são recalculados; aviso
   não se repete no mesmo dia).

## R2 — A planilha do caixa não foi lida
**Sintoma:** Importação de vendas mostra "Não foi lida", ou o fechamento diz que as vendas não entraram.
1. Conferir se o arquivo é `.xlsx` e tem as colunas de `docs/FORMATO-PLANILHA-CAIXA.md`. No log da
   rodada, procurar a linha com problema ("vendas.xlsx, linha 3: Hora não é uma hora no formato
   hh:mm"): uma linha fora do formato recusa a planilha inteira (X1, item 2).
2. Salvar a planilha corrigida na pasta (`PASTA_VENDAS_CAIXA`). Ela entra na próxima madrugada, ou
   agora: `python backend/manage.py importar_vendas`. Dia de venda que já entrou não
   entra de novo, qualquer que seja o nome do arquivo; a planilha com o nome de uma já lida entra se
   foi regravada depois daquela leitura.
3. Depois, recalcular: `python backend/manage.py agregar_consumo` e `python backend/manage.py calcular_previsao`.

## R3 — O aviso não chegou no celular
1. Era horário de movimento (10h30–13h00, 16h30–18h00)? Então está segurado e sai às 13h00 ou 18h00.
2. Rodar `python backend/manage.py enviar_avisos` e ler a saída: "não saiu" mostra o motivo no log.
3. Sem internet ou token errado: os avisos ficam guardados e saem na próxima tentativa.
4. Celular trocado: `python backend/manage.py vincular_telegram --login joao`.

## R4 — O painel não abre ("sem conexão com o sistema")
1. `python publicar.py --sem-atualizar` (roda os testes e sobe tudo de novo).
2. Se não subir, ler `logs/api.log` e `logs/painel.log`; conferir se as portas 8000 e 8090 estão livres.

## R5 — O banco parou
**Sintoma:** erro de conexão na porta 5432. 1. Abrir o Docker. 2. `docker compose up -d --wait`.
3. `python publicar.py --sem-atualizar`.

## R6 — Voltar para a versão anterior (rollback)
1. `python publicar.py --parar`.
2. `git log --oneline` e `git checkout <commit anterior>`.
3. Se a versão nova criou migração, desfazer antes de trocar o código:
   `python backend/manage.py migrate <app> <migração anterior>` — **com backup antes** (ver backup).
4. `python publicar.py --sem-atualizar`. Para voltar ao normal: `git checkout main`.

## R7 — Alguém esqueceu a senha
`python backend/manage.py changepassword <login>`. As sessões abertas daquela pessoa caem.

## R8 — Estoque negativo ou diferente da prateleira
Não é falha do sistema: faltou registrar uma entrada, ou a contagem estava errada. Registrar a
entrada que faltou; perda a mais se registra em Avarias. Nada se apaga (RN01).

## R9 — O computador estava desligado às 03h00
Ligar e rodar `python backend/manage.py rodada_diaria`. O consumo refaz os últimos 30 dias, então
nenhum dia se perde.

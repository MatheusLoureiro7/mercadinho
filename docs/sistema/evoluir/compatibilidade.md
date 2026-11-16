# Matriz de compatibilidade

*Atualizado em 16/11/2026.* Com o que o sistema foi testado e com o que deve funcionar.

| Peça | Testado em 16/11/2026 | Exigido | Observação |
|---|---|---|---|
| Sistema operacional | macOS (computador do Matheus) | macOS, Windows ou Linux com Docker | Passo a passo do Windows em `COMO-RODAR.md` |
| Python | 3.14.7 | 3.11 ou mais novo | CLAUDE.md |
| Django | 5.2.18 | 5.2 (LTS) | `requirements.txt` |
| PostgreSQL | 17.11, em Docker | 17 | Fixado pela Apostila IV |
| Navegador do painel | Chromium (o do Playwright, nos 100+ testes de tela) | Chrome, Edge ou Firefox atuais | Firefox, Edge e Safari não são testados automaticamente |
| Tamanho de tela | 360 px (celular) e 1024 px (computador da loja) | De 360 px em diante | Abaixo de 860 px a tabela vira cartão |
| Planilha do caixa | Excel `.xlsx` | `.xlsx` com as colunas combinadas; coluna Pagamento preenchida para o caixa fechar | `.xls` e `.csv` não são lidos |
| Telegram | Bot API, envio e webhook | Internet de saída; webhook só com `https://` público | — |
| Agendador | cron do macOS | cron, com as 4 linhas de `agenda_cron` | No Windows as linhas teriam de ser adaptadas ao Agendador de Tarefas: não testado. Computador desligado às 03h00: a rodada é recuperada em até uma hora depois de ligar |

Versões das bibliotecas, licenças e fim de suporte: `evoluir/dependencias.md`.

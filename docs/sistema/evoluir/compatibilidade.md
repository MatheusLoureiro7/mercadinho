# Matriz de compatibilidade

*Atualizado em 13/11/2026.* Com o que o sistema foi testado e com o que deve funcionar.

| Peça | Testado em 13/11/2026 | Exigido | Observação |
|---|---|---|---|
| Sistema operacional | macOS (computador do Matheus) | macOS, Windows ou Linux com Docker | Passo a passo do Windows em `COMO-RODAR.md` |
| Python | 3.14.7 | 3.11 ou mais novo | CLAUDE.md |
| Django | 5.2.18 | 5.2 (LTS) | `requirements.txt` |
| PostgreSQL | 17.11, em Docker | 17 | Fixado pela Apostila IV |
| Navegador do painel | Chromium (o do Playwright, nos 100+ testes de tela) | Chrome, Edge ou Firefox atuais | Firefox, Edge e Safari não são testados automaticamente |
| Tamanho de tela | 360 px (celular) e 1024 px (computador da loja) | De 360 px em diante | Abaixo de 860 px a tabela vira cartão |
| Planilha do caixa | Excel `.xlsx` | `.xlsx` com as colunas combinadas | `.xls` e `.csv` não são lidos |
| Telegram | Bot API, envio e webhook | Internet de saída; webhook só com `https://` público | — |

Versões das bibliotecas, licenças e fim de suporte: `evoluir/dependencias.md`.

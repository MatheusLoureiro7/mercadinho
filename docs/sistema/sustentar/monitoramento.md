# Monitoramento

*Atualizado em 16/11/2026.* **Situação: parcial.** O sistema registra tudo em log e mostra a situação
de cada importação na tela, mas **não há painel de métricas nem alerta automático para a equipe**
quando algo falha — está no roadmap.

## O que existe

| Onde | O que registra | Quem olha |
|---|---|---|
| `logs/mercadinho.log` | Tudo da aplicação, com data e nível (troca de arquivo a cada 5 MB, guarda os 5 últimos) | N2 |
| `logs/rodada.log` | Cada rodada da madrugada: um "ok" ou "FALHOU" por passo; e, de hora em hora, a verificação da rodada perdida | N2, toda manhã |
| `logs/ultima-rodada.txt` | O dia da última rodada (com ou sem falha) | A verificação de hora em hora |
| `logs/publicacoes.log` | Cada publicação: data, versão (commit) e resultado | N2 |
| `logs/api.log`, `logs/painel.log` | A saída dos servidores | N2, se o painel não abrir |
| Tela Importação de vendas | Situação de cada planilha (Lida / com vendas a conferir / Não foi lida) | Sobrinho, toda manhã |
| Tabela `alerta` | Situação de cada aviso: pendente, segurado, enviado, cancelado | N2 |

Nenhum log guarda senha nem token (RNF12).

## O que cada registro significa

| Registro | Significa | Fazer |
|---|---|---|
| `Rodada de dd/mm/aaaa concluída.` | Tudo certo | — |
| `com falha em: Importação das vendas do caixa` | Pasta não configurada ou planilha ilegível | Runbook R2 |
| `vendas.xlsx, linha 3: Hora não é uma hora no formato hh:mm.` (em `mercadinho.log`) | Linha fora do formato: a planilha inteira foi recusada | Runbook R2 |
| `copia.xlsx: as vendas desta planilha já tinham entrado.` | A planilha repete um dia já importado; nada foi gravado | Apagar a cópia da pasta |
| `A rodada de dd/mm/aaaa não tinha acontecido: rodando agora.` | O computador estava desligado às 03h00; a rodada foi recuperada | Runbook R9, se repetir |
| `A rodada de dd/mm/aaaa já aconteceu.` | A verificação de hora em hora, sem nada a fazer | — |
| `com falha em: Envio dos avisos pelo Telegram` | Sem internet, token ou celular não ligado | Runbook R3 |
| `NÃO publicado — falhou em: Rodar todos os testes` | A versão nova quebrou algo; o sistema no ar não mudou | Corrigir antes de publicar |
| `publicado, mas não respondeu` | API ou painel não subiu | Runbook R4 |

## Conferência diária (2 minutos, N2)
1. A última linha de `logs/rodada.log` é "concluída"?
2. Importação de vendas sem planilha "Não foi lida"?
3. O Sr. João recebeu a mensagem da manhã?

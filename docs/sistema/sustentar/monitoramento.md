# Monitoramento

*Atualizado em 13/11/2026.* **Situação: parcial.** O sistema registra tudo em log e mostra a situação
de cada importação na tela, mas **não há painel de métricas nem alerta automático para a equipe**
quando algo falha — está no roadmap.

## O que existe

| Onde | O que registra | Quem olha |
|---|---|---|
| `logs/mercadinho.log` | Tudo da aplicação, com data e nível (troca de arquivo a cada 5 MB, guarda os 5 últimos) | N2 |
| `logs/rodada.log` | Cada rodada da madrugada: um "ok" ou "FALHOU" por passo | N2, toda manhã |
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
| `com falha em: Envio dos avisos pelo Telegram` | Sem internet, token ou celular não ligado | Runbook R3 |
| `NÃO publicado — falhou em: Rodar todos os testes` | A versão nova quebrou algo; o sistema no ar não mudou | Corrigir antes de publicar |
| `publicado, mas não respondeu` | API ou painel não subiu | Runbook R4 |

## Conferência diária (2 minutos, N2)
1. A última linha de `logs/rodada.log` é "concluída"?
2. Importação de vendas sem planilha "Não foi lida"?
3. O Sr. João recebeu a mensagem da manhã?

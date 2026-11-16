# Backup e continuidade

*Atualizado em 16/11/2026.* **Situação: o backup automático ainda NÃO existe.** A especificação pede
**backup diário fora do servidor** (RNF09; Apostila IV, comunicação nº 10: "rotina de backup →
armazenamento externo, 1× por dia"). Nenhuma tarefa do cronograma o implementou; está no roadmap e
precisa de decisão do grupo sobre onde guardar a cópia.

## Hoje: cópia manual

Gerar a cópia (com o banco no ar):

```
docker compose exec -T banco pg_dump -U mercadinho mercadinho > backup-AAAA-MM-DD.sql
```

Guardar o arquivo **fora do computador** (pen drive ou nuvem). Restaurar numa base vazia:

```
docker compose exec -T banco psql -U mercadinho mercadinho < backup-AAAA-MM-DD.sql
```

## O que precisa de cópia

| Dado | Precisa? | Por quê |
|---|---|---|
| Banco: tabelas de origem (produto, lote, movimentação, venda, fechamento…) | **Sim** | É o registro do que aconteceu; não se recria |
| Banco: consumo diário, previsão e avisos | Não | São recalculados (`agregar_consumo --desde`, `calcular_previsao`) |
| Planilhas do caixa na pasta | Sim | Permitem importar, num banco restaurado, os dias depois da cópia (dia que já está no banco não entra de novo) |
| Arquivo `.env` | Sim, guardado à parte | Segredos; nunca no git |
| Código | Não | Está no GitHub |

## Objetivos propostos

| Indicador | Proposta | Explicação |
|---|---|---|
| RPO (quanto dado se pode perder) | 24 horas | Uma cópia por dia, depois da rodada |
| RTO (em quanto tempo voltar) | 2 horas | Instalar o ambiente (README), restaurar a cópia, `publicar.py` |

## Se o computador quebrar
1. Instalar o ambiente noutro computador (`COMO-RODAR.md`).
2. Restaurar a última cópia e o `.env`.
3. `python publicar.py --sem-atualizar` e instalar o cron.
4. Reimportar as planilhas dos dias depois da cópia (`importar_vendas`).
Enquanto isso, a loja continua vendendo: só os avisos param.

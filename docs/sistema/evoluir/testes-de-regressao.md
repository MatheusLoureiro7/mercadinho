# Testes de regressão

*Atualizado em 13/11/2026.* A suíte que prova que uma mudança ou atualização não quebrou nada.

## A suíte

**1.047 testes automáticos, todos aprovados em 13/11/2026**, no PostgreSQL de verdade (num banco
próprio), com pytest e Playwright. Cada tarefa entrou com os seus testes; as 16 regras de negócio
têm teste com o nome da regra (ver `manter/rastreabilidade.md`).

| Tipo | O que prova |
|---|---|
| Regra | Cada regra com o exemplo da Apostila I, pelo "sim" e pelo "não" de cada losango dos fluxogramas |
| API | Aceita e recusa o que deve; cada perfil só entra nas suas telas (RN14) |
| Banco | Cada tabela igual ao `schema.sql` da Apostila IV |
| Tela | Navegador real: login, preenchimento, resultado na tela e no banco; no celular e no computador |
| Guarda | Previsão sem ler movimentação direto (RN11); toda regra com teste (J1); documentação em dia |

## Quando roda

- A cada tarefa, antes do commit.
- **Sempre antes de publicar**: `publicar.py` só troca o sistema no ar se a suíte inteira passar.
- Antes e depois de atualizar Django, Python ou PostgreSQL (`evoluir/guia-de-migracao.md`).

## Como rodar

```
pytest                    # tudo (~2 minutos)
pytest -m "not tela"      # sem os testes no navegador
```

## Como sabemos que os testes pegam erro
Ao fim de cada tarefa, o grupo coloca **defeitos de propósito** no código (perda somada às vendas,
semana contada errada, aviso repetido…) e confere que algum teste falha. Quando um defeito passou, o
teste foi reforçado antes da entrega. O relatório para o professor está em
`docs/testes/RELATORIO-DE-TESTES.pdf` (versão 1.2, de 05/11/2026; a 1.3 sai na J1).

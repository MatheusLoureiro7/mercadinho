# Testes de regressão

*Atualizado em 25/11/2026.* A suíte que prova que uma mudança ou atualização não quebrou nada.

## A suíte

**1.144 testes automáticos, todos aprovados em 16/11/2026**, no PostgreSQL de verdade (num banco
próprio), com pytest e Playwright. Cada tarefa entrou com os seus testes; as 16 regras de negócio
têm teste com o nome da regra (ver `manter/rastreabilidade.md`). A cobertura foi fechada na J1
(16/11/2026, 1.053 testes); a revisão X1, no mesmo dia, acrescentou 84, um conjunto por achado, e a página da documentação
(X2), 7.

| Tipo | O que prova |
|---|---|
| Regra | Cada regra com o exemplo da Apostila I, pelo "sim" e pelo "não" de cada losango dos fluxogramas |
| API | Aceita e recusa o que deve; cada perfil só entra nas suas telas (RN14) |
| Banco | Cada tabela igual ao `schema.sql` da Apostila IV |
| Tela | Navegador real: login, preenchimento, resultado na tela e no banco; no celular e no computador |
| Guarda | Previsão sem ler movimentação direto (RN11); toda regra com teste (J1); documentação em dia; diferenças do banco para o `schema.sql` limitadas às registradas (L28); toda tela que converte número confere o ambíguo |
| Concorrência | Duas rodadas em paralelo de verdade, com a primeira atrasada no meio da gravação: nada em dobro (ADR-013) |

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
teste foi reforçado antes da entrega: 130 defeitos de propósito até 16/11/2026, todos pegos. O
relatório para o professor está em `docs/testes/RELATORIO-DE-TESTES.pdf` (versão 2.0, de
25/11/2026, emitido com 1.144 testes, depois da revisão X1); o material de trabalho, em
`docs/TESTES.md`.

Na revisão X1 a prova foi outra: cada teste novo foi escrito **antes** da correção e visto falhar
pelo motivo certo; só então o código mudou.

## Teste que só falha na suíte inteira
Se um teste passa sozinho e falha junto com os outros, algum estado está vazando de um teste para
outro. Caso já visto (J1, 16/11/2026): o DRF acrescenta `head` nas ações de uma rota na primeira
chamada, e o documento da API gerado mudava; o gerador passou a ignorar `head`.

# Documentação do sistema

*Atualizado em 13/11/2026.* Organizada como nos slides "Documentação de Software" do professor:
**cada documento responde a uma pergunta**, e são quatro perguntas. Tudo fica versionado junto com
o código ("docs as code") e é atualizado na mesma entrega que muda o sistema. O PDF
`DOCUMENTACAO-DO-SISTEMA.pdf` é gerado a partir destes arquivos (`python docs/sistema/gerar.py`).

| Pergunta | Quem lê | Pasta |
|---|---|---|
| **Usar** — como faço meu trabalho com o sistema? | Sr. João, esposa, sobrinho | `usar/` |
| **Manter** — como o sistema funciona e por que é assim? | Desenvolvedores | `manter/` |
| **Sustentar** — como mantenho o sistema no ar e recupero quando cai? | Quem opera (N2) | `sustentar/` |
| **Evoluir** — como atualizo sem quebrar? | Quem decide a arquitetura | `evoluir/` |

Situação: **Pronto** (cobre o sistema de hoje) · **Parcial** (existe, com lacuna declarada no próprio
documento) · **Gerado** (sai do código; um teste falha se ficar velho).

## Os 24 documentos

| Pergunta | Documento (slides) | Arquivo | Situação | Atualizado em |
|---|---|---|---|---|
| Usar | Manual do usuário | `usar/manual-do-usuario.md` | Pronto | 13/11/2026 |
| Usar | Guia de início rápido | `usar/inicio-rapido.md` | Pronto | 13/11/2026 |
| Usar | FAQ | `usar/faq.md` | Pronto | 13/11/2026 |
| Usar | Glossário de negócio | `usar/glossario.md` | Pronto | 13/11/2026 |
| Usar | Release notes do usuário | `usar/novidades.md` | Pronto | 13/11/2026 |
| Usar | Material de treinamento | `usar/treinamento.md` | Parcial: sessões e vídeos na J5 (23/11/2026) | 13/11/2026 |
| Manter | Requisitos e regras de negócio | `docs/REGRAS-NEGOCIO.md`, `docs/ESPECIFICACAO.md` e `manter/rastreabilidade.md` | Gerado | 13/11/2026 |
| Manter | Arquitetura (C4) | `manter/arquitetura.md` | Pronto | 13/11/2026 |
| Manter | ADRs | `manter/adrs.md` | Pronto | 13/11/2026 |
| Manter | Modelo e dicionário de dados | `manter/dicionario-de-dados.md` | Gerado | 13/11/2026 |
| Manter | Contratos de API | `manter/contratos-da-api.md` | Gerado | 13/11/2026 |
| Manter | README e guia de dev + testes | `README.md`, `COMO-RODAR.md` e `manter/guia-do-desenvolvedor.md` | Pronto | 13/11/2026 |
| Sustentar | Deploy e infraestrutura | `sustentar/deploy-e-infraestrutura.md` | Pronto | 13/11/2026 |
| Sustentar | Runbooks | `sustentar/runbooks.md` | Pronto | 13/11/2026 |
| Sustentar | Monitoramento | `sustentar/monitoramento.md` | Parcial: sem alerta automático para a equipe | 13/11/2026 |
| Sustentar | Matriz de suporte e SLA | `sustentar/suporte-e-sla.md` | Parcial: proposta, contatos na J6 (23 a 27/11/2026) | 13/11/2026 |
| Sustentar | Backup e continuidade | `sustentar/backup-e-continuidade.md` | Parcial: backup automático ainda não existe (RNF09) | 13/11/2026 |
| Sustentar | Segurança e base de conhecimento | `sustentar/seguranca-e-lgpd.md` | Pronto | 13/11/2026 |
| Evoluir | Inventário de dependências (SBOM) | `evoluir/dependencias.md` | Gerado | 13/11/2026 |
| Evoluir | Roadmap e dívida técnica | `evoluir/roadmap-e-divida-tecnica.md` | Pronto | 13/11/2026 |
| Evoluir | Changelog e versionamento | `evoluir/changelog.md` | Pronto | 13/11/2026 |
| Evoluir | Guias de migração | `evoluir/guia-de-migracao.md` | Pronto | 13/11/2026 |
| Evoluir | Matriz de compatibilidade | `evoluir/compatibilidade.md` | Pronto | 13/11/2026 |
| Evoluir | Testes de regressão | `evoluir/testes-de-regressao.md` | Pronto | 13/11/2026 |

## Critérios de aceite (slide 7)

| Critério | Como o projeto atende | Situação |
|---|---|---|
| Teste do estranho | `COMO-RODAR.md` leva do zero às telas abertas; `publicar.py` faz o deploy com um comando | A fazer: alguém de fora do grupo seguir só os documentos, na J6 |
| Docs as code | Documentação no git com o código; 4 documentos gerados do código; `backend/tests/test_documentacao.py` falha se algo ficar velho ou sem índice | Atende desde 13/11/2026 |
| Transferência de conhecimento | Roteiros de treinamento por pessoa (`usar/treinamento.md`) | A fazer: sessões gravadas com as perguntas, na J5 |

## Como alimentar

Toda tarefa que muda o sistema atualiza, no mesmo commit, o que mudou. Depois de editar:
`python docs/sistema/gerar.py` (regenera os gerados e o PDF) e `pytest backend/tests/test_documentacao.py`.

| Quando a tarefa… | Atualizar |
|---|---|
| cria ou muda uma tela | `usar/manual-do-usuario.md`; se mudar o passo a passo, `usar/inicio-rapido.md` e `usar/treinamento.md` |
| cria um endpoint | a descrição em `DESCRICOES` (`gerar.py`) — sem ela o teste falha |
| cria ou muda uma tabela ou regra | só regenerar (dicionário e rastreabilidade); termo novo vai para `usar/glossario.md` |
| toma uma decisão de arquitetura | um ADR novo em `manter/adrs.md` |
| muda como o sistema sobe, roda ou é publicado | `sustentar/deploy-e-infraestrutura.md` e, se houver incidente novo, `sustentar/runbooks.md` |
| acrescenta dependência (com decisão do grupo) | só regenerar (`evoluir/dependencias.md`); revisar `evoluir/compatibilidade.md` |
| fecha uma versão | `evoluir/changelog.md` e `usar/novidades.md` |
| resolve ou cria pendência | `evoluir/roadmap-e-divida-tecnica.md` |
| responde uma dúvida de quem usa | `usar/faq.md` |

Ao mudar um documento, trocar a data "Atualizado em" dele e a desta tabela.

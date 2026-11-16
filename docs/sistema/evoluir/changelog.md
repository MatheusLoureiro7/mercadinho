# Changelog e versionamento

*Atualizado em 16/11/2026.* Versionamento semântico (SemVer), adotado pelo grupo em 13/11/2026:

- **MAIOR** (1.0.0, 2.0.0): mudança que quebra algo — dado que precisa ser convertido, tela que some,
  formato da planilha do caixa que muda. Vem sempre com guia de migração.
- **MENOR** (0.3.0): funcionalidade nova, sem quebrar o que existe.
- **CORREÇÃO** (0.3.1): conserto, sem funcionalidade nova.

Enquanto a versão começar com 0, o sistema está em construção; a **1.0.0** é a da entrega, em
01/12/2026. Cada versão aponta o commit. A versão para quem usa, em linguagem da loja, está em
`usar/novidades.md`.

## 0.4.0 — 16/11/2026 — commit `f4104c2`
Revisão geral do código contra a especificação (tarefa extra X1): 22 achados, todos corrigidos, um
commit por item (`fa2866e` a `f4104c2`). Lista completa em `docs/REVISAO-FABLE.md`.

- **Novo:** coluna "Quando acaba" na Consulta de estoque e campos `previsao` e `dias_ate_acabar` em
  `/api/estoque/` (RF08, RN09). Campo "Dia do caixa" no Fechamento; `?data=` em
  `/api/fechamentos/apurado/` e `data` opcional no registro. `rodada_diaria --se-faltar`.
  Confirmação antes de ligar a venda pendente.
- **Corrigido — importação:** vendas reconhecidas pelo dia, não pelo nome do arquivo; linha ilegível
  recusa a planilha; um registro de importação por dia; total do cupom arredondado por item; venda a
  mais descontada da carga seguinte.
- **Corrigido — avisos:** silêncio do "Sim, pedir" limitado ao prazo de entrega; produto sem
  fornecedor avisa ao acabar; produto sem venda não avisa; mensagem dividida entre avisos.
- **Corrigido — caixa e cadastro:** "espécie" conta como dinheiro; venda sem forma de pagamento
  recusa o fechamento; nome de produto comparado sem maiúscula nem acento; durabilidade até 3650
  dias; número ambíguo ("1.000") recusado nas telas.
- **Robustez:** trava do PostgreSQL contra duas rodadas juntas (ADR-013); API publicada sempre com
  `DJANGO_DEBUG=false`; detalhes do banco criados pelo Django registrados (L28, ADR-014).
- Banco: migração `estoque.0003_padrao_data_hora_now` (só o padrão de uma coluna em banco antigo;
  nada a converter). Nenhuma coluna nova.
- **Atenção ao atualizar:** gerar o crontab de novo (4 linhas). Ver `evoluir/guia-de-migracao.md`.
- **Documentação (versão 1.1 do MDGS-DOC-001):** os documentos atualizados para esta versão; página
  navegável e PDF gerados dos mesmos arquivos (ADR-015); a rastreabilidade passou a mostrar o RF14
  como coberto (ele é a RN14; faltava a sigla no código).

## 0.3.1 — 13/11/2026 — commit `756a65f`
- **Corrigido:** sugestão de compra de produto em UN ou PCT arredonda para o inteiro seguinte.
- **Novo:** esteira de publicação `publicar.py` (A5). Documentação do sistema em `docs/sistema/`.
- Banco: nenhuma migração nova.

## 0.3.0 — 12/11/2026 — commit `8e63b3c`
- **Novo:** consumo diário (G1), médias por dia e por dia da semana (G2), previsão gravada (G3),
  "ainda aprendendo" (G4), rodada diária por cron (G5), aviso "vai acabar" e de fim de semana (H3),
  tela de Importação de vendas e conciliação das pendentes (E4, E5), Balanço da semana (I3), carga
  de produtos e contagem de partida por planilha (J2, J3).
- Banco: migrações `previsao.0001_consumo_diario` e `previsao.0002_previsao_produto` (tabelas novas
  da Apostila IV; nada a converter).
- Quebra: nenhuma.

## 0.2.0 — 05/11/2026 — commit `c322824`
- **Novo:** tabelas de venda (E2), formato da planilha do caixa (E1), importação das vendas (E3),
  fechamento de caixa gravado (I1).
- Banco: migrações de `vendas` e `caixa`. Nova dependência: `openpyxl` (decisão do grupo).

## 0.1.0 — 09/10/2026 — commit `cfaa8a3`
- **Novo:** fundação (banco, API, login e três perfis), cadastros, entrada de mercadoria, saldo,
  perdas, consulta de estoque, aviso de validade pelo Telegram, tela de fechamento de caixa.

## A fazer na 1.0.0 (01/12/2026)
Fechar J4, J5 e J6 (J1 fechada em 16/11/2026); marcar a versão no git (`git tag v1.0.0`).

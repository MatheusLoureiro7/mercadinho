# Roadmap e dívida técnica

*Atualizado em 16/11/2026.* O que ainda precisa ser feito ou melhorado, e por quê.

## Até a entrega (01/12/2026)

| Tarefa | O quê | Data prevista |
|---|---|---|
| J4 | Teste em movimento real, num sábado cheio (simulado) | 21/11/2026 |
| J5 | Treinamento das três pessoas (`usar/treinamento.md`) | 23/11/2026 |
| J6 | Implantação no computador do Matheus e primeira semana simulada | 23 a 27/11/2026 |

## Depois da primeira versão

| Item | Por quê | Origem |
|---|---|---|
| **Backup diário automático fora do computador** | Pedido pela especificação e ainda não feito; precisa decidir onde guardar a cópia | RNF09, comunicação nº 10 |
| Sistema num endereço `https://` público | Sem isso, o toque em "Sim, pedir" não volta ao sistema | H7, D05 |
| Servidor de produção no lugar do servidor do Django | O de hoje é para demonstração | ADR-011 |
| Aviso automático para a equipe quando a rodada falha | Hoje só aparece no log | `sustentar/monitoramento.md` |
| Integração contínua (testes a cada envio ao GitHub) | Hoje os testes rodam na esteira e a cada tarefa, na máquina | `sustentar/deploy-e-infraestrutura.md` |
| Apoio ao inventário mensal | Requisito desejável, não coberto na primeira versão | RF16 |
| Produtos vendidos juntos | Requisito desejável, não coberto na primeira versão | RF17 |
| Véspera de feriado nos críticos de fim de semana | Fora do escopo desta versão, declarado | L03 |
| Antecedência do aviso de validade por categoria | Hoje é um valor só para todas | L01 |
| Telas de usuários e de parâmetros | Hoje pelo terminal e pelo banco | L14 |
| Operação de ajuste de estoque | Contagem que acha menos do que o sistema só se acerta como perda | L10 |

## Dívida técnica

| Dívida | Impacto | Como pagar |
|---|---|---|
| Decisões a confirmar pelo grupo: dia da semana 0 = domingo (L27), semana de segunda a domingo no balanço, unidade "reais" no pedido mínimo (L24) | Pequeno; cada uma muda num lugar só | Confirmar e registrar |
| Registrar numa versão 1.1 da Apostila IV o que o código precisou acrescentar sem mudar tabela: tabelas internas do Django (L09), valores de severidade (L11), origem `INVENTARIO` (J3) | Divergência de documentação | Versão 1.1 da apostila |
| Sugestão de compra ignora o pedido mínimo do fornecedor | Pode sugerir pedido menor que o mínimo | Decisão do grupo (L15) |
| Produto que o caixa escreve com outro nome fica pendente todo dia | Trabalho repetido para o sobrinho | Acertar o nome no cadastro; ou um campo de apelido (mudaria o modelo de dados, L05) |
| Motivo da planilha recusada só aparece no log | A tela diz "Não foi lida" e quantas linhas; a linha e o motivo ficam em `logs/` | Mostrar na tela pediria coluna nova em `importacao_pdv` (modelo de dados) |
| Dia importado sem a coluna Pagamento fica sem fechamento | O dia não entra de novo, então o caixa daquele dia não fecha | Garantir a coluna na exportação do caixa; ou a operação de reimportar um dia (decisão do grupo) |
| Venda ligada ao produto errado não tem desfazer | A tela confirma antes, mas o erro confirmado só se acerta com entrada e perda | Depende da L10 |
| Datas e números do relatório semanal digitados à mão | Risco de divergir do acompanhamento | Gerar do `docs/ACOMPANHAMENTO.md` |

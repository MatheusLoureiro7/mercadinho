# Matriz de suporte e níveis de serviço

*Atualizado em 13/11/2026.* **Situação: proposta do grupo, a confirmar na implantação (J6).** O
mercado é fictício (30/10/2026), então não há contrato; a matriz abaixo é a que o grupo propõe para
uma loja deste porte.

## Níveis

| Nível | Quem | Resolve | Material |
|---|---|---|---|
| N1 | Sobrinho (e esposa) | Dúvida de uso, venda para conferir, senha esquecida dos outros | Manual, FAQ, início rápido |
| N2 | Grupo MDGS — Matheus (o sistema roda no computador dele) | Rodada que falhou, aviso que não chegou, publicação, rollback, backup | Runbooks, monitoramento |
| N3 | Grupo MDGS — desenvolvimento | Defeito no código, regra nova, mudança de formato do caixa | Guia do desenvolvedor, ADRs |

**Escalonamento:** N1 tenta pela FAQ; não resolveu, chama o N2; o N2 abre um defeito para o N3 quando
o runbook não resolve. Os contatos (telefone e e-mail de cada um) são preenchidos na implantação.

## Níveis de serviço propostos

| Situação | Prazo proposto | Base |
|---|---|---|
| Avisos no ar em horário comercial | Rodada das 03h00 todo dia; atraso tolerado até o meio da manhã | RNF08 |
| Sistema fora do ar | Atendimento do N2 no mesmo dia útil | RNF08 |
| Defeito que impede registrar entrada ou perda | Correção em até 2 dias úteis | RNF05 |
| Dúvida de uso | Resposta no mesmo dia | RNF02 |

O caixa da loja não depende do sistema (RNF07): nenhuma falha aqui para a venda.

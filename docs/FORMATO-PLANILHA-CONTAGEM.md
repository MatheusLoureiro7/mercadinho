# Formato da planilha de contagem de partida

Tarefa **J3** · feito pelo grupo em **12/11/2026** · base: RN01 (saldo só nasce de movimentação),
RN04 (validade do lote de perecível), operação 02 (entrada de mercadoria) e as tabelas `lote` e
`movimentacao` da Apostila IV.

Exemplo pronto: `docs/exemplos/contagem-de-partida.xlsx` — a contagem simulada dos 49 produtos de
exemplo da J2 (o mercado é fictício). Numa loja de verdade, a equipe contaria prateleira por
prateleira e anotaria nesta planilha, antes de o sistema começar a valer.

---

## Como lançar

```bash
python backend/manage.py carregar_produtos docs/exemplos/produtos-iniciais.xlsx    # J2, antes
python backend/manage.py carregar_contagem docs/exemplos/contagem-de-partida.xlsx
```

**Decisão do grupo (12/11/2026):** a contagem entra **como entrada de mercadoria**, pelo mesmo
serviço da tela de Entrada. Cada linha contada vira um **lote** com a sua movimentação `ENTRADA`,
marcada com `origem = 'INVENTARIO'` — um valor novo na coluna `movimentacao.origem`, que já existe
e não tem restrição no banco (o `schema.sql` cita `TELA`, `IMPORTACAO_PDV` e `AJUSTE` só num
comentário). Assim o perecível contado já tem validade, entra no aviso de validade (RN05) e sai
pelo lote que vence primeiro (RN02).

- **Tudo ou nada:** se uma linha estiver errada, nada é lançado; o comando lista todas (linha no
  Excel e coluna).
- **É de partida:** produto que já tinha estoque registrado antes da carga é mantido como está.
  Rodar de novo não lança a contagem duas vezes. Correção depois disso é pela tela de Entrada ou
  de Avarias, que deixam rastro.

## A aba Contagem

O nome da aba e das colunas é procurado sem diferenciar maiúscula nem acento; a ordem das colunas
não importa. Linha em branco é ignorada. **O mesmo produto pode vir em várias linhas, uma por
validade** — cada linha vira um lote.

| Coluna | Obrigatória | Formato | Exemplo | Vai para |
|---|---|---|---|---|
| **Produto** | sim | nome como está no cadastro (sem diferenciar maiúscula nem acento) | `Frango resfriado 1 kg` | `lote.produto_id` |
| **Categoria** | só se o nome existir em duas categorias | nome da categoria | `Açougue` | (escolhe o produto) |
| **Quantidade contada** | sim | 0 ou mais, até 3 casas; **zero não lança nada** | `3,5` | `lote.quantidade_inicial` e `movimentacao.quantidade` |
| **Validade** | não | dd/mm/aaaa, como na embalagem | `20/11/2026` | `lote.data_validade` |
| **Custo unitário** | não | em reais, 2 casas | `11,80` | `lote.custo_unitario` (perdas no balanço, I3) |

**Validade (RN04):** produto perecível sem validade na planilha ganha **data da contagem +
durabilidade** do produto. Validade que já passou é recusada — produto vencido não é estoque:
sai pela tela de Avarias e quebras. Produto não perecível pode ficar sem validade.

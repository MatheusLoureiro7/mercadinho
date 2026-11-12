# Formato da planilha de carga dos produtos

Tarefa **J2** · feito pelo grupo em **12/11/2026** · base: RF01 (cadastro de produtos), RF02
(fornecedores), RF15 (produtos críticos), RN03 e as tabelas `categoria`, `fornecedor` e `produto`
da Apostila IV.

Exemplo pronto: `docs/exemplos/produtos-iniciais.xlsx` (9 categorias, 6 fornecedores, 49 produtos).
O Mercado do Sr. João é fictício (decisão de 30/10/2026): a lista é de exemplo, feita pelo grupo.
Numa loja de verdade, a esposa preencheria esta mesma planilha junto com a equipe.

---

## Como carregar

```bash
python backend/manage.py carregar_produtos docs/exemplos/produtos-iniciais.xlsx
```

- Cada linha passa pelas **mesmas conferências da tela de Produtos** (operação 01): nome
  obrigatório, unidade KG, UN, L ou PCT (L17), nome único na categoria, prazo de entrega do
  fornecedor e a **RN03** (perecível precisa dizer quantos dias dura).
- **Tudo ou nada:** se uma linha estiver errada, nada é gravado. O comando lista todas as linhas
  com problema — aba, número da linha no Excel e coluna — para corrigir de uma vez.
- **Rodar de novo não duplica:** o que já está cadastrado com o mesmo nome é mantido como está.
  A planilha não altera cadastro existente; alteração é pela tela de Produtos.

## As abas

Três abas, na ordem em que o cadastro depende uma da outra. O nome das abas e das colunas é
procurado sem diferenciar maiúscula nem acento; a ordem das colunas não importa. Linha em branco é
ignorada. **Categorias** e **Fornecedores** podem faltar se já estiverem cadastrados.

### Categorias

| Coluna | Obrigatória | Formato | Exemplo | Vai para |
|---|---|---|---|---|
| **Categoria** | sim | texto, até 80 letras | `Açougue` | `categoria.nome` |
| **Perecível** | não | `sim` ou `não` (vazio = não) | `sim` | `categoria.perecivel_padrao` |

### Fornecedores

| Coluna | Obrigatória | Formato | Exemplo | Vai para |
|---|---|---|---|---|
| **Fornecedor** | sim | texto | `Frigorífico Boi Bom` | `fornecedor.nome` |
| **Prazo de entrega (dias)** | sim | número inteiro, 0 ou mais | `3` | `fornecedor.prazo_entrega_dias` |
| **Pedido mínimo (R$)** | não | em reais, 2 casas (L24) | `800,00` | `fornecedor.pedido_minimo` |
| **Contato** | não | texto | `(11) 3333-4444` | `fornecedor.contato` |

### Produtos

| Coluna | Obrigatória | Formato | Exemplo | Vai para |
|---|---|---|---|---|
| **Produto** | sim | texto | `Frango resfriado 1 kg` | `produto.nome` |
| **Categoria** | sim | nome de uma categoria da aba Categorias ou já cadastrada | `Açougue` | `produto.categoria_id` |
| **Unidade** | sim | `KG`, `UN`, `L` ou `PCT` (L17) | `KG` | `produto.unidade_medida` |
| **Perecível** | não | `sim` ou `não`; vazio = o padrão da categoria (L19) | | `produto.perecivel` |
| **Dura quantos dias** | se perecível (**RN03**) | número inteiro maior que zero | `4` | `produto.durabilidade_dias` |
| **Preço de custo** | não | em reais, 2 casas | `11,80` | `produto.preco_custo` |
| **Preço de venda** | não | em reais, 2 casas | `17,90` | `produto.preco_venda` |
| **Estoque mínimo** | não | até 3 casas (carne em quilo fracionado) | `10` | `produto.estoque_minimo` |
| **Fornecedor** | não | nome de um fornecedor da aba Fornecedores ou já cadastrado | `Frigorífico Boi Bom` | `produto.fornecedor_padrao_id` |
| **Não pode faltar no fim de semana** | não | `sim` ou `não` (vazio = não) — RF15, RN10 | `sim` | `produto.critico_fim_semana` |

Na planilha de exemplo, as colunas **Unidade**, **Perecível** e **Não pode faltar no fim de
semana** têm lista de escolha, para não escrever errado.

## O que a planilha não faz

- Não lança estoque: o saldo de partida é a contagem física da **J3**, que entra como movimentação
  (RN01 — saldo só nasce de movimentação).
- Não cria usuário nem altera parâmetro.
- Nenhuma coluna nova no banco: tudo cabe nas tabelas da Apostila IV.

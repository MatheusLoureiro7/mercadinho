# Painel web (HTML + CSS + JS puro)

Arquivos estáticos que consomem a API REST por `fetch`. Nunca acessam o banco (Apostila IV,
seção 3). Sem framework, sem biblioteca, sem fonte externa — o computador da loja é antigo (RNF06).

| Arquivo | O quê |
|---|---|
| `design-system/mercado-do-sr-joao/MASTER.md` | Sistema de design gerado pela UI UX Pro Max, com as **adaptações do projeto** no topo |
| `css/base.css` | Cores, espaçamento, cabeçalho, botões, formulário, tabela, etiquetas |
| `js/formatos.js` | Dinheiro e quantidade no formato brasileiro; "12,90" digitado → "12.90" para a API |
| `js/dados-de-exemplo.js` | Faz o papel da API até a B7 (mesmo formato de resposta e de erro). Sai na B7 |
| `produtos.html` · `js/produtos.js` | Tela de Produtos (B5) |

Telas por tarefa: B5 Produtos · B6 Fornecedores · C5 Entrada de mercadoria · D3 Avarias e
quebras · E5 Importação de vendas · F3 Consulta de estoque · I2 Fechamento de caixa. Toda tela é
feita com a skill **UI UX Pro Max** e conferida com a skill **accessibility** (CLAUDE.md).

## Ver as telas

```bash
cd frontend
python -m http.server 8090      # http://127.0.0.1:8090/produtos.html
```

Até a B7 as telas usam dados de exemplo e não precisam da API rodando.

## Regras de tela

- Rótulo sempre visível; erro embaixo do campo e resumo no topo, que recebe o foco.
- Recusa da API: **manter tudo o que foi digitado** e apontar só o campo com problema (fluxograma 01).
- A tela não decide regra de negócio — mostra o que a API responde.
- Alvos de clique com no mínimo 44 px; texto base 16 px; contraste WCAG AA; foco visível.
- Precisa funcionar em 1024 px (o computador da loja) sem rolar de lado, e em 375 px.
- Vocabulário da loja (RNF10): "Não pode faltar no fim de semana", nunca "crítico".

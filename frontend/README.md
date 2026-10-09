# Painel web (HTML + CSS + JS puro)

Arquivos estáticos que consomem a API REST por `fetch`. Nunca acessam o banco (Apostila IV,
seção 3). Sem framework, sem biblioteca, sem fonte externa — o computador da loja é antigo (RNF06).

| Arquivo | O quê |
|---|---|
| `design-system/mercado-do-sr-joao/MASTER.md` | Sistema de design gerado pela UI UX Pro Max, com as **adaptações do projeto** no topo |
| `css/base.css` | Cores, espaçamento, cabeçalho, botões, formulário, tabela, etiquetas |
| `js/formatos.js` | Dinheiro e quantidade no formato brasileiro; "12,90" digitado → "12.90" para a API |
| `js/api.js` | **Porta única para a API** (B7): token, sem conexão, demora e sessão vencida tratados num lugar |
| `js/sessao.js` | Sessão e menu do perfil (B7, RN14): token na aba, telas do papel, guarda de cada tela |
| `js/falha.js` | Linha "Não foi possível carregar a lista" com "Tentar de novo" (B7) |
| `login.html` · `js/login.js` | Tela de Login (B7, L22) |
| `produtos.html` · `js/produtos.js` | Tela de Produtos (B5, ligada à API na B7) |
| `fornecedores.html` · `js/fornecedores.js` | Tela de Fornecedores (B6, ligada à API na B7) |
| `entrada-mercadoria.html` · `js/entrada-mercadoria.js` | Tela de Entrada de mercadoria (C5, RF03, fluxograma 02) |
| `avarias.html` · `js/avarias.js` | Tela de Avarias e quebras (D3, RF04, fluxograma 03) |
| `js/formulario.js` | Erros embaixo do campo, resumo com foco, confirmação no formulário (telas de registro) |
| `js/procurar-produto.js` | "Procurar o produto" sem acento numa lista nativa (Entrada, Avarias) |
| `consulta-estoque.html` · `js/consulta-estoque.js` | Tela de Consulta de estoque (F3, RF07, RN16) — os três perfis |
| `js/tabela-cartoes.js` | Até 860 px (celular e tablet), cada linha de tabela vira um cartão "rótulo: valor"; põe o nome da coluna em cada célula e os papéis de tabela para o leitor de tela |
| `js/situacao.js` | Situação do lote em palavra e cor: vencido, vence em N dias… (Avarias, Consulta) |
| `servir.py` | Servidor de desenvolvimento: painel + `/api/` repassado ao Django, mesma origem (L25) |

Telas por tarefa: B5 Produtos · B6 Fornecedores · C5 Entrada de mercadoria · D3 Avarias e
quebras · E5 Importação de vendas · F3 Consulta de estoque · I2 Fechamento de caixa. Toda tela é
feita com a skill **UI UX Pro Max** e conferida com a skill **accessibility** (CLAUDE.md).

## Ver as telas

```bash
python backend/manage.py runserver      # a API
python frontend/servir.py               # o painel: http://127.0.0.1:8090/ (abre o Login)
```

As telas falam com a API de verdade desde a B7: é preciso um usuário (`criar_usuario`, no README
principal). O endereço da API nunca é escrito no código do painel — é sempre `/api/...`.

## Nova tela (C5, D3, F3, I2…)

1. No começo do script: `if (!(await entrarNaTela("chave_da_tela"))) return;` — a chave é a da
   tabela `ACESSO_POR_TELA` (RN14). Ela confere a sessão, monta o menu e recusa outro perfil.
2. Em `js/sessao.js`, troque `endereco: null` da tela pelo nome do arquivo: ela entra no menu.
3. Toda chamada à API por `api.ler` / `api.criar` / `api.alterar`; nunca `fetch` direto (um teste
   confere). A resposta é sempre `{ ok, status, dados }` ou `{ ok, status, erro }`.

## Regras de tela

- Rótulo sempre visível; erro embaixo do campo e resumo no topo, que recebe o foco.
- Recusa da API: **manter tudo o que foi digitado** e apontar só o campo com problema (fluxograma 01).
- A tela não decide regra de negócio — mostra o que a API responde.
- Lista que não carregou diz o porquê e oferece "Tentar de novo"; nunca aparece como vazia.
- Tela de registro em sequência (Entrada, Avarias): a confirmação fica no topo do formulário até o
  próximo registro, não num aviso flutuante que cobriria os campos (C5).
- Tabela sem botão dentro: a área que rola de lado recebe `tabindex="0"`, `role="region"` e nome,
  para rolar pelo teclado no celular (WCAG 2.1.1, C5).
- Erro embaixo do campo some enquanto a pessoa corrige (`input`), nunca no `blur`: sumir no `blur`
  encolhe o formulário no meio do clique em "Salvar" e o clique se perde (achado na B7).
- Alvos de clique com no mínimo 44 px; texto base 16 px; contraste WCAG AA; foco visível.
- Precisa funcionar em 1024 px (o computador da loja) sem rolar de lado, e em 375 px.
- Vocabulário da loja (RNF10): "Não pode faltar no fim de semana", nunca "crítico".

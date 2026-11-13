# Contratos da API

> Gerado automaticamente por `docs/sistema/gerar.py` a partir do código. Não edite à mão: a suíte de testes falha se este arquivo ficar diferente do código.

A API REST é a porta única de entrada (Apostila IV, seção 3). Tudo é JSON. Toda requisição,
fora a entrada no sistema e o webhook do Telegram, leva `Authorization: Bearer <token>`; o
perfil (RN14) é conferido antes de qualquer operação, pela tela que cada endereço declara.

Formato de erro, igual em toda a API (`backend/comum/erros.py`):

```
{"erro": {"codigo": "validacao", "mensagem": "Confira os campos destacados.",
          "campos": {"durabilidade_dias": ["..."]}, "regra": "RN03"}}
```

| Endereço | Métodos | Quem pode usar | O que faz |
|---|---|---|---|
| `/api/` | GET | qualquer pessoa com login | Lista os endereços da API para quem já entrou. |
| `/api/balancos/` | GET | tela `balanco_semana` — GESTAO | GET ?semana=AAAA-MM-DD: vendas, perdas e resultado da semana (RF13, L16). |
| `/api/categorias/` | GET, POST | tela `produtos` — OPERACAO | GET lista; POST cria categoria, de dentro da tela de Produtos (B2, L18). |
| `/api/categorias/{pk}/` | GET, PATCH, PUT | tela `produtos` — OPERACAO | GET uma categoria; PUT/PATCH altera. Não existe exclusão (tabela de origem). |
| `/api/estoque/` | GET | tela `consulta_estoque` — DONO, GESTAO, OPERACAO | Saldo de cada produto, com abaixo do mínimo e vencidos (RF07, RN01, RN16). |
| `/api/estoque/lotes/` | GET | tela `consulta_estoque` — DONO, GESTAO, OPERACAO | Os lotes de cada produto, do que vence primeiro ao último (RN02, RN16). |
| `/api/fechamentos/` | GET, POST | tela `fechamento_caixa` — GESTAO | GET fechamentos do dia; POST {valor_contado} registra o fechamento (RF12, RN15). |
| `/api/fechamentos/apurado/` | GET | tela `fechamento_caixa` — GESTAO | O valor apurado pelo sistema: vendas em dinheiro do dia do fechamento (L12). |
| `/api/fornecedores/` | GET, POST | tela `fornecedores` — OPERACAO | GET lista (filtro por nome); POST cadastra fornecedor (RF02). |
| `/api/fornecedores/{pk}/` | GET, PATCH, PUT | tela `fornecedores` — OPERACAO | GET um fornecedor; PUT/PATCH altera. Não existe exclusão. |
| `/api/importacoes/` | GET | tela `importacao_vendas` — OPERACAO | As últimas 30 planilhas do caixa lidas, com a situação de cada uma (E5). |
| `/api/itens-pendentes/` | GET | tela `importacao_vendas` — OPERACAO | Vendas da planilha que não casaram com o cadastro, para conferir (E4, L26). |
| `/api/itens-pendentes/{pk}/casar/` | POST | tela `importacao_vendas` — OPERACAO | POST {produto}: liga a venda ao produto e baixa o estoque no dia da venda (RN01, RN02). |
| `/api/lotes/` | GET, POST | tela `entrada_mercadoria` — OPERACAO | GET lotes do dia ou do produto; POST registra a mercadoria que chegou, com a RN04 (operação 02). |
| `/api/lotes/{pk}/` | GET | tela `entrada_mercadoria` — OPERACAO | GET um lote. Lote não se edita nem se apaga (RN01). |
| `/api/perdas/` | GET, POST | tela `avarias` — OPERACAO | GET perdas do dia; POST registra perda com motivo, saindo do lote certo (RF04, RN02, RN16). |
| `/api/perdas/{pk}/` | GET | tela `avarias` — OPERACAO | GET uma perda. Perda não se edita nem se apaga (RN01). |
| `/api/produtos/` | GET, POST | tela `produtos` — OPERACAO | GET lista (filtros por nome e categoria); POST cadastra produto, com a RN03 (RF01, RF15). |
| `/api/produtos/{pk}/` | GET, PATCH, PUT | tela `produtos` — OPERACAO | GET um produto; PUT/PATCH altera, com a RN03. Não existe exclusão. |
| `/api/sessoes/` | POST | sem login (entrada no sistema) | POST {login, senha}: entra no sistema e recebe o token (A4, L09). |
| `/api/sessoes/atual/` | GET | qualquer pessoa com login | Quem está usando e as telas do menu daquele perfil (RN14). |
| `/api/telegram/` | POST | segredo do Telegram (H7) | Webhook: recebe o toque do Sr. João em "Sim, pedir" (H7). Só com o segredo do Telegram. |

O detalhe de cada campo está no serializer correspondente (`backend/*/serializers.py`) e nos testes da tarefa.

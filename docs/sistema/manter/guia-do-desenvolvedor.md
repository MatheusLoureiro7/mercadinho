# Guia do desenvolvedor e testes

*Atualizado em 16/11/2026.* Como subir o ambiente, os padrões do código e como rodar os testes. O
passo a passo de instalação está no `README.md` (macOS e Linux) e no `COMO-RODAR.md` (Windows, do
zero) — este guia não repete, aponta.

## Ambiente em 5 comandos

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt && playwright install chromium
cp .env.example .env            # DJANGO_SECRET_KEY e POSTGRES_PASSWORD
docker compose up -d --wait     # o PostgreSQL
python backend/manage.py migrate && pytest
```

## Onde fica cada coisa

| Pasta | O quê |
|---|---|
| `backend/<módulo>/` | `models.py` (tabelas), serviços com as regras (`entrada.py`, `projecao.py`…), `serializers.py`, `views.py`, `management/commands/` |
| `backend/tests/` | Um arquivo por tarefa (`test_g2_consumo_medio.py`), `conftest.py` com as funções comuns |
| `frontend/` | Uma página por tela + `js/` (um script por tela; `api.js` é a porta única para a API) + `css/` |
| `docs/` | Especificação entregue (não editar sem decisão do grupo), roteiro, acompanhamento, lacunas |
| `docs/sistema/` | Esta documentação: os `.md`, o gerador (`gerar.py`) e o estilo e o script da página (`modelo/`) |
| `schema.sql` | O modelo de dados da Apostila IV — referência que os testes conferem |

## Padrões

- **Português** em tudo: tabelas, colunas e endpoints com os nomes exatos da Apostila IV; endpoints no plural.
- **Dinheiro e quantidade em `Decimal`**, nunca `float`. Quantidade com 3 casas (carne em quilo fracionado).
- **"Hoje" é `timezone.localdate()`** (fuso de São Paulo), nunca `date.today()` nem o `CURRENT_DATE` do banco.
- **Regra em módulo de serviço**, com `transaction.atomic`; nada de regra na view ou na tela.
- **Todo endpoint declara `tela`** (RN14). Nunca `AllowAny` fora da entrada no sistema.
- **Conferir e gravar, só sob trava.** Processo que pergunta "já existe?" e depois grava (importação,
  avisos) chama `comum.trava.travar(nome)` dentro do `transaction.atomic` (ADR-013).
- **Número digitado na tela** passa por `numerosAmbiguos` antes de `numeroParaApi` (`js/formatos.js`);
  um teste de guarda falha se uma tela nova esquecer.
- **Vocabulário da loja** nas mensagens (RNF10): "o frango acaba em 2 dias".
- **Dependência nova só com decisão do grupo.** `ruff check` e `ruff format` antes de cada commit.
- **Um commit por tarefa**, começando pelo código dela: `G2: consumo médio e por dia da semana (RN06, RN07)`.

## Testes

| Comando | O quê |
|---|---|
| `pytest` | A suíte inteira (~2 minutos), no PostgreSQL, num banco próprio (`test_mercadinho`) |
| `pytest -m "not tela"` | Sem os testes de tela no navegador (bem mais rápido) |
| `pytest backend/tests/test_g2_consumo_medio.py` | Os testes de uma tarefa |

- Teste escrito **antes** do código e **visto falhar** pelo motivo certo; nome com a regra:
  `test_rn03_perecivel_sem_durabilidade_e_recusado`.
- Teste de tela não basta para desenho: confira a captura no computador e em 375 px (foi assim que
  apareceu o botão que o CSS não escondia, na revisão X1).
- Cada losango dos fluxogramas da Apostila II vira dois testes: o "sim" e o "não".
- Ao fim de cada tarefa, **defeitos de propósito**: muda-se o código para errado e confere-se que algum teste falha.
- Testes de guarda: tabela igual ao `schema.sql`, previsão sem ler movimentação direto (RN11), toda
  regra com teste (J1) e documentação em dia (`test_documentacao.py`).

## Ao terminar uma tarefa
1. Marcar no `docs/ROTEIRO.md` e no `docs/ACOMPANHAMENTO.md` (data, commit, diário).
2. Atualizar `docs/sistema/` conforme a tabela "Como alimentar" do `LEIA-ME.md` e rodar
   `python docs/sistema/gerar.py`.

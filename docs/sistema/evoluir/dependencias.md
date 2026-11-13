# Inventário de dependências (SBOM)

> Gerado automaticamente por `docs/sistema/gerar.py` a partir do código. Não edite à mão: a suíte de testes falha se este arquivo ficar diferente do código.

Só as bibliotecas que o projeto pede (`requirements.txt` e `requirements-dev.txt`); o resto vem
junto com elas. Dependência nova só entra com decisão do grupo (CLAUDE.md). Nenhuma biblioteca
roda no navegador: o painel é HTML, CSS e JavaScript puros, com fontes servidas pelo próprio
painel (licença OFL, `frontend/fontes/`).

| Biblioteca | Pedida | Instalada | Licença | Uso | Para quê | Suporte |
|---|---|---|---|---|---|---|
| Django | `>=5.2,<6` | 5.2.18 | BSD-3-Clause | execução | — | 5.2 é LTS: correções de segurança até abril de 2028 |
| djangorestframework | `>=3.15,<4` | 3.18.3 | BSD-3-Clause | execução | — | acompanha as versões do Django |
| psycopg | `(binary)>=3.2,<4` | 3.3.6 | LGPL-3.0-only | execução | driver do PostgreSQL (Apostila IV fixa o banco) | série 3, ativa |
| python-dotenv | `>=1.0,<2` | 1.2.4 | BSD-3-Clause | execução | lê o arquivo .env | ativa |
| openpyxl | `>=3.1,<4` | 3.1.5 | MIT License | execução | lê a planilha de vendas do caixa (D01 = Excel; decisão do grupo, 05/11/2026) | ativa |
| pytest | `>=8,<9` | 8.4.2 | MIT License | desenvolvimento | — | série 8, ativa |
| pytest-django | `>=4.9,<5` | 4.14.0 | BSD License | desenvolvimento | — | ativa |
| pytest-playwright | `>=0.7,<0.10` | 0.9.0 | Apache Software License | desenvolvimento | — | ativa |
| ruff | `>=0.6` | 0.16.10 | MIT | desenvolvimento | — | ativa |

Componentes fora do Python: **PostgreSQL 17** (fixado pela Apostila IV; suporte até novembro de
2029), rodando em contêiner Docker (`docker-compose.yml`), e **Python 3.11 ou mais novo** (3.11
tem suporte até outubro de 2027). A versão de cada um no computador do Matheus está na
matriz de compatibilidade (`evoluir/compatibilidade.md`).

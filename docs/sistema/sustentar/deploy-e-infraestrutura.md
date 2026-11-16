# Deploy e infraestrutura

*Atualizado em 16/11/2026.* Onde o sistema roda, como é publicado e onde ficam os segredos.

## Onde roda

Decisão D05 (30/10/2026): **no computador do Matheus**. O professor assiste à demonstração.

| Peça | Endereço | Como sobe |
|---|---|---|
| Banco PostgreSQL 17 | 127.0.0.1:5432 (só a própria máquina) | `docker compose up -d --wait` (`docker-compose.yml`) |
| API Django | 127.0.0.1:8000 | `publicar.py` (servidor do Django, `--noreload`) |
| Painel | 127.0.0.1:8090 (repassa `/api/` para a API) | `publicar.py` (`frontend/servir.py`) |
| Rodada diária | — | cron: 03h00 `rodada_diaria`; 13h00 e 18h00 `enviar_avisos`; de hora em hora (aos 30 min) `rodada_diaria --se-faltar` |

Infraestrutura como código: o banco é descrito no `docker-compose.yml`; as linhas do cron saem do
comando `agenda_cron`, a partir da tabela de parâmetros.

## Esteira de publicação (A5)

```
python publicar.py                  # atualiza, confere, testa e, se tudo passar, publica
python publicar.py --sem-atualizar  # sem git pull
python publicar.py --parar          # desliga API e painel
```

Ordem: `git pull` → dependências → banco → `ruff check` → `ruff format --check` → **todos os
testes** → migrações → troca da API e do painel → confere que respondem. Se um passo falha, nada
muda no que está no ar. Cada publicação vai para `logs/publicacoes.log`.

**Integração contínua:** não há servidor de CI (GitHub Actions ou similar); a suíte roda na própria
esteira, antes de cada publicação, e a cada tarefa. Ver o roadmap.

## Instalar a rodada diária (uma vez)

```
python backend/manage.py agenda_cron   # mostra as 4 linhas com os caminhos desta máquina
crontab -e                             # cole as linhas no fim e salve
```

O computador deve estar **ligado às 03h00** e no **horário de São Paulo**. Se estiver desligado ou
dormindo, a linha de hora em hora (`--se-faltar`) faz a rodada assim que ele voltar: o dia da última
rodada fica anotado em `logs/ultima-rodada.txt` (revisão X1, item 11). **Quem já instalou o crontab
antes de 16/11/2026 precisa gerar as linhas de novo e trocar** — a quarta linha é nova. No macOS, se o cron
não ler a pasta, dar a ele *Acesso Total ao Disco*.

## Segredos

Ficam **só no arquivo `.env`** da raiz, que **nunca vai para o git** (RNF12). Modelo: `.env.example`.

| Variável | Para quê |
|---|---|
| `DJANGO_SECRET_KEY` | Assina os tokens de sessão. Obrigatória com `DJANGO_DEBUG=false` |
| `DJANGO_DEBUG` | `true` só em desenvolvimento. O `publicar.py` sobe a API com `false` de qualquer jeito (revisão X1, item 20) |
| `DJANGO_ALLOWED_HOSTS` | Endereços pelos quais a API aceita ser chamada |
| `SESSAO_VALIDADE_HORAS` | Quanto dura a sessão (12 horas) |
| `API_NUM_PROXIES` | Quantos repassadores há na frente da API; usado no limite de tentativas de login (0 em desenvolvimento) |
| `POSTGRES_*` | Conexão com o banco (o Docker usa as mesmas) |
| `TELEGRAM_BOT_TOKEN` | O bot dos avisos. Vazio: os avisos ficam guardados e não saem |
| `TELEGRAM_WEBHOOK_SEGREDO` | Segredo que o Telegram manda no webhook do "Sim, pedir" |
| `PASTA_VENDAS_CAIXA` | Pasta onde o sobrinho salva a planilha do caixa |
| `LOG_ARQUIVO`, `LOG_NIVEL` | Onde e quanto registrar no log |

## Limites conhecidos
- O webhook do "Sim, pedir" só funciona com o sistema num endereço `https://` público; rodando só no
  computador do Matheus, a mensagem e o botão chegam, mas o toque não volta ao sistema (J6).
- O servidor do Django é para demonstração (ADR-011).

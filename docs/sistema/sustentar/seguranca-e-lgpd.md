# Segurança e LGPD

*Atualizado em 16/11/2026.* Base: RNF12 (segurança básica), RN14 (perfis) e a Lei Geral de Proteção
de Dados (Lei 13.709/2018).

## Acessos

| Controle | Como é feito | Onde |
|---|---|---|
| Três perfis, cada um só com as suas telas | Perfil conferido antes de qualquer operação, pela tela que o endpoint declara; endpoint sem tela é recusado | `comum/permissoes.py` (RN14) |
| Senha | Guardada só como hash (algoritmo do Django); nunca aparece na tela nem no log | `cadastro/models.py` |
| Sessão | Token assinado, válido por 12 horas; cai antes se a senha for trocada ou o usuário desativado | `comum/autenticacao.py` |
| Funcionários da loja | Não têm usuário | RN14 |
| Banco | Só aceita conexão da própria máquina (127.0.0.1); sem acesso externo | `docker-compose.yml` |
| Webhook do Telegram | Só aceita quem traz o segredo combinado, comparado em tempo constante; só grava resposta do chat do dono | `comum/permissoes.py`, `alertas/respostas.py` |
| Segredos | Só no `.env`, fora do git | ver deploy |
| Página técnica de erro | Nunca aparece no sistema publicado: o `publicar.py` sobe a API com `DJANGO_DEBUG=false`, qualquer que seja o `.env` | `publicar.py` |
| Endereço ou número inválido | Responde erro de validação ou "não encontrado" em JSON, nunca erro interno | `comum/erros.py` |

## Dados pessoais (LGPD)

| Dado | De quem | Para quê | Onde |
|---|---|---|---|
| Nome e login | Os 3 usuários | Entrar no sistema e saber quem registrou | `usuario` |
| Chat do Telegram | Sr. João | Mandar os avisos | `usuario.telegram_chat_id` |
| Quem registrou cada entrada, perda e fechamento | Os 3 usuários | Rastro das operações (RN01, RN15) | `movimentacao`, `fechamento_caixa` |

**O sistema não guarda dado de cliente da loja:** a planilha do caixa traz cupom, produto, preço e
forma de pagamento — sem nome, CPF ou cartão. Os dados acima são dos próprios donos e do sobrinho,
usados para operar a loja (base legal: execução do trabalho e legítimo interesse). Usuário que sai
é desativado, não apagado, porque o rastro das operações precisa continuar (RN15).

## Base de conhecimento — incidentes recorrentes
Nenhum incidente de segurança registrado até 16/11/2026. A revisão X1 (16/11/2026) encontrou e
corrigiu um ponto de exposição: o modelo de configuração vinha com o modo de depuração ligado. Os problemas de operação conhecidos estão
nos runbooks (`sustentar/runbooks.md`); as dúvidas de uso, na FAQ.

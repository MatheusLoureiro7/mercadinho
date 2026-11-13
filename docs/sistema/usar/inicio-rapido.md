# Guia de início rápido

*Atualizado em 13/11/2026.* Os primeiros passos de cada pessoa, em poucos minutos. O manual completo
está em `usar/manual-do-usuario.md`.

## Antes do primeiro dia (a equipe faz uma vez)

1. Criar os três usuários: `python backend/manage.py criar_usuario --login sobrinho --nome "Sobrinho" --papel OPERACAO`
   (e o mesmo para `esposa`/GESTAO e `joao`/DONO). A senha é pedida duas vezes.
2. Carregar os produtos pela planilha (J2): `python backend/manage.py carregar_produtos produtos.xlsx`.
3. Lançar a contagem de partida (J3): `python backend/manage.py carregar_contagem contagem.xlsx`.
4. Ligar o celular do Sr. João: `python backend/manage.py vincular_telegram --login joao` — abra o
   link que aparece no celular dele e toque em **Iniciar**.
5. Colocar no ar: `python publicar.py` e instalar a rodada das 03h00 (`agenda_cron`, ver
   `sustentar/deploy-e-infraestrutura.md`).

## Sobrinho — 5 minutos
1. Entre com o seu login. O menu mostra as suas cinco telas.
2. Chegou mercadoria? **Entrada de mercadoria** → procure o produto → quantidade, validade → **Registrar**.
3. Algo estragou? **Avarias e quebras** → produto → quanto → motivo → **Registrar perda**.
4. Toda manhã, olhe **Importação de vendas**: se houver venda para conferir, escolha o produto dela.
5. Salve a planilha do caixa do dia na pasta combinada antes de ir embora.

## Esposa — 3 minutos
1. Entre com o seu login.
2. De manhã: **Fechamento de caixa** → digite o dinheiro contado na gaveta ontem → **Registrar fechamento**.
3. Segunda-feira: **Balanço da semana** → **Semana anterior** para ver a semana fechada.

## Sr. João — 1 minuto
Nada a fazer no computador: os avisos chegam no Telegram. Quando aparecer "vai acabar", toque em
**Sim, pedir** se for pedir. Quer conferir algo? **Consulta de estoque** com o seu login.

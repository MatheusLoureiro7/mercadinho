# Guias de migração

*Atualizado em 13/11/2026.* Como passar de uma versão para outra, ou trocar uma peça, sem perder dado.

## De uma versão do sistema para a seguinte
1. Cópia do banco (`sustentar/backup-e-continuidade.md`).
2. `python publicar.py` — atualiza o código, roda todos os testes e só então aplica as migrações.
3. Ler o `evoluir/changelog.md` da versão: se houver "Quebra", seguir o passo a passo que vem junto.
Até a 0.3.1 nenhuma versão exigiu conversão de dado: as migrações só criaram tabelas novas.

## Scripts de dados

| Situação | Comando |
|---|---|
| Carregar produtos de uma planilha | `python backend/manage.py carregar_produtos arquivo.xlsx` |
| Lançar a contagem de partida | `python backend/manage.py carregar_contagem arquivo.xlsx` |
| Recalcular o consumo depois de mudar uma regra (ex.: L27) | `python backend/manage.py agregar_consumo --desde AAAA-MM-DD` |
| Recalcular a previsão | `python backend/manage.py calcular_previsao` |
| Reimportar planilhas do caixa | `python backend/manage.py importar_vendas` |

Consumo, previsão e avisos são dados calculados: podem ser apagados e refeitos. As tabelas de
origem (lote, movimentação, venda, fechamento) nunca são apagadas nem reescritas.

## Trocar uma peça

| Troca | Passos |
|---|---|
| Django 5.2 → 6.x | Ler as notas de versão; subir em `requirements.txt`; `pip install`; `python -Wd backend/manage.py check`; rodar a suíte inteira. Fazer antes de abril de 2028 (fim do suporte da 5.2) |
| Python | Criar um `.venv` novo na versão nova, instalar e rodar a suíte |
| PostgreSQL 17 → maior | `pg_dump` na versão velha, trocar a imagem no `docker-compose.yml`, banco novo, restaurar e rodar a suíte |
| Formato da planilha do caixa | Escrever um leitor novo que siga a interface `LeitorDeArquivoDoCaixa` (`vendas/leitor.py`) e testar com uma planilha do caixa novo; o importador não muda (ADR-007) |
| Canal de aviso (outro no lugar do Telegram) | Escrever uma classe que siga `CanalDeAviso` (`alertas/canal.py`); as regras não mudam (ADR-009) |

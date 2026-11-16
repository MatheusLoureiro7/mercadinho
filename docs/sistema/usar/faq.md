# Perguntas frequentes

*Atualizado em 16/11/2026.* Dúvidas e erros comuns, com o que fazer. Problema técnico (sistema fora
do ar, aviso que não sai) está nos runbooks: `sustentar/runbooks.md`.

**A venda de ontem não apareceu.**
As vendas entram de madrugada, às 03h00, a partir da planilha do caixa salva na pasta combinada.
Veja em **Importação de vendas → Planilhas lidas**: se a planilha "Não foi lida", confira se é do
Excel (.xlsx), se tem as colunas combinadas e se cada linha está no formato (data dd/mm/aaaa, hora
hh:mm, quantidade e preço com números): uma única linha errada impede a planilha inteira de entrar.
Corrija e salve de novo na pasta; ela é tentada de novo na madrugada seguinte.

**Salvei a planilha do mesmo dia duas vezes, com nomes diferentes. A venda vai contar em dobro?**
Não. O sistema reconhece as vendas pelo dia, não pelo nome do arquivo: o dia que já entrou é
ignorado na cópia. Na madrugada, o registro da rodada diz "as vendas desta planilha já tinham
entrado". Pode apagar a cópia da pasta.

**Apareceu "venda para conferir". O que é?**
O caixa escreveu o produto com um nome que o cadastro não tem. Ache a linha na planilha pela data,
hora e preço e escolha o produto em **Importação de vendas**. Para não repetir, deixe o nome no
cadastro igual ao do caixa.

**O estoque de um produto ficou negativo.**
A planilha mostrou uma venda maior do que o estoque registrado. A venda é gravada inteira, porque
ela aconteceu: o negativo mostra que faltou registrar uma entrada ou que a contagem estava errada.
Registre a entrada que faltou.

**O produto aparece "ainda aprendendo".**
O sistema só calcula quando acaba depois de 14 dias de venda daquele produto (RN09). Até lá, não
mostra número, para não dar um "acaba em 2 dias" errado.

**Não consigo registrar o lote: "Essa validade já passou".**
Validade anterior a hoje é recusada (RN04). Confira a data na embalagem. Mercadoria vencida não
entra: vai direto para Avarias e quebras.

**Não consigo salvar um produto perecível.**
Perecível precisa dizer quantos dias dura (RN03). Preencha "Dura quantos dias".

**Registrei uma perda errada. Como apago?**
Perda, lote e fechamento de caixa **não se apagam** (RN01, RN15): são o registro do que aconteceu.
Uma perda a mais se corrige registrando a entrada correspondente; um fechamento errado, registrando
outro fechamento — o anterior continua visível.

**O Sr. João não recebeu o aviso.**
Nos horários de movimento (10h30–13h00 e 16h30–18h00) nada é enviado: o aviso sai no fim do
horário. Depois de "Sim, pedir", o produto não é avisado de novo até a mercadoria chegar. Se nada
chegou fora desses casos, ver `sustentar/runbooks.md`.

**De onde vem a quantidade "Pedir 30 KG"?**
É o que o produto deve vender no prazo de entrega do fornecedor mais 7 dias, menos o que já tem
(L15). Produto vendido por unidade ou pacote é arredondado para cima. Ver o glossário.

**O fechamento de caixa diz que as vendas ainda não entraram.**
O fechamento é do dia anterior e só pode ser feito depois que a planilha daquele dia foi importada.
Confira a planilha em Importação de vendas.

**O balanço mostra "não entrou" num dia.**
A planilha do caixa daquele dia ainda não foi importada: o balanço da semana está incompleto até ela entrar.

**A tela diz "sem conexão com o sistema".**
O computador onde o sistema roda está desligado ou o sistema parou. Avise quem cuida do sistema (N2,
`sustentar/suporte-e-sla.md`). O caixa continua vendendo normalmente.

**Esqueci a senha.**
Quem cuida do sistema troca: `python backend/manage.py changepassword <login>`.

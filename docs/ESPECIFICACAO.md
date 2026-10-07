# Especificação — requisitos, restrições e escopo

Transcrição da **Apostila III**. Os textos dos requisitos são os da apostila, sem reescrita.

---

## Requisitos funcionais

| ID | Requisito | Descrição | Prioridade |
|---|---|---|---|
| RF01 | Cadastrar produtos | Nome, categoria, unidade de medida, se é perecível e por quantos dias dura, preço de custo, preço de venda e estoque mínimo. | Essencial |
| RF02 | Cadastrar fornecedores | Nome, contato e, principalmente, em quantos dias o fornecedor entrega depois do pedido. | Essencial |
| RF03 | Registrar entrada de mercadoria | Cada carga que chega vira um lote, com quantidade, custo, fornecedor e data de validade. | Essencial |
| RF04 | Registrar perdas | O que venceu, quebrou ou estragou sai do estoque com o motivo anotado. | Essencial |
| RF05 | Dar baixa no estoque por venda | Toda venda reduz o saldo do produto, tirando do lote de validade mais próxima. | Essencial |
| RF06 | Importar as vendas do caixa | Trazer para o sistema o que foi vendido, a partir do que o caixa eletrônico da loja registrou. | Essencial |
| RF07 | Consultar o estoque | Ver o saldo por produto e por categoria, com destaque para o que está abaixo do mínimo e o que está vencendo. | Essencial |
| RF08 | Calcular a previsão de consumo | A partir do histórico de vendas, estimar quanto sai por dia e em quantos dias o produto acaba. | Essencial |
| RF09 | Avisar que um produto vai acabar | Enviar aviso ao celular do dono antes de o produto faltar, com antecedência suficiente para o fornecedor entregar. | Essencial |
| RF10 | Avisar que um produto vai vencer | Enviar aviso ao celular quando um lote perecível estiver perto da data de validade. | Essencial |
| RF11 | Sugerir quanto comprar | Indicar a quantidade a pedir de cada produto, considerando o prazo do fornecedor. | Importante |
| RF12 | Fazer o fechamento de caixa | Comparar o dinheiro contado com o valor apurado pelo sistema e registrar a diferença. | Importante |
| RF13 | Emitir o balanço da semana | Vendas, perdas e resultado do período, com as perdas separadas das vendas. | Importante |
| RF14 | Controlar o acesso por perfil | Cada pessoa enxerga e faz apenas o que corresponde à sua função na loja. | Importante |
| RF15 | Marcar produtos críticos | Sinalizar os itens que não podem faltar no fim de semana, para serem avaliados com antecedência. | Importante |
| RF16 | Apoiar o inventário mensal | Auxiliar a contagem física que o dono já faz uma vez por mês. | **Desejável** |
| RF17 | Mostrar produtos vendidos juntos | Identificar pares de produtos que costumam sair na mesma compra. | **Desejável** |

**RF16 e RF17 não entram na primeira versão.** A Apostila IV, seção 8, marca os dois como
"não coberto" e diz, com todas as letras, que foi escolha e não esquecimento. Não implemente sem
decisão do grupo.

---

## Requisitos não-funcionais

| ID | Requisito | O que significa no código |
|---|---|---|
| RNF01 | O sistema avisa; o usuário não consulta | O valor do produto está no envio automático, não na tela. Avisos chegam ao celular sem o dono abrir nada. |
| RNF02 | Simplicidade de uso | Telas operáveis por quem tem informática básica, sem treinamento longo. |
| RNF03 | Treinamento incluído | Cada pessoa aprende só a parte que usa. |
| RNF04 | Três usuários com acesso | Dono, esposa e sobrinho. Os dois funcionários não acessam. |
| RNF05 | Entrada de dados rápida | A operação da loja não para para alimentar o sistema. Formulários curtos, nada de campo opcional obrigatório. |
| RNF06 | Rodar em equipamento modesto | O computador da loja é antigo. Telas leves, sem framework pesado no navegador. |
| RNF07 | A venda não pode parar | Se a internet cair, o caixa continua vendendo; só o aviso atrasa. O sistema **nunca** fica no caminho da venda. |
| RNF08 | Disponibilidade em horário comercial | O serviço de avisos precisa estar no ar enquanto a loja funciona. |
| RNF09 | Backup diário fora do servidor | Uma cópia do banco por dia, guardada em outro lugar. |
| RNF10 | Vocabulário do cliente | Telas e mensagens usam os termos da loja, não os técnicos. |
| RNF11 | Respeitar os horários de pico | Nenhum aviso nos dois períodos de maior movimento (ver RN12). |
| RNF12 | Segurança básica | Senha com hash, uma única porta exposta na internet, banco sem acesso externo. |

Citações do cliente que sustentam RNF01, RNF02, RNF05, RNF06 e RNF10 estão na Apostila III,
seção 4.

---

## Restrições

Limites que a equipe não escolheu.

| ID | Restrição | O que significa na prática |
|---|---|---|
| R01 | Orçamento | Investimento inicial em torno de R$ 10.000 e mensalidade baixa. |
| R02 | Equipe pequena | Cinco pessoas na loja, apenas três com acesso ao sistema. |
| R03 | Espaço físico apertado | A loja não tem sala de equipamento, nem nobreak. |
| R04 | Computador antigo | O equipamento disponível é velho e não foi comprado para isso. |
| R05 | O caixa não será substituído | O caixa eletrônico continua registrando a venda e emitindo a nota fiscal. |
| R06 | Conhecimento de informática básico | Nenhum usuário tem formação técnica. |
| R07 | Dois picos de movimento por dia | 10h30 ao almoço e 16h30 às 18h a loja fica cheia. |
| R08 | A loja tem internet | Confirmado pelo cliente — viabiliza o aviso pelo celular. |

**R03 é a restrição que mais influencia o projeto** e pesa contra rodar o sistema dentro da loja.

**R06 e RNF02 valem para cada tela que você escrever.** Se a tela precisa de explicação, ela está
errada.

---

## Fora de escopo

| Não faz parte do sistema | Motivo |
|---|---|
| Emissão de nota fiscal | O caixa eletrônico já emite quando o cliente pede. |
| Substituir o caixa / PDV | Não é o problema relatado e multiplicaria o custo. |
| Leitor de código de barras | A loja não possui leitor; o operador digita o produto no caixa. |
| Controle de vale-alimentação | O cliente informou que não trabalha com essa forma de pagamento. |
| Venda fiado | Não há requisito confirmado. Precisa ser perguntado antes de entrar. |
| Contagem de estoque por foto | Erra bastante e custa caro. Um aviso errado sobre carne é pior que nenhum aviso. |
| Controle financeiro e contábil | A loja já tem contador, que recebe as notas fiscais. |

---

## Dimensionamento

Números que a Apostila III usa para dimensionar a máquina — servem também para você saber o
tamanho dos problemas:

- até **2.000 produtos** diferentes
- **300 a 600 vendas por dia**
- **3 pessoas** usando o sistema
- o banco cresce perto de **1 GB por ano**

Isso significa que o sistema é pequeno. Não há motivo para cache, fila de mensagens, microsserviço
ou qualquer coisa do gênero. O que exige atenção não é potência: é continuidade. Se a máquina cair
num sábado, o dono volta a controlar a loja no olho — e sábado é o dia de maior movimento.

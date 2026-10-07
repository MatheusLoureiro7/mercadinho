# avisos Specification

## Purpose

Avisar o dono no celular, pelo Telegram, antes que um produto vença ou acabe — sem ele abrir nada
e sem atrapalhar os horários de pico. Origem: RF09, RF10, RNF01, RNF11, RN05, RN08, RN10, RN12,
RN13; operação 03. Tarefas H1 a H7.

## Requirements

### Requirement: Aviso de validade próxima

A rodada diária SHALL gerar um `alerta` `tipo = 'VALIDADE'`, `status = 'PENDENTE'` para cada lote
de produto perecível com saldo e que esteja a N dias ou menos do vencimento, sendo N o parâmetro
`dias_aviso_validade`. (RN05, RF10)

A apostila diz que N vale por categoria, mas o parâmetro é global (docs/LACUNAS.md, L01).

Mensagem no vocabulário da loja, por exemplo: "O presunto vence em 3 dias — 2,5 kg na prateleira."

#### Scenario: Lote dentro do prazo de aviso
- **WHEN** em 21/09 um lote vence em 24/09 e o parâmetro é 3 dias
- **THEN** é gerado aviso de validade para o lote

#### Scenario: Lote fora do prazo de aviso
- **WHEN** em 21/09 um lote vence em 30/09 e o parâmetro é 3 dias
- **THEN** nenhum aviso é gerado

#### Scenario: Lote zerado
- **WHEN** o lote está dentro do prazo mas com `quantidade_atual` igual a zero
- **THEN** nenhum aviso é gerado

### Requirement: Aviso de ruptura

Quando o saldo do produto cair igual ou abaixo do ponto de pedido, a rodada diária SHALL gerar um
`alerta` `tipo = 'RUPTURA'`. (RN08, RF09)

Mensagem no vocabulário da loja, por exemplo: "O frango acaba em 2 dias."

#### Scenario: Saldo no ponto de pedido
- **WHEN** o saldo da carne é 28 kg e o ponto de pedido é 28,8 kg
- **THEN** é gerado aviso de ruptura

#### Scenario: Saldo acima do ponto de pedido
- **WHEN** o saldo está acima do ponto de pedido
- **THEN** nenhum aviso de ruptura é gerado

### Requirement: Itens críticos de fim de semana

Na quinta-feira, os produtos com `critico_fim_semana` SHALL ser avaliados contra
`ponto_pedido × (1 + folga_fim_semana_pct / 100)`, gerando `alerta` `tipo = 'FIM_SEMANA'`, para
garantir presença no sábado, domingo e vésperas de feriado. (RN10, RF15)

O calendário de feriados não está definido (docs/LACUNAS.md, L03).

#### Scenario: Carvão na quinta-feira
- **WHEN** é quinta-feira e o saldo do carvão, marcado como crítico, está abaixo do ponto de pedido com a folga
- **THEN** é gerado aviso de fim de semana

#### Scenario: Outro dia da semana
- **WHEN** não é quinta-feira
- **THEN** a avaliação de fim de semana não gera aviso

### Requirement: Janela de silêncio

Nenhum aviso SHALL ser enviado entre 10h30 e 13h00 nem entre 16h30 e 18h00, no horário local da loja
(parâmetros `janela_silencio_manha` e `janela_silencio_tarde`). A verificação MUST acontecer na
hora do envio, não da geração; o aviso retido vai para `status = 'SEGURADO'` e sai na primeira
janela livre. (RN12, RNF11)

#### Scenario: Aviso no pico do almoço
- **WHEN** um aviso é gerado às 11h15
- **THEN** ele fica `SEGURADO`
- **AND** é enviado às 13h05

#### Scenario: Aviso fora do pico
- **WHEN** o envio acontece às 09h00
- **THEN** o aviso é enviado

### Requirement: Avisos agrupados em uma mensagem

Todos os avisos `PENDENTE` e `SEGURADO` de uma mesma janela de envio SHALL ser reunidos em uma
única mensagem, ordenados por urgência (severidade, depois `gerado_em`), enviados numa só chamada
ao Telegram e marcados como `ENVIADO` com o mesmo `enviado_em`. (RN13)

Os valores de severidade não estão definidos (docs/LACUNAS.md, L11).

#### Scenario: Seis avisos pendentes
- **WHEN** há 6 avisos pendentes às 13h05
- **THEN** é enviada uma única mensagem com os 6 itens, começando pelo mais urgente

### Requirement: Canal de aviso substituível

O envio SHALL passar por uma interface de canal (`CanalDeAviso.enviar(destinatario, mensagem)`),
com o Telegram como implementação, e o canal usado fica em `alerta.canal`. O aviso vai para o
`telegram_chat_id` do usuário `DONO`. (D04; tarefas H5 e H6)

#### Scenario: Aviso enviado pelo Telegram
- **WHEN** um aviso é enviado
- **THEN** ele fica registrado com `canal = 'TELEGRAM'` e destinatário o usuário `DONO`

### Requirement: Resposta do dono

A resposta do dono no Telegram (por exemplo "Sim, pedir") SHALL ser recebida pela API e gravada em
`alerta.resposta_usuario`. (Operação 03, passos 13 e 14; tarefa H7)

#### Scenario: Dono responde
- **WHEN** o dono responde "Sim, pedir" a um aviso
- **THEN** a resposta fica registrada no aviso

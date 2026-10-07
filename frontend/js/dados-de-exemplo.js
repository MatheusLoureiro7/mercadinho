/*
 * DADOS DE EXEMPLO — tarefa B5 (docs/ROTEIRO.md).
 *
 * "As telas B5 e B6 começam com dados fixos no próprio código e só em B7 passam a falar com a API."
 * Este módulo faz o papel da API enquanto isso: mesmos nomes de campo e mesmo formato de resposta e
 * de erro ({"erro": {"codigo", "mensagem", "campos"}}). Na B7 ele é trocado por js/api.js e
 * apagado. As recusas abaixo só imitam as respostas da API para a tela poder ser montada — a regra
 * de verdade mora no backend.
 */

const categorias = [
  { id: 1, nome: "Açougue", perecivel_padrao: true },
  { id: 2, nome: "Bebidas", perecivel_padrao: false },
  { id: 3, nome: "Frios", perecivel_padrao: true },
  { id: 4, nome: "Secos e molhados", perecivel_padrao: false },
];

const fornecedores = [
  { id: 1, nome: "Atacadão Central", prazo_entrega_dias: 2 },
  { id: 2, nome: "Distribuidora Sol", prazo_entrega_dias: 1 },
  { id: 3, nome: "Frigorífico Boi Bom", prazo_entrega_dias: 3 },
];

let produtos = [
  produto(1, "Alcatra", 1, 3, "KG", true, 3, "39.90", "54.90", "5.000", true),
  produto(2, "Asinha de frango", 1, 3, "KG", true, 4, "14.50", "21.90", "4.000", true),
  produto(3, "Linguiça toscana", 1, 3, "KG", true, 5, "18.00", "26.90", "3.000", true),
  produto(4, "Cerveja lata 350 ml", 2, 2, "UN", false, null, "2.90", "4.49", "48.000", true),
  produto(5, "Refrigerante 2 L", 2, 2, "UN", false, null, "6.20", "9.99", "12.000", false),
  produto(6, "Iogurte natural", 3, 2, "UN", true, 15, "2.10", "3.79", null, false),
  produto(7, "Presunto", 3, 2, "KG", true, 7, "28.00", "42.90", "2.000", false),
  produto(8, "Arroz 5 kg", 4, 1, "PCT", false, null, "21.00", "27.90", "10.000", false),
  produto(9, "Carvão 3 kg", 4, 1, "PCT", false, null, "11.00", "18.90", "8.000", true),
  produto(10, "Feijão carioca 1 kg", 4, 1, "PCT", false, null, "6.50", "8.99", "10.000", false),
];

function produto(id, nome, categoria, fornecedor, unidade, perecivel, durabilidade, custo, venda, minimo, critico) {
  return {
    id: id,
    nome: nome,
    categoria: categoria,
    categoria_nome: categorias.find((c) => c.id === categoria).nome,
    fornecedor_padrao: fornecedor,
    fornecedor_padrao_nome: fornecedores.find((f) => f.id === fornecedor).nome,
    unidade_medida: unidade,
    perecivel: perecivel,
    durabilidade_dias: durabilidade,
    preco_custo: custo,
    preco_venda: venda,
    estoque_minimo: minimo,
    critico_fim_semana: critico,
  };
}

function resposta(valor) {
  // Pequena espera, como a rede, para a tela mostrar o estado "carregando".
  return new Promise((resolver) => setTimeout(() => resolver(JSON.parse(JSON.stringify(valor))), 150));
}

function semAcento(texto) {
  return texto.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
}

export const fonte = {
  nome: "dados de exemplo",

  listarCategorias() {
    return resposta(categorias.slice().sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR")));
  },

  listarFornecedores() {
    return resposta(fornecedores);
  },

  listarProdutos(filtros) {
    const busca = semAcento((filtros && filtros.busca) || "");
    const categoria = filtros && filtros.categoria ? Number(filtros.categoria) : null;
    const lista = produtos
      .filter((p) => !busca || semAcento(p.nome).indexOf(busca) >= 0)
      .filter((p) => !categoria || p.categoria === categoria)
      .sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"));
    return resposta({ ok: true, dados: lista });
  },

  criarCategoria(dados) {
    const nome = (dados.nome || "").trim();
    if (!nome) return resposta(erroDeCampos({ nome: ["Este campo não pode ser em branco."] }));
    if (categorias.some((c) => c.nome === nome)) {
      return resposta(erroDeCampos({ nome: ["Já existe uma categoria com esse nome."] }));
    }
    const nova = { id: categorias.length + 1, nome: nome, perecivel_padrao: !!dados.perecivel_padrao };
    categorias.push(nova);
    return resposta({ ok: true, dados: nova });
  },

  salvarProduto(dados, id) {
    const campos = {};
    if (!dados.nome) campos.nome = ["Este campo não pode ser em branco."];
    if (!dados.categoria) campos.categoria = ["Escolha a categoria do produto."];
    if (!dados.unidade_medida) campos.unidade_medida = ["Escolha a unidade: KG, UN, L ou PCT."];
    if (Object.keys(campos).length) return resposta(erroDeCampos(campos));

    const repetido = produtos.some((p) => p.nome === dados.nome && p.categoria === Number(dados.categoria) && p.id !== id);
    if (repetido) return resposta(erroDeCampos({ nome: ["Já existe um produto com esse nome nesta categoria."] }));

    if (dados.perecivel && !(Number(dados.durabilidade_dias) > 0)) {
      const mensagem =
        "Produto perecível precisa do prazo de durabilidade em dias. " +
        "Sem ele o sistema não consegue avisar quando o produto vai vencer.";
      return resposta({
        ok: false,
        erro: { codigo: "regra_de_negocio", regra: "RN03", mensagem: mensagem, campos: { durabilidade_dias: [mensagem] } },
      });
    }

    const salvo = produto(
      id || produtos.length + 1,
      dados.nome,
      Number(dados.categoria),
      dados.fornecedor_padrao ? Number(dados.fornecedor_padrao) : 1,
      dados.unidade_medida,
      !!dados.perecivel,
      dados.durabilidade_dias ? Number(dados.durabilidade_dias) : null,
      dados.preco_custo,
      dados.preco_venda,
      dados.estoque_minimo,
      !!dados.critico_fim_semana
    );
    if (!dados.fornecedor_padrao) {
      salvo.fornecedor_padrao = null;
      salvo.fornecedor_padrao_nome = null;
    }
    produtos = produtos.filter((p) => p.id !== salvo.id).concat([salvo]);
    return resposta({ ok: true, dados: salvo });
  },
};

function erroDeCampos(campos) {
  return { ok: false, erro: { codigo: "validacao", mensagem: "Confira os campos destacados.", campos: campos } };
}

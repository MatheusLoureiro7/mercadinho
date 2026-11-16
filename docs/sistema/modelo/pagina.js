/*
 * Documentação do Sistema — o que a página faz (X2, 16/11/2026). Entra dentro do HTML gerado.
 * Sem biblioteca: procurar no menu ("/"), marcar no menu o documento que está na tela, trocar o
 * tema, copiar bloco de código e abrir o menu no celular. Sem isto a página continua legível.
 */
(function () {
  "use strict";
  var raiz = document.documentElement;
  var $ = function (id) { return document.getElementById(id); };
  var semAcento = function (texto) {
    return texto.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
  };

  // ---------------------------------------------------------------- Tema (lembrado neste navegador)
  function guardado() { try { return localStorage.getItem("doc-tema"); } catch (e) { return null; } }
  function escuroAgora() {
    var tema = raiz.dataset.tema;
    return tema ? tema === "escuro" : window.matchMedia("(prefers-color-scheme: dark)").matches;
  }
  function rotular() { $("botao-tema").textContent = escuroAgora() ? "Tema claro" : "Tema escuro"; }
  if (guardado()) raiz.dataset.tema = guardado();
  rotular();
  $("botao-tema").addEventListener("click", function () {
    raiz.dataset.tema = escuroAgora() ? "claro" : "escuro";
    try { localStorage.setItem("doc-tema", raiz.dataset.tema); } catch (e) { /* sem armazenamento: vale só agora */ }
    rotular();
  });

  // ---------------------------------------------------------------- Menu no celular
  var abrir = $("abrir-menu");
  function fechar() { document.body.classList.remove("menu-aberto"); abrir.setAttribute("aria-expanded", "false"); }
  abrir.addEventListener("click", function () {
    var aberto = document.body.classList.toggle("menu-aberto");
    abrir.setAttribute("aria-expanded", String(aberto));
    if (aberto) $("campo-busca").focus();
  });
  $("menu").addEventListener("click", function (evento) { if (evento.target.closest("a")) fechar(); });
  document.addEventListener("keydown", function (evento) { if (evento.key === "Escape") fechar(); });

  // ---------------------------------------------------------------- Procurar
  // Procura no título, nas seções e no texto de cada documento; o menu mostra só o que casou.
  var itens = Array.prototype.map.call(document.querySelectorAll("#menu li[data-doc]"), function (li) {
    var artigo = $(li.dataset.doc);
    return {
      li: li,
      titulo: semAcento(li.querySelector(".menu__doc").textContent),
      secoes: Array.prototype.map.call(li.querySelectorAll(".menu__secoes li"), function (s) {
        return { li: s, texto: semAcento(s.textContent) };
      }),
      corpo: artigo ? semAcento(artigo.textContent) : "",
    };
  });
  var campo = $("campo-busca");
  function procurar() {
    var termo = semAcento(campo.value.trim());
    var achados = 0;
    $("menu").classList.toggle("buscando", termo !== "");
    itens.forEach(function (item) {
      var noTitulo = item.titulo.indexOf(termo) >= 0;
      var algumaSecao = false;
      item.secoes.forEach(function (secao) {
        var casa = termo === "" || noTitulo || secao.texto.indexOf(termo) >= 0;
        secao.li.hidden = !casa;
        algumaSecao = algumaSecao || (termo !== "" && secao.texto.indexOf(termo) >= 0);
      });
      var casa = termo === "" || noTitulo || algumaSecao || item.corpo.indexOf(termo) >= 0;
      item.li.hidden = !casa;
      if (casa) achados += 1;
    });
    document.querySelectorAll("#menu .menu__grupo").forEach(function (grupo) {
      grupo.hidden = !grupo.querySelector("li[data-doc]:not([hidden])");
    });
    $("resultado-busca").textContent =
      termo === "" ? "" : achados === 0 ? "Nenhum documento fala disso." : achados === 1 ? "1 documento." : achados + " documentos.";
  }
  campo.addEventListener("input", procurar);
  campo.addEventListener("keydown", function (evento) {
    if (evento.key === "Enter") {
      var primeiro = document.querySelector("#menu li[data-doc]:not([hidden]) .menu__doc");
      if (primeiro) { primeiro.click(); primeiro.focus(); }
    } else if (evento.key === "Escape") {
      campo.value = "";
      procurar();
    }
  });
  document.addEventListener("keydown", function (evento) {
    var digitando = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
    if (evento.key === "/" && !digitando && !evento.ctrlKey && !evento.metaKey) {
      evento.preventDefault();
      campo.focus();
      campo.select();
    }
  });

  // ---------------------------------------------------------------- Onde estou
  var porDoc = {};
  document.querySelectorAll("#menu li[data-doc]").forEach(function (li) { porDoc[li.dataset.doc] = li.querySelector(".menu__doc"); });
  var docs = Array.prototype.slice.call(document.querySelectorAll("article.doc"));
  var atual = null;
  function marcar() {
    var linha = window.innerHeight * 0.3;
    var naTela = null;
    docs.forEach(function (doc) { if (doc.getBoundingClientRect().top <= linha) naTela = doc; });
    var id = naTela ? naTela.id : null;
    if (id === atual) return;
    if (atual && porDoc[atual]) porDoc[atual].removeAttribute("aria-current");
    atual = id;
    if (id && porDoc[id]) {
      porDoc[id].setAttribute("aria-current", "true");
      if (!campo.value) porDoc[id].scrollIntoView({ block: "nearest" });
    }
  }
  var esperando = false;
  window.addEventListener("scroll", function () {
    if (esperando) return;
    esperando = true;
    window.requestAnimationFrame(function () { esperando = false; marcar(); });
  }, { passive: true });
  marcar();

  // ---------------------------------------------------------------- Copiar bloco de código
  document.querySelectorAll(".codigo").forEach(function (bloco) {
    if (!navigator.clipboard) return;
    var botao = document.createElement("button");
    botao.type = "button";
    botao.className = "botao copiar";
    botao.textContent = "Copiar";
    botao.addEventListener("click", function () {
      navigator.clipboard.writeText(bloco.querySelector("pre").textContent).then(function () {
        botao.textContent = "Copiado";
        setTimeout(function () { botao.textContent = "Copiar"; }, 1600);
      });
    });
    bloco.appendChild(botao);
  });
})();

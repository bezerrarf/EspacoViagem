/**
 * ====================================================================
 * SCRIPT DE BUSCA CÓSMICA CENTRALIZADA (NASA + WIKIPEDIA)
 * ====================================================================
 * - Filtragem ao vivo ao digitar (debounce de 400ms)
 * - Abertura de imagem em MODAL DE ALTA RESOLUÇÃO ao clicar
 * - Botão "Carregar Mais Imagens" com paginação real da API
 */

document.addEventListener("DOMContentLoaded", function () {
    // ---- Referências dos elementos HTML ----
    const inputBusca = document.getElementById("input-busca-cosmica");
    const btnBusca = document.getElementById("btn-disparar-busca");
    const painelResultados = document.getElementById("painel-resultados-busca");
    const containerGradeResultados = document.getElementById("grade-resultados-busca");
    const tituloTermoBuscado = document.getElementById("termo-busca-destaque");
    const resumoWikipediaBox = document.getElementById("resumo-wikipedia-busca");

    if (!inputBusca || !btnBusca || !painelResultados) return;

    let temporizadorDebounce = null;
    let termoBuscaAtual = "";
    let paginaAtual = 1;
    let temMaisImagens = false;

    // ====================================================================
    // MODAL DE VISUALIZAÇÃO DA IMAGEM EM ALTA RESOLUÇÃO
    // ====================================================================
    const modalOverlay = document.createElement("div");
    modalOverlay.id = "modal-imagem-cosmica";
    modalOverlay.style.cssText = `
        display: none; position: fixed; inset: 0; z-index: 9999;
        background: rgba(0,0,0,0.95); backdrop-filter: blur(8px);
        align-items: center; justify-content: center; padding: 1.5rem;
        cursor: zoom-out;
    `;
    modalOverlay.innerHTML = `
        <div style="position: relative; max-width: 1100px; width: 100%; max-height: 92vh; display: flex; flex-direction: column; gap: 1rem;" onclick="event.stopPropagation()">
            <button id="btn-fechar-modal" style="position: absolute; top: -3rem; right: 0; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #fff; border-radius: 9999px; width: 40px; height: 40px; font-size: 1.2rem; cursor: pointer; display: flex; align-items: center; justify-content: center;">✕</button>
            <img id="modal-imagem-src" src="" alt="" style="width: 100%; max-height: 72vh; object-fit: contain; border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.9);">
            <div style="background: rgba(17,24,39,0.95); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 1.25rem;">
                <h3 id="modal-titulo" style="color: #fff; font-family: 'Space Grotesk', sans-serif; margin-bottom: 0.5rem;"></h3>
                <p id="modal-descricao" style="color: #94a3b8; font-size: 0.88rem; line-height: 1.6; margin-bottom: 0.5rem;"></p>
                <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                    <span id="modal-data" style="color: #64748b; font-size: 0.8rem;"></span>
                    <a id="modal-link-hd" href="#" target="_blank" style="color: #38bdf8; font-size: 0.85rem; font-weight: 600;">Abrir em Alta Resolução (HD) →</a>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modalOverlay);

    // Fecha o modal ao clicar no fundo escuro
    modalOverlay.addEventListener("click", () => fecharModal());
    document.getElementById("btn-fechar-modal").addEventListener("click", () => fecharModal());

    // Fecha o modal com a tecla Escape
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") fecharModal(); });

    function abrirModal(titulo, descricaoCompleta, urlHd, dataRegistro) {
        document.getElementById("modal-imagem-src").src = urlHd;
        document.getElementById("modal-imagem-src").alt = titulo;
        document.getElementById("modal-titulo").innerText = titulo;
        document.getElementById("modal-descricao").innerText = descricaoCompleta || "Fotografia oficial da biblioteca de imagens da NASA.";
        document.getElementById("modal-data").innerText = dataRegistro ? `Data: ${dataRegistro}` : "";
        document.getElementById("modal-link-hd").href = urlHd;
        modalOverlay.style.display = "flex";
        document.body.style.overflow = "hidden";
    }

    function fecharModal() {
        modalOverlay.style.display = "none";
        document.body.style.overflow = "";
    }

    // ====================================================================
    // RENDERIZAÇÃO DOS CARTÕES DE IMAGEM (COM EVENTO DE CLIQUE PARA MODAL)
    // ====================================================================
    function renderizarCartaoNasa(item, container) {
        const cartao = document.createElement("div");
        cartao.className = "cartao-astro";
        cartao.style.cursor = "pointer";
        cartao.innerHTML = `
            <div class="container-imagem-astro" style="position: relative;">
                <img src="${item.url_imagem}" alt="${item.titulo}" class="imagem-astro"
                    onerror="this.src='https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800'">
                <div style="position: absolute; inset: 0; background: rgba(0,0,0,0); transition: background 0.3s; display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.3s;" class="overlay-zoom">
                    <span style="font-size: 2.5rem;">🔍</span>
                </div>
            </div>
            <div class="corpo-astro">
                <span class="badge-nasa" style="width: fit-content;">NASA: ${item.centro_nasa || 'Acervo'}</span>
                <h4 class="nome-astro" style="font-size: 1.05rem; margin-top: 0.4rem;">${item.titulo}</h4>
                <p style="color: #94a3b8; font-size: 0.83rem; line-height: 1.5;">${item.descricao}</p>
                <span style="color: #64748b; font-size: 0.75rem; margin-top: auto;">📅 ${item.data_criacao || 'Registro NASA'}</span>
            </div>
        `;

        // Efeito de hover no overlay
        const overlay = cartao.querySelector(".overlay-zoom");
        cartao.querySelector(".container-imagem-astro").addEventListener("mouseenter", () => {
            overlay.style.opacity = "1";
            overlay.style.background = "rgba(0,0,0,0.4)";
        });
        cartao.querySelector(".container-imagem-astro").addEventListener("mouseleave", () => {
            overlay.style.opacity = "0";
            overlay.style.background = "rgba(0,0,0,0)";
        });

        // Clique na imagem abre o modal em alta resolução
        cartao.querySelector(".container-imagem-astro").addEventListener("click", () => {
            abrirModal(item.titulo, item.descricao_completa, item.url_hd || item.url_imagem, item.data_criacao);
        });

        container.appendChild(cartao);
    }

    // ====================================================================
    // FUNÇÃO PRINCIPAL DE BUSCA
    // ====================================================================
    async function executarBuscaCosmica(termo, pagina = 1) {
        const termoLimpo = termo.trim();

        if (!termoLimpo) {
            painelResultados.style.display = "none";
            return;
        }

        // Feedback visual
        if (pagina === 1) {
            btnBusca.innerText = "Buscando... 🔭";
            btnBusca.disabled = true;
        }

        // Remove botão "Carregar Mais" anterior
        const btnCarregarMaisExistente = document.getElementById("btn-carregar-mais-nasa");
        if (btnCarregarMaisExistente) btnCarregarMaisExistente.remove();

        try {
            const usuarioAtivo = JSON.parse(localStorage.getItem("usuario_espacial") || "null");
            const idUsuario = usuarioAtivo ? usuarioAtivo.id : "";

            const resposta = await fetch(`/api/busca?termo=${encodeURIComponent(termoLimpo)}&usuario_id=${idUsuario}&pagina=${pagina}`);
            const dados = await resposta.json();

            if (dados.sucesso) {
                // 1. Atualiza Wikipedia (somente na primeira página)
                if (pagina === 1 && resumoWikipediaBox && dados.wikipedia) {
                    resumoWikipediaBox.innerHTML = `
                        <div class="box-resumo-wiki" style="margin-bottom: 1.5rem;">
                            <span class="badge-wiki">📚 Resumo Científico (Wikipedia)</span>
                            <h3 style="color: #ffffff; margin: 0.5rem 0;">${dados.wikipedia.titulo}</h3>
                            <p style="color: #cbd5e1; line-height: 1.6;">${dados.wikipedia.resumo}</p>
                            <a href="${dados.wikipedia.url_pagina_completa}" target="_blank"
                               style="color: #38bdf8; font-size: 0.85rem; font-weight: 600; display: inline-block; margin-top: 0.5rem;">
                               Ler artigo completo na Wikipedia →
                            </a>
                        </div>
                    `;
                }

                // 2. Renderiza os cartões (limpa se for nova busca, acumula se for "carregar mais")
                if (pagina === 1) {
                    containerGradeResultados.innerHTML = "";
                }

                if (dados.resultados_nasa && dados.resultados_nasa.length > 0) {
                    dados.resultados_nasa.forEach(item => {
                        renderizarCartaoNasa(item, containerGradeResultados);
                    });
                } else if (pagina === 1) {
                    containerGradeResultados.innerHTML = `
                        <p style="color: #94a3b8; grid-column: 1/-1; text-align: center; padding: 2rem;">
                            Nenhuma fotografia encontrada para "<strong>${termoLimpo}</strong>" na NASA.
                        </p>`;
                }

                // 3. Exibe o botão "Carregar Mais" se houver mais imagens
                temMaisImagens = dados.tem_mais;
                if (temMaisImagens) {
                    const btnMais = document.createElement("div");
                    btnMais.id = "btn-carregar-mais-nasa";
                    btnMais.style.cssText = "grid-column: 1 / -1; display: flex; justify-content: center; margin-top: 0.5rem;";
                    btnMais.innerHTML = `
                        <button id="btn-ver-mais" style="
                            background: rgba(56, 189, 248, 0.12);
                            border: 1px solid rgba(56, 189, 248, 0.4);
                            color: #38bdf8; font-weight: 700; font-size: 0.95rem;
                            padding: 0.9rem 2.5rem; border-radius: 9999px; cursor: pointer;
                            transition: all 0.3s; display: flex; align-items: center; gap: 0.5rem;
                        ">
                            🚀 Carregar Mais Imagens da NASA (Página ${pagina + 1})
                        </button>
                    `;
                    containerGradeResultados.parentElement.appendChild(btnMais);

                    document.getElementById("btn-ver-mais").addEventListener("click", () => {
                        paginaAtual++;
                        executarBuscaCosmica(termoBuscaAtual, paginaAtual);
                    });
                    document.getElementById("btn-ver-mais").addEventListener("mouseenter", (e) => {
                        e.target.style.background = "rgba(56, 189, 248, 0.25)";
                        e.target.style.transform = "scale(1.03)";
                    });
                    document.getElementById("btn-ver-mais").addEventListener("mouseleave", (e) => {
                        e.target.style.background = "rgba(56, 189, 248, 0.12)";
                        e.target.style.transform = "scale(1)";
                    });
                }

                if (tituloTermoBuscado) tituloTermoBuscado.innerText = termoLimpo;
                painelResultados.style.display = "block";

                // Scrolla ao painel apenas na primeira página
                if (pagina === 1) {
                    painelResultados.scrollIntoView({ behavior: "smooth", block: "start" });
                }
            }
        } catch (erro) {
            console.error("Erro na busca cósmica:", erro);
        } finally {
            btnBusca.innerText = "Pesquisar 🚀";
            btnBusca.disabled = false;
        }
    }

    // ====================================================================
    // EVENTOS
    // ====================================================================

    // Botão pesquisar (clique)
    btnBusca.addEventListener("click", () => {
        termoBuscaAtual = inputBusca.value;
        paginaAtual = 1;
        executarBuscaCosmica(termoBuscaAtual, 1);
    });

    // Tecla Enter
    inputBusca.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            termoBuscaAtual = inputBusca.value;
            paginaAtual = 1;
            executarBuscaCosmica(termoBuscaAtual, 1);
        }
    });

    // Filtragem ao vivo ao digitar (debounce 400ms)
    inputBusca.addEventListener("input", function () {
        clearTimeout(temporizadorDebounce);
        const termo = this.value;

        if (termo.trim().length >= 2) {
            temporizadorDebounce = setTimeout(() => {
                termoBuscaAtual = termo;
                paginaAtual = 1;
                executarBuscaCosmica(termoBuscaAtual, 1);
            }, 400);
        } else if (termo.trim().length === 0) {
            painelResultados.style.display = "none";
        }
    });

    // Sugestões rápidas
    document.querySelectorAll(".btn-sugestao").forEach(btn => {
        btn.addEventListener("click", function () {
            const termo = this.getAttribute("data-termo") || this.innerText.replace(/^[^\w\sÀ-ÿ]+/, "").trim();
            inputBusca.value = termo;
            termoBuscaAtual = termo;
            paginaAtual = 1;
            executarBuscaCosmica(termoBuscaAtual, 1);
        });
    });
});

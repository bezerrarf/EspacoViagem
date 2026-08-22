/**
 * ====================================================================
 * SCRIPT DE CONTROLE DO CARROSSEL PLANETÁRIO
 * ====================================================================
 * Gerencia a navegação suave por setas, autoplay a cada 6 segundos
 * e pausa automática quando o usuário passa o mouse sobre o carrossel.
 */

document.addEventListener("DOMContentLoaded", function () {
    const trilho = document.getElementById("trilho-planetas");
    const btnAnterior = document.getElementById("btn-seta-anterior");
    const btnProximo = document.getElementById("btn-seta-proximo");

    if (!trilho) return;

    const distanciaRolagem = 345;
    let intervaloAutoplay = null;

    function avancarCarrossel() {
        if (trilho.scrollLeft + trilho.clientWidth >= trilho.scrollWidth - 15) {
            trilho.scrollTo({ left: 0, behavior: "smooth" });
        } else {
            trilho.scrollBy({ left: distanciaRolagem, behavior: "smooth" });
        }
    }

    function voltarCarrossel() {
        if (trilho.scrollLeft <= 10) {
            trilho.scrollTo({ left: trilho.scrollWidth, behavior: "smooth" });
        } else {
            trilho.scrollBy({ left: -distanciaRolagem, behavior: "smooth" });
        }
    }

    if (btnProximo) btnProximo.addEventListener("click", avancarCarrossel);
    if (btnAnterior) btnAnterior.addEventListener("click", voltarCarrossel);

    function iniciarAutoplay() {
        if (!intervaloAutoplay) {
            intervaloAutoplay = setInterval(avancarCarrossel, 6000);
        }
    }

    function pausarAutoplay() {
        clearInterval(intervaloAutoplay);
        intervaloAutoplay = null;
    }

    trilho.addEventListener("mouseenter", pausarAutoplay);
    trilho.addEventListener("mouseleave", iniciarAutoplay);

    iniciarAutoplay();
});
